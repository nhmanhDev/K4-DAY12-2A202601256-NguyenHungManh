# Thông tin deploy — Checkpoint 5

> Repository công khai. Tài liệu này chỉ ghi **tên** biến môi trường, không ghi token hoặc chuỗi kết nối.

## Thông tin học viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Nguyễn Hùng Mạnh |
| Mã học viên | 2A202601256 |
| Repo | https://github.com/nhmanhDev/K4-DAY12-2A202601256-NguyenHungManh |

## Service production

| Mục | Nội dung |
|---|---|
| Public URL | https://day12-chat-cjnn.onrender.com |
| Platform | Render — Web Service (Docker, Singapore) |
| Ngày deploy | 2026-08-10 |
| Health check | `/healthz` |

## Hạ tầng và biến môi trường

Redis được tạo riêng cho service: Render Key Value `day12-chat-redis`, cùng region Singapore. Service kết nối bằng private connection; không chia sẻ keyspace với ứng dụng khác.

| Biến | Đã set | Nguồn/ghi chú |
|---|---|---|
| `PORT` | ✅ | Render tự gán |
| `API_TOKEN` | ✅ | Render Environment, giá trị không nằm trong repo |
| `REDIS_URL` | ✅ | Private connection tới `day12-chat-redis` |
| `BUCKET_CAPACITY` | ✅ | 10 |
| `REFILL_PER_MINUTE` | ✅ | 10 |
| `DAILY_BUDGET_USD` | ✅ | 1.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Kết quả kiểm tra production

Kiểm tra trực tiếp sau redeploy ngày 2026-08-10:

```text
GET  /healthz                 -> 200
GET  /readyz                  -> 200
POST /chat (không token)      -> 401
POST /chat (Bearer API_TOKEN) -> 200, có trường reply
```

## Lệnh kiểm tra lại

```bash
BASE_URL=https://day12-chat-cjnn.onrender.com

curl -i "$BASE_URL/healthz"
curl -i "$BASE_URL/readyz"

# Kỳ vọng 401 cùng header WWW-Authenticate
curl -i -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'

# Đặt API_TOKEN trong shell, không ghi token vào repository
curl -i -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "X-Client-Id: sv-test" \
  -d '{"message":"Deploy là gì?"}'
```
