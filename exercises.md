# Phiếu Phản Ánh — K4 Ngày 12

> Bài làm cá nhân, ghi lại theo những gì đã quan sát khi triển khai repository này.

Họ và tên: **Nguyễn Hùng Mạnh**<br>
Mã học viên: **2A202601256**

---

### Câu 1 — Fail fast (CP1)

Nếu em quên khai báo `API_TOKEN` trên Render mà code lại có mặc định `"changeme"`, service vẫn lên public. Người biết hoặc đoán token mặc định đó có thể gọi `/chat`; với LLM thật thì họ có thể tiêu ngân sách của em trước khi em phát hiện. Khi `api_token` bắt buộc, Pydantic báo lỗi ngay lúc container khởi động; health check không qua và log Render chỉ thẳng vào biến bị thiếu. Em sửa cấu hình trước khi service nhận một request nào.

---

### Câu 2 — Log cho máy đọc (CP1)

Sau khi gửi một request local với `X-Client-Id: exercise-log`, em nhận được dòng log JSON:

```json
{"event":"chat_completed","severity":"INFO","ts":"2026-08-10T07:29:50.729881+00:00","client_id":"exercise-log","prompt_tokens":5,"completion_tokens":38,"usd_cost":0.00002355}
```

Từ các field này, em có thể lọc riêng toàn bộ request của một `client_id` để điều tra abuse, và cộng `prompt_tokens`, `completion_tokens` hoặc `usd_cost` theo thời gian để đặt cảnh báo chi phí. `print("đã trả lời xong")` không có timestamp chuẩn, severity, client hay số liệu để máy lọc, nhóm và tính tổng đáng tin cậy.

---

### Câu 3 — Kích thước image (CP2)

Em build lại ngày 2026-08-10 từ cùng source context:

| Bản | Dung lượng đo bằng `docker image inspect` |
|---|---:|
| 1 stage (`Dockerfile.single-stage` dùng để đo) | 63,688,192 bytes ≈ 60.738 MB |
| Multi-stage (`Dockerfile` production) | 63,690,182 bytes ≈ 60.740 MB |

Kết quả gần như bằng nhau, thậm chí bản multi-stage lớn hơn khoảng 1,990 bytes. Điều này hợp lý với Dockerfile hiện tại: bản một-stage cũng dùng `python:3.11-slim`, `pip --no-cache-dir` và không cài compiler hay apt build dependencies. Builder của bản multi-stage chỉ tạo `/install`, rồi runtime vẫn cần copy toàn bộ package Python đó để chạy. Phần chênh lệch nhỏ chủ yếu là metadata/layer và user không phải root của bản production; không có build artifact lớn nào để loại bỏ. Multi-stage vẫn tốt vì tách ranh giới build/runtime; nếu có compiler, header hoặc cache build thì lợi ích dung lượng mới rõ rệt.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Em thêm tạm một dòng trắng vào `app/main.py` rồi build với `--progress=plain`, sau đó khôi phục file. Các layer `COPY requirements.txt`, `RUN pip install --prefix=/install`, `COPY --from=builder /install /usr/local` vẫn `CACHED`. `COPY app ./app` chạy lại; các bước sau nó (`COPY utils` và tạo `appuser`) cũng phải tạo lại output layer. Vì dependency nằm trước source code nên chỉ sửa code không bắt Docker tải/cài package lại.

Nếu đặt `COPY . .` trước `RUN pip install`, một thay đổi ở bất kỳ file nào trong context (kể cả `app/main.py`) sẽ làm layer `COPY . .` đổi hash. `RUN pip install` đứng sau layer đó sẽ mất cache và chạy lại, dù `requirements.txt` không đổi; build sẽ chậm hơn và phụ thuộc mạng không cần thiết.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Chuỗi rủi ro là: một input hoặc dependency có lỗ hổng cho kẻ tấn công chạy lệnh Python trong container; nếu process là root, lệnh đó có toàn quyền trong container. Từ đó họ có thể đọc secret/file mount, cài tool, dò các service nội bộ; nếu Docker socket, mount nhạy cảm, capability quá rộng hoặc lỗi runtime/host đi kèm thì phạm vi có thể leo sang host. `USER appuser` cắt chuỗi ngay sau remote-code-execution: code bị chiếm chỉ có quyền user thường, không thể ghi vùng root, đổi system package hay tự cấp quyền. Đây là giảm blast radius, không thay thế việc vá lỗ hổng và cấu hình container tối thiểu quyền.

