# 🎤 KỊCH BẢN THUYẾT TRÌNH DỰ ÁN (PRESENTATION SCRIPT)
## K4 — Ngày 12: Hạ Tầng Cloud & Deployment
**Diễn giả**: Nguyễn Hùng Mạnh (Mã HV: 2A202601256)  
**Thời lượng dự kiến**: 5 – 7 phút  
**Tệp slide đi kèm**: `presentation.html` (14 slide)

---

### 🟢 SLIDE 1: TRANG BÌA & GIỚI THIỆU
*(Thời gian: 30 giây)*

* **Lời nói**:  
  "Em xin chào Lab Coach và toàn thể các bạn! Em tên là Nguyễn Hùng Mạnh, mã học viên 2A202601256.  
  Hôm nay em xin phép thuyết trình về bài tập cá nhân K4 - Ngày 12 với chủ đề: **Hạ tầng Cloud và Deployment**.  
  Mục tiêu trọng tâm của bài lab này là đưa một Chat Service chạy trên môi trường `localhost:8000` lên một địa chỉ cloud công khai hoạt động thật, đảm bảo các tiêu chuẩn bảo mật, giới hạn chi phí, có khả năng scale ngang và triển khai không gián đoạn (zero-downtime deployment)."

---

### 🟢 SLIDE 2: MỤC TIÊU BÀI LAB
*(Thời gian: 45 giây)*

* **Lời nói**:  
  "Để hoàn thành được mục tiêu đưa ứng dụng lên production một cách an toàn và chuẩn mực, dự án của em giải quyết 6 bài toán hạ tầng cốt lõi:
  1. **12-Factor Config**: Tách hoàn toàn cấu hình ra khỏi code, đặc biệt các bí mật như API token phải bắt buộc có, không dùng giá trị mặc định để fail fast.
  2. **Multi-stage Docker**: Đóng gói container chuẩn hóa, chạy dưới quyền user thường (non-root) và tối ưu kích thước image dưới 400MB.
  3. **API Security**: Bảo vệ endpoint bằng Bearer token theo chuẩn RFC 6750, kết hợp thuật toán Token Bucket rate limit và Cost Guard quản lý chi phí theo ngày.
  4. **Health & Graceful Shutdown**: Phân biệt rành mạch giữa Liveness probe và Readiness probe, đồng thời bắt tín hiệu SIGTERM để không rớt request khi deploy bản mới.
  5. **Stateless Architecture**: Lưu trữ trạng thái hội thoại hoàn toàn ngoài process (tại Redis) để sẵn sàng scale ngang.
  6. **Cloud Deployment**: Triển khai thực tế ứng dụng lên dịch vụ Render với hạ tầng Redis private."

---

### 🟢 SLIDE 3: KIẾN TRÚC TỔNG QUAN LUỒNG REQUEST
*(Thời gian: 45 giây)*

* **Lời nói**:  
  "Trên màn hình là sơ đồ kiến trúc luồng xử lý của endpoint chính `POST /chat`.  
  Khi một client gửi request tới, request sẽ đi qua một chuỗi các lớp kiểm tra nghiêm ngặt **TRƯỚC KHI** chạm tới Mock LLM:
  * **Bước 1**: Kiểm tra Bearer token qua `verify_bearer_token`. Nếu thiếu hoặc sai -> Trả về ngay **401 Unauthorized**.
  * **Bước 2**: Kiểm tra Token Bucket rate limiter. Nếu client gọi quá dồn dập -> Trả về **429 Too Many Requests**.
  * **Bước 3**: Kiểm tra Cost Guard. Nếu client đã tiêu hết ngân sách trong ngày -> Trả về **402 Payment Required**.
  * **Bước 4**: Chỉ sau khi vượt qua cả 3 lớp bảo vệ, hệ thống mới lấy lịch sử hội thoại từ Redis Store, gọi Mock LLM tạo câu trả lời, ghi nhận token & chi phí, rồi mới trả về kết quả 200 cho client.

  *Điểm mấu chốt ở đây là: Việc kiểm tra bảo mật và hạn mức chi phí luôn được thực hiện trước khi gọi LLM để tránh tình trạng vừa bị tốn tiền vừa phải trả lỗi cho người dùng.*"

---

### 🟢 SLIDE 4: CẤU TRÚC MÃ NGUỒN DỰ ÁN
*(Thời gian: 30 giây)*

