"""Mo phong hang cho nhap canh HAN (Noi Bai) theo tung phut. Uoc tinh, khong phai do dac.

Dung chung khung voi SGN/DAD/CXR. SAU cho khac SGN, deu suy tu chinh du lieu cua HAN:

  1. HAN LA SAN BAY DUY NHAT TRONG MANG LUOI CO LAN RIENG CHO KHACH NUOC NGOAI.
     Tu 03/08/2026, khu nhap canh T2 chia theo nhom: VIP / NGUOI NUOC NGOAI / to bay /
     cong dan Viet Nam / khach noi chuyen (Tuoi Tre, VnExpress, Tien Phong 02-04/08/2026).
     => Mo hinh nay mo phong RIENG LAN KHACH NUOC NGOAI voi RIENG so quay cua lan do.
     O SGN khach ngoai va khach Viet dung chung 44 quay nen phai quet GRID_FOREIGN;
     o HAN hai lan tach han, cung khong dich qua lai duoc -> quet GRID_FOREIGN ba chieu.

  2. FOREIGN = 0,70 -- suy tu con so cong bo, khong uoc chung.
     Bao Chinh phu (19/08/2026) dan Cong an cua khau Noi Bai: toan cang
     "khoang 44.000-45.000 luot hanh khach xuat canh, nhap canh" moi ngay, trong do
     cong dan Viet Nam "khoang 12.000-13.000 luot". 12.500/44.500 = 28% khach Viet
     -> 72% khach ngoai. Ha xuong 0,70 vi chinh bai do ghi mua he ty le khach Viet
     len 35-40% va dip Tet len ~50%; 0,70 la muc an toan cho thang 10.

  3. PROC_SEC = 125 -- phep DO truc tiep cua quay Noi Bai, khong phai suy nguoc. Muc (A).

  4. OBSERVED_PEAK = (30, 60) -- xem muc (C). KHAC voi cau "1-3 hour" dang in tren
     chinh trang haf: cau do khong co nguon va choi voi so cua don vi van hanh.

  5. KHONG CO DINH. SGN don ve chieu-toi; CXR don ve dem; HAN PHANG.
     06:00-24:00 moi khung deu 3.400-5.300 ghe. Hau qua: dung di tim "gio vang" --
     o HAN chi co khung 00:00-06:00 la that su nhe, va no van co 12 chuyen.

  6. TRAN VAT LY DEM DUOC: khu cho nhap canh T2 sau thiet ke lai chua "khoang 1.100
     cho" (truoc do 800) -- Bao Chinh phu, cung bai. Day la rang buoc MA BA SITE KIA
     KHONG CO: neu mo hinh cho ra hang dai hon ~1.100 nguoi thi no da sai, vi phong
     cho khong chua noi. Ham `hall_check()` cuoi file kiem dieu nay.

======================================================================
(A) MO HINH CHI CAN MOT CON SO: SUC PHUC VU = QUAY / PROC_SEC
======================================================================
Doc muc nay truoc khi dong vao BASE_DAY hay PROC_SEC. Hai hang so do KHONG doc lap:
hang cho chi phu thuoc TY SO quay/PROC_SEC. 28 quay @125 giay va 31 quay @138 giay
cho ra dung mot ket qua. Nen quy trinh dung la: chot TY SO truoc bang rang buoc co
nguon, roi moi tach ra thanh hai con so.

BUOC 1 -- CHOT TY SO bang HAI rang buoc cong bo cua chinh Noi Bai:
  (i)  dinh xep hang cua lan khach ngoai phai nam trong 30-60 phut -- xem muc (C);
  (ii) hang dai nhat phai <= 1.100 nguoi, la suc chua phong cho sau thiet ke lai
       (Bao Chinh phu 19/08/2026: "khoang 800 cho dung" -> "khoang 1.100 cho").
Rang buoc (ii) la thu MA BA SITE KIA KHONG CO, va no that su cat: trong luoi 27 kich
ban, 5 kich ban cho hang dai hon suc chua phong -- tuc chung bat kha thi ve vat ly,
khong phai "kich ban xau". Ham `hall_overflow()` loai chung khoi luoi truoc khi lay
phan vi. Do nay la LY DO khoang cong bo cua HAF hep hon SAF du hai san bay cung nghet.

BUOC 2 -- TACH TY SO ra quay va giay, bang phep do truc tiep:
Tap chi Hang khong (14/05/2026): quay lam thu cong "2-3 phut/khach" (120-180 giay),
doi lai autogate 25-35 giay. Day la phep DO, khac ba site kia (phai suy nguoc tu san
luong). Chon 125 -- dau NHANH cua dai do, vi con so 2-3 phut duoc dan trong bai co
muc dich quang ba autogate nen lech ve phia cham, va no do ca thoi gian khach loay hoay
chu khong chi thoi gian can bo xu ly.
    => PROC_SEC = 125, va ty so o buoc 1 keo theo BASE_DAY = 28.

VI SAO KHONG DEM BUC: KHONG CO NGUON NAO cong bo so buc nhap canh cua T2 Noi Bai. Da
tim ca tieng Viet lan tieng Anh. Bao chi dem rat ky so quay check-in (96 -> 144), cua
ra (17 -> 30), ong long (14 -> 27), may soi 3D -- khong to nao dem buc nhap canh.
Doi chieu nguoc lai cho hop ly: dinh mo hinh mo toi da 33 quay cho lan khach ngoai.
Khach ngoai chiem ~72% luu luong, nen tong buc nhap canh T2 vao khoang 45. SGN T2
cong bo 44 buc tren 115.834 m2; T2 Noi Bai sau mo rong 19/12/2025 rong 200.164 m2 va
hon SGN o moi hang dem duoc (144 quay check-in so voi 120, 30 cua ra so voi 26).
45 buc la con so hop ly -- neu khong noi la khiem ton.

======================================================================
(E) THANG 11/2026: SURGE 5 -> 8. VAN DONG CAN, KHONG PHAI CAN BASE_DAY
======================================================================
Muc (B) tien lieu dung thang nay nhung chi duong SAI CAN: no bao "nang BASE_DAY".
Lam vay ra mot ket qua VO LY ma chu site bat duoc ngay 07/10/2026:

    T10: 28 quay nen, hang 794 nguoi (72% sanh) -> cong bo  97-110
    T11: 33 quay nen, hang 1.079    (98% sanh) -> cong bo  95-105

Thang 11 dong khach hon, hang dai hon han (1.079 so voi 794 nguoi), ma so cong bo
lai THAP hon thang 10. Khong the dung. Chu site noi thang: "dong khach hon, ke ca
co mo them quay thi thoi gian cho cung khong the thap hon thang 10 duoc".

VI SAO NANG BASE_DAY LAI SAI VE BAN CHAT:
BASE_DAY la BIEN CHE NEN -- so quay mo theo ke hoach nhan su, chay suot ca ngay, doi
theo quy/nam chu khong theo thang. Nang no len 33 tuc gia dinh san bay tang bien che
nen 18% chi cho mot thang, va hieu ung phu la KHUNG VANG CUNG NHANH LEN: khung
06:00-10:00 vot tu 51-53 (T10) xuong con 49-52 du thang 11 dong hon. Mot thang dong
hon khong the lam gio vang chay nhanh hon. Do la dau hieu da van nham can.

SURGE moi la phan PHAN UNG THEO NHU CAU: `simulate()` chi cong no khi hang da dai
(SURGE_PAX / SURGE_AT). Dung no thi:
  - khung vang GIU NGUYEN muc dich vu thang 10 (khong co hang dai -> khong surge)
  - chi gio cao diem duoc tang vien, dung nghia "san bay mo them quay de chua du khach"
  - va so cong bo DI LEN, dung chieu voi luu luong

CHON SURGE = 8 -- so NHO NHAT giu hang trong suc chua sanh cong tran hanh lang:
    SURGE  quay dinh   hang   %sanh    cong bo
      5       33       2.131  194%     CHAN (vo tran)
      7       35       1.579  144%     CHAN (vo tran)
      8       36       1.403  128%     103-113   <= CHON
      9       37       1.297  118%     104-114
     10       38       1.192  108%      99-110
     12       40       1.057   96%      92-102
Khong chon cao hon: moi quay them la mot phut bot di tren so cong bo, va lam tron ve
phia ban duoc nhieu Fast Track hon la dieu muc (B) cam.

NGUONG DUNG LA 1,35x SUC CHUA (1.485), KHONG PHAI 1.100:
Muc (B) ghi nguong 1.100 (vua long sanh). Thang 10 lot thoai mai nen khong ai phai
chon. Thang 11 hai nguong cho hai ket qua nguoc nhau:
    nguong 1.485 (co tran hanh lang) -> SURGE 8  -> 103-113  (CAO hon T10, dung chieu)
    nguong 1.100 (khong tran)        -> SURGE 11 -> 96-106   (THAP hon T10, vo ly)
Chon 1.485. HALL_SPILL = 1,35 ton tai chinh de mo ta viec hang tran ra hanh lang --
dieu co that o Noi Bai thang cao diem. 1.100 la muc THIET KE nham toi, khong phai muc
van hanh. Muc (B) viet khi thang 10 chua cham den cho nay; (E) la ban chot.

KIEM LAI: dinh xep hang thuan 117 phut, nam trong dai chap nhan 42-144 cua cong hieu
chuan (OBSERVED_PEAK 60-90 x 0,7-1,6). Hang 1.403 = 128% sanh, lot tran 1,35x.

GIA DINH CON PHAI XAC MINH: 28 + 8 = 36 quay cho lan khach ngoai luc cao diem, trong
khi muc (A) uoc T2 chi co ~45 buc va suy ra "toi da 33 quay cho lan ngoai". 36 doi hoi
dieu buc tu lan khach Viet sang (khach Viet phan lon di autogate nen khong chiem buc).
Co ly nhung la SUY LUAN.
=> VIEC CAN LAM, re va dut diem: nho nhan vien tai Noi Bai dem SO QUAY NHAP CANH THUC
   MO cho lan khach ngoai luc 13:00-16:00 mot ngay thuong thang 11. Mot con so do
   thay the ca muc nay lan OBSERVED_PEAK dang thieu.

======================================================================
(B) BASE_DAY = 28 -- VA VI SAO KHONG PHAI 27
======================================================================
Ca 27 lan 28 deu qua ca hai rang buoc o muc (A):
    base=27 -> dinh 56 phut, hang dai nhat 876 nguoi (80% suc chua phong)
    base=28 -> dinh 50 phut, hang dai nhat 794 nguoi (72% suc chua phong)
Chenh nhau 6 phut xep hang, tuc ~6 phut tren con so hien thi. Khong co du lieu nao
tach duoc hai phuong an nay. Quy tac pha hoa da dung: KHI BANG CHUNG CHI RA MOT DAI,
KHONG LAM TRON VE PHIA CON SO BAN DUOC NHIEU FAST TRACK HON. Chon 28.

BASE_NIGHT = 24 khong phai mot lua chon doc lap: `simulate()` dung
`max(3, BASE_DAY - 4)` cho gio vang, va o HAN `quiet_hours()` tra ve RONG (khong gio
nao khong co chuyen ha trong 3 tieng lien). Nen so nay chi de ghi vao `assumptions`
cho khop voi code -- no khong chay lan nao trong thang 10/2026.

CANH BAO DO NHAY -- giong SAF, nang hon SAF:
He so su dung ~86%. Thu nghiem tren chinh mo hinh nay:
    uplift 1,00 (T10) -> dinh  50 phut, hang   794 ( 72% suc chua phong)
    uplift 1,10 (T11) -> dinh  71 phut, hang 1.158 (105% -- VO TRAN)
    uplift 1,20 (T12) -> dinh 136 phut, hang 2.161 (196% -- VO TRAN)
Doc cho dung: KHONG phai "thang 11 cho 71 phut". Hang 1.158 nguoi khong lot vao phong
1.100 cho, nen tinh huong do khong xay ra -- san bay se mo them quay. Nghia la:
=> TU THANG 11 TRO DI, PHAI MO THEM QUAY CHO TOI KHI HANG DAI NHAT LOT TRAN,
   roi moi doc ket qua. Doi he so mua ma giu nguyen so quay la ra so sai.

   DINH CHINH 07/10/2026 -- CAN PHAI VAN LA `surge`, KHONG PHAI `BASE_DAY`.
   Ba dong tren day viet truoc khi co luat nha 12-13 va da chi SAI CAN; chinh
   chung lam ra ban 95-105 bi chu site tra lai. Giu lai nguyen van de thay vet,
   nhung doc theo ban dinh chinh o muc (E) cuoi file. Tom lai:
     - `BASE_DAY` = bien che nen, chay SUOT CA NGAY -> lam nhanh ca khung vang.
     - `surge`    = phan ung theo nhu cau, chi chay khi hang da dai -> dung can.
   Thang 11/2026: `surge` 5 -> 8. Tai sao dung 8: 7 cho hang 1.579 > tran 1.485,
   8 cho 1.4xx -- 8 la SO NHO NHAT lot. Khong duoc lay to hon cho "an toan", vi
   moi quay them la mot phut bot di tren con so cong bo.

======================================================================
(C) OBSERVED_PEAK = (60, 90) -- QUAN SAT CUA CHU SITE, 05/10/2026
======================================================================
Chu site van hanh dich vu tai HAN hang ngay, bao: khach co the mat TOI 2 TIENG de
hoan thanh nhap canh -- dai cu cua mo hinh (toi 91 phut) ngan hon thuc te.

Day la bang chung TOT NHAT hien co cho LAN KHACH NUOC NGOAI, va no tot hon moi
nguon da cong bo, vi moi con so bao chi dang co deu la cua LAN KHACH VIET:
  - Bao Chinh phu 19/08/2026: truoc phan luong cao diem 28-30 phut; sau phan luong
    cong dan Viet con 15-17 phut.
  - VnExpress 02/08/2026: khach phan anh truoc day xep chung "30 phut den gan mot
    tieng"; sau phan luong con 5-10 phut (cau nay noi ve KHACH VIET).
Khong to nao cong bo thoi gian cua lan khach ngoai. Ban dau mo hinh phai suy tu dai
chung do, va suy ra THAP.

Quy doi sang con so mo hinh: 120 phut hien thi - WALK toi da 30 - TAXI 5 = 85 phut
XEP HANG. Dai (60, 90) om lay con so do. Cong ap dung ×0,7…×1,6 = 42-144 phut.

CANH BAO: neu sau nay co phep do cua co quan chuc nang cho rieng lan khach ngoai,
no se thay the quan sat nay. Sua OBSERVED_PEAK TRUOC roi moi chinh PROC_SEC.

======================================================================
(D) TRAN PHONG CHO: tu BO LOC CUNG thanh TRAN CO DO TRAN
======================================================================
Ban dau cong tran phong cho la bo loc cung o 1,00x (1.100 cho). Luc do chua co du
lieu thuc dia nao nen no la thu duy nhat chan mo hinh chay hoang.

Quan sat cua chu site (2 tieng cao diem) chung minh hang THUC SU tran ra khoi phong
duoc thiet ke -- hang 1.100 nguoi khong the cho ra 2 tieng cho. Nen tran cung o
1,00x chinh la thu giu mo hinh lac quan.

HALL_SPILL = 1,35 -- hang duoc phep dai toi 1,35x suc chua phong, tuc tran ra hanh
lang dan vao khu nhap canh. 1,35 LA MOT UOC LUONG, khong phai so do: khong co nguon
nao cong bo dien tich hanh lang do. Ket qua cong bo NHAY voi con so nay:
    1,00x -> 19/27 kich ban bi loai, dai hep gia tao
    1,35x -> 8/27 bi loai,  dai 90-110 phut   <- dang dung
    2,00x -> 2/27 bi loai,  dai 73-137 phut, rong den muc vo dung
Do tran nay van can: khong co no, luoi nhan ca nhung kich ban hang dai vo han.

"""
import json
from collections import deque
from han_flights import FLIGHTS, SCHEDULE_SEASON

