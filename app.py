# import nonexistent_module_xyz 
from flask import Flask, request, Response
from datetime import datetime
from zoneinfo import ZoneInfo
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import os
app = Flask(__name__)
IST = ZoneInfo("Asia/Kolkata")

# ---- Prometheus metrics ----
REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 'HTTP request latency in seconds',
    ['endpoint']
)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
# ---- end Prometheus metrics ----

def get_ist_time():
    return datetime.now(IST).strftime("%d-%m-%Y %H:%M:%S IST")

DB_PASS = "admin@123"

@app.route("/")
def home():
    current_time = get_ist_time()
    return f"""
    <html>
        <head>
            <title>Python Web App</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    text-align: center;
                    padding-top: 100px;
                }}
                .container {{
                    background: white;
                    width: 500px;
                    margin: auto;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
                }}
                h1 {{
                    color: #2c3e50;
                }}
                p {{
                    font-size: 20px;
                    color: #27ae60;
                }}
                .timestamp {{
                    font-size: 14px;
                    color: #7f8c8d;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Hello GSPANN From DSSP Portal</h1>
                <p>Python Pipeline Test Successful</p>
                <div class="timestamp">Deployed at: {current_time}</div>
            </div>
        </body>
    </html>
    """

@app.route("/health")
def health():
    return {
        "status": "UP",
        "timestamp": get_ist_time()
    }

class PrefixMiddleware:
    def __init__(self, app, prefix=""):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ["PATH_INFO"].startswith(self.prefix):
            environ["PATH_INFO"] = environ["PATH_INFO"][len(self.prefix):]
            environ["SCRIPT_NAME"] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response("404", [("Content-Type", "text/plain")])
            return [b"This URL does not belong to the app."]

app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=os.environ.get("URL_PREFIX", ""))

if __name__ == "__main__":
    print(f"[LOG] Flask App Started at {get_ist_time()}")
    app.run(host="0.0.0.0", port=5000)