* **Lời nói**:  
  "Toàn bộ mã nguồn backend được tổ chức gọn gàng trong thư mục `app/` theo từng trách nhiệm đơn lẻ (Single Responsibility Principle):
  * `config.py`: Đọc cấu hình môi trường.
  * `main.py`: Điểm ráp nối FastAPI, định nghĩa các endpoint và lifecycle.
  * `auth.py`: Đảm nhận xác thực Bearer token.
  * `rate_limiter.py`: Cài đặt thuật toán Token Bucket.
  * `cost_guard.py`: Quản lý ngân sách chi phí theo ngày.
  * `store.py`: Tương tác với Redis để lưu hội thoại.
  * `lifecycle.py`: Xử lý tín hiệu tắt ứng dụng (Graceful Shutdown).
  * `logging_utils.py`: Tạo log định dạng JSON cấu trúc."

---

### 🟢 SLIDE 5: CP1 — 12-FACTOR CONFIG & STRUCTURED LOGGING
*(Thời gian: 45 giây)*

* **Lời nói**:  
  "Ở Checkpoint 1, em áp dụng hai nguyên tắc thiết kế quan trọng:  
  Thứ nhất, cấu hình ứng dụng được định nghĩa qua `pydantic-settings`. Đặc biệt, trường `api_token` **không được phép có giá trị mặc định**. Nếu quên đặt biến môi trường trên Cloud, ứng dụng sẽ dứt khoát dừng ngay (Fail Fast) khi khởi động chứ không chạy âm thầm với token mặc định dễ bị tấn công.  
  Thứ hai là **Structured Logging**. Thay vì dùng `print()` văn bản thông thường, em xuất log dạng JSON 1 dòng chứa đầy đủ các trường `event`, `severity`, `ts`, `client_id` và `usd_cost`. Nhờ đó, các hệ thống theo dõi trên cloud có thể tự động đọc, lọc sự cố hoặc đặt cảnh báo chi phí một cách chính xác."

---

### 🟢 SLIDE 6: CP2 — DOCKER MULTI-STAGE & BẢO MẬT IMAGE
*(Thời gian: 45 giây)*

* **Lời nói**:  
  "Sang Checkpoint 2 về đóng gói ứng dụng, em sử dụng kỹ thuật **Multi-stage Dockerfile**:
  * Stage `builder` chuyên tải và cài đặt các package Python vào một thư mục tạm `/install`.
  * Stage `runtime` chỉ copy phần thư viện đã cài đặt và mã nguồn ứng dụng, giúp loại bỏ toàn bộ rác build. Kết quả thu được image vô cùng gọn nhẹ, chỉ khoảng **61 MB** (nhỏ hơn rất nhiều so với hạn mức 400MB).
  * Về bảo mật: Em tạo và chuyển sang chạy dưới quyền user thường `USER appuser` thay vì `root`. Nhỡ như ứng dụng có lỗ hổng code execution, kẻ tấn công cũng bị chặn lại bởi quyền hạn tối thiểu, không thể thao tác lên hệ thống root của container.
  * Ngoài ra, em cấu hình file `docker-compose.yml` gồm 3 service `chat`, `redis` và `nginx` làm load balancer hỗ trợ test scale 3 instance."

---

### 🟢 SLIDE 7: CP3 — API SECURITY: BEARER TOKEN
*(Thời gian: 45 giây)*

* **Lời nói**:  
  "Ở Checkpoint 3 về bảo mật API:  
  Em tuân thủ chuẩn **RFC 6750**, yêu cầu token nằm trong header `Authorization: Bearer <token>`.  
  Một điểm kỹ thuật quan trọng khi so sánh token: Em sử dụng hàm `secrets.compare_digest(token, api_token)` thay vì phép so sánh `==`. Phép `==` thông thường sẽ dừng ngay ở ký tự đầu tiên bị sai, khiến thời gian phản hồi bị chênh lệch và lộ thông tin cho các cuộc tấn công quét thời gian (Timing Attack). `compare_digest` đảm bảo thời gian so sánh luôn cố định.  
  Bên cạnh đó, mọi trường hợp 401 đều trả về chung một thông báo lỗi cùng header `WWW-Authenticate: Bearer` theo đúng chuẩn HTTP."

---

### 🟢 SLIDE 8: CP3 — TOKEN BUCKET & COST GUARD
*(Thời gian: 50 giây)*

