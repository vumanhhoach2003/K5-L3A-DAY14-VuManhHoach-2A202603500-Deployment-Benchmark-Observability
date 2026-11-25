# Benchmark & Observability Report — Day 14

**Họ tên:** Vũ Mạnh Hoạch  
**MSSV:** 2A202603500  
**Lớp:** K5-L3A  
**Khóa học:** AICB-P1 VinUniversity 2026  
**Ngày chạy:** 2026-11-25  
**Môi trường:** Windows 10/11 x64, Docker Desktop (WSL2 Linux Engine), Python 3.12, 4 Cores CPU / 8GB RAM  

---

## 1. SLO của agent

| SLI | SLO | Lý do chọn ngưỡng này |
|---|---|---|
| p95 latency `/ask` | < 500 ms | Đảm bảo trải nghiệm tương tác conversational AI mượt mà, phản hồi tức thời cho người dùng. |
| Error rate `/ask` | < 2.0 % | Đảm bảo độ sẵn sàng cao của dịch vụ, phòng ngừa timeout, rate limit và sự cố nghẽn mạng upstream. |
| Accuracy trên golden dataset | ≥ 95.0 % | Đảm bảo agent cung cấp thông tin chính xác, tin cậy về kiến thức kỹ thuật và nghiệp vụ, ngăn chặn hallucination. |

---

## 2. Benchmark hiệu năng (develop, `load_test.py`)

### 2.1 Concurrency vs latency (agent v2)

*Dữ liệu trích xuất từ các file report tại `reports/load_v2_c*.json`:*

| Concurrency | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Error rate | SLO |
|---|---|---|---|---|---|---|
| 1 | 5.19 | 169.5 | 202.8 | 1652.9 | 1.00% | PASS |
| 10 | 42.08 | 172.4 | 444.0 | 1650.9 | 1.67% | PASS |
| 50 | 68.88 | 327.5 | 1706.9 | 2456.6 | 1.33% | FAIL |
| 100 | 39.25 | 1028.5 | 5171.4 | 5447.3 | 1.67% | FAIL |

**Nhận xét:** RPS có tăng tuyến tính theo concurrency không? Vì sao?

- **RPS không tăng tuyến tính theo concurrency**:
  - Khi concurrency tăng từ 1 lên 10, RPS tăng mạnh từ 5.19 lên 42.08 req/s (~8.1x) do tận dụng tốt cơ chế non-blocking async I/O của FastAPI và Uvicorn trong lúc chờ mock LLM.
  - Khi concurrency tăng lên 50, RPS đạt đỉnh ở mức 68.88 req/s.
  - Tuy nhiên, khi concurrency tiếp tục tăng lên 100, RPS **giảm mạnh xuống 39.25 req/s** đồng thời độ trễ tăng vọt (p50 nhảy từ 327.5ms lên 1028.5ms, p95 lên tới 5171.4ms).
  - **Nguyên nhân**: Single process / single event loop của Python bị bão hòa. Chi phí context switching giữa 100 coroutine đồng thời cùng với hiện tượng tranh chấp CPU và xếp hàng request (queuing effect) khiến thời gian chờ trong hàng đợi vượt quá thời gian xử lý thực tế, làm suy giảm nghiêm trọng throughput toàn hệ thống.

### 2.2 Tail latency

*Dữ liệu trích xuất từ các file report tại `reports/load_v2_slow_*.json`:*

| `MOCK_SLOW_RATE` | avg (ms) | p95 (ms) | p99 (ms) |
|---|---|---|---|
| 0 | 252.7 | 499.8 | 623.7 |
| 0.03 (mặc định) | 239.0 | 485.3 | 1709.6 |
| 0.1 | 380.1 | 1722.8 | 1888.7 |

**Nhận xét:** Chỉ số nào nhạy nhất với request chậm? Vì sao SLO không nên đặt theo average?

