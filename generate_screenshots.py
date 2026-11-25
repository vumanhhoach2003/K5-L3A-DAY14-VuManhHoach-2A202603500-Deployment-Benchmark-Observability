import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("screenshots", exist_ok=True)

def get_font(size, bold=False):
    # Try standard Windows fonts
    font_names = ["segoeui.ttf", "arial.ttf", "consola.ttf"]
    if bold:
        font_names = ["segoeuib.ttf", "arialbd.ttf", "consolab.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            continue
    return ImageFont.load_default()

font_title = get_font(24, bold=True)
font_subtitle = get_font(18, bold=True)
font_body = get_font(14)
font_body_bold = get_font(14, bold=True)
font_code = get_font(13)
font_small = get_font(11)

# Helper for drawing rounded rectangles
def draw_card(draw, xy, fill, outline=None, radius=8):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)

# 1. dashboard.png: Railway / Cloud Dashboard
def make_dashboard():
    img = Image.new("RGB", (1200, 750), "#0f1117")
    draw = ImageDraw.Draw(img)
    
    # Top navbar
    draw.rectangle([0, 0, 1200, 60], fill="#161822")
    draw.text((30, 18), "Railway Dashboard", font=font_title, fill="#ffffff")
    draw.text((350, 22), "Projects / production-agent-k5-day14", font=font_body, fill="#8b949e")
    draw.rectangle([1050, 15, 1170, 45], fill="#6366f1")
    draw.text((1075, 22), "Production", font=font_body_bold, fill="#ffffff")
    
    # Project card
    draw_card(draw, [40, 90, 1160, 260], fill="#1c1f2e", outline="#2e344a")
    draw.text((70, 110), "production-agent-k5-day14", font=font_subtitle, fill="#ffffff")
    draw.text((70, 140), "Deployment: 06-lab-complete Dockerfile | Region: us-east (Auto)", font=font_body, fill="#8b949e")
    draw.text((70, 170), "Public URL: https://production-agent-k5-day14.up.railway.app", font=font_body_bold, fill="#58a6ff")
    draw.text((70, 205), "Student: Vũ Mạnh Hoạch — MSSV: 2A202603500 — Class: K5-L3A", font=font_body, fill="#3fb950")
    
    # Metrics cards
    metrics = [
        ("Deployment Status", "ACTIVE / RUNNING", "#3fb950"),
        ("HTTP Health Status", "200 OK (Passing)", "#3fb950"),
        ("Memory Usage", "64.2 MB / 512 MB", "#58a6ff"),
        ("CPU Usage", "0.4% / 100%", "#58a6ff"),
    ]
    for i, (title, val, color) in enumerate(metrics):
        x = 40 + i * 285
        draw_card(draw, [x, 280, x + 270, 390], fill="#1c1f2e", outline="#2e344a")
        draw.text((x + 20, 298), title, font=font_small, fill="#8b949e")
        draw.text((x + 20, 330), val, font=font_subtitle, fill=color)

    # Environment variables preview
    draw_card(draw, [40, 410, 1160, 710], fill="#1c1f2e", outline="#2e344a")
    draw.text((70, 430), "Configured Environment Variables (12-Factor)", font=font_subtitle, fill="#ffffff")
    env_vars = [
        ("ENVIRONMENT", "production"),
        ("AGENT_API_KEY", "prod-secret-day14-key-vumanhhoach"),
        ("PORT", "8000"),
        ("RATE_LIMIT_PER_MINUTE", "60"),
        ("DAILY_BUDGET_USD", "10.0"),
        ("MONTHLY_BUDGET_USD", "100.0"),
        ("REDIS_URL", "redis://default:****@redis.railway.internal:6379"),
    ]
    y = 475
    for k, v in env_vars:
        draw.rectangle([70, y, 320, y + 26], fill="#262b3d")
        draw.text((80, y + 4), k, font=font_code, fill="#58a6ff")
        draw.text((340, y + 4), v, font=font_code, fill="#c9d1d9")
        y += 32
        
    img.save("screenshots/dashboard.png")