* **Lời nói**:  
  "Cũng trong CP3, em cài đặt hai cơ chế giới hạn tài nguyên:
  1. **Token Bucket Rate Limiter**: Mỗi client có một 'xô' chứa tối đa 10 token, tự nạp lại với tốc độ 10 token/phút. Thuật toán này cho phép người dùng gửi một đợt request dồn dập (burst) khi cần nhưng vẫn chặn đứng các cuộc tấn công spam liên tục. Đặc biệt, em luôn giới hạn `min(capacity, tokens)` để tránh trường hợp client im lặng lâu ngày tích lũy vô hạn token.
  2. **Cost Guard theo ngày**: Hạn mức được chốt theo **ngày** (mặc định $1.00/ngày) thay vì theo tháng. Key Redis gắn nhãn theo ngày UTC (ví dụ `spend:client1:2026-08-10`). Lý do là nếu xảy ra sự cố lãng phí API lúc 2 giờ sáng, thiệt hại tối đa chỉ là $1 và sang ngày hôm sau dịch vụ tự động phục hồi mà không cần can thiệp thủ công."

---

### 🟢 SLIDE 9: CP4 — SCALING & RELIABILITY
*(Thời gian: 50 giây)*

* **Lời nói**:  
  "Checkpoint 4 tập trung vào tính tin cậy và khả năng mở rộng:
  * **Stateless**: Lịch sử hội thoại được đẩy toàn bộ ra ngoài process và lưu trong **Redis List**, chỉ giữ 12 tin nhắn gần nhất (`LTRIM`) và hết hạn sau 3 ngày. Việc này giúp ứng dụng có thể scale lên N instance đằng sau Load Balancer mà không lo mất nhớ hội thoại.
  * **Tách riêng Health Check**:
    * Endpoint `/healthz` (Liveness) cực nhẹ, không kết nối Redis, chỉ trả lời câu hỏi 'process còn sống không?'.
    * Endpoint `/readyz` (Readiness) mới thực hiện `ping()` tới Redis.  
    * *Ý nghĩa*: Nếu gộp 2 endpoint này, khi Redis chập chờn 30s, orchestrator sẽ tưởng container bị chết và restart liên tục, gây ra thảm họa 'restart storm'.
  * **Graceful Shutdown**: Hệ thống bắt tín hiệu `SIGTERM`, bật cờ `draining = True` để `/healthz` trả 503 cho Load Balancer ngắt traffic mới, sau đó xử lý nốt các request dở dang rồi mới thoát an toàn."

---

### 🟢 SLIDE 10: CP5 — CLOUD DEPLOYMENT TRÊN RENDER
*(Thời gian: 40 giây)*

* **Lời nói**:  
  "Ở Checkpoint 5, em đã deploy thành công Chat Service lên nền tảng **Render (Web Service)** tại hạ tầng Singapore, đi kèm với dịch vụ Render Key Value Redis riêng biệt.  
  Địa chỉ công khai hiện tại của bài lab là: `https://day12-chat-cjnn.onrender.com`.  
  Tất cả biến môi trường nhạy cảm như `API_TOKEN` và `REDIS_URL` đều được cấu hình an toàn trên Dashboard của Render, hoàn toàn không bị rò rỉ trong git repository.  
  Kết quả Smoke test trực tiếp trên môi trường thật cho thấy `/healthz` 200, `/readyz` 200, thử gọi thiếu token trả 401 và gọi đúng token trả về 200 kèm phản hồi của LLM."

---

### 🟢 SLIDE 11: BONUS — CI/CD VỚI GITHUB ACTIONS
*(Thời gian: 35 giây)*

* **Lời nói**:  
  "Bên cạnh các phần bắt buộc, em đã tự dựng một pipeline CI/CD hoàn chỉnh bằng **GitHub Actions** tại `.github/workflows/ci.yml`:
  * Mỗi khi có commit hoặc Pull Request, workflow sẽ tự động chạy bộ test `pytest`.
  * Nếu test pass, bước tiếp theo sẽ thực thi `docker build` để kiểm tra việc đóng gói image.
  * Khi code được gộp vào nhánh `main`, hệ thống sẽ tự động gọi webhook của Render để trigger việc deploy bản mới lên production. Toàn bộ quy trình diễn ra tự động và khép kín."

---

### 🟢 SLIDE 12: TỔNG KẾT ĐIỂM DỰ ÁN
*(Thời gian: 25 giây)*

