# Danh Sách Nhiệm Vụ Nâng Cấp Ứng Dụng (Todo List)

## Giai đoạn 1: Lọc sự cố hôm nay & Cải tiến Exporter Shift Report theo tab (Hình 1, 2, 3)

### Task 1: Cập nhật DetailView chỉ hiển thị sự cố trong ngày hôm nay khi khởi động
- [x] Trong `ui/views/detail_view.py`, thay thế `load_all_incidents()` bằng `load_today_incidents()` trong hàm `__init__`.
- [x] Đặt giá trị mặc định của 2 DateEntry `date_from` và `date_to` là ngày hôm nay.
- [x] Nhãn thanh trạng thái `lbl_status` hiển thị rõ: "📅 Hôm nay: [YYYY-MM-DD] | Số lượng: [X] sự cố".
- [x] Bấm nút "🔍 Lọc" sẽ lọc theo khoảng ngày chọn; bấm "↺ Xem tất cả" mới hiển thị toàn bộ lịch sử sự cố.
- **Acceptance criteria:**
  - [x] Khi khởi động hoặc chuyển tab Detail, chỉ hiển thị sự cố có ngày trùng ngày hiện tại.
  - [x] Bộ lọc ngày và nút Xem tất cả hoạt động chính xác.
- **Verification:**
  - [x] Chạy ứng dụng kiểm tra danh sách sự cố mặc định chỉ tải đúng ngày hôm nay.
- **Dependencies:** None
- **Files touched:** `ui/views/detail_view.py`
- **Scope:** Small (1 file)

---

### Task 2: Cải tiến bố cục định dạng Shift Report khớp 100% Hình 1 & 2
- [x] Sửa thông tin tiêu đề:
  - `Sect.: Dx Engineering Team` (thay cho `IT Management`).
  - Tiêu đề: `Shift Report` (E1), ngày báo cáo `(DD-Mon-YYYY)` (E2).
  - Thêm mục `Group: B` (hoặc lấy từ header).
- [x] Chuẩn hóa lại vị trí các dòng chi tiết:
  - Dòng 19: `2. Detail`
  - Dòng 20: Header bảng `Category`, `Time`, `Failure`, `Reason`, `Solution`, `Current Situation`, `Contact Number` (Màu nền `#CCFFFF`).
  - Dòng 21-22: `Indoor Environment` (Nhiệt độ dòng 21, Độ ẩm dòng 22).
  - Dòng 23-31: `H/W Inspection` (MES Server -> Network).
  - Dòng 32-35: `Facility Inspection` (UPS, Điều hòa, Cháy chập, Bình chữa cháy).
  - Dòng 36: `Security Inspection` (Khóa cửa).
  - Dòng 37: `MES Server Backup` (`OK`).
  - Dòng 38: `MES Application` (`OK`).
  - Dòng 39: `Remark` (`OK`, nội dung ghi chú ở cột D).
- [x] Chuẩn hóa bảng 3. HMI Checking (Hình 2):
  - Dòng 41: Khung viền đậm `3. HMI checking` căn giữa từ cột B đến H.
  - Dòng 42: Header bảng: `Line` (cột B), `MES link SCC` (cột C), `SCC Link PLC` (cột D), `Application Link` (gộp E:F), `Remark` (gộp G:H).
  - Dòng 43-48: Các chuyền PCM, CAL, FH-RCL, CR-RCL, PDS, CLTS với các ô gộp E:F và G:H tương ứng.
- **Acceptance criteria:**
  - [x] Bố cục các dòng, cột, ô gộp và màu nền trùng khớp 100% với Hình 1 và Hình 2.
- **Verification:**
  - [x] Xuất thử file Excel kiểm tra từng tọa độ ô và gộp cột.
- **Dependencies:** None
- **Files touched:** `services/export_service.py`, `config/settings.py`
- **Scope:** Small (2 files)

---

