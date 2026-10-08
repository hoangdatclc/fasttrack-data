Chạy quy trình **cập nhật trang chủ hàng tháng** cho site **HAF — Hà Nội (Nội Bài) (HAN)**.

Phiên này **chạy không người trông**. Tự quyết mọi thứ, **không hỏi người, không dừng chờ xác nhận** ở bất kỳ mốc nào. Báo cáo bằng tiếng Việt.

---

## 0. 🔴 THÁNG CẦN TÍNH — SAI CHỖ NÀY LÀ SAI CẢ RUN

Lịch nổ **03:00 ngày 1 giờ Việt Nam**. Container chạy **UTC**, nên lúc nổ thì UTC vẫn đang ở **ngày cuối tháng TRƯỚC**. `date` trần và cả dòng "Today's date" trong prompt hệ thống đều sẽ ra **sai một tháng**.

Lấy tháng **đúng một cách duy nhất**:

```bash
TZ=Asia/Ho_Chi_Minh date +%Y-%m      # -> ví dụ 2026-11
```

Ví dụ cụ thể: nổ 00:00 ICT 01/11/2026 thì UTC là 17:00 ngày 31/10/2026 — `date +%Y-%m` ra `2026-10`, **sai**; `TZ=Asia/Ho_Chi_Minh date +%Y-%m` ra `2026-11`, **đúng**.

Tháng cần tính là **chính tháng vừa bắt đầu**, không phải tháng vừa kết thúc. Dạng `YYYY-MM`, **không kèm ngày**.

Trước khi viết một chữ nào: in ra tháng vừa tính và đối chiếu với tên file `haf/zones/zones-*.json` đã có trong repo. Nếu tháng đó **đã có file** thì nghĩa là đã chạy rồi — dừng, báo, đừng ghi đè.

---

## 1. Dựng workspace — container này là container TRẮNG

```bash
cd /home/claude && git clone https://github.com/hoangdatclc/fasttrack-data
cd fasttrack-data
```

Nếu clone lỗi vì quyền: gọi tool `add_repo` với `owner=hoangdatclc`, `repo=fasttrack-data`, `access=push` rồi clone theo đúng lệnh nó trả về. **Cần `access=push`** vì bước 5 phải đẩy ngược lên.

Kiểm đủ 4 thứ, thiếu một là dừng:

```bash
ls tools/text_zones.py tools/monthly_publish.py haf/home/base.txt haf/zones/
```

**`haf/home/base.txt` là nguồn chuẩn duy nhất.** Không dựng lại trang từ trí nhớ, không dùng bản HTML cũ đã giao, không lấy từ project doc trừ khi base.txt mất.

---

## 2. Gọi skill — đúng thứ tự, đúng một file site

Gọi skill **`update-fast-track-monthly`**.

1. Đọc **hết** `SKILL.md` trước.
2. Rồi `Read` **đúng một** file: `sites/haf.md`.
3. **Không đọc file site khác.** Mỗi sân bay có bộ số riêng — số element, số ảnh, số FAQ, vùng đóng băng, mức thời gian chờ. Lẫn sang nhau là ra trang sai, đã dính thật một lần.

Skill là nguồn chuẩn. Prompt này chỉ chốt tháng, chốt cách đẩy repo, và chốt dạng giao hàng.

---

## 3. Dữ kiện riêng của HAF

- Site duy nhất đóng khung con số là **"Save | 1 - 3 hours"**, không phải "Queue". Đừng viết "queue time" vào thẻ số.
- **12 vùng**, không phải 10 — có **3 vùng FAQ** (`faq-night`, `faq-delay`, `faq-connection`). Đó là chỗ để viết dài, dùng nó.
- **Ba** shortcode giá trên trang, không phải hai. Đếm đủ.
- 🔴 **BẪY 6 — thẻ FAQ bị cắt âm thầm.** Thẻ FAQ có `max-height: 500px` + `overflow:hidden`. Viết dài quá là **cắt mất chữ mà không ai báo**, và desktop xếp 2 cột nên không lộ. Bắt buộc: mở hết thẻ bằng JS rồi **đo `scrollHeight` so với chiều cao hiện** của từng thẻ, ở **cả 390px và 1440px**. Đã dính thật 08/10/2026.
- Hai mức thời gian cùng tồn tại có chủ ý: "khoảng 15 phút" (Fast Track) và "15–20 phút" (khối Connection). Cả hai đã chốt, **không đụng**.

**Vùng:** 12 vùng trên trang, **5 vùng đổi được hàng tháng**.
**Đóng băng:** `save-figure`, `compare-row1`, `hero-bullet` — `--apply` tự chặn. **Không gõ `--allow-frozen`** để đi vòng.
**Ngân sách độ dài:** `peak-body` 145 ký tự. `save-note` tháng 10 không đổi; `peak-body` chỉ **145 ký tự** — ngân sách ngoài FAQ ngắn nhất trong 5 site.

---

## 4. Làm theo 8 bước của skill §6

Không bỏ bước nào. Ba chỗ hay bị bỏ:

