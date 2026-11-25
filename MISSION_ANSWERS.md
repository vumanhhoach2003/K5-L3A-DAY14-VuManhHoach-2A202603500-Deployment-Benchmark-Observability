# Day 14 Lab — Mission Answers

> **Sinh viên:** Vũ Mạnh Hoạch  
> **MSSV:** 2A202603500  
> **Lớp:** K5-L3A  
> **Repository:** K5-L3A-DAY14-VuManhHoach-2A202603500-Deployment-Benchmark-Observability  

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns tìm thấy trong bản develop (`01-localhost-vs-production/develop/app.py`)
1. **Hardcode secrets:** Khóa bí mật API key (`API_KEY = "super-secret-key-12345"`) và LLM key được ghi trực tiếp trong mã nguồn, nguy cơ lộ khi commit lên Git repository.
2. **Host & Port cố định:** Cấu hình cố định `host="127.0.0.1"`, `port=8000`, không đọc biến môi trường `$PORT` do nền tảng Cloud cấp động.
3. **Debug mode bật trên production:** Chạy server với chế độ reload/debug, làm rò rỉ stack trace và thông tin nhạy cảm của hệ thống khi có lỗi.
4. **Thiếu Health Check Endpoints:** Không có route `/health` (Liveness) và `/ready` (Readiness), khiến orchestrator (Kubernetes/Docker) không thể biết khi nào app bị treo hoặc chưa sẵn sàng.
5. **Không có cơ chế Graceful Shutdown:** Khi nhận tín hiệu tắt (SIGTERM/SIGINT), process tắt đột ngột cắt ngang các request người dùng đang được xử lý.
6. **Lưu trữ State trong RAM cục bộ:** Dữ liệu lưu trong biến bộ nhớ `MEMORY_STORE = {}`, mất sạch khi server restart và không thể scale ngang nhiều instance.
7. **Dùng `print()` thay vì Structured Logging:** Sử dụng hàm print thông thường, thiếu timestamp, request_id, level (INFO/ERROR) và định dạng JSON để phục vụ lưu trữ, tìm kiếm và phân tích.

### Exercise 1.2: Kết quả chạy thử nghiệm bản develop
Lệnh gọi API:
```bash
curl -X POST "http://localhost:8000/ask?question=Hello" -H "Content-Type: application/json"
```
Kết quả phản hồi (HTTP 200):
```json
{
  "question": "Hello",
  "answer": "Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic."
}
```

### Exercise 1.3: Bảng so sánh Basic (Develop) vs Advanced (Production)

| Đặc tính | Basic (Develop) | Advanced (Production) | Tại sao quan trọng? |
| :--- | :--- | :--- | :--- |
| **Config & Secrets** | Hardcode trong code | Đọc từ biến môi trường (12-Factor) | Đảm bảo bảo mật, dễ dàng thay đổi cấu hình giữa dev/staging/prod mà không cần build lại code. |
| **Health Check** | Không có | Tách biệt `/health` và `/ready` | Giúp Cloud orchestrator biết khi nào container còn sống (liveness) và khi nào sẵn sàng nhận tải (readiness). |
| **Structured Logging** | `print()` text thô | JSON logs có timestamp, level, metadata | Dễ dàng thu thập, lập chỉ mục và truy vấn trên hệ thống quản lý log tập trung (ELK, Loki). |
| **Graceful Shutdown** | Tắt đột ngột (Hard exit) | Bắt SIGTERM, hoàn thành in-flight request | Ngăn chặn việc làm mất dữ liệu hoặc trả lỗi dở dang cho người dùng khi restart/deploy phiên bản mới. |
| **State Storage** | Bộ nhớ RAM nội bộ | Lưu trữ ngoài (Redis) | Cho phép ứng dụng Stateless để scale ngang không giới hạn qua Load Balancer. |

---

## Part 2: Docker Containerization

### Exercise 2.1: Trả lời câu hỏi Dockerfile
1. **Base image là gì:** Sử dụng `python:3.11-slim` — hệ điều hành nền Debian tối giản chứa sẵn môi trường thực thi Python 3.11.
2. **Working directory là gì:** Thư mục `/app` bên trong container, là nơi đặt toàn bộ mã nguồn và là context mặc định cho các lệnh tiếp theo.
3. **Tại sao `COPY requirements.txt` phải đứng trước `COPY . .`:** Tận dụng cơ chế Layer Caching của Docker. File `requirements.txt` ít thay đổi hơn mã nguồn; tách riêng giúp Docker bỏ qua bước `pip install` khi chỉ sửa code ứng dụng, rút ngắn thời gian build.
4. **Khác biệt giữa CMD và ENTRYPOINT:** `ENTRYPOINT` xác định tiến trình cố định chạy khi container khởi động, còn `CMD` cung cấp các tham số hoặc lệnh mặc định có thể bị ghi đè khi gọi lệnh `docker run`.

### Exercise 2.2 & 2.3: Đo lường kích thước Image (Multi-stage build)
- **Kích thước Image Develop (Single-stage):** `1.02 GB`
- **Kích thước Image Production (Multi-stage slim):** `56 MB`
- **Tỉ lệ giảm:** `94.5%`
- **Giải thích:** Stage 1 (Builder) sử dụng đầy đủ công cụ biên dịch (`gcc`, `python3-dev`) để compile thư viện. Stage 2 (Runtime) chỉ copy thư mục gói đã build vào base `python:3.11-slim` và chạy dưới quyền user non-root `appuser`.

### Exercise 2.4: Sơ đồ kiến trúc Docker Compose Stack
```text
  [ Client Request ]
          │
          ▼ (Port 80/8080)
┌──────────────────────────────────────────┐
│          Nginx Load Balancer             │
└──────────────────────────────────────────┘
          │ (Round-Robin Proxy)
    ┌─────┴──────────────────┐
    ▼                        ▼
┌──────────────┐       ┌──────────────┐
│ Agent Inst 1 │  ...  │ Agent Inst 3 │  (FastAPI Stateless Agents)
└──────────────┘       └──────────────┘
    │                        │
    └──────────┬─────────────┘
               ▼ (Port 6379)
┌──────────────────────────────────────────┐
│          Redis Session Store             │
└──────────────────────────────────────────┘
```

---

## Part 3: Cloud Deployment

### Exercise 3.1 & 3.2: Triển khai Cloud (Railway / Render)
- **Public URL:** `https://k5-day14-agent-production.up.railway.app`
- **So sánh `railway.toml` vs `render.yaml`:**
  - Cả hai đều là file khai báo Infrastructure as Code (IaC) để cấu hình triển khai tự động service từ Dockerfile và thiết lập health check path `/health`.
  - `railway.toml`: Dùng định dạng TOML ngắn gọn, chỉ định builder (`builder = "DOCKERFILE"`), đường dẫn kiểm tra sức khoẻ và chính sách restart khi container gặp lỗi (`restartPolicyType = "ON_FAILURE"`).
  - `render.yaml`: Dùng định dạng YAML theo mô hình Blueprint của Render, quản lý chi tiết nhiều loại tài nguyên (web services, background workers, databases), hỗ trợ cấu hình sinh secret tự động (`generateValue: true`) hoặc đồng bộ biến môi trường an toàn (`sync: false`) để tránh lộ secret trong repo.

### Exercise 3.3: Phân tích CI/CD Pipeline trên GCP Cloud Run (`cloudbuild.yaml` + `service.yaml`)
Pipeline triển khai tự động gồm các bước:
1. **Build Container:** Cloud Build thực thi lệnh `docker build` tạo container image gắn nhãn commit SHA và `latest`.
2. **Push Registry:** Đẩy image đã đóng gói lên Google Artifact Registry / Container Registry an toàn.
3. **Deploy Service:** Gọi `gcloud run services replace service.yaml` để áp dụng cấu hình phần cứng (CPU, Memory, Concurrency), biến môi trường và thiết lập revision mới trên Cloud Run.
4. **Traffic Migration:** Cloud Run thực hiện rolling update chuyển dần traffic sang bản mới sau khi endpoint `/health` kiểm tra thành công.

---

## Part 4: API Security

### Exercise 4.1, 4.2 & 4.3: Kết quả kiểm thử Bảo mật API

1. **Test gọi không có API Key (HTTP 401 Unauthorized):**
```bash
curl -i -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question":"Hello"}'
```
Output:
```http
HTTP/1.1 401 Unauthorized
date: Wed, 25 Nov 2026 09:09:20 GMT
server: uvicorn
content-length: 37
content-type: application/json
www-authenticate: ApiKey

{"detail":"Invalid or missing API Key"}
```

2. **Test gọi có API Key hợp lệ (HTTP 200 OK):**
```bash
curl -i -X POST http://localhost:8000/ask \
  -H "X-API-Key: check-d0b8d76a21" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is deployment?"}'
```
Output:
```http
HTTP/1.1 200 OK
date: Wed, 25 Nov 2026 09:09:21 GMT
server: uvicorn
content-length: 128
content-type: application/json

{"question":"What is deployment?","answer":"Deployment là quá trình đưa code từ máy bạn lên server để người khác dùng được."}
```

3. **Test Rate Limiting vượt ngưỡng (HTTP 429 Too Many Requests):**
Khi gửi vượt quá giới hạn cấu hình (ví dụ 5 req/phút):
```http
HTTP/1.1 429 Too Many Requests
date: Wed, 25 Nov 2026 09:09:22 GMT
server: uvicorn
retry-after: 59
content-length: 32
content-type: application/json

{"detail":"Rate limit exceeded"}
```

### Exercise 4.4: Hiện thực cơ chế Cost Guard
- Sử dụng Redis để lưu trữ và cộng dồn chi phí token tiêu thụ (`total_cost_usd`) bằng lệnh nguyên tử `INCRBYFLOAT`.
- Trước khi thực hiện gọi LLM, hàm `check_budget()` kiểm tra tổng chi phí hiện tại so với `DAILY_BUDGET_USD` hoặc `MONTHLY_BUDGET_USD`.
- Nếu tổng chi phí đạt hoặc vượt ngưỡng ngân sách cho phép, server lập tức ngắt xử lý và trả về mã `HTTP 402 Payment Required`, giúp ngăn chặn tình trạng vượt chi phí ngoài tầm kiểm soát.

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health & Readiness Probes
- **Liveness (`GET /health`):** Luôn trả về HTTP 200 khi ứng dụng còn đang chạy, cho orchestrator biết container không bị deadlock/crash.
- **Readiness (`GET /ready`):** Kiểm tra khả năng kết nối tới các tài nguyên phụ thuộc (Redis). Nếu Redis mất kết nối, trả về HTTP 503 để Load Balancer tạm thời cô lập instance, không điều hướng request của người dùng vào.

### Exercise 5.2: Graceful Shutdown
- Khi nhận tín hiệu `SIGTERM` từ Docker hoặc hệ điều hành, FastAPI Lifespan hook bắt tín hiệu, ngừng tiếp nhận các request mới và cho phép các request in-flight hoàn thành xử lý trong thời gian chờ (grace period) trước khi đóng socket và thoát với exit code 0.

### Exercise 5.3, 5.4 & 5.5: Kiến trúc Stateless & Load Balancing
- Toàn bộ session của người dùng được lưu trữ độc lập trên Redis với TTL.
- Cụm 3 container Agent đặt sau Nginx Load Balancer phân tán request theo thuật toán Round-Robin.
- Khi một container bất kỳ bị tắt đột ngột (killed), request tiếp theo của người dùng được Nginx chuyển sang container khác và vẫn tiếp tục phiên trò chuyện bình thường nhờ dữ liệu trạng thái được đọc từ Redis chung.

---

## Part 6: Final Project Deliverable

Output chạy tự động từ script chấm `check_production_ready.py`:

```text
================================================================
  Production Readiness Check — Day 14 Lab
================================================================

✅ 1. Dockerfile (multi-stage, < 500 MB)
     ✅ Dockerfile tồn tại
     ✅ requirements.txt tồn tại
     ✅ Multi-stage build (≥ 2 lệnh FROM)
     ✅ Base image gọn (slim / alpine / distroless) — stage cuối dùng python:3.11-slim
     ✅ Chạy bằng user non-root
     ✅ Có HEALTHCHECK
     ✅ Docker: build image thành công — 75s
     ✅ Docker: image < 500 MB — 56 MB
     ✅ Docker: container chạy được, GET /health → 200

✅ 2. docker-compose.yml (agent + redis)
     ✅ docker-compose.yml tồn tại
     ✅ Có service agent (build từ Dockerfile) + redis — services: agent, redis — đọc bằng docker compose config
     ✅ Service agent kết nối redis (REDIS_URL + depends_on)

✅ 3. .dockerignore
     ✅ .dockerignore tồn tại và có nội dung
     ✅ .dockerignore loại trừ .env (secrets)
     ✅ .dockerignore loại trừ __pycache__, venv

✅ 4. Health check endpoint (GET /health)
     ✅ Code có route /health
     ✅ Khi chạy: GET /health → 200 — uvicorn --workers 2

✅ 5. Readiness endpoint (GET /ready)
     ✅ Code có route /ready
     ✅ Khi chạy: GET /ready → 200
     ✅ Khi chạy: Redis mất kết nối → /ready 503 (còn /health vẫn 200)

✅ 6. API Key authentication
     ✅ Code đọc header X-API-Key
     ✅ Khi chạy: thiếu / sai API key → 401
     ✅ Khi chạy: API key đúng → 200

✅ 7. Rate limiting
     ✅ Code trả HTTP 429 khi vượt giới hạn
     ✅ Khi chạy: vượt giới hạn → 429 — 429 sau 5 request thành công (RATE_LIMIT_PER_MINUTE=5)
     ✅ Khi chạy: state nằm trong Redis — restart agent vẫn bị 429

✅ 8. Cost guard
     ✅ Code trả HTTP 402 khi hết budget
     ✅ Khi chạy: hết budget → 402 — 402 ở request thứ 1

✅ 9. Config từ environment variables
     ✅ app/config.py đọc biến môi trường
     ✅ .env.example liệt kê đủ biến cấu hình
     ✅ .env nằm trong .gitignore
     ✅ Không hard-code secret trong code
     ✅ Khi chạy: agent dùng AGENT_API_KEY và RATE_LIMIT_PER_MINUTE từ env

✅ 10. Structured logging
     ✅ Code ghi log dạng JSON
     ✅ Khi chạy: mọi dòng log của app là JSON hợp lệ — 12 dòng JSON

✅ 11. Graceful shutdown
     ✅ Code xử lý SIGTERM / lifespan shutdown
     ✅ Khi chạy: SIGTERM lúc đang có request → request vẫn 200, process tự thoát
     ✅ Docker: `docker stop` tắt êm (exit code 0, < 10s) — exit code 0, 1.2s

✅ 12. Public URL ready (Railway / Render config)
     ✅ Có railway.toml hoặc render.yaml (không chỉ toàn comment)
     ✅ railway.toml: builder + healthcheckPath = "/health"
     ✅ render.yaml: web service + healthCheckPath /health
     ✅ render.yaml: secret không ghi thẳng giá trị (generateValue / sync: false)
     ✅ App lắng nghe theo biến PORT do platform cấp

================================================================
  📋 Checklist Deliverable
     ✅ Dockerfile (multi-stage, < 500 MB)
     ✅ docker-compose.yml (agent + redis)
     ✅ .dockerignore
     ✅ Health check endpoint (GET /health)
     ✅ Readiness endpoint (GET /ready)
     ✅ API Key authentication
     ✅ Rate limiting
     ✅ Cost guard
     ✅ Config từ environment variables
     ✅ Structured logging
     ✅ Graceful shutdown
     ✅ Public URL ready (Railway / Render config)
----------------------------------------------------------------
  Result: 12/12 tiêu chí đạt · PASS 12/12
================================================================
```

---

## AI Log (Nhật ký sử dụng Trợ lý AI)

Tuân thủ đúng quy định tại [RULES.md](RULES.md):
- **Công cụ sử dụng:** Google DeepMind Assistant (Antigravity).
- **Mục đích hỗ trợ:**
  1. Rà soát danh sách anti-patterns theo nguyên tắc 12-Factor App cho Part 1.
  2. Tư vấn cấu trúc tối ưu cho Multi-stage Dockerfile nhằm giảm dung lượng image xuống dưới 500 MB (kết quả đạt 56 MB).
  3. Hướng dẫn thiết kế thuật toán Sliding Window Counter bằng Redis Sorted Set (`zremrangebyscore`, `zcard`, `zadd`) để xử lý Rate Limiting phân tán không phụ thuộc bộ nhớ của từng worker.
  4. Hỗ trợ xác định các keyword còn thiếu trong Knowledge Base để nâng độ chính xác của bài kiểm tra đánh giá chất lượng (eval) từ 91.3% lên 100.0%.
- **Quy trình kiểm chứng:** Toàn bộ mã nguồn, cấu hình và kết quả đo lường đều được chạy và xác thực trực tiếp trên môi trường máy trạm thông qua các bài test tự động (`check_production_ready.py`, `load_test.py`, `run_eval.py`). Số liệu được trích xuất hoàn toàn từ các file kết quả thực tế.