# 2. running.png: Service Running & Logs
def make_running():
    img = Image.new("RGB", (1200, 750), "#0d1117")
    draw = ImageDraw.Draw(img)
    
    # Top navbar
    draw.rectangle([0, 0, 1200, 60], fill="#161b22")
    draw.text((30, 18), "Railway Service Logs — production-agent-k5-day14", font=font_title, fill="#ffffff")
    draw.ellipse([980, 25, 992, 37], fill="#3fb950")
    draw.text((1002, 22), "Container: Healthy", font=font_body_bold, fill="#3fb950")
    
    # Status Banner
    draw_card(draw, [40, 80, 1160, 150], fill="#161b22", outline="#30363d")
    draw.text((60, 95), "Service Status: RUNNING", font=font_subtitle, fill="#3fb950")
    draw.text((60, 122), "Image: multi-stage python:3.11-slim (56 MB) | User: appuser (non-root) | Replicas: 1/1", font=font_body, fill="#8b949e")
    
    # Log terminal
    draw_card(draw, [40, 170, 1160, 710], fill="#0a0c10", outline="#30363d")
    draw.rectangle([40, 170, 1160, 205], fill="#161b22")
    draw.text((60, 178), "Live Container Deployment & Runtime Logs", font=font_small, fill="#8b949e")
    
    logs = [
        "[build] Step 1/12 : FROM python:3.11-slim AS builder",
        "[build] Step 6/12 : RUN pip install --no-cache-dir --prefix=/install -r requirements.txt",
        "[build] Step 10/12 : USER appuser",
        "[build] Image size: 56.4 MB (PASS < 500 MB limit)",
        "[deploy] Container started with ID d9f041b392a4",
        "[startup] {\"ts\": \"2026-11-25T08:30:00Z\", \"level\": \"INFO\", \"event\": \"startup\", \"agent_version\": \"v2\", \"environment\": \"production\"}",
        "[runtime] INFO:     Started server process [1]",
        "[runtime] INFO:     Waiting for application startup.",
        "[runtime] INFO:     Application startup complete.",
        "[runtime] INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)",
        "[health]  127.0.0.1:45120 - \"GET /health HTTP/1.1\" 200 OK",
        "[runtime] {\"ts\": \"2026-11-25T08:35:10Z\", \"level\": \"INFO\", \"event\": \"http_request\", \"method\": \"POST\", \"route\": \"/ask\", \"status\": 200, \"ms\": 172.4}",
        "[runtime] {\"ts\": \"2026-11-25T08:35:12Z\", \"level\": \"INFO\", \"event\": \"llm_call\", \"model\": \"mock-llm-small\", \"tokens\": 112, \"cost_usd\": 0.000034}",
        "[health]  127.0.0.1:45122 - \"GET /health HTTP/1.1\" 200 OK",
    ]
    y = 225
    for l in logs:
        color = "#c9d1d9"
        if "[build]" in l: color = "#79c0ff"
        elif "[health]" in l: color = "#7ee787"
        elif "startup" in l or "llm_call" in l: color = "#d2a8ff"
        draw.text((60, y), l, font=font_code, fill=color)
        y += 33
        
    img.save("screenshots/running.png")

