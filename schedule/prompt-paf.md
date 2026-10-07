Chạy cập nhật trang chủ **PAF — Phú Quốc (PQC)** cho tháng mới.

Trang hiện tại: Project doc `claude/paf-homepage-source.txt`, hoặc bản chủ site vừa dán nếu mới hơn.

## 0. LUẬT CỨNG — PHIÊN NÀY PHẢI RA ĐƯỢC SỐ

Kết thúc mà không có trang để giao là phiên **HỎNG**. Cổng nổ **KHÔNG phải điểm dừng** — nó
báo **MỘT GIẢ ĐỊNH ĐANG SAI**. Tìm ra giả định đó, sửa kèm lý do viết ra, chạy lại tới khi
cổng qua **một cách trung thực**.

- **ĐƯỢC PHÉP:** đổi giả định mô hình — dựng lại lịch bay, chỉnh số quầy (`surge`), chỉnh hệ
  số mùa (`month_uplift`), chỉnh mốc hiệu chuẩn — **có ghi lý do**, rồi chạy lại.
- **CẤM:** nới / tắt / đi vòng một cổng, hay chọn con số sao cho lọt cổng. Cả hệ cổng sinh
  ra để chặn đúng cái đó.

Phân loại cổng trước khi sửa:

| Loại | Ví dụ | Cách xử |
|---|---|---|
| **CƠ HỌC** | hợp đồng vùng `dat:zone`, mùa lịch bay, nhãn tháng, vân tay cấu trúc | **Không bao giờ đi vòng.** Cách sửa luôn là *làm nốt việc còn thiếu*. |
| **PHÁN ĐOÁN** | hiệu chuẩn `OBSERVED_PEAK`, trần phòng chờ, số học hàng `SAVE` | Hỏi: **trong các đầu vào, cái nào ít căn cứ nhất?** Sửa đúng cái đó, ghi lý do. |

**Thử hết cách vẫn chưa chắc: VẪN GIAO**, kèm cảnh báo nói thẳng **NGAY TRONG** phần bàn
giao (không chôn ở cuối). Giữ lại không giao gì mới là tệ nhất — chủ site mất trang, và mất
luôn thông tin rằng có vấn đề.

## 1. Gọi skill

Gọi skill **`update-fast-track-vietnam`** và làm theo nó. Skill là nguồn chuẩn; prompt này chỉ nhắc những chỗ
đã từng nhầm. Luật nhà đầy đủ ở skill mẹ `update-fast-track-vietnam` →
`reference/house-rules.md`, **luật 11–16** là phần mới nhất.

Lấy mã nguồn từ repo `hoangdatclc/fasttrack-data` theo đúng khối `curl` trong skill —
**đừng dán lại code từ trí nhớ**. Nhớ lấy cả `tools/prev_bands.py` và
`paf/home/latest.json`.

## 2. Tháng cần tính

Phiên này nổ vào **ngày 1**, nên tháng cần tính là **chính tháng vừa bắt đầu** — không phải
tháng vừa kết thúc. Chạy 01/11 → tính `2026-11`.

Dạng `YYYY-MM`, **không kèm ngày**: cổng mùa chỉ nhận đúng dạng đó. Trước đây nó cứ cắt bớt
phần thừa rồi chạy tiếp, nên `2026-10-25` — đúng ngày đổi mùa — bị coi là tháng 10 mà không
báo gì. Nay nó dừng, nhưng vẫn đừng truyền kèm ngày.

## 3. Lịch bay và cổng mùa

Lịch IATA đổi **Chủ nhật cuối tháng 3** (sang S) và **Chủ nhật cuối tháng 10** (sang W).
`run_month.py` có cổng tự kiểm: danh sách chuyến khai `SCHEDULE_SEASON`, lệch với mùa của
tháng là **dừng ngay**, kèm hướng dẫn trong chính câu lỗi. Đây là **việc dự kiến**, không
phải hỏng — phải dựng lại danh sách chuyến quốc tế đến cho mùa mới, ghi đè, rồi mới sửa
`SCHEDULE_SEASON`. **Sửa `SCHEDULE_SEASON` mà không dựng lại lịch là nói dối với cổng này.**