* **Lời nói**:  
  "Tổng kết lại kết quả đánh giá tự động từ file `grade.py`:
  Dự án đạt điểm tối đa **100/100 điểm** trên tất cả các tiêu chí: CP1 (15đ), CP2 (15đ), CP3 (20đ), CP4 (20đ), CP5 (15đ), 10 câu hỏi phản ánh `exercises.md` (15đ) và điểm cộng Bonus CI/CD (+10đ)."

---

### 🟢 SLIDE 13: BÀI HỌC RÚT RA
*(Thời gian: 40 giây)*

* **Lời nói**:  
  "Qua bài lab Ngày 12 này, em đã rút ra 6 bài học thực tế rất giá trị khi thiết kế hệ thống cloud:
  1. Nguyên tắc **Fail Fast** giúp phát hiện sớm sai sót cấu hình ngay lúc deploy.
  2. Chiến lược **Defense in Depth** (bảo vệ nhiều lớp: Auth ➔ Rate Limit ➔ Cost Guard) giúp kiểm soát rủi ro triệt để.
  3. Tuyệt đối **không gộp Liveness và Readiness probe** để tránh lỗi dồn dập.
  4. Giữ ứng dụng **Stateless** là chìa khóa vàng để scale ngang.
  5. Xử lý **Graceful Shutdown** giúp mang lại trải nghiệm 0-downtime cho người dùng.
  6. **Structured Logging** là công cụ không thể thiếu để vận hành ứng dụng trên Cloud."

---

### 🟢 SLIDE 14: KẾT THÚC
*(Thời gian: 15 giây)*

* **Lời nói**:  
  "Bài thuyết trình của em đến đây là kết thúc. Em xin cảm ơn Lab Coach và các bạn đã chú ý theo dõi!  
  Em rất sẵn sàng nhận các câu hỏi phản biện và đóng góp ý kiến từ Lab Coach ạ!"

---

## 💡 GỢI Ý CÁC CÂU HỎI LAB COACH CÓ THỂ HỎI & CÁCH TRẢ LỜI (Q&A PREPARATION)

1. **Hỏi**: *Vì sao `api_token` lại không được đặt giá trị mặc định trong `config.py`?*  
   * **Trả lời**: "Dạ, vì nếu có giá trị mặc định (như 'changeme'), khi deploy lên cloud mà em quên set biến `API_TOKEN`, container vẫn sẽ khởi động bình thường. Người ngoài có thể đoán được token mặc định và sử dụng API trái phép làm tiêu tốn ngân sách trước khi em kịp phát hiện. Việc không đặt mặc định buộc ứng dụng phải crash ngay lúc khởi động (Fail Fast) để ta nhận ra lỗi cấu hình lập tức."

2. **Hỏi**: *Tại sao lại dùng `secrets.compare_digest` mà không dùng phép so sánh `==` trong `auth.py`?*  
   * **Trả lời**: "Dạ, phép so sánh `==` sẽ dừng ngay ở ký tự đầu tiên bị sai, khiến thời gian phản hồi của request sai ở ký tự thứ 1 khác với request sai ở ký tự thứ 10. Kẻ tấn công có thể đo thời gian chênh lệch này (Timing Attack) để dò từng ký tự của token. `secrets.compare_digest` luôn duyệt hết toàn bộ chuỗi nên thời gian phản hồi là cố định, triệt tiêu nguy cơ này."

3. **Hỏi**: *Sự khác nhau giữa `/healthz` và `/readyz` là gì?*  
   * **Trả lời**: "Dạ, `/healthz` (Liveness probe) chỉ kiểm tra xem process Python/FastAPI có đang chạy không, không gọi tới Redis. Nếu `/healthz` lỗi, container sẽ bị restart. Trong khi đó `/readyz` (Readiness probe) sẽ ping tới Redis để xem service đã sẵn sàng xử lý dữ liệu chưa. Nếu Redis sập, `/readyz` trả 503 để Load Balancer không đẩy traffic vào, nhưng container vẫn sống chờ Redis hồi phục chứ không bị restart liên tục."

4. **Hỏi**: *Tại sao trong Dockerfile lại cần tạo `USER appuser`?*  
   * **Trả lời**: "Dạ, mặc định Docker chạy ứng dụng bằng quyền `root`. Nếu code hoặc thư viện có lỗ hổng thi hành mã từ xa (RCE), kẻ tấn công sẽ có toàn quyền root trong container. Đổi sang `appuser` (non-root) giúp giới hạn tối đa phạm vi ảnh hưởng (blast radius), chặn kẻ tấn công ghi đè hệ thống hoặc leo thang đặc quyền."
