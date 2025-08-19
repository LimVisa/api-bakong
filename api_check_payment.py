from flask import Flask, request, jsonify
from bakong_khqr import KHQR
import os

app = Flask(__name__)

# Configuration - consider moving this to environment variables
KHQR_TOKEN = os.getenv("KHQR_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiOTYzOGFlMDExMGEyNGFkNSJ9LCJpYXQiOjE3NTM2NTg4ODEsImV4cCI6MTc2MTQzNDg4MX0.Zo5tlVnf03XfcgfxKXaYMVP-MAehkUcF61TA-QMzq5E")

try:
    # Initialize KHQR instance with your token
    khqr = KHQR(KHQR_TOKEN)
except Exception as e:
    raise RuntimeError(f"Failed to initialize KHQR: {str(e)}")

@app.route("/")
def home():
    """Render a professional developer-friendly home page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>KHQR Payment Checker API</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #4a6bff;
                --primary-dark: #3a56cc;
                --secondary: #f8f9fa;
                --text: #333;
                --text-light: #6c757d;
                --success: #28a745;
                --info: #17a2b8;
                --warning: #ffc107;
                --danger: #dc3545;
                --light: #f8f9fa;
                --dark: #343a40;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Roboto', sans-serif;
                line-height: 1.6;
                color: var(--text);
                padding: 0;
                margin: 0;
                background: linear-gradient(135deg, #f5f7ff, #e8ecff, #d9e0ff, #c9d3ff);
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
                min-height: 100vh;
            }

            @keyframes gradient {
                0% {
                    background-position: 0% 50%;
                }
                50% {
                    background-position: 100% 50%;
                }
                100% {
                    background-position: 0% 50%;
                }
            }
            
            .container {
                max-width: 1000px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            header {
                background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                color: white;
                padding: 2rem 0;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .header-content {
                max-width: 1000px;
                margin: 0 auto;
                padding: 0 2rem;
            }
            
            h1 {
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
                font-weight: 700;
            }
            
            .subtitle {
                font-size: 1.2rem;
                font-weight: 300;
                opacity: 0.9;
            }
            
            .card {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                backdrop-filter: blur(5px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            h2 {
                color: var(--primary);
                margin-bottom: 1rem;
                font-size: 1.5rem;
                border-bottom: 2px solid var(--secondary);
                padding-bottom: 0.5rem;
            }
            
            h3 {
                color: var(--text);
                margin: 1rem 0 0.5rem;
                font-size: 1.2rem;
            }
            
            p {
                margin-bottom: 1rem;
                color: var(--text-light);
            }
            
            ul, ol {
                margin-left: 1.5rem;
                margin-bottom: 1rem;
            }
            
            li {
                margin-bottom: 0.5rem;
            }
            
            code {
                background: var(--secondary);
                padding: 0.2rem 0.4rem;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                color: var(--danger);
            }
            
            pre {
                background: var(--dark);
                color: white;
                padding: 1rem;
                border-radius: 6px;
                overflow-x: auto;
                margin: 1rem 0;
                font-size: 0.9rem;
            }
            
            .method-get {
                display: inline-block;
                background: var(--success);
                color: white;
                padding: 0.3rem 0.6rem;
                border-radius: 4px;
                font-weight: 500;
                font-size: 0.8rem;
                margin-right: 0.5rem;
            }
            
            .endpoint {
                font-weight: 500;
                color: var(--primary);
            }
            
            .example-request {
                background: var(--secondary);
                padding: 1rem;
                border-radius: 6px;
                margin: 1rem 0;
                border-left: 4px solid var(--info);
            }
            
            .response-block {
                position: relative;
            }
            
            .copy-btn {
                position: absolute;
                top: 0.5rem;
                right: 0.5rem;
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.8rem;
            }
            
            .copy-btn:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            
            footer {
                text-align: center;
                margin-top: 3rem;
                padding: 1rem;
                color: var(--text-light);
                font-size: 0.9rem;
            }

            .telegram-link {
                display: inline-block;
                margin-top: 1rem;
                padding: 0.5rem 1rem;
                background: #0088cc;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: background 0.3s ease;
            }

            .telegram-link:hover {
                background: #0077b3;
            }

            .telegram-link i {
                margin-right: 0.5rem;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 1rem;
                }
                
                header {
                    padding: 1.5rem 0;
                }
                
                h1 {
                    font-size: 2rem;
                }
            }
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    </head>
    <body>
        <header>
            <div class="header-content">
                <h1>KHQR Payment Checker API</h1>
                <p class="subtitle">A secure service for verifying KHQR payment statuses</p>
            </div>
        </header>
        
        <div class="container">
            <div class="card">
                <h2>API Documentation</h2>
                <p>Welcome to the KHQR Payment Checker API. This service allows you to verify the status of payments made via KHQR codes.</p>
                <a href="https://t.me/MonnyYuda168" class="telegram-link" target="_blank">
                    <i class="fab fa-telegram"></i>Contact on Telegram
                </a>
            </div>
            
            <div class="card">
                <h2>API Endpoint</h2>
                
                <div class="endpoint-header">
                    <span class="method-get">GET</span>
                    <span class="endpoint">/api/check_payment</span>
                </div>
                
                <p>Check payment status for a given transaction MD5 hash.</p>
                
                <h3>Request Parameters</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 1rem;">
                    <thead>
                        <tr style="background-color: var(--secondary);">
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Parameter</th>
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Type</th>
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Required</th>
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #ddd;">Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 0.75rem; border: 1px solid #ddd;"><code>md5</code></td>
                            <td style="padding: 0.75rem; border: 1px solid #ddd;">string</td>
                            <td style="padding: 0.75rem; border: 1px solid #ddd;">Yes</td>
                            <td style="padding: 0.75rem; border: 1px solid #ddd;">32-character MD5 hash of the transaction</td>
                        </tr>
                    </tbody>
                </table>
                
                <h3>Example Request</h3>
                <div class="example-request">
                    <code>GET /api/check_payment?md5=5d41402abc4b2a76b9719d911017c592</code>
                </div>
            </div>
            
            <div class="card">
                <h2>Response</h2>
                
                <h3>Successful Response</h3>
                <div class="response-block">
                    <pre>{
    "md5": "5d41402abc4b2a76b9719d911017c592",
    "status": "paid"
}</pre>
                </div>
                
                <h3>Possible Status Values</h3>
                <ul>
                    <li><code>paid</code> - Payment was successfully completed</li>
                    <li><code>pending</code> - Payment is in progress</li>
                    <li><code>not_found</code> - No payment found with this MD5 hash</li>
                </ul>
                
                <h3>Error Responses</h3>
                <p>400 Bad Request - Invalid or missing parameters:</p>
                <pre>{
    "error": "Missing md5 parameter"
}</pre>
                
                <p>500 Internal Server Error - Server encountered an error:</p>
                <pre>{
    "error": "Internal server error"
}</pre>
            </div>
            
            <div class="card">
                <h2>Usage Example</h2>
                <p>Here's how you might call this API using JavaScript:</p>
                <pre>fetch('/api/check_payment?md5=5d41402abc4b2a76b9719d911017c592')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));</pre>
            </div>
        </div>
        
        <footer>
            <p>KHQR Payment Checker API &copy; 2023 | Version 1.0.0</p>
            <a href="https://t.me/MonnyYuda168" class="telegram-link" target="_blank">
                <i class="fab fa-telegram"></i>Contact on Telegram
            </a>
        </footer>
        
        <script>
            // Simple copy functionality for code blocks
            document.querySelectorAll('pre').forEach(pre => {
                const button = document.createElement('button');
                button.className = 'copy-btn';
                button.textContent = 'Copy';
                button.addEventListener('click', () => {
                    const text = pre.textContent;
                    navigator.clipboard.writeText(text).then(() => {
                        button.textContent = 'Copied!';
                        setTimeout(() => {
                            button.textContent = 'Copy';
                        }, 2000);
                    });
                });
                pre.style.position = 'relative';
                pre.appendChild(button);
            });
        </script>
    </body>
    </html>
    """

@app.route("/api/check_payment", methods=["GET"])
def check_payment():
    md5 = request.args.get("md5")
    if not md5:
        return jsonify({"error": "Missing md5 parameter"}), 400
    
    # Basic MD5 format validation (32 hex characters)
    if not (isinstance(md5, str) and len(md5) == 32 and all(c in '0123456789abcdef' for c in md5.lower())):
        return jsonify({"error": "Invalid md5 format"}), 400

    try:
        payment_status = khqr.check_payment(md5)
        return jsonify({
            "md5": md5,
            "status": payment_status
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error checking payment for {md5}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Check if SSL files exist
    ssl_context = None
    if os.path.exists("cert.pem") and os.path.exists("key.pem"):
        ssl_context = ("cert.pem", "key.pem")
    else:
        app.logger.warning("SSL certificate files not found, running without HTTPS")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context=ssl_context,
        debug=True
    )