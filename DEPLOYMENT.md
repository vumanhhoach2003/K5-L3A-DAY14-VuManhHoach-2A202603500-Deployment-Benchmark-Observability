# Deployment Information

## Public URL
https://k5-day14-agent-production.up.railway.app

## Platform
Railway (Hỗ trợ cấu hình song song `railway.toml` và `render.yaml`)

## Test Commands

Bốn lệnh kiểm tra trực tiếp theo đúng chuẩn Checkpoint 6 (sử dụng cờ `-sS -o /dev/null -w '%{http_code}\n'` để in HTTP status code):

### 1. Health Check (Liveness Probe)
```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://k5-day14-agent-production.up.railway.app/health
# Expected Output: 200
```

### 2. Readiness Check (Readiness Probe)
```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://k5-day14-agent-production.up.railway.app/ready
# Expected Output: 200
```

### 3. API Test — Không có API Key (Bị từ chối)
```bash
curl -sS -o /dev/null -w '%{http_code}\n' -X POST https://k5-day14-agent-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Expected Output: 401
```

### 4. API Test — Có API Key hợp lệ (Thành công)
```bash
curl -sS -o /dev/null -w '%{http_code}\n' -X POST https://k5-day14-agent-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: day14-lab-key" \
  -d '{"question": "What is deployment?"}'
# Expected Output: 200
```

---

## Environment Variables Configured on Platform
Các biến môi trường được cấu hình trực tiếp trên dashboard của nền tảng (không hardcode vào mã nguồn):
- `PORT`: 8000 (hoặc biến do platform cấp động)
- `ENVIRONMENT`: `production`
- `AGENT_API_KEY`: `day14-lab-key`
- `REDIS_URL`: `redis://default:secret@redis-service:6379/0` (kết nối Redis instance nội bộ)
- `RATE_LIMIT_PER_MINUTE`: `10`
- `DAILY_BUDGET_USD`: `1.0`
- `MONTHLY_BUDGET_USD`: `10.0`
- `LOG_LEVEL`: `INFO`

---

## Screenshots
- [Deployment Dashboard](screenshots/dashboard.png)
- [Service Running & Logs](screenshots/running.png)
- [Public URL Test Results](screenshots/test.png)
