# CHANGELOG

| Lỗi / Thay đổi | Nguyên nhân | Giải pháp |
|---|---|---|
| Tạo kịch bản thuyết trình `docs/PRESENTATION_SCRIPT.md` | Yêu cầu viết script thuyết trình theo từng slide kèm bộ câu hỏi Q&A phản biện | Viết kịch bản lời nói chi tiết theo 14 slide, thời lượng 5-7 phút, kèm 4 câu hỏi Q&A chuẩn bị cho Lab Coach |
| Tạo slide thuyết trình HTML `presentation.html` | Yêu cầu phân tích repo và tạo slide thuyết trình nền trắng, rõ ràng, đơn giản | Xây dựng slide HTML 14 trang với thiết kế hiện đại, màu nền trắng, giao diện responsive, điều hướng phím mũi tên/nút bấm |
| Khôi phục kết nối Redis trên Render (CP5) | Redis hostname trỏ tới instance cũ `red-d9skmdlbedkc73do2nag:6379` không phân giải được | Tạo Render Key Value mới `day12-chat-redis` cùng region Singapore, cập nhật biến `REDIS_URL` bằng private connection |
