# Prompt của 5 lịch chạy hàng tháng

Năm file `prompt-{site}.md` trong thư mục này là **bản gốc** của prompt gắn vào 5 scheduled
task. Lịch chạy giữ prompt trong dịch vụ, không ở đâu khác — nên khi cần sửa, bản trong
dịch vụ là bản *đang chạy* nhưng **không đọc lại được qua API**. Ngày 07/10/2026 đã dính
đúng chuyện đó: cần sửa 4 prompt mà không lấy lại được nội dung cũ, phải viết lại từ đầu.

Nên từ nay: **sửa file ở đây trước, rồi `update_trigger` lấy nguyên văn file**. File là
nguồn chuẩn, dịch vụ là bản sao.

| Site | trigger id | Giờ chạy (Asia/Ho_Chi_Minh) |
|---|---|---|
| PAF Phú Quốc | `trig_01JPhahPfcUm7MHF1Ptv2GDA` | 00:00 ngày 1 |
| CAF Nha Trang | `trig_019Dv7wDQE8YQVM8p6XupLKp` | 02:10 ngày 1 |
| DAF Đà Nẵng | `trig_017SA6m1RgfBpTDaCEJuT5hU` | 04:10 ngày 1 |
| HAF Hà Nội | `trig_019BqnnBm7ALu4Mpc2TeZV27` | 06:10 ngày 1 |
| SAF TP.HCM | `trig_012pEidcfXPGTYMBk7n8U8uw` | 08:10 ngày 1 |

Chạy **lệch 2 tiếng mỗi site**, tuần tự, không song song — mỗi phiên là một ngữ cảnh
riêng, chạy chồng nhau là nhầm site.

**Đừng ghi bảng số cứng vào các prompt này** (luật nhà 16). Mốc đối chiếu lấy từ
`{site}/home/latest.json`, khoá `baseline`.