- **Chỉ số nhạy nhất với request chậm là p99** (và sau đó là p95 khi tỷ lệ slow request tăng lên 10%):
  - Khi `MOCK_SLOW_RATE` tăng từ 0 lên 0.03 (3% request bị chậm ~1.5s): Giá trị `avg` thậm chí không tăng (252.7ms vs 239.0ms), `p95` vẫn nằm trong khoảng an toàn (< 500ms), nhưng `p99` lập tức **tăng gấp gần 3 lần** từ 623.7ms lên 1709.6ms.
  - Khi `MOCK_SLOW_RATE` tăng lên 0.1 (10% request bị chậm): Cả `p95` (1722.8ms) và `p99` (1888.7ms) đều vượt ngưỡng 1.7 giây.
- **Vì sao SLO KHÔNG nên đặt theo average?**
  - Giá trị trung bình (`average`) bị "che giấu" bởi phần lớn (90-95%) các request nhanh. Ngay cả khi có 3% đến 5% người dùng gặp phải thời gian chờ cực kỳ tồi tệ (1.5 - 2 giây), chỉ số `avg` vẫn hiển thị ở mức ~240ms rất "đẹp".
  - Nếu đặt SLO theo `avg`, hệ thống sẽ bỏ lọt các sự cố nghẽn cổ chai nghiêm trọng ảnh hưởng trực tiếp đến trải nghiệm của người dùng thực tế. Do đó, các tiêu chuẩn sản xuất luôn bắt buộc phải đặt SLO theo các ngưỡng percentile như `p95` và `p99`.

---

## 3. Benchmark chất lượng (develop, `eval/run_eval.py`)

*Dữ liệu trích xuất từ `reports/eval_v1.json`, `reports/eval_v2.json`, và `reports/eval_v2_fixed.json`:*

| Chỉ số | Agent v1 | Agent v2 | Agent v2 (sau khi sửa KB) |
|---|---|---|---|
| Accuracy | 4.3% (1/23) | 91.3% (21/23) | **100.0% (23/23)** |
| Avg tokens / câu | 174.5 | 110.8 | **111.4** |
| Tổng cost (USD) | $0.000402 | $0.000760 | **$0.000772** |
| Cost / câu đúng (USD) | $0.00040215 | $0.00003619 | **$0.00003357** |
| Quality gate | FAIL | FAIL | **PASS** |

**Những câu v2 trả lời sai ban đầu và cách bạn sửa:**

| ID | Keyword bị thiếu | Bạn đã sửa gì |
|---|---|---|
| `security-02` | `expiration` | Bổ sung entry trong Knowledge Base (`mock_llm.py`) về cơ chế xác thực JWT trong FastAPI, bao gồm kiểm tra chữ ký (`signature verification`), hạn sử dụng (`expiration / exp claim`), và sử dụng thư viện `PyJWT`/`python-jose`. |
| `scaling-03` | `metrics` | Bổ sung entry trong Knowledge Base (`mock_llm.py`) về nguyên lý hoạt động của Kubernetes HPA (Horizontal Pod Autoscaler), tính toán số replica dựa trên `metrics` (CPU/Memory utilization và custom metrics từ Metrics Server). |

**Nhận xét về trade-off chất lượng / chi phí / latency giữa v1 và v2:**

- **Về chất lượng:** Agent v1 không có RAG/Knowledge Base nên phải tự sinh câu trả lời (hallucination cao, accuracy chỉ 4.3%). Ngược lại, Agent v2 tích hợp context retrieval giúp câu trả lời cực kỳ chính xác, sau khi tinh chỉnh KB đạt độ chính xác hoàn hảo **100.0%**.
- **Về chi phí:**
  - Agent v1 sinh văn bản dài dòng không trúng trọng tâm (trung bình 129.2 output tokens/câu).
  - Agent v2 có context định hướng nên sinh câu trả lời ngắn gọn, chuẩn xác (chỉ 36.4 output tokens/câu).
  - Mặc dù tổng chi phí của v2 cao hơn v1 một chút do thêm input tokens từ context ($0.000772 vs $0.000402 cho 23 câu), nhưng xét trên chỉ số **Cost / câu đúng (Cost per Correct Answer)**, Agent v2 rẻ hơn Agent v1 tới gần **12 lần** ($0.00003357 so với $0.00040215). Đây là minh chứng rõ rệt cho giá trị kinh tế của giải pháp RAG trong production.
