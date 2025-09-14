from flask import Flask, request, jsonify
import requests
import hashlib
import logging
from datetime import datetime
import os
import re

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.source_api_url = os.getenv('SOURCE_API_URL', 'https://mengtopup.shop/api')
        self.source_api_url = self.source_api_url.rstrip('/')
    
    def _call_source_api(self, md5_hash: str):
        """
        Internal method to call the hidden source API with better error handling
        """
        try:
            url = f"{self.source_api_url}/check_payment?md5={md5_hash}"
            logger.info(f"Calling source API: {url}")
            
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'BakongPaymentGateway/1.0'
            })
            
            logger.info(f"Source API response status: {response.status_code}")
            
            # Check if response is successful
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    # If JSON parsing fails, try to handle text response
                    logger.warning(f"Non-JSON response: {response.text[:100]}")
                    return {"raw_response": response.text, "status": "unknown"}
            else:
                logger.error(f"Source API returned error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Source API timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Source API connection error")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Source API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in source API call: {str(e)}")
            return None
    
    def _is_valid_md5(self, md5_hash: str) -> bool:
        """Validate MD5 hash format"""
        if not md5_hash or len(md5_hash) != 32:
            return False
        return bool(re.match(r'^[a-fA-F0-9]{32}$', md5_hash))
    
    def check_payment_status(self, md5_hash: str):
        """
        Public method to check payment status
        """
        # Validate input
        if not self._is_valid_md5(md5_hash):
            return {
                "status": "error",
                "error_code": "INVALID_HASH",
                "message": "Invalid MD5 hash format. Must be 32-character hexadecimal string.",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"Checking payment status for hash: {md5_hash}")
        
        # Call the hidden source API
        source_response = self._call_source_api(md5_hash)
        
        if source_response is None:
            return {
                "status": "error",
                "error_code": "SERVICE_UNAVAILABLE",
                "message": "Payment service is temporarily unavailable. Please try again later.",
                "timestamp": datetime.now().isoformat()
            }
        
        # Transform the response
        return self._transform_response(source_response, md5_hash)
    
    def _transform_response(self, source_data: dict, md5_hash: str):
        """
        Transform the source API response to standardized format
        """
        # Handle case where source API returns raw text instead of JSON
        if isinstance(source_data, dict) and "raw_response" in source_data:
            return {
                "status": "unknown",
                "transaction_hash": md5_hash,
                "message": "Received unexpected response format from payment processor",
                "checked_at": datetime.now().isoformat(),
                "service": "bakong_payment_gateway"
            }
        
        # Extract status from various possible field names
        status = source_data.get('status') or source_data.get('Status') or source_data.get('STATE') or 'unknown'
        
        # Create standardized response
        response = {
            "status": str(status).lower(),
            "transaction_hash": md5_hash,
            "checked_at": datetime.now().isoformat(),
            "service": "bakong_payment_gateway",
            "details": {}
        }
        
        # Map common fields from source API response
        field_mappings = {
            'amount': ['amount', 'AMOUNT', 'Value'],
            'currency': ['currency', 'CURRENCY', 'Currency'],
            'merchant': ['merchant', 'MERCHANT', 'shop_id'],
            'user': ['user', 'USER', 'customer_id'],
            'time': ['time', 'TIME', 'timestamp', 'created_at'],
            'description': ['description', 'DESCRIPTION', 'desc']
        }
        
        for target_field, source_fields in field_mappings.items():
            for source_field in source_fields:
                if source_field in source_data and source_data[source_field] is not None:
                    response["details"][target_field] = source_data[source_field]
                    break
        
        # Add appropriate message based on status
        status_messages = {
            'success': 'Payment completed successfully',
            'completed': 'Payment completed successfully',
            'paid': 'Payment completed successfully',
            'pending': 'Payment is being processed',
            'processing': 'Payment is being processed',
            'failed': 'Payment failed or was declined',
            'rejected': 'Payment was rejected',
            'expired': 'Payment session expired',
            'cancelled': 'Payment was cancelled',
            'unknown': 'Payment status could not be determined'
        }
        
        response["message"] = status_messages.get(response["status"], 'Payment status unknown')
        
        return response
    
    def generate_transaction_hash(self, data: str):
        """
        Generate a transaction hash for clients to use
        """
        if not data or not isinstance(data, str):
            return {
                "status": "error",
                "message": "Valid data string is required",
                "timestamp": datetime.now().isoformat()
            }
        
        md5_hash = hashlib.md5(data.encode()).hexdigest()
        
        return {
            "status": "success",
            "transaction_reference": data,
            "payment_hash": md5_hash,
            "generated_at": datetime.now().isoformat(),
            "message": "Use this hash to check payment status"
        }

# Initialize the payment service
payment_service = PaymentService()

@app.route('/api/bakong/check_payment/', methods=['GET'])
def check_payment():
    """
    Public endpoint to check payment status
    """
    md5_hash = request.args.get('md5')
    
    if not md5_hash:
        return jsonify({
            "status": "error",
            "error_code": "MISSING_PARAMETER",
            "message": "MD5 hash parameter is required. Usage: /api/bakong/check_payment/?md5=your_hash",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    # Process the payment check
    result = payment_service.check_payment_status(md5_hash)
    
    # Determine appropriate HTTP status code
    if result['status'] == 'error':
        status_code = 400 if result.get('error_code') == 'INVALID_HASH' else 503
    else:
        status_code = 200
    
    return jsonify(result), status_code

@app.route('/api/bakong/create_payment', methods=['POST'])
def create_payment():
    """
    Create a payment reference and return a hash for status checking
    """
    try:
        data = request.get_json()
        
        if not data or 'reference_id' not in data:
            return jsonify({
                "status": "error",
                "error_code": "MISSING_REFERENCE",
                "message": "reference_id is required in JSON body",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        reference_id = data['reference_id']
        result = payment_service.generate_transaction_hash(reference_id)
        
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error in create_payment: {str(e)}")
        return jsonify({
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/bakong/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "operational",
        "service": "Bakong Payment Gateway",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/')
def home():
    """Root endpoint with API information"""
    return jsonify({
        "service": "Bakong Payment Gateway API",
        "version": "1.0.0",
        "endpoints": {
            "check_payment": "GET /api/bakong/check_payment/?md5=HASH",
            "create_payment": "POST /api/bakong/create_payment",
            "health": "GET /api/bakong/health"
        },
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