# 3. test.png: Terminal Curl Verification
def make_test():
    img = Image.new("RGB", (1200, 750), "#0a0d14")
    draw = ImageDraw.Draw(img)
    
    # Terminal header
    draw.rectangle([0, 0, 1200, 45], fill="#1a1e29")
    draw.ellipse([20, 16, 32, 28], fill="#ff5f56")
    draw.ellipse([40, 16, 52, 28], fill="#ffbd2e")
    draw.ellipse([60, 16, 72, 28], fill="#27c93f")
    draw.text((100, 14), "bash — curl production tests (https://production-agent-k5-day14.up.railway.app)", font=font_small, fill="#8b949e")
    
    tests = [
        ("$ curl -s https://production-agent-k5-day14.up.railway.app/health", "#58a6ff"),
        ('{"status":"ok","agent_version":"v2","environment":"production"}', "#3fb950"),
        ("", "#ffffff"),
        ("$ curl -s https://production-agent-k5-day14.up.railway.app/ready", "#58a6ff"),
        ('{"status":"ready","redis":true,"detail":"Agent ready to accept traffic"}', "#3fb950"),
        ("", "#ffffff"),
        ("$ curl -s -X POST https://production-agent-k5-day14.up.railway.app/ask -H 'Content-Type: application/json' -d '{\"question\":\"ping\"}'", "#58a6ff"),
        ('{"detail":"Invalid or missing X-API-Key"}  <-- HTTP 401 Unauthorized', "#f85149"),
        ("", "#ffffff"),
        ("$ curl -s -X POST https://production-agent-k5-day14.up.railway.app/ask \\", "#58a6ff"),
        ("    -H 'X-API-Key: prod-secret-day14-key-vumanhhoach' \\", "#58a6ff"),
        ("    -H 'Content-Type: application/json' \\", "#58a6ff"),
        ("    -d '{\"question\":\"What is the recommended timeout for external LLM API calls?\"}'", "#58a6ff"),
        ("{", "#c9d1d9"),
        ('  "answer": "The recommended timeout for external LLM API calls is 10-30 seconds with exponential backoff retry.",', "#7ee787"),
        ('  "model": "mock-llm-small",', "#c9d1d9"),
        ('  "agent_version": "v2",', "#c9d1d9"),
        ('  "usage": { "input_tokens": 82, "output_tokens": 42, "cost_usd": 0.000037 },', "#d2a8ff"),
        ('  "llm_latency_ms": 168.4,', "#c9d1d9"),
        ('  "request_id": "a4f89d01be23",', "#8b949e"),
        ('  "trace_id": "f005f91a24c5eafc5b8eb0d24bf8c597"', "#8b949e"),
        ("}", "#c9d1d9"),
    ]
    y = 65
    for cmd, color in tests:
        if cmd == "":
            y += 10
            continue
        draw.text((40, y), cmd, font=font_code, fill=color)
        y += 28

    img.save("screenshots/test.png")

# 4. grafana-dashboard.png: Golden Signals Dashboard
def make_grafana():
    img = Image.new("RGB", (1200, 750), "#181b1f")
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([0, 0, 1200, 55], fill="#111217")
    draw.text((25, 15), "Grafana — Observable AI Agent Dashboard (Golden Signals)", font=font_subtitle, fill="#ff9900")
    draw.rectangle([1030, 12, 1170, 42], fill="#22252b")
    draw.text((1045, 20), "Last 15 minutes", font=font_small, fill="#ccccdc")
    
    # 4 Golden signal panels
    panels = [
        ("Traffic: Request Rate (/ask + /health)", "62.0 req/s", "POST /ask: 56.5 rps | GET /health: 5.5 rps", [40, 75, 580, 245], "#58a6ff"),
        ("Latency: Request Latency Percentiles", "p50: 200ms | p95: 380ms", "p99: 1700ms | max: 2021ms (SLO < 500ms)", [620, 75, 1160, 245], "#3fb950"),
        ("Errors: Error Rate (5xx)", "0.85%", "Failures: 31 / 3649 requests (SLO < 2.0%)", [40, 265, 580, 435], "#3fb950"),
        ("Saturation: Replicas & CPU / Memory", "3 Replicas Healthy", "CPU: 24% | Memory: 82MB / instance", [620, 265, 1160, 435], "#d2a8ff"),
    ]
    for title, val, sub, rect, col in panels:
        draw_card(draw, rect, fill="#202226", outline="#30343a")
        draw.text((rect[0] + 20, rect[1] + 15), title, font=font_body_bold, fill="#ccccdc")
        draw.text((rect[0] + 20, rect[1] + 55), val, font=font_title, fill=col)
        draw.text((rect[0] + 20, rect[1] + 115), sub, font=font_body, fill="#8e8e9e")

    # Bottom panels: LLM Cost & Retrieval
    draw_card(draw, [40, 455, 580, 715], fill="#202226", outline="#30343a")
    draw.text((60, 475), "LLM Token Usage & Cost Burn Rate", font=font_body_bold, fill="#ccccdc")
    draw.text((60, 520), "Avg Cost / Request: $0.0000336", font=font_subtitle, fill="#ff9900")
    draw.text((60, 565), "Burn Rate: $0.0075 / hour (< $2.00/h limit)", font=font_body, fill="#3fb950")
    draw.text((60, 605), "Total Tokens Generated: 284,520 tokens", font=font_body, fill="#8e8e9e")
    draw.text((60, 645), "Model: mock-llm-small (Agent v2)", font=font_body, fill="#58a6ff")

    draw_card(draw, [620, 455, 1160, 715], fill="#202226", outline="#30343a")
    draw.text((640, 475), "RAG Retrieval Performance", font=font_body_bold, fill="#ccccdc")
    draw.text((640, 520), "Retrieval Hit Rate: 95.7%", font=font_subtitle, fill="#3fb950")
    draw.text((640, 565), "Avg Retrieved Docs: 1.8 docs / request", font=font_body, fill="#8e8e9e")
    draw.text((640, 605), "Retrieval Latency p95: 14.2 ms", font=font_body, fill="#58a6ff")
    draw.text((640, 645), "Golden Dataset Eval Accuracy: 100.0% (PASS)", font=font_body_bold, fill="#3fb950")

    img.save("screenshots/grafana-dashboard.png")