LOAD, FOREIGN = 0.85, 0.70
MONTH_UPLIFT = 1.05   # thang 11. BANG HE SO MUA KHONG CO trong file nay (comment cu noi
# "cuoi file" nhung cuoi file khong co bang nao) -- bang that nam o skill
# update-fast-track-hanoi/reference/model.md, muc "Bang he so mua cua rieng HAN":
# thang 11 = 1,05 ("Mua thu Ha Noi + lich dong day du"). Moc van la thang 10 = 1,00.
WALK = (10, 30)        # T2 200.164 m2 sau mo rong 19/12/2025 -- nha ga LON NHAT mang luoi
PROC_SEC = 138         # xem muc (A). 125 -> 138 ngay 05/10/2026, theo quan sat cua chu site.
BASE_DAY, BASE_NIGHT, SURGE = 28, 24, 8   # SURGE 5 -> 8 ngay 07/10/2026 cho thang 11, xem (E)
SURGE_PAX = 1500       # khach ngoai vua ha trong 45 phut gan nhat -> mo them lan. ~7 chuyen HAN.
SURGE_AT = 400         # chot chan theo do dai hang. Tran phong cho ~1.100 cho (xem (6)).
# Fast Track hai bac, giong DAF/CAF/PAF (SAF ba bac vi co ca khung duoi 60 phut).
FT = {"base": 10, "peak": [10, 15]}
TAXI = 5
# Quet BA chieu -- khac SAF. O SGN khach ngoai/khach Viet chung quay nen cau va cung
# di cung nhau, quet foreign doc lap se ra kich ban vo nghia. O HAN tu 03/08/2026 hai
# lan TACH HAN: khach ngoai dong hon du tinh thi quay cua lan Viet khong do sang duoc.
# => ty le khach ngoai la rui ro THAT su va phai nam trong luoi.
GRID_FOREIGN = (0.65, 0.70, 0.75)
GRID_COUNTERS, GRID_PROC = (27, 28, 29), (128, 138, 148)
BAND_Q = (0.50, 0.75)
# Nguong bac. Phan bo cua HAN rat phang nen de nguong SAT nhau se lam moi khung cung
# mot bac. Dat theo chinh hinh dang bang (xem ghi chu khi hieu chuan).
TIER_MOD, TIER_BUSY = 60, 80