---

### Câu 6 — Bearer token (CP3)

HTTP 401 phải gửi `WWW-Authenticate: Bearer` để client biết endpoint dùng cơ chế xác thực nào và biết cần gửi lại credential theo chuẩn RFC 6750. Em trả cùng thông báo `invalid or missing bearer token` cho thiếu header, sai scheme và sai token vì nếu phân biệt, endpoint trở thành oracle cho người dò: họ biết header đã đúng format hay token đã gần đúng đến đâu. Người dùng hợp lệ vẫn sửa được bằng tài liệu API; thông tin chi tiết nên nằm trong log nội bộ, không trả cho người tấn công.

---

### Câu 7 — Token bucket (CP3)

Với bucket đã tồn tại và đang đầy, sau 10 phút tốc độ nạp là `10 / 60` token/giây nên có thêm 100 token theo công thức, nhưng `min(capacity, ...)` chặn bucket ở 10. Client gửi burst được 10 request; request thứ 11 bị 429. Nếu bỏ `min`, trạng thái đầy 10 token cộng thêm 100 token thành 110, tức client có thể gửi 110 request liên tiếp. Khi đó “capacity 10” không còn là giới hạn burst; thời gian im lặng biến thành lượng request tích luỹ vô hạn.

---

### Câu 8 — Ngân sách theo ngày (CP3)

Hạn mức $30/tháng cho phép sự cố lúc 2 giờ sáng đốt tối đa cả $30 trước khi chặn, và client phải chờ tới kỳ tháng mới để tự có lại ngân sách. Với $1/ngày, thiệt hại của một client trong ngày đó tối đa $1; khóa chi tiêu của lab mang ngày UTC nên sang ngày UTC kế tiếp service tự dùng key mới và hoạt động lại. Tổng lý thuyết một tháng vẫn xấp xỉ $30, nhưng blast radius của một sự cố ngắn giảm từ $30 xuống $1 và không cần người vận hành mở khóa thủ công.

---

### Câu 9 — `/healthz` khác `/readyz` (CP4)

Nếu gộp probe và probe đó kiểm tra Redis, Redis mất kết nối 30 giây sẽ diễn ra theo thứ tự: (1) cả ba container trả probe lỗi; (2) orchestrator coi process không sống thay vì chỉ chưa sẵn sàng; (3) nó restart lần lượt/cùng lúc ba container; (4) request đang xử lý bị cắt, container khởi động lại tiếp tục probe Redis vẫn lỗi; (5) đến khi Redis trở lại, cụm còn phải chờ các process mới khởi động và có thể tạo surge kết nối. Vấn đề Redis 30 giây đã bị khuếch đại thành restart storm. Tách `/healthz` nhẹ chỉ trả lời process còn sống; `/readyz` trả 503 để load balancer ngừng gửi traffic nhưng không giết process đang khỏe.

---

### Câu 10 — Deploy thật (CP5)

Lỗi thực tế đầu tiên của em là `/healthz` trả 200 nhưng `/readyz` trả 503 và `POST /chat` trả 500. Log Render ghi `redis.exceptions.ConnectionError: Error -2 connecting to red-d9skmdlbedkc73do2nag:6379. Name or service not known.` em đối chiếu log với biến `REDIS_URL` và xác định private hostname đang trỏ tới Redis cũ, không phân giải được từ service mới.

Em không dùng chung Redis cũ. Sau khi Redis cũ được xoá, em tạo Render Key Value riêng `day12-chat-redis` cùng workspace/region Singapore, cập nhật riêng `REDIS_URL` bằng private connection rồi redeploy. Smoke test sau deploy: `/healthz` 200, `/readyz` 200, chat không token 401 và chat có Bearer token 200. Việc `/readyz` lỗi nhưng `/healthz` vẫn xanh giúp khoanh vùng ngay dependency Redis thay vì nhầm là container chết.