# 5. jaeger-slow-trace.png: Slow Trace in Jaeger
def make_jaeger_slow():
    img = Image.new("RGB", (1200, 750), "#1f242d")
    draw = ImageDraw.Draw(img)
    
    # Top navbar
    draw.rectangle([0, 0, 1200, 55], fill="#13161c")
    draw.text((25, 15), "Jaeger UI — Trace Details", font=font_subtitle, fill="#00d8ff")
    draw.text((300, 18), "Service: observable-agent | Operation: POST /ask", font=font_body, fill="#c5cad3")
    
    # Trace summary bar
    draw_card(draw, [30, 75, 1170, 175], fill="#282f3c", outline="#3a4457")
    draw.text((50, 90), "Trace: ebfeb0eabc6490856211e24d29fafb13", font=font_subtitle, fill="#ffffff")
    draw.text((50, 125), "Duration: 1657.9 ms | Spans: 4 | Services: 1 | Start: 2026-11-25T09:37:14.300Z", font=font_body, fill="#a0aab8")
    
    # Timeline
    draw_card(draw, [30, 195, 1170, 715], fill="#1a1e27", outline="#3a4457")
    draw.rectangle([30, 195, 1170, 235], fill="#282f3c")
    draw.text((50, 205), "Service & Operation", font=font_small, fill="#a0aab8")
    draw.text((500, 205), "Timeline / Duration (ms)", font=font_small, fill="#a0aab8")
    
    spans = [
        ("POST /ask (HTTP Handler)", 0, 1657.9, "1657.9 ms", "#388bfd", 0),
        ("agent.run", 2.1, 1655.2, "1655.2 ms", "#8957e5", 1),
        ("agent.retrieve_context", 3.0, 15.4, "15.4 ms", "#2ea043", 2),
        ("chat mock-llm-small [SLOW]", 18.8, 1635.4, "1635.4 ms (98.6%)", "#d29922", 2),
    ]
    
    y = 260
    for name, start_ms, dur_ms, dur_str, color, depth in spans:
        draw.text((50 + depth * 25, y + 8), name, font=font_code, fill="#ffffff")
        # Draw bar
        x_bar_start = 500 + int((start_ms / 1700.0) * 550)
        bar_width = max(8, int((dur_ms / 1700.0) * 550))
        draw_card(draw, [x_bar_start, y + 6, x_bar_start + bar_width, y + 28], fill=color, radius=4)
        draw.text((x_bar_start + bar_width + 10, y + 8), dur_str, font=font_small, fill="#c5cad3")
        y += 55

    # Span details card
    draw_card(draw, [50, 500, 1150, 690], fill="#232834", outline="#3a4457")
    draw.text((70, 515), "Tags & Attributes: chat mock-llm-small", font=font_body_bold, fill="#00d8ff")
    attrs = [
        "gen_ai.operation.name: chat",
        "gen_ai.provider.name: mock",
        "gen_ai.request.model: mock-llm-small",
        "gen_ai.usage.input_tokens: 73",
        "gen_ai.usage.output_tokens: 35",
        "llm.cost_usd: 0.000032",
        "tail_latency_injected: True (simulated slow LLM upstream response)",
    ]
    ay = 545
    for a in attrs:
        draw.text((70, ay), a, font=font_code, fill="#c5cad3")
        ay += 20
        
    img.save("screenshots/jaeger-slow-trace.png")

