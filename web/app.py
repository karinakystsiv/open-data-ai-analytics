from flask import Flask, send_from_directory, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import time

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total request count', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency in seconds', ['endpoint'])

REPORTS_DIR = "/app/reports"


@app.before_request
def before_request():
    request._start_time = time.time()


@app.after_request
def after_request(response):
    if hasattr(request, '_start_time'):
        latency = time.time() - request._start_time
        REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
    return response


@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


@app.route('/')
def index():
    quality_report = ""
    research_results = ""

    if os.path.exists(f"{REPORTS_DIR}/data_quality_report.md"):
        with open(f"{REPORTS_DIR}/data_quality_report.md", "r", encoding="utf-8") as f:
            quality_report = f.read()

    if os.path.exists(f"{REPORTS_DIR}/research_results.txt"):
        with open(f"{REPORTS_DIR}/research_results.txt", "r", encoding="utf-8") as f:
            research_results = f.read()

    # Знаходимо всі графіки
    figures = []
    figures_dir = os.path.join(REPORTS_DIR, "figures")
    if os.path.exists(figures_dir):
        figures = sorted([f for f in os.listdir(figures_dir) if f.endswith('.png')])

    figures_html = ""
    for fig in figures:
        label = fig.replace('.png', '').replace('_', ' ').title()
        figures_html += f"""
            <div style="margin-bottom: 20px;">
                <p><b>{label}</b></p>
                <img src="/plots/{fig}" width="500" style="border: 1px solid #ddd; border-radius: 5px;">
            </div>
        """

    return f"""
    <html>
        <head>
            <title>Vehicle Registration Analytics 2024</title>
            <meta charset="utf-8">
        </head>
        <body style="font-family: sans-serif; padding: 40px; line-height: 1.6; max-width: 1000px; margin: 0 auto;">
            <h1>🚗 Аналітика реєстрацій транспортних засобів (2024)</h1>
            <p>Аналіз операцій реєстрації ТЗ в Україні за 2024 рік на основі відкритих даних.</p>
            <hr>

            <h2>📝 Звіт про якість даних</h2>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap;">{quality_report}</pre>

            <h2>🔬 Результати дослідження гіпотез</h2>
            <pre style="background: #eef; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap;">{research_results}</pre>

            <h2>📈 Візуалізації</h2>
            <div style="display: flex; flex-direction: column; gap: 20px;">
                {figures_html}
            </div>

            <hr>
            <p style="color: #888; font-size: 0.9em;">Дані: <a href="https://data.gov.ua">data.gov.ua</a> | Docker Workspace Project</p>
        </body>
    </html>
    """


@app.route('/plots/<path:filename>')
def plots(filename):
    return send_from_directory(f"{REPORTS_DIR}/figures", filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