### Task 3: Nâng cấp Export Service xuất vào Tab mới trong Master File (Hình 3)
- [x] Xây dựng hàm xác định đường dẫn file Master: `get_shift_report_path(date_str)` trả về `D:\Report\<YYYY>\<Month_name>\Shift report <MM-YYYY>.xlsx` (tự động tạo thư mục nếu chưa có).
- [x] Quy tắc đặt tên tab: `DD-Mon-YYYY (Shift 1)` cho Ca Ngày và `DD-Mon-YYYY (Shift 2)` cho Ca Đêm (ví dụ: `29-Oct-2026 (Shift 2)`).
- [x] Nếu file đã tồn tại: mở bằng `openpyxl.load_workbook()`; nếu tab đã có thì xóa tab cũ và thay thế bằng tab mới cập nhật. Nếu file chưa có thì tạo mới workbook.
- [x] Thêm tùy chọn trên hộp thoại để người dùng duyệt chọn file khác nếu không muốn lưu vào đường dẫn mặc định.
- **Acceptance criteria:**
  - [x] Xuất trực tiếp vào tab trong file tháng `D:\Report\...\Shift report MM-YYYY.xlsx` mà không tạo file rời.
  - [x] Ghi đè/cập nhật tab cũ an toàn nếu tab đã tồn tại.
- **Verification:**
  - [x] Chạy test xuất 2 ca trực khác nhau trên cùng 1 ngày, kiểm tra file có đủ 2 tab `(Shift 1)` và `(Shift 2)`.
- **Dependencies:** Task 2
- **Files touched:** `services/export_service.py`, `ui/views/detail_view.py`
- **Scope:** Small (2 files)

---

### 🏁 Checkpoint 1: Xác nhận Giai đoạn 1
- [x] Tab Detail mặc định hiển thị đúng sự cố hôm nay.
- [x] Xuất Shift Report tạo đúng tab trong file `D:\Report\...\Shift report MM-YYYY.xlsx`.
- [x] Cấu trúc tab xuất ra khớp hoàn toàn với Hình 1 và Hình 2.

---

## Giai đoạn 2: Dịch vụ & Giao diện Tab Daily Inspection (Hình 4)

### Task 4: Xây dựng Daily Inspection Service & Excel Exporter
- [x] Tạo `services/daily_inspection_service.py`:
  - Định nghĩa danh sách 28 hạng mục kiểm tra (Server, Storage, Network, UPS, Air condition, PCCC, An ninh...).
  - Định nghĩa 24 mốc giờ: Ca 1 (`8:00` -> `19:00`), Ca 2 (`20:00` -> `7:00`).
  - Hàm `generate_default_daily_data(date_str, inspector_name)`: điền sẵn 22°C, 46%, tất cả `V`, `-` cho Man IN-OUT, tên người kiểm tra.
  - Hàm `save_daily_inspection(date_str, data)` và `load_daily_inspection(date_str)`: lưu/đọc dữ liệu theo ngày trong SQLite.
  - Hàm `export_daily_inspection_to_excel(date_str, data, filepath)`: ghi tab có tên `DD-MM-YYYY` (ví dụ: `29-10-2026`) vào file `D:\Report\<YYYY>\<Month_name>\Daily inspection <MM-YYYY>.xlsx` khớp 100% mẫu Hình 4.
- **Acceptance criteria:**
  - [x] Lưu và đọc dữ liệu 24 mốc giờ không bị mất mát.
  - [x] File Excel `Daily inspection MM-YYYY.xlsx` được ghi thêm tab chuẩn định dạng Hình 4.
- **Verification:**
  - [x] Viết test tự động kiểm tra lưu DB và xuất file Excel Daily Inspection.
- **Dependencies:** Task 3
- **Files touched:** `services/daily_inspection_service.py`, `database/schema.py`
- **Scope:** Medium (2 files)

---

### Task 5: Xây dựng giao diện DailyInspectionView
- [x] Tạo `ui/views/daily_inspection_view.py`:
  - Thanh công cụ trên cùng: Bộ chọn ngày kiểm tra, nút `⚡ Tạo dữ liệu mặc định hôm nay`, nút `💾 Lưu dữ liệu`, nút `📤 Xuất Excel Daily Inspection`.
  - Bảng lưới hiển thị 28 hạng mục x 24 cột khung giờ.
  - Cho phép click để chuyển đổi nhanh giữa `V` (Bình thường) và `X` (Bất thường).
  - Dòng nhiệt độ, độ ẩm, người kiểm tra và ghi chú cho phép chỉnh sửa dễ dàng.
  - Giao diện có thanh cuộn ngang/dọc mượt mà.