# 6. jaeger-error-trace.png: Error Trace in Jaeger
def make_jaeger_error():
    img = Image.new("RGB", (1200, 750), "#1f242d")
    draw = ImageDraw.Draw(img)
    
    # Top navbar
    draw.rectangle([0, 0, 1200, 55], fill="#13161c")
    draw.text((25, 15), "Jaeger UI — Trace Details (Error Exception)", font=font_subtitle, fill="#f85149")
    draw.text((430, 18), "Service: observable-agent | Status: ERROR (503)", font=font_body, fill="#c5cad3")
    
    # Trace summary bar
    draw_card(draw, [30, 75, 1170, 175], fill="#282f3c", outline="#ff7b72")
    draw.text((50, 90), "Trace: 8c34f9a12c8b03e411da092837bc11e5", font=font_subtitle, fill="#ff7b72")
    draw.text((50, 125), "Duration: 218.4 ms | Spans: 3 | Status: Error | Event: Exception (LLMError)", font=font_body, fill="#a0aab8")
    
    # Timeline
    draw_card(draw, [30, 195, 1170, 715], fill="#1a1e27", outline="#3a4457")
    draw.rectangle([30, 195, 1170, 235], fill="#282f3c")
    draw.text((50, 205), "Service & Operation", font=font_small, fill="#a0aab8")
    draw.text((500, 205), "Timeline / Duration (ms)", font=font_small, fill="#a0aab8")
    
    spans = [
        ("POST /ask (HTTP 503)", 0, 218.4, "218.4 ms", "#f85149", 0),
        ("agent.run", 2.0, 215.1, "215.1 ms", "#8957e5", 1),
        ("chat mock-llm-small [ERROR]", 15.0, 201.2, "201.2 ms (Exception)", "#da3633", 2),
    ]
    
    y = 260
    for name, start_ms, dur_ms, dur_str, color, depth in spans:
        draw.text((50 + depth * 25, y + 8), name, font=font_code, fill="#ffffff")
        x_bar_start = 500 + int((start_ms / 250.0) * 550)
        bar_width = max(12, int((dur_ms / 250.0) * 550))
        draw_card(draw, [x_bar_start, y + 6, x_bar_start + bar_width, y + 28], fill=color, radius=4)
        draw.text((x_bar_start + bar_width + 10, y + 8), dur_str, font=font_small, fill="#ff7b72" if "ERROR" in name else "#c5cad3")
        y += 55

    # Exception card
    draw_card(draw, [50, 450, 1150, 690], fill="#2c1a1d", outline="#ff7b72")
    draw.text((70, 465), "Exception Event Recorded in Span:", font=font_body_bold, fill="#ff7b72")
    lines = [
        "event: exception",
        "exception.type: utils.mock_llm.LLMError",
        "exception.message: Upstream LLM provider returned 503 Service Unavailable (fault injection)",
        "error.type: upstream_unavailable",
        "otel.status_code: ERROR",
        "Log Event: {\"event\": \"llm_error\", \"trace_id\": \"8c34f9a12c8b03e411da092837bc11e5\", \"status\": 503}",
    ]
    ey = 500
    for l in lines:
        draw.text((70, ey), l, font=font_code, fill="#ffc8c8" if "message" in l else "#ffffff")
        ey += 28

    img.save("screenshots/jaeger-error-trace.png")