- **Về độ trễ:** Quá trình tìm kiếm context cục bộ chỉ tốn thêm 10-15ms, hoàn toàn xứng đáng với mức tăng vọt về độ chính xác từ 4.3% lên 100%.

---

## 4. Observability stack (production)

### 4.1 Screenshot

- [x] Dashboard Grafana khi đang có tải (thấy rõ Golden Signals): [grafana-dashboard.png](file:///F:/K5-L3A-DAY14-VuManhHoach-2A202603500-Deployment-Benchmark-Observability/screenshots/grafana-dashboard.png)
- [x] Một trace chậm trong Jaeger (thấy span nào chiếm thời gian): [jaeger-slow-trace.png](file:///F:/K5-L3A-DAY14-VuManhHoach-2A202603500-Deployment-Benchmark-Observability/screenshots/jaeger-slow-trace.png)
- [x] Một trace lỗi trong Jaeger (có event `exception`): [jaeger-error-trace.png](file:///F:/K5-L3A-DAY14-VuManhHoach-2A202603500-Deployment-Benchmark-Observability/screenshots/jaeger-error-trace.png)
- [x] Trang Alerts của Prometheus với ít nhất 1 alert đang **firing**: [prometheus-alert-firing.png](file:///F:/K5-L3A-DAY14-VuManhHoach-2A202603500-Deployment-Benchmark-Observability/screenshots/prometheus-alert-firing.png)

### 4.2 Thí nghiệm "phá hệ thống"

| # | Thay đổi | Alert nào firing | Thời gian từ lúc đổi → firing | Panel nào phản ánh rõ nhất |
|---|---|---|---|---|
| A | `MOCK_ERROR_RATE=0.2` | `AgentHighErrorRate` | ~65s (evaluation 5s + for 60s) | Error rate /ask & Request volume |
| B | `MOCK_SLOW_RATE=0.3` | `AgentHighLatencyP95` | ~125s (evaluation 5s + for 120s) | Request Latency (p50, p95, p99) |
| C | `LLM_MODEL=mock-llm-large` | `LLMCostBurnRateHigh` | ~125s (cost vượt $2.0/h) | Token Usage & LLM Cost / Hour |
| D | `docker pause` 1 instance | `AgentInstanceDown` | ~35s (evaluation 5s + for 30s) | Instances Up / Agent Health |
| E | `AGENT_VERSION=v1` | *(Không có alert nào firing)* | N/A | Retrieval hit rate giảm về 0 |

**Thí nghiệm E không làm alert nào firing. Bạn sẽ phát hiện loại sự cố này trong production bằng cách nào?**

- **Bản chất vấn đề:** Khi cấu hình `AGENT_VERSION=v1`, agent không thực hiện truy xuất context (RAG). Về mặt hạ tầng, các request vẫn trả về HTTP 200, độ trễ thậm chí còn nhanh hơn, do đó không vi phạm bất kỳ alert hạ tầng nào (5xx, latency, instance down). Tuy nhiên, chất lượng câu trả lời bị suy giảm nghiêm trọng (hallucination, accuracy rơi từ 100% xuống 4.3%).
- **Cách phát hiện trong môi trường Production:**
  1. **Continuous Synthetic Evaluation (Giám sát định kỳ chất lượng):** Thiết lập cronjob chạy tự động bộ test `eval/run_eval.py` trên tập golden dataset (mỗi 15 hoặc 30 phút) gọi trực tiếp vào production canary endpoint. Nếu accuracy rớt xuống dưới 95%, kích hoạt alert mức Critical `AgentQualityDegraded`.
  2. **Custom Business Metric Alert:** Giám sát metric `retrieval_hits_total` (hoặc retrieval hit rate). Nếu traffic request `/ask` > 0 nhưng `rate(retrieval_hits_total[5m]) == 0`, lập tức kích hoạt alert cảnh báo module RAG bị vô hiệu hóa hoặc cấu hình sai phiên bản.
  3. **User Feedback Loop (Phản hồi người dùng):** Gắn cơ chế thu thập phản hồi (thumbs up / thumbs down) tại giao diện người dùng. Đẩy metric `agent_user_feedback_total{type="negative"}` vào Prometheus và alert khi tỷ lệ negative feedback tăng đột biến.
  4. **Distributed Tracing Audit:** Kiểm tra trong Jaeger xem các trace của `/ask` có thiếu span `agent.retrieve_context` hay không.

### 4.3 Debug bằng trace

Chọn 1 trace chậm nhất tìm được từ hệ thống:

- `trace_id`: `ebfeb0eabc6490856211e24d29fafb13`
- Tổng thời gian: `1657.9` ms
- Span chiếm nhiều thời gian nhất: `chat mock-llm-small` (`1635.4` ms, chiếm **98.6%** tổng thời gian request)
- Dòng log tương ứng (grep theo `trace_id`):

```json
{"ts": "2026-11-25T09:37:14.300138+00:00", "level": "INFO", "service": "observable-agent", "instance": "249279dbe019", "event": "http_request", "trace_id": "ebfeb0eabc6490856211e24d29fafb13", "span_id": "045f76db17b35071", "request_id": "fb9cdb4a6ac3", "method": "POST", "route": "/ask", "status": 200, "ms": 1657.9}
```

Và log chi tiết của span LLM:
```json
{"ts": "2026-11-25T09:37:14.299496+00:00", "level": "INFO", "service": "observable-agent", "instance": "249279dbe019", "event": "llm_call", "trace_id": "ebfeb0eabc6490856211e24d29fafb13", "span_id": "045f76db17b35071", "request_id": "fb9cdb4a6ac3", "model": "mock-llm-small", "agent_version": "v2", "input_tokens": 73, "output_tokens": 35, "cost_usd": 3.2e-05, "llm_ms": 1635.4}
```

---

## 5. Benchmark scaling (production, Locust headless, 100 users, 1 phút)

*Dữ liệu trích xuất từ `benchmark-results/scale_1_stats.csv` và `benchmark-results/scale_3_stats.csv`:*

| Số instance | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Failures |
|---|---|---|---|---|---|
| 1 | 56.45 | 200 | 680 | 1700 | 38 (1.15%) |
| 3 | 56.57 | 200 | **380** | 1700 | **31 (0.93%)** |

*(Ghi chú: Xét trên toàn bộ request bao gồm cả `/health`, RPS tổng đạt 62.00 req/s ở 1 instance và 62.03 req/s ở 3 instances).*

**Giải thích kết quả:** Scale có cải thiện p95 không? Nút thắt nằm ở đâu?

- **Scale có cải thiện đáng kể p95 latency:**
  - Ở 1 instance: Độ trễ p95 của `/ask` là **680 ms** (vi phạm SLO < 500 ms).
  - Khi scale lên 3 instances: Độ trễ p95 của `/ask` **giảm mạnh xuống 380 ms** (giảm 44.1%), đưa hệ thống đạt chuẩn SLO đề ra!
  - Số lượng request bị lỗi/timeout cũng giảm từ 38 xuống 31 request.
- **Nút thắt (Bottleneck) nằm ở đâu?**
  - **Upstream Latency & Concurrency:** Mỗi request LLM đều có độ trễ nền xử lý (~120 - 200ms). Với 1 instance, hàng đợi request bị tích lũy nhanh chóng khi 100 users đồng thời gửi request, làm đội tail latency p95 lên cao.
  - Khi scale lên 3 instances, Nginx đóng vai trò Load Balancer phân bổ đều lưu lượng qua thuật toán round-robin tới 3 container độc lập. Mỗi worker chỉ cần gánh 1/3 số kết nối đồng thời, triệt tiêu hiện tượng nghẽn hàng đợi (queue saturation), giúp p95 giảm về mức an toàn.
  - Tuy nhiên, p99 (1700ms) không giảm vì nó phản ánh tỷ lệ ngẫu nhiên 3% của simulated slow upstream (`MOCK_SLOW_RATE=0.03`). Để khắc phục nút thắt này ở tầng ứng dụng, cần áp dụng timeout ngắn kết hợp retry với exponential backoff hoặc sử dụng mô hình Hedged Requests.

---

## 6. Kết luận

- **3 điều bạn học được về benchmark & observability:**
  1. **Average latency là một cái bẫy:** Tuyệt đối không dùng giá trị trung bình để đánh giá SLA/SLO của hệ thống microservices. Phải sử dụng Percentiles (`p95`, `p99`) để nắm bắt chính xác trải nghiệm của nhóm người dùng bị ảnh hưởng bởi tail latency.
  2. **Sức mạnh hiệp đồng của "3 Trụ cột Observability":**
     - **Metrics (Prometheus & Grafana):** Giúp phát hiện triệu chứng sự cố trong vài giây (Golden Signals: Latency, Traffic, Errors, Saturation).
     - **Traces (OpenTelemetry & Jaeger):** Giúp cô lập chính xác vị trí và span gây chậm hoặc sinh exception trong toàn bộ chuỗi xử lý.
     - **Structured Logs (JSON):** Gắn kết chặt chẽ với Trace qua `trace_id`, giúp truy xuất đầy đủ payload, input tokens, error stacktrace mà không cần mò mẫm phỏng đoán.
  3. **Đánh giá AI Agent bắt buộc phải đo lường 2 chiều:** Không chỉ đo hiệu năng kỹ thuật (RPS, Latency, Concurrency) mà còn phải đo lường chất lượng thông minh (Accuracy, Token cost per correct answer). Kỹ thuật RAG kết hợp LLM nhỏ tối ưu hóa toàn diện cả về chi phí lẫn độ chính xác so với việc gọi LLM lớn đơn thuần.

- **Nếu đưa agent này lên production thật, bạn sẽ thêm metric / alert nào nữa?**
  1. **Semantic Cache Hit Rate:** Bổ sung Redis Semantic Cache phía trước LLM để cache các câu hỏi tương đồng ngữ nghĩa. Giám sát tỷ lệ cache hit (`cache_hit_ratio`), giúp giảm 40-60% chi phí và đưa p95 về < 20ms đối với các câu hỏi lặp lại.
  2. **Upstream LLM Token Quota & Budget Alerts:** Cảnh báo trước khi hạn mức API key của nhà cung cấp (OpenAI / Anthropic / Gemini) chạm ngưỡng 80% hoặc khi tốc độ tiêu thụ ($/giờ) vượt ngân sách dự toán ngày.
  3. **Circuit Breaker Status Metric:** Đo lường trạng thái Circuit Breaker (Closed, Open, Half-Open) kết nối tới upstream LLM để tự động kích hoạt chế độ fallback (trả về câu trả lời từ offline cache hoặc switch sang model backup) khi nhà cung cấp LLM chính gặp sự cố gián đoạn.
  4. **Hallucination & Toxicity Detection Rate:** Tích hợp pipeline kiểm tra an toàn và ảo giác (sử dụng Guardrails hoặc model eval nhỏ), đo lường tỷ lệ vi phạm chính sách nội dung trên từng phiên bản agent.
