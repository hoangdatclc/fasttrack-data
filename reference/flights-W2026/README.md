# Lich bay W2026 — BAN NGHIEN CUU, CHUA KICH HOAT

Dung ngay 07/10/2026, **truoc** moc doi lich 25/10. Day la ket qua chay thu thang
11/2026 ma chu site da duyet con so, KHONG phai danh sach dang chay.

## Vi sao de o day chu khong dat thang vao {site}/src/

Neu dat vao src va khai SCHEDULE_SEASON = "W2026" thi cong mua lich bay se KHONG no
vao 01/11, va run thang 11 se chay thang tren danh sach nay ma khong kiem lai. Trong
khi:
  · ca 5 danh sach deu duoc chinh agent dung no cham **MEDIUM** -- phan lon dong la
    bang gio mua HE be sang, chua co xac nhan rieng cho mua dong;
  · hai nguon tot nhat (flight.info co cua so hieu luc theo mua, airportia) bi chan
    quyen truy cap trong phien do;
  · **sau 25/10 bang gio truc tiep CHINH LA lich dong** -- mot luot fetch bien phan
    lon dong "be sang" thanh dong xac nhan. Re va tot hon han.

## Cach dung dung, cho run ngay 01/11

Cong mua van no nhu thiet ke. Khi dung lai danh sach W2026, LAY FILE O DAY LAM DIEM
XUAT PHAT roi **doi chieu lai voi bang gio that**, dung chep nguyen. Moi dong trong
cac file nay deu co nhan [W-OK] / [W-RT] / [CARRY]:
  [W-OK]  da co filing NW26 ghi ngay hieu luc -> gan nhu chac, van nen liec lai
  [W-RT]  tuyen chac co trong mua dong, nhung gio/so hieu lay tu mua he -> KIEM
  [CARRY] khong co xac nhan mua dong nao -> KIEM TRUOC TIEN

## Vai dinh chinh da tim ra, dung de mat

  · `WE` la **Parata Air** (Han Quoc), KHONG phai Thai Smile. Ca DAD lan CXR deu
    dang bo sot mot chuyen that vi nham nay -- rieng DAD la 294 ghe/ngay.
  · Skill ghi "CNX va CEB bat dau 25-26/10" -- **SAI voi Cebu**: CNX noi lai 25/10,
    con CEB tan **10/11/2026** (3 chuyen/tuan, duoi nguong >=4 ngay/tuan nen khong
    vao danh sach ngay dai dien).
  · aeroroutes.com chan toc do: ~6 lan fetch lien tiep la HTTP 429, cho 75 giay van
    chua het. Gian ra.