- **Bước 4 — bắt buộc web search.** Lịch bay và lịch nghỉ lễ đổi từng năm. Viết theo trí nhớ là viết sai. Checklist dữ kiện ở skill §8.
- **Bước 6 — cổng.** `--check --freeze ...` phải PASS, rồi `monthly_publish.py` phải PASS. ⚠️ **Nếu cổng in "tổng số từ" dưới 500 thì đừng tin chữ PASS** — đó là dấu hiệu cổng từ khoá đang chạy rỗng. Trang thật dày 190–200 KB, phải ra hàng nghìn từ. Lỗi âm này đã dính thật 08/10/2026 ở CAF.
- **Bước 7 — render.** Playwright 1440px **và** 390px. Font DM Sans + Cormorant Garamond cài từ mirror GitHub của Google Fonts (`fonts.googleapis.com` bị chặn ở shell). Vùng trong thẻ gập phải **đo `scrollHeight`**, không kiểm bằng mắt.

**Không nới cổng, không tắt cổng, không chọn chữ sao cho lọt cổng.** Cổng nổ nghĩa là một giả định đang sai — tìm ra giả định đó, sửa, chạy lại.

---

## 5. Đẩy repo — 5 phiên cách nhau 1 tiếng, có thể chồng nhau

5 site chạy tuần tự cách nhau **1 tiếng**. Nếu một phiên chạy quá giờ thì hai phiên sẽ push gần nhau, và push thứ hai sẽ bị `non-fast-forward`. **Đây là việc dự kiến, không phải hỏng.**

```bash
git add haf/home/base.txt haf/zones/ haf/home/latest.xml haf/home/latest.json
git commit -m "HAF tháng <YYYY-MM>: <đổi vùng nào>"
git pull --rebase origin HEAD && git push
```

Push lỗi → `git pull --rebase` rồi push lại, **tối đa 5 lần**. Vẫn lỗi → vẫn **giao trang** (bước 6), và nói rõ trong báo cáo là chưa đẩy được repo kèm nguyên văn câu lỗi.

**Chỉ `git add` file của site này.** Đừng `git add -A` — sẽ cuốn theo file của phiên khác.

Commit message kết thúc bằng:

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

---

## 6. 🔴 GIAO HÀNG — ĐÚNG THỨ TỰ NÀY

Thứ tự này do chủ site chốt và **ghi đè thứ tự ở skill §9** (skill để link lên đầu; ở đây link xuống cuối).

**(1) Nói rõ đã thay đổi những gì.** Bảng từng vùng đã đổi:

| Vùng | Bậc | Text cũ | Text mới | Dữ kiện dùng | Nguồn |
|---|---|---|---|---|---|

Text cũ và text mới **viết nguyên văn**, không tóm tắt.

**(2) Vùng đã khoanh nhưng không đổi** — liệt kê, kèm lý do từng vùng.

**(3) Dữ kiện đã loại và vì sao.** Thứ tra được nhưng chưa chắc thì nói rõ là để dành, đừng đưa lên trang.

**(4) Kết quả nghiệm thu.** `--check` (kèm **tổng số từ** mà cổng từ khoá in ra), `monthly_publish.py`, render 390px và 1440px, **kết quả đo `scrollHeight` của 11 thẻ FAQ**, sha256 của trang. Chỗ nào chưa chắc thì nói thẳng **ngay tại đây**, đừng chôn ở cuối.

**(5) CUỐI CÙNG — link sửa trang, click được:**

> **[Mở trang sửa HAF →](https://hanoiairportfasttrack.com/wp-admin/post.php?post=15&action=edit)**

**(6) NGAY DƯỚI LINK — file HTML đã cập nhật.** Gửi bằng `SendUserFile`, tên `haf-homepage-YYYY-MM.html`, `status: "proactive"`. Việc của chủ site chỉ còn: mở link, dán đè, bấm Update.

Đừng dán toàn văn HTML vào thân tin nhắn — gửi file.

---

## 7. Changelog

`project_write` vào project doc `claude/haf-monthly-changelog.md` của project **Vietnam Airport Fast Track**. Đọc trước (`project_read`), thêm mục cho tháng mới, ghi lại **nguyên bản đầy đủ** — không có patch tại chỗ.

Ghi: đổi vùng nào, bằng dữ kiện gì, nguồn ở đâu, dữ kiện nào để dành và vì sao. **Đọc file này trước khi viết** để không lặp lại dữ kiện của tháng trước.

---

## 8. Luật giao — chỉ hai lý do được phép không giao trang

| | Trường hợp | Phải làm gì |
|---|---|---|
| **A** | Trang thật **lệch vân tay** (đã bị sửa tay ngoài quy trình) | Dừng, báo lệch chỗ nào, xin bản export mới. **Không ghi đè.** |
| **B** | Cả tháng **không tìm được một dữ kiện kiểm chứng được nào** | Không đổi vùng nào, nói thẳng tháng này không có gì đáng cập nhật. Giữ nguyên còn hơn sửa suông. |

Mọi thứ khác — cổng nổ, render vỡ, thiếu nguồn, câu chưa ưng — **không phải lý do dừng**. Sửa rồi chạy lại cho tới khi cổng qua một cách trung thực.

Run kết thúc mà không có trang để giao, ngoài hai trường hợp trên, là **run hỏng**.