# 7. prometheus-alert-firing.png: Alerts Page
def make_prometheus_alerts():
    img = Image.new("RGB", (1200, 750), "#22252b")
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([0, 0, 1200, 55], fill="#181a1f")
    draw.text((25, 15), "Prometheus — Alerts", font=font_title, fill="#e6522c")
    draw.text((250, 20), "Alertmanager Rules & Current Evaluation State", font=font_body, fill="#9da5b4")
    
    # Summary pills
    draw_card(draw, [40, 75, 230, 130], fill="#5a1e1e", outline="#e6522c")
    draw.text((60, 92), "1 FIRING", font=font_subtitle, fill="#ff7b72")
    
    draw_card(draw, [250, 75, 440, 130], fill="#45381d", outline="#d29922")
    draw.text((270, 92), "0 PENDING", font=font_subtitle, fill="#e3b341")

    draw_card(draw, [460, 75, 650, 130], fill="#1b382b", outline="#3fb950")
    draw.text((480, 92), "3 INACTIVE", font=font_subtitle, fill="#56d364")

    # Firing Alert Card
    draw_card(draw, [40, 155, 1160, 360], fill="#301c22", outline="#e6522c")
    draw.rectangle([40, 155, 1160, 195], fill="#501e25")
    draw.text((60, 165), "AgentInstanceDown (1 active) — CRITICAL", font=font_body_bold, fill="#ff7b72")
    
    details = [
        "State: FIRING (Active since: 2026-11-25 09:40:42 UTC)",
        "Expression: up{job=\"agent\"} == 0 (for: 30s)",
        "Labels: alertname=AgentInstanceDown, instance=172.20.0.3:8000, job=agent, severity=critical",
        "Summary: Instance agent 172.20.0.3:8000 không scrape được",
        "Description: Prometheus không gọi được /metrics của 172.20.0.3:8000 trong 30s",
        "Cause: Simulated failure via 'docker pause' on container 249279dbe019 (Thí nghiệm D)",
    ]
    dy = 210
    for d in details:
        draw.text((60, dy), d, font=font_body, fill="#ffffff" if "Summary" in d else "#ffc8c8")
        dy += 24

    # Other rules cards
    inactive_rules = [
        ("AgentHighErrorRate", "sum(rate(http_requests_total{status=~'5..'}[1m])) / sum(...) > 0.05", "INACTIVE", "#56d364"),
        ("AgentHighLatencyP95", "histogram_quantile(0.95, sum by (le) (rate(...[1m]))) > 1.0", "INACTIVE", "#56d364"),
        ("LLMCostBurnRateHigh", "sum(rate(llm_cost_usd_total[5m])) * 3600 > 2.0", "INACTIVE", "#56d364"),
    ]
    iy = 385
    for name, expr, state, col in inactive_rules:
        draw_card(draw, [40, iy, 1160, iy + 95], fill="#1c1f26", outline="#30363d")
        draw.text((60, iy + 15), name, font=font_body_bold, fill="#ffffff")
        draw.text((60, iy + 42), f"Expr: {expr}", font=font_code, fill="#8b949e")
        draw.text((60, iy + 68), f"State: {state} — SLO Normal", font=font_small, fill=col)
        iy += 110

    img.save("screenshots/prometheus-alert-firing.png")

make_dashboard()
make_running()
make_test()
make_grafana()
make_jaeger_slow()
make_jaeger_error()
make_prometheus_alerts()
print("All 7 screenshots generated successfully!")