- **Acceptance criteria:**
  - [x] Giao diện trực quan, thao tác nhanh chỉ với 1 click để tạo dữ liệu mặc định hoặc chuyển đổi V/X.
  - [x] Bấm lưu hoặc xuất Excel có thông báo phản hồi rõ ràng.
- **Verification:**
  - [x] Khởi tạo view, click tạo dữ liệu mặc định và lưu thành công.
- **Dependencies:** Task 4
- **Files touched:** `ui/views/daily_inspection_view.py`, `ui/views/__init__.py`
- **Scope:** Medium (2 files)

---

### Task 6: Tích hợp Tab Daily Inspection vào main.py
- [x] Trong `main.py`, khởi tạo `DailyInspectionView` và thêm vào Notebook làm tab thứ 4: `notebook.add(self.daily_view, text="  📋 4. Daily Inspection  ")`.
- [x] Đồng bộ tên người trực từ Header ca trực vào trường `Inspected by` của Daily Inspection.
- **Acceptance criteria:**
  - [x] Ứng dụng có đủ 4 tab: Dashboard, Detail, HMI Checking, Daily Inspection.
  - [x] Chuyển tab mượt mà, không giật lag.
- **Verification:**
  - [x] Chạy `python main.py` kiểm tra tab mới hiển thị và hoạt động đầy đủ tính năng.
- **Dependencies:** Task 5
- **Files touched:** `main.py`
- **Scope:** Small (1 file)

---

### 🏁 Checkpoint 2: Xác nhận Giai đoạn 2
- [x] Tab Daily Inspection hoạt động đầy đủ trên giao diện.
- [x] Nút xuất Excel tạo đúng tab ngày trong file `Daily inspection MM-YYYY.xlsx` giống hệt Hình 4.

---

## Giai đoạn 3: Kiểm thử toàn diện & Hoàn thiện

### Task 7: Viết Unit Tests tự động cho các chức năng mới
- [x] Tạo `tests/test_daily_inspection.py` kiểm thử service daily inspection.
- [x] Bổ sung test kiểm tra xuất tab vào file Excel có sẵn và ghi đè tab trong `tests/test_export_service.py`.
- **Acceptance criteria:**
  - [x] 100% các bài test tự động vượt qua (0 failure, 0 error).
- **Verification:**
  - [x] Chạy lệnh `python -m unittest discover tests`.
- **Dependencies:** Task 6
- **Files touched:** `tests/test_daily_inspection.py`, `tests/test_export_service.py`
- **Scope:** Small (2 files)

---

### Task 8: Cập nhật tài liệu README.md & Đồng bộ GitHub
- [x] Cập nhật `README.md` mô tả tab Daily Inspection mới và cơ chế xuất file Excel Master theo tháng.
- [x] Commit toàn bộ mã nguồn lên Git và Push lên GitHub `origin/main`.
- **Acceptance criteria:**
  - [x] README.md phản ánh đầy đủ cấu trúc mới.
  - [x] GitHub đồng bộ hoàn tất.
- **Verification:**
  - [x] Kiểm tra `git status` sạch và `git push` thành công.
- **Dependencies:** Task 7
- **Files touched:** `README.md`
- **Scope:** Small (1 file)

---

### 🏁 Checkpoint 3 (Final): Hoàn tất nghiệm thu
- [x] Tất cả 4 yêu cầu của người dùng được giải quyết trọn vẹn:
  1. Tab Detail mặc định chỉ hiện sự cố hôm nay.
  2. Xuất Shift Report vào tab trong file tháng `D:\Report\...\Shift report MM-YYYY.xlsx`.
  3. Cấu trúc Shift Report khớp 100% Hình 1 & 2.
  4. Tab Daily Inspection và xuất Excel giống hệt Hình 4.
