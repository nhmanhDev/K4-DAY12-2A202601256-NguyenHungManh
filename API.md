# API production — Day 12 Chat Service

Tài liệu tương tác đã bật sẵn trên service:

- Swagger UI: `https://day12.ai42e.com/docs`
- ReDoc: `https://day12.ai42e.com/redoc`
- OpenAPI JSON: `https://day12.ai42e.com/openapi.json`

Nếu custom domain đang chờ DNS/TLS, dùng URL Render thay thế: `https://day12-chat-cjnn.onrender.com`.

## Quy ước chung

| Mục | Giá trị |
|---|---|
| Content type cho body | `application/json` |
| Xác thực `/chat` | `Authorization: Bearer <API_TOKEN>` |
| Định danh client | Header tùy chọn `X-Client-Id`; thiếu thì dùng `anonymous` |
| Lưu state | Redis — lịch sử, rate limit và chi phí được tách theo `client_id` |
| LLM | Mock LLM chạy offline; không cần API key OpenAI |

`API_TOKEN` là secret. Chỉ điền vào Postman Environment/Vault hoặc biến môi trường ở máy; không đưa token vào collection, README, screenshot công khai hay Git.

## Endpoint reference

### `GET /healthz` — liveness

Không cần header xác thực. Dùng để biết process còn sống, nên không gọi Redis.

| Kết quả | Khi nào | Ví dụ body |
|---|---|---|
| `200 OK` | Process đang chạy | `{"status":"ok","service":"day12-chat-service","version":"1.0.0"}` |
| `503 Service Unavailable` | Process nhận tín hiệu shutdown và đang draining | `{"status":"draining"}` |

### `GET /readyz` — readiness

Không cần header xác thực. Dùng để quyết định có nên gửi traffic mới vào service; endpoint ping Redis.

| Kết quả | Khi nào | Ví dụ body |
|---|---|---|
| `200 OK` | Redis sẵn sàng, service không draining | `{"status":"ready","redis":true}` |
| `503 Service Unavailable` | Redis lỗi/mất kết nối | `{"status":"not ready","redis":false}` |
| `503 Service Unavailable` | Service đang draining | `{"status":"draining"}` |

### `POST /chat` — chat chính

#### Headers

| Header | Bắt buộc | Giá trị | Ý nghĩa |
|---|---:|---|---|
| `Authorization` | Có | `Bearer <API_TOKEN>` | Xác thực request theo RFC 6750 |
| `Content-Type` | Có | `application/json` | Khai báo JSON body |
| `X-Client-Id` | Không | Ví dụ `postman-demo` | Tách lịch sử, token bucket và ngân sách theo client |

#### Request body

```json
{
  "message": "Docker và Render giúp gì cho deployment?"
}
```

`message` là chuỗi bắt buộc, từ 1 đến 2.000 ký tự.

#### Response `200 OK`

```json
{
  "reply": "...",
  "client_id": "postman-demo",
  "turns_before": 0,
  "usd_cost": 0.00001,
  "usage": {
    "prompt": 7,
    "completion": 32
  }
}
```

| Trường | Ý nghĩa |
|---|---|
| `reply` | Phản hồi từ mock LLM |
| `client_id` | Client được lấy từ `X-Client-Id`, hoặc `anonymous` nếu không gửi header |
| `turns_before` | Số message lịch sử Redis trước request hiện tại |
| `usd_cost` | Chi phí mô phỏng của request hiện tại, USD |
| `usage.prompt` / `usage.completion` | Số token mô phỏng đầu vào / đầu ra |

#### Lỗi có thể gặp

| HTTP | `detail` / dấu hiệu | Cách kiểm tra hoặc xử lý |
|---:|---|---|
| `401` | `invalid or missing bearer token` và `WWW-Authenticate: Bearer` | Chọn đúng Environment và kiểm tra `Authorization` dùng `Bearer {{api_token}}` |
| `402` | `daily budget exceeded` | Đổi `X-Client-Id` cho demo mới hoặc đợi ngày UTC mới; đây là cost guard theo ngày |
| `422` | FastAPI validation error | Body phải là JSON có `message` không rỗng, tối đa 2.000 ký tự |
| `429` | `rate limit exceeded`, header `Retry-After` | Chờ số giây trong header, hoặc dùng `X-Client-Id` khác cho demo |
| `503` | Thường ở `/readyz` khi Redis không sẵn sàng/draining | Kiểm tra trạng thái Render và Redis Key Value |

## Test production bằng Postman

### Cách nhanh nhất: import sẵn collection

1. Trong Postman, bấm **Import**.
2. Chọn hai file trong repo:

   - `postman/Day12-Production.postman_collection.json`
   - `postman/Day12-Production.postman_environment.json`

3. Góc trên phải, chọn environment **Day12 Production**.
4. Mở environment, điền `api_token` bằng giá trị `API_TOKEN` đang set trong Render. Giữ token ở **Current value** hoặc Postman Vault; không commit/export token.
5. Giữ `base_url` là `https://day12.ai42e.com`. Nếu domain chứng chỉ chưa xong, thay bằng `https://day12-chat-cjnn.onrender.com`.

### Thứ tự demo đề xuất

1. Chạy **01 - Healthz** → mong đợi `200`.
2. Chạy **02 - Readyz** → mong đợi `200` và `redis: true`.
3. Chạy **03 - Chat without token** → mong đợi `401`; request này cố ý không có Authorization.
4. Chạy **04 - Chat authenticated** → mong đợi `200`; response có `reply`, `usage`, `usd_cost`.
5. Chạy lại **04 - Chat authenticated** với cùng `X-Client-Id` → `turns_before` tăng, chứng minh history nằm trong Redis.

Collection đã có test assertion cho các status nêu trên. Trong Collection Runner, chọn bốn request theo thứ tự này và bấm **Run DAY12 Production** để chạy một lượt.

### Tự tạo request nếu không import collection

Tạo Environment:

| Variable | Initial value | Current value |
|---|---|---|
| `base_url` | `https://day12.ai42e.com` | cùng giá trị hoặc URL Render fallback |
| `api_token` | để trống | API token production — đánh dấu secret nếu Postman hỗ trợ |

Tạo request `POST {{base_url}}/chat`:

- Tab **Authorization**: Type `Bearer Token`, Token `{{api_token}}`.
- Tab **Headers**: `Content-Type: application/json`, `X-Client-Id: postman-demo`.
- Tab **Body** → raw → JSON:

```json
{
  "message": "Xin chào từ Postman"
}
```

## Bằng chứng nộp bài CP5

Chụp ảnh Postman thể hiện lần lượt `/healthz` 200, `/readyz` 200, `/chat` không token 401, và `/chat` có Bearer token 200. Che `api_token` trước khi đưa ảnh vào `screenshots/`; không cần (và không nên) chụp token.

Thông tin nền tảng, URL Render và lệnh curl đối chiếu được duy trì trong [DEPLOYMENT.md](DEPLOYMENT.md).
