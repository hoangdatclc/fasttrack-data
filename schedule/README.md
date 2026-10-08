# Prompt của 5 lịch chạy hàng tháng

Năm file `prompt-{site}.md` trong thư mục này là **bản gốc** của prompt gắn vào 5 scheduled
task. Lịch chạy giữ prompt trong dịch vụ, không ở đâu khác — nên khi cần sửa, bản trong
dịch vụ là bản *đang chạy* nhưng **không đọc lại được qua API**. Ngày 07/10/2026 đã dính
đúng chuyện đó: cần sửa 4 prompt mà không lấy lại được nội dung cũ, phải viết lại từ đầu.

Nên từ nay: **sửa file ở đây trước, rồi `update_trigger` lấy nguyên văn file**. File là
nguồn chuẩn, dịch vụ là bản sao.

## Lịch hiện hành — tạo 08/10/2026, cho hệ cập nhật text theo tháng

| Site | trigger id | Cron | Giờ chạy (ICT) | Lần nổ đầu |
|---|---|---|---|---|
| PAF Phú Quốc | `trig_01TjGSBWtdcLVEY2Dc2PULwR` | `CRON_TZ=Asia/Ho_Chi_Minh 0 0 1 * *` | 00:00 ngày 1 | 01/11/2026 00:05 |
| CAF Nha Trang | `trig_01TGuAatEzxdwCYnfME8TyEV` | `CRON_TZ=Asia/Ho_Chi_Minh 0 1 1 * *` | 01:00 ngày 1 | 01/11/2026 01:00 |
| DAF Đà Nẵng | `trig_01DDAAENN2Y7W4J8eg9CvkQu` | `CRON_TZ=Asia/Ho_Chi_Minh 0 2 1 * *` | 02:00 ngày 1 | 01/11/2026 02:02 |
| HAF Hà Nội | `trig_01Njr6CjFYkT5pTTdZGQ9hvm` | `CRON_TZ=Asia/Ho_Chi_Minh 0 3 1 * *` | 03:00 ngày 1 | 01/11/2026 03:05 |
| SAF TP.HCM | `trig_01RUZVkitWNqKby1YSqYMNJV` | `CRON_TZ=Asia/Ho_Chi_Minh 0 4 1 * *` | 04:00 ngày 1 | 01/11/2026 04:02 |

Chạy **lệch 1 tiếng mỗi site**, tuần tự, không song song — mỗi phiên là một ngữ cảnh
riêng, chạy chồng nhau là nhầm site. Dịch vụ tự lệch vài phút quanh mốc giờ (chống dồn
tải), nên khoảng cách thực tế vẫn ~1 tiếng chứ không đúng phút 00.

Năm lịch cũ (hệ mô phỏng thời gian chờ) đã xoá ngày 08/10/2026 theo yêu cầu chủ site.

## Hai cái bẫy đã chốt vào prompt

**1. Tháng bị lệch một tháng.** Cron nổ 00:00–04:00 ICT ngày 1, tức **17:00–21:00 UTC
ngày cuối tháng TRƯỚC**. Container chạy UTC, nên `date +%Y-%m` và cả dòng "Today's date"
trong prompt hệ thống đều ra sai một tháng. Prompt bắt buộc dùng:

```bash
TZ=Asia/Ho_Chi_Minh date +%Y-%m
```

**2. Push chồng nhau.** 1 tiếng có thể không đủ nếu một phiên chạy dài. Prompt yêu cầu
`git pull --rebase origin HEAD` trước khi push, retry tối đa 5 lần, và **chỉ `git add` file
của site mình** — không `git add -A`.

## Dạng giao hàng

Thứ tự do chủ site chốt 08/10/2026, **ghi đè §9 của skill** (skill để link lên đầu):

1. Nói rõ đã thay đổi những gì — bảng text cũ cạnh text mới, từng vùng
2. Vùng đã khoanh nhưng không đổi, kèm lý do
3. Dữ kiện đã loại và vì sao
4. Kết quả nghiệm thu
5. **Cuối cùng**: link sửa trang, click được
6. **Ngay dưới link**: file HTML đã cập nhật (`SendUserFile`)

**Đừng ghi bảng số cứng vào các prompt này.** Dữ kiện riêng site nằm ở
`sites/{mã}.md` của skill `update-fast-track-monthly`; mốc đối chiếu ở
`{site}/home/latest.json`.