Bản nghiên cứu lịch **W2026** đã có sẵn ở `reference/flights-W2026/` trong repo —
`paf-W2026-draft.py` và `paf-inputs-2026-11-draft.json`. **Đó là điểm BẮT ĐẦU, không
phải bản chốt**: nó dựng ngày 06–07/10/2026, trước mốc đổi lịch 25/10, và tự xếp mình
MEDIUM confidence. Đối chiếu lại với bảng chuyến thật rồi mới dùng. Hai đính chính đã biết:
`WE` là **Parata Air** (Hàn Quốc), không phải Thai Smile; **CEB bắt đầu 10/11/2026**, không
phải 25–26/10.

## 4. Đòn bẩy theo tháng nằm trong `inputs-YYYY-MM.json`

Hai khoá **`month_uplift`** và **`surge`**. **KHÔNG sửa hằng số module** —
sửa hằng số là tháng cũ không dựng lại được nữa. Đã dính thật 07/10/2026: đổi `SURGE` cho
tháng 11 làm trang tháng 10 của HAF (đã phát hành) vỡ cổng khi dựng lại.

Hằng số module giờ chỉ còn là **mặc định cho bản chạy tay**. Mỗi tháng mang đòn bẩy của
chính nó.

**`surge` hay `BASE_DAY`?** Tháng đông hơn thì nâng **`surge`**, không nâng `BASE_DAY`:

| | `BASE_DAY` | `surge` |
|---|---|---|
| là gì | **biên chế nền** theo kế hoạch nhân sự | **phần phản ứng theo nhu cầu** |
| chạy khi nào | **suốt cả ngày**, mọi khung | chỉ khi hàng đã dài |
| đổi theo | quý / năm | **tháng**, theo lưu lượng |
| đụng giờ vắng | **CÓ** — và đó là chỗ lộ ra khi dùng sai | không |

"Sân bay mở thêm quầy để chứa đủ khách" chính là `surge`. Lấy **số nhỏ nhất** đạt ràng buộc
vật lý; tăng 1 rồi chạy lại, đừng nhảy. Mỗi quầy thêm là một phút bớt đi trên con số công
bố, và làm tròn về phía bán được nhiều Fast Track hơn là điều **đã bị cấm**.

## 5. PHÉP THỬ ĐƠN ĐIỆU — cổng bắt buộc trước khi giao

```bash
python3 tools/prev_bands.py --prev paf/home/latest.json --new paf-wait-YYYY-MM.json
```

> **Tháng đông khách hơn KHÔNG THỂ cho thời gian chờ thấp hơn.**

Xét **ba đầu mốc riêng** (dải là khoảng tin cậy, không phải min/max trải nghiệm):

- **cận dưới tụt** khi đông hơn → **VI PHẠM**
- **trung điểm tụt** khi đông hơn → **VI PHẠM**
- **trần tụt** → **hợp lệ NẾU đã thêm quầy** (thêm quầy cắt đuôi xấu của lưới, dải hẹp lại
  quanh một tâm cao hơn) — nhưng **phải nói rõ trong bàn giao**. Trần tụt mà không thêm quầy
  thì là vi phạm.

Đo lưu lượng bằng **`pax`**, không bằng số chuyến: cùng 13 chuyến mà đổi đời tàu bay là lệch
cả trăm khách.

Mã thoát **0** qua · **1** vi phạm · **2** chưa kết luận được. **Mã 1 hay 2 đều không phải
giấy phép để dừng** (mục 0) — mã 1 nói rằng *đã vặn nhầm cần*. Sửa cần rồi chạy lại.