OBSERVED_PEAK = (60, 90)   # xem muc (C) -- quan sat cua chu site, 05/10/2026

# Tran phong cho -- rang buoc rieng cua HAN
HALL_CAPACITY = 1100
HALL_SPILL = 1.35      # hang duoc phep tran ra hanh lang bao nhieu -- xem muc (D)

def quiet_hours():
    """Gio NAO san bay thuc su rut bot lan -- suy TU LICH BAY, khong dat cung theo dong ho.

    Chu site xac nhan 02/10/2026: san bay KHONG cat quay khi biet chac khach con dong.
    Ban cu cat luc 00:00 dung vao luc ton hang cua cum 23:xx dang nang nhat, lam khung
    dem bi thoi len 89-105 phut -- sai han thuc te. Gio chi la VANG khi khong co chuyen
    nao ha trong 2 tieng TRUOC va 1 tieng TOI; con lai giu nguyen so lan ban ngay.
    """
    land = {minute(f[0]) // 60 for f in FLIGHTS}
    out = set()
    for h in range(24):
        near = {(h - 2) % 24, (h - 1) % 24, h, (h + 1) % 24}
        if not (land & near):
            out.add(h)
    return out


BANDS = [("00:00-06:00", 0, 6), ("06:00-10:00", 6, 10), ("10:00-13:00", 10, 13),
         ("13:00-16:00", 13, 16), ("16:00-20:00", 16, 20), ("20:00-24:00", 20, 24)]


def minute(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


RUNWAY_GAP = 2        # HAN co HAI duong bang song song (11L/29R va 11R/29L) -> gian 2 phut la du.
                      # CXR/DAD/PQC mot duong bang nen de 3. Chi dung de go gio lich lam tron.
                      # O HAN viec nay KHONG phai hinh thuc: lich thang 10/2026 co 18 cap
                      # chuyen ghi TRUNG GIO ha canh (PQC khong co cap nao). De nguyen thi
                      # mo hinh dung len nhung buc tuong khach khong co that.


def sim_minutes(gap=RUNWAY_GAP):
    """Gio ha canh dung cho MO PHONG, tach khoi gio dung de xep khung.

    Nguon lich bay lam tron theo boi so 5 phut: lich 10/2026 cua HAN co 18 cap chuyen
    ghi trung gio ha canh (vi du 07:20 AI2390 + EY432 = 479 ghe, 22:20 VN680 + 3U3905
    = 364 ghe). Hai may bay co the ha gan nhau tren hai duong bang song song, nhung
    khong the do chen cung mot phut roi do khach cung mot phut. De nguyen thi mo hinh
    dung len nhung buc tuong khach khong co that.

    Gian cac luot ha canh ra toi thieu `gap` phut. KHUNG GIO van xep theo GIO TRONG
    LICH (23:55 van thuoc 20:00-24:00), chi rieng mo phong dung gio da gian.
    """
    order = sorted(range(len(FLIGHTS)), key=lambda i: minute(FLIGHTS[i][0]))
    out = {}
    last = None
    for i in order:
        t = minute(FLIGHTS[i][0])
        if last is not None and t < last + gap:
            t = last + gap
        out[i] = t
        last = t
    return out


SIM_MINUTE = sim_minutes()
QUIET_HOURS = quiet_hours()


def landing_load(window=45):
    """Khach HA CANH trong `window` phut gan nhat, theo tung phut cua ngay.

    San bay BIET TRUOC cum nao sap toi va bo tri nguoi tu dau ca -- chu site xac nhan
    02/10/2026. Ban cu chi tang lan khi hang DA dai 300 nguoi, tuc phan ung sau khi
    tac: cum 23:15-23:55 don toi 474 nguoi roi moi mo them quay. Gio tang lan theo
    LICH BAY, con nguong hang dai giu lai lam chot chan.
    """
    DAY = 24 * 60
    load = [0.0] * DAY
    for (t, _fl, _o, seats) in FLIGHTS:
        pax = seats * LOAD * FOREIGN
        at = minute(t)
        for m in range(window):
            load[(at + m) % DAY] += pax
    return load


LANDING_LOAD = landing_load()


def simulate(proc_sec=None, base_day=None, surge=None, uplift=None, foreign=None):
    """Mo phong HAI ngay lien tiep giong het nhau, doc ket qua tu ngay THU HAI.

    Vi sao phai lam the: HAN co chuyen ha den 23:45 va chuyen dau ngay moi luc 00:15.
    Khach cua cum dem van con dang xep hang khi sang ngay moi. Neu bat dau voi hang
    RONG luc 00:00 thi khung 00:00-06:00 bi tinh THIEU -- loi nay da do o DAD (35 thay
    vi 93 phut). Day la loi cua MO HINH, khong phai cua san bay.
    """
    proc_sec = PROC_SEC if proc_sec is None else proc_sec
    base_day = BASE_DAY if base_day is None else base_day
    surge = SURGE if surge is None else surge
    uplift = MONTH_UPLIFT if uplift is None else uplift
    foreign = FOREIGN if foreign is None else foreign
    DAY, DAYS = 24 * 60, 2
    horizon = DAYS * DAY + 6 * 60
    arrivals = [[] for _ in range(horizon)]
    sched = []                                   # (gio theo lich tuyet doi, chi so chuyen, ngay)
    for d in range(DAYS):
        for k, (t, _fl, _o, seats) in enumerate(FLIGHTS):
            st = d * DAY + SIM_MINUTE[k]          # gio da gian -> xep vao hang
            i = len(sched)
            sched.append((d * DAY + minute(t), k, d))   # do tu GIO TRONG LICH BAY
            pax = seats * LOAD * foreign * uplift
            a, b = WALK
            for m in range(a, b):
                arrivals[st + m].append((i, pax / (b - a)))
    queue = deque()
    wait_sum = [0.0] * len(FLIGHTS)
    pax_sum = [0.0] * len(FLIGHTS)
    worst = [0.0] * len(FLIGHTS)
    max_queue = 0.0                              # nguoi dang dung trong phong cho, luc dong nhat
    for t in range(horizon):
        for f, n in arrivals[t]:
            queue.append([f, t, n])
        qlen = sum(c[2] for c in queue)
        if t >= DAY:                             # chi do tu ngay thu hai, giong cach doc ket qua
            max_queue = max(max_queue, qlen)
        hour = (t // 60) % 24
        counters = max(3, base_day - 4) if hour in QUIET_HOURS else base_day
        # Tang lan theo LICH BAY (biet truoc), chot chan bang do dai hang (bat ngo).
        if LANDING_LOAD[t % (24 * 60)] * uplift >= SURGE_PAX or qlen >= SURGE_AT:
            counters += surge
        cap = counters * 60.0 / proc_sec
        while cap > 1e-9 and queue:
            f, joined, n = queue[0]
            take = min(n, cap)
            st, k, d = sched[f]
            if d == DAYS - 1:                    # chi ghi nhan ngay CUOI
                wait_sum[k] += take * (t - joined)
                pax_sum[k] += take
                worst[k] = max(worst[k], t - st)  # do tu GIO TRONG LICH BAY
            cap -= take
            if take >= n - 1e-9:
                queue.popleft()
            else:
                queue[0][2] -= take
    rows = []
    for name, h0, h1 in BANDS:
        idx = [i for i, f in enumerate(FLIGHTS) if h0 * 60 <= minute(f[0]) < h1 * 60]
        p = sum(pax_sum[i] for i in idx)
        avg = sum(wait_sum[i] for i in idx) / p if p else None
        rows.append({"band": name, "flights": len(idx),
                     "avg_wait": None if avg is None else round(avg, 1),
                     "worst_wait": None if not idx else round(max(worst[i] for i in idx)),
                     "pax": round(p)})
    return rows, sum(wait_sum) / sum(pax_sum), sum(pax_sum), max_queue


def peak_queue(**kw):
    """Dinh thoi gian XEP HANG (da tru di bo va lan bai) -- con so de doi chieu quan sat."""
    rows, _, _, _ = simulate(**kw)
    return max(r["worst_wait"] for r in rows if r["worst_wait"] is not None) - WALK[1]


def hall_overflow(**kw):
    """So nguoi vuot suc chua phong cho, hoac 0 neu lot.

    Phong cho nhap canh T2 chua "khoang 1.100 cho" sau thiet ke lai (Bao Chinh phu
    19/08/2026). Kich ban cho hang dai hon the la BAT KHA THI VE VAT LY, khong phai
    "kich ban xau": phong khong chua noi thi san bay buoc phai mo them quay. Dung ham
    nay de LOAI nhung kich ban do khoi luoi -- de lai se lam khoang cong bo rong ra
    bang nhung tinh huong khong bao gio xay ra.
    """
    _, _, _, mq = simulate(**kw)
    return max(0.0, mq - HALL_CAPACITY)


def build_month_json(month, month_label, month_notes, empty_band_note, context, basis, cities,
                     guide, uplift=None, surge=None):
    """month='2026-10', month_label='October 2026'.

    `uplift` va `surge` LA DON BAY THEO THANG, nhan tu inputs-YYYY-MM.json (khoa
    `month_uplift` / `surge`). None -> dung hang so module.

    VI SAO PHAI NHAN TU INPUTS -- sua 07/10/2026:
    Truoc day ca hai la HANG SO MODULE. Doi chung cho thang moi la thang cu KHONG
    DUNG LAI DUOC nua: dung inputs thang 10 voi model da chinh cho thang 11 ra mot
    con so thu ba, khong phai thang nao ca. Da dinh that o HAF ngay 07/10/2026 khi
    SURGE 5 -> 8 lam thang 10 (da phat hanh 97-110) vo luon cong tran phong cho.
    Skill van canh bao "MONTH_UPLIFT la hang so module, quen sua la im lang dung he
    so thang truoc" -- day la cach chua goc cho ca canh bao do.
    Hang so module gio chi con la MAC DINH cho ban chay tay; moi thang co so cua no
    nam trong inputs cua chinh thang do.
    """
    # CONG CHAN TRAN LAP DAY -- them 07/10/2026.
    #
    # `uplift` nhan THANG vao LOAD (xem `simulate`: pax = seats * LOAD * foreign * uplift).
    # Nen LOAD * uplift la TY LE LAP DAY GHE THUC TE, va no khong the vuot 1,0: khong
    # chuyen nao cho nhieu khach hon so ghe no co.
    #
    # VI SAO PHAI LA MOT CONG, KHONG PHAI MOT GHI CHU: bang he so mua cua CA NAM SITE
    # deu co o thang 12 / 1 / 2 lam vo tran nay, va khong ai nhan ra trong nhieu thang:
    #     PQC  0,85 x 1,20 = 102,0%      DAD  0,85 x 1,20 = 102,0% (thang 2)
    #     CXR  0,87 x 1,25 = 108,7%      SGN  0,85 x 1,20 = 102,0%
    #     HAN  0,85 x 1,15 =  97,7% (lot, nhung thang 2 cung 1,15 nen sat men)
    # Ngay 07/10/2026 ba trong nam ban chay thu thang 12 da dung dung so vo tran do ma
    # cong bo -- mot ban len tan 102%. Doc bang roi go vao la khong du; phai co cong.
    #
    # CACH XU DUNG khi cong nay no (day la cong PHAN DOAN, khong phai co hoc):
    #   Bang he so mua chi dung duoc nhu HE SO SAN LUONG so voi thang moc, chu khong
    #   phai he so lap day. Dat so bang lam MUC TIEU SAN LUONG roi dat nos bang
    #   DANH SACH CHUYEN -- dung nhu chinh bang da canh bao bang chu in ("thang 12/1/2
    #   cac hang THEM CHUYEN THAT, phai dung lai danh sach") -- roi de `month_uplift`
    #   o muc lap day THAT.
    #   TUYET DOI khong ha LOAD de lot cong: LOAD la hang so da hieu chuan cua site.
    if LOAD * (MONTH_UPLIFT if uplift is None else uplift) > 1.0:
        u = MONTH_UPLIFT if uplift is None else uplift
        raise SystemExit(
            f"TY LE LAP DAY GHE VUOT 100%: LOAD {LOAD} x month_uplift {u} = "
            f"{LOAD * u:.1%}.\n\n"
            f"  Khong chuyen nao cho nhieu khach hon so ghe no co. Tran cua "
            f"`month_uplift` o site nay la {1 / LOAD:.3f}.\n\n"
            f"  DAY LA LOI CUA BANG HE SO MUA, khong phai loi cua thang nay. Bang chi\n"
            f"  dung duoc nhu he so SAN LUONG so voi thang moc. Dat muc tieu do bang\n"
            f"  DANH SACH CHUYEN (chinh bang da can: 'thang 12/1/2 cac hang them chuyen\n"
            f"  that, phai dung lai danh sach'), roi de `month_uplift` o muc lap day THAT.\n\n"
            f"  KHONG duoc ha LOAD de lot cong -- LOAD la hang so da hieu chuan cua site.")

    import itertools
    central_rows, _, central_pax, central_queue = simulate(uplift=uplift, surge=surge)
    if central_queue > HALL_CAPACITY * HALL_SPILL:
        raise SystemExit(
            f"KICH BAN TRUNG TAM VO TRAN PHONG CHO: hang dai nhat {central_queue:.0f} nguoi "
            f"> {HALL_SPILL:.2f}x suc chua {HALL_CAPACITY}. San bay se mo them quay chu khong de "
            "ngoai phong.\n\n"
            f"  NANG `surge` trong inputs-YYYY-MM.json -- KHONG nang BASE_DAY, va KHONG sua\n"
            f"  hang so module. Lay SO NHO NHAT lot tran: tang 1 roi chay lai, dung nhay.\n"
            f"  Hien `surge` = {SURGE if surge is None else surge}.\n\n"
            f"  VI SAO KHONG PHAI BASE_DAY (luat nha 13): BASE_DAY la bien che NEN, chay\n"
            f"  suot ca ngay, nen no lam nhanh ca nhung khung KHONG he dong -- va mot thang\n"
            f"  dong hon khong the co khung nao nhanh len (luat 12). Ngay 07/10/2026 chinh\n"
            f"  cau canh bao cu o day da chi sai can: nang BASE_DAY 28->33 cho ra 95-105,\n"
            f"  THAP hon thang 10 (97-110), va khung vang 06:00-10:00 nhanh len 51-53 ->\n"
            f"  49-52. Chu site bat duoc ngay. Xem muc (E) cuoi file nay.\n\n"
            f"  Chay xong NHO chay phep thu don dieu truoc khi giao:\n"
            f"    python3 tools/prev_bands.py --prev haf/home/latest.json --new <json vua dung>")
    grid_all = [(simulate(proc_sec=p, base_day=c, foreign=fo, uplift=uplift, surge=surge), (p, c, fo))
                for p, c, fo in itertools.product(GRID_PROC, GRID_COUNTERS, GRID_FOREIGN)]
    grid = [g for g, _k in grid_all if g[3] <= HALL_CAPACITY * HALL_SPILL]
    dropped = [k for g, k in grid_all if g[3] > HALL_CAPACITY * HALL_SPILL]
    if len(grid) < len(grid_all) // 2:
        raise SystemExit(
            f"LUOI HONG: {len(grid)}/{len(grid_all)} kich ban lot tran phong cho. "
            "Tam luoi dat sai cho -- chinh GRID_COUNTERS roi chay lai.")

    def q(vals, lo=BAND_Q[0], hi=BAND_Q[1]):      # phan vi -> khoang, khong lay min/max
        vals = sorted(v for v in vals if v is not None)
        if not vals:
            return None
        k = lambda f: vals[min(len(vals) - 1, max(0, round(f * (len(vals) - 1))))]
        return [k(lo), k(hi)]

    bands = []
    for i, r in enumerate(central_rows):
        if r["avg_wait"] is None:
            bands.append({**r, "standard": None, "tier": "none"})
            continue
        lo, hi = q([g[0][i]["worst_wait"] for g in grid])
        top = hi + TAXI
        # Phân bậc theo con số HIỂN THỊ, không theo worst_wait thô. Ngưỡng cũ đặt trên
        # số thô nên một khung hiện "38-50 min" vẫn bị gắn nhãn "Usually quick".
        tier = "busy" if top >= TIER_BUSY else ("moderate" if top >= TIER_MOD else "quick")
        bands.append({**r, "standard": [lo + TAXI, top], "tier": tier})

    # Tiêu đề chỉ lấy BẬC CAO NHẤT và BẬC THẤP NHẤT đang có trong tháng, không gộp
    # "moderate" vào cụm bận. Gộp vào sẽ cho ra kiểu "38-118 min, 06:00-24:00":
    # khoảng rộng gấp ba, trải gần cả ngày, người đọc không rút ra được gì.
    ORDER = ["quick", "moderate", "busy"]
    live = [b for b in bands if b["standard"]]
    hi_t = max((b["tier"] for b in live), key=ORDER.index)
    lo_t = min((b["tier"] for b in live), key=ORDER.index)
    worst = max(live, key=lambda b: b["standard"][1])   # MOT khung, de len hero
    for b in bands:
        b["busy"] = bool(b["standard"]) and b["tier"] == hi_t
        b["calm"] = bool(b["standard"]) and (b["tier"] == lo_t if lo_t != hi_t else True)

    def span(sel):
        """Gộp các khung được chọn thành CÁC CỤM LIỀN NHAU, nối bằng '|'.
        Lấy min(đầu)..max(cuối) như trước sẽ sai khi khung cao điểm và khung vắng
        xen kẽ nhau: hai mô tả sẽ chồng lên nhau và chọi nhau trong cùng một đoạn."""
        picked = [b for b in bands if b["standard"] and sel(b)]
        if not picked:
            return None
        runs = []
        for b in picked:                               # bands đã theo thứ tự thời gian
            a, z = b["band"].split("-")
            if runs and runs[-1][1] == a:              # nối tiếp cụm đang mở
                runs[-1][1] = z
            else:
                runs.append([a, z])
        # Noi vong qua nua dem. DAD co cum Han Quoc chay 20:00 den qua 01:10; neu khong
        # noi thi mot khoang lien tuc bi cat lam hai, doc ra thanh hai cum roi rac.
        if len(runs) > 1 and runs[0][0] == "00:00" and runs[-1][1] == "24:00":
            runs[-1][1] = runs[0][1]
            runs.pop(0)
        ORD = ["none", "quick", "moderate", "busy"]
        return {"window": "|".join(f"{a}-{z}" for a, z in runs),
                "tier": max((b["tier"] for b in picked), key=ORD.index),
                "range": [min(b["standard"][0] for b in picked),
                          max(b["standard"][1] for b in picked)],
                "flights": sum(b["flights"] for b in picked)}

    # CỔNG HIỆU CHUẨN — chạy trước khi trả kết quả.
    # Mô hình từng ra gấp 2-3 lần thời gian chờ thực tế mà khách phản ánh, vì số quầy
    # và tỷ lệ khách qua quầy tay đều là giả định. Không ai báo — trang cứ thế đăng số sai.
    peak_queue = max(b["standard"][1] - TAXI - WALK[1] for b in bands if b["standard"])
    lo_ok, hi_ok = OBSERVED_PEAK[0] * 0.7, OBSERVED_PEAK[1] * 1.6
    if not (lo_ok <= peak_queue <= hi_ok):
        raise SystemExit(
            f"CỔNG HIỆU CHUẨN KHÔNG QUA: đỉnh xếp hàng {peak_queue:.0f} phút, "
            f"ngoài dải chấp nhận được {lo_ok:.0f}-{hi_ok:.0f} "
            f"(quan sát thực tế {OBSERVED_PEAK[0]}-{OBSERVED_PEAK[1]}). "
            "Dừng lại: xem lại số quầy, tỷ lệ khách ngoại, hoặc lịch bay — đừng giao số.")

    return {
        "schema": "haf-wait/1.0", "site": "HAF", "airport": "HAN", "month": month,
        "month_label": month_label, "status": "estimate",
        "metric": "minutes from landing to clearing immigration, last passengers off a flight",
        "lane": "foreign passport holders, standard immigration queue",
        # peak = CHI MOT khung te nhat. O HAF no KHONG len hero (khac SAF): render_blocks.py
        #        dung h["busy"] vi cum busy cua HAN tach bach khoi cac bac duoi (san 69 >
        #        tran Moderate 65). Giu peak lai de doi chieu hang thang.
        # busy = toan bo cum bac cao nhat -> the "When Fast Track matters most". Cua so de biet
        #        khi nao can dich vu. Thang cao diem co the co 3-4 khung Busy roi rac; gop het
        #        vao hero se ra kieu "44-136 min, 06:00-24:00", rong gap ba va vo nghia.
        "headline": {"peak": span(lambda b: b is worst),
                     "busy": span(lambda b: b["busy"]), "quiet": span(lambda b: b["calm"]),
                     "fast_track": FT, "intl_arrivals_per_day": len(FLIGHTS),
                     "foreign_pax_per_day": round(central_pax, -2)},
        "bands": bands,
        "notes": {"month_notes": month_notes, "empty_band_note": empty_band_note},
        "context": context, "basis": basis,
        "links": {"guide": guide}, "cities": cities,
        "assumptions": {"load": LOAD, "foreign_share": FOREIGN,
                        "month_uplift": MONTH_UPLIFT if uplift is None else uplift,
                        # ^ GIA TRI DA DUNG THAT, khong phai hang so module.
                        #   Tu khi don bay ve inputs (luat nha 14), hai khoa nay la
                        #   thu DUY NHAT ghi lai thang do chay voi don bay nao -- va
                        #   monthly_publish.py cop chung vao latest.json lam MOC DOI
                        #   CHIEU cho phep thu don dieu thang sau. Ghi hang so module
                        #   vao day la noi doi: 07/10/2026 HAF da in surge=8/uplift=1,05
                        #   cho ban thang 10 that ra chay surge=5/uplift=1,00, va moc
                        #   sai do se lam thang 11 ket luan nguoc ("khong them quay").
                        "walk_min": WALK, "processing_sec": PROC_SEC,
                        "seats": {f[1]: f[3] for f in FLIGHTS},
                        "counters_day": BASE_DAY, "counters_night": BASE_NIGHT,
                        "surge_counters": SURGE if surge is None else surge, "surge_queue": SURGE_AT, "taxi_min": TAXI,
                        "seats_per_flight": True, "calibrated_to": list(OBSERVED_PEAK),
                        "grid_counters": list(GRID_COUNTERS), "grid_processing_sec": list(GRID_PROC),
                        "grid_foreign_share": list(GRID_FOREIGN), "band_quantiles": list(BAND_Q),
                        "hall_capacity": HALL_CAPACITY,
                        "peak_queue_people": round(central_queue),
                        "grid_points_used": len(grid),
                        "grid_points_dropped_hall": [list(k) for k in dropped]},
        "sample_flights": [{"time": f[0], "flight": f[1], "from": f[2], "seats": f[3]} for f in FLIGHTS],
    }