Ca thật đã bắt được: HAF tháng 11/2026, nâng `BASE_DAY` 28 → 33 cho ra `95–105`, **thấp hơn**
tháng 10 (`97–110`) dù hàng dài hơn hẳn. Dấu hiệu lộ rõ nhất không ở hero mà ở **khung vắng
06:00–10:00 nhanh lên 51–53 → 49–52**. Chủ site bắt được ngay.

## 6. Lưu ý riêng của PAF (Phú Quốc · PQC)

- Skill của PAF là **skill mẹ** `update-fast-track-vietnam`, mục §SITE: PAF.
- Model: `paf/src/paf_queue_model.py` — **lịch bay nằm trong chính file model**, không có
  `paf_flights.py` riêng. `SCHEDULE_SEASON` cũng ở đó.
- Có **hàng SAVE**, nên `headline_range()` giữ `min_gap=10`. **Đừng** bê `min_gap=30` của
  SAF sang: ở PAF nó cho ra dải vỡ cổng số học hàng SAVE.
- Hàng SAVE luôn là **một khoảng**, bước nửa giờ, tối thiểu 1 giờ, lấy theo **dải thô đã
  công bố** (không trừ Fast Track). Cổng 2 của `saved()` kiểm cận dưới **sau** bước nới
  rộng khoảng — thứ tự đó đã sửa 07/10/2026, đừng đảo lại.
- Miễn thị thực 30 ngày cho **mọi quốc tịch** khi bay thẳng tới Phú Quốc. Miễn thị thực
  **không phải** miễn xếp hàng — đừng viết lẫn.
- Giá luôn dùng shortcode `[paf_price service="..."]`, **không bao giờ gõ số tiền cứng**.
- `OBSERVED_PEAK = (45, 60)`: comment trong code nói "báo cáo thực địa" — **nói quá**. Căn
  cứ thật là trang của đối thủ. Đừng dựa vào nó như số đo chính thức.
- Lịch bay PQC mỏng, có khung **không có chuyến nào** (ô trống trên bảng). `prev_bands.py`
  sẽ báo *ô trống — đối chiếu tay* cho những khung đó; đối chiếu thật, đừng bỏ qua.

## 7. Giao hàng

Theo đúng §Giao cho chủ site của skill:

1. **`SendUserFile`** file HTML hoàn chỉnh `paf-home-YYYY-MM.txt`.
2. **Ngay sát thẻ file** — dòng liền trước hoặc liền sau, KHÔNG có đoạn văn chen giữa — in
   link sửa trang thành **link bấm được**, trên một dòng riêng:

   **[Mở trang sửa Phú Quốc →](https://phuquocairportfasttrack.com/wp-admin/post.php?post=15&action=edit)**

   Đừng bọc URL trong backtick (bấm không được), đừng để link ở cuối câu trả lời.

3. **Rồi mới** viết báo cáo, **bằng tiếng Việt**, gồm đủ:
   - Dải công bố trên hero: **tháng trước → tháng này**.
   - **Bảng cả sáu khung** với dải của tháng trước bên cạnh tháng này.
   - **Kết quả phép thử đơn điệu cả sáu khung** — kể cả khi qua hết. Khung nào trần tụt thì
     nói rõ vì đã thêm quầy.
   - `month_uplift` và `surge` đã dùng, và **vì sao** nếu khác tháng trước.
   - Lịch bay: tổng số chuyến quốc tế đến, mùa (`S`/`W`), nguồn, và **mức tự tin**.
   - Cổng nào đã nổ, sửa giả định nào, **lý do**.
   - Nếu có chỗ nào chưa chắc: **nói thẳng ở đây**, đừng chôn xuống cuối.

Đừng kèm file trung gian, đừng kèm hướng dẫn dài.

## 8. Nếu bế tắc thật

Vẫn giao con số có căn cứ tốt nhất dựng được, kèm cảnh báo nói thẳng. Nói rõ chỗ nào yếu và
vì sao. Cổng tồn tại để chặn trang **sai trong im lặng**; một trang kèm cảnh báo rõ ràng thì
không im lặng.
