# IT Incident Logger & Shift Report Dashboard

Ứng dụng Desktop (Tkinter) chuyên nghiệp phục vụ quản lý, ghi nhận sự cố IT (IT Incident Logger), theo dõi kiểm tra đường truyền HMI chuyền sản xuất, nhật ký kiểm tra 24 giờ hằng ngày (Daily Inspection) và kết xuất báo cáo ca trực định dạng Excel vào các file Master theo tháng.

Dự án được xây dựng theo chuẩn **Clean Modular Architecture**, sẵn sàng cho môi trường thực tế (Production-Ready) với khả năng mở rộng cao.

---

## 1. Cấu Trúc Thư Mục và Công Dụng Từng Module

```
IT Incident Logger/
├── config/                  # Quản lý cấu hình tập trung và hằng số nghiệp vụ
│   ├── settings.py          # Đường dẫn DB động (.exe & script), cấu hình app, cờ AUTH_ENABLED, logging
│   └── constants.py         # Danh mục sự cố (Category/Sub-item), lines HMI, bảng màu UI, font chữ
│
├── database/                # Tầng truy xuất và quản trị cơ sở dữ liệu SQLite
│   ├── connection.py        # Quản lý kết nối, Context Manager an toàn (db_session) tự động commit/rollback
│   └── schema.py            # Khởi tạo bảng (incidents, hmi_monitoring, daily_inspection, users) & indexes
│
├── services/                # Tầng nghiệp vụ xử lý logic độc lập
│   ├── session_service.py   # Quản lý phiên làm việc, danh sách kỹ sư trực ca, khung AuthBackend mở rộng
│   ├── incident_service.py  # Nghiệp vụ CRUD sự cố, bộ lọc ngày & từ khóa, tính toán số liệu Dashboard
│   ├── hmi_service.py       # Nghiệp vụ lưu & tải trạng thái giám sát HMI của 6 chuyền sản xuất
│   ├── daily_inspection_service.py # Nghiệp vụ Daily Inspection 24H (28 hạng mục), SQLite & Excel exporter
│   └── export_service.py    # Nghiệp vụ kết xuất Shift Report vào tab trong Master File tháng
│
├── ui/                      # Tầng giao diện người dùng (Tkinter & ttk)
│   ├── styles.py            # Cấu hình theme clam và bảng màu hiện đại đồng bộ
│   ├── components/          # Các Reusable UI Component dùng lại
│   │   ├── stat_card.py     # Thẻ hiển thị số liệu KPI (Total, Today, Open issues)
│   │   ├── date_time_picker.py # Widget chọn ngày kết hợp giờ:phút chuyên dụng
│   │   └── data_table.py    # Bảng Treeview bọc sẵn thanh cuộn 2 chiều, định dạng cột linh hoạt
│   ├── dialogs/             # Các hộp thoại Modal
│   │   └── incident_dialog.py # Hộp thoại Thêm/Sửa sự cố chuẩn modular
│   └── views/               # 4 Màn hình chức năng chính
│       ├── header_view.py   # Thanh thông tin ca trực (Dept, Date, Shift, Người trực)
│       ├── dashboard_view.py# Tab 1: Tổng quan số liệu thống kê & phân bố sự cố
│       ├── detail_view.py   # Tab 2: Danh sách sự cố (mặc định hôm nay), lọc ngày & xuất Shift Report
│       ├── hmi_view.py      # Tab 3: Bảng kiểm tra kết nối HMI theo chuyền
│       ├── daily_inspection_view.py # Tab 4: Bảng kiểm tra 24 giờ hằng ngày (Daily Inspection)
│       └── login_view.py    # (Extensible) Module đăng nhập sẵn có cho tương lai
│
├── tests/                   # Bộ kiểm thử tự động (Unit Tests) độc lập
│   ├── test_database.py     # Kiểm thử kết nối, schema và rollback transaction
│   ├── test_session_service.py # Kiểm thử quản lý session, hash mật khẩu PBKDF2
│   ├── test_incident_service.py # Kiểm thử thêm, sửa, xóa, lọc sự cố & HMI
│   ├── test_export_service.py # Kiểm thử xuất tab Shift Report vào file Master
│   └── test_daily_inspection.py # Kiểm thử lưu DB và xuất tab Daily Inspection 24H
│
├── dist/
│   └── it_errors.db         # Cơ sở dữ liệu SQLite chứa dữ liệu sự cố thực tế
├── requirements.txt         # Khai báo các thư viện phụ thuộc (openpyxl, tkcalendar, babel)
├── IT_Error_Logger_v2.spec  # Cấu hình đóng gói PyInstaller
└── main.py                  # Entry point tinh gọn (~115 dòng) khởi động ứng dụng
```

---

## 2. Các Tính Năng Nổi Bật Mới Cập Nhật

### 1. Tab Detail - Mặc định chỉ hiển thị sự cố trong ngày
- Khi khởi động ứng dụng hoặc chuyển sang tab Detail, bảng sự cố chỉ tải **danh sách sự cố của ngày hôm nay**.
- Có nút **📅 Hôm nay** để nhanh chóng quay lại ngày hiện tại.
- Bấm **🔍 Lọc** để xem các ngày tùy chọn; bấm **↺ Xem tất cả** khi cần xem toàn bộ lịch sử.

### 2. Shift Report xuất trực tiếp vào Tab trong Master Workbook
- Không tạo file rời rạc mà tự động ghi thêm tab mới vào file Master theo tháng:
  `D:\Report\<YYYY>\<Tháng>\Shift report <MM-YYYY>.xlsx` (ví dụ: `D:\Report\2026\Oct\Shift report 10-2026.xlsx`).
- Tên tab chuẩn hóa: `DD-Mon-YYYY (Shift 1)` cho Ca Ngày và `DD-Mon-YYYY (Shift 2)` cho Ca Đêm (ví dụ: `29-Oct-2026 (Shift 2)`).
- Nếu tab đã tồn tại, ứng dụng sẽ ghi đè và làm mới dữ liệu tab đó mà không ảnh hưởng tới các tab ngày khác.
- Bố cục báo cáo khớp 100% biểu mẫu chuẩn nhà máy (Rows 19–39: Detail, Rows 41–48: HMI checking với ô gộp E:F và G:H).

### 3. Tab Daily Inspection (Kiểm Tra 24 Giờ Hằng Ngày)
- Giao diện lưới 28 hạng mục thiết bị x 24 mốc giờ:
  - **Ca 1 (1st Shift):** `8:00` -> `19:00`
  - **Ca 2 (2nd Shift):** `20:00` -> `7:00`
- Nút **⚡ Tạo Mặc Định Hôm Nay**: Điền nhanh toàn bộ bảng với 1 click (22°C, 46%, tất cả `V`, `-` cho Man IN-OUT, phân bổ tên người trực theo ca).
- Thao tác nhanh click để chuyển đổi giữa `V` (🟢 Bình thường) và `X` (🔴 Bất thường).
- Lưu trữ SQLite độc lập theo ngày và kết xuất Excel vào file Master:
  `D:\Report\<YYYY>\<Tháng>\Daily inspection <MM-YYYY>.xlsx` với tab có tên `DD-MM-YYYY` (ví dụ `29-10-2026`).

---

## 3. Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

### Chạy ứng dụng:
```bash
python main.py
```

### Chạy kiểm thử tự động (Unit Tests):
```bash
python -m unittest discover tests
```

---

## 4. Khả Năng Mở Rộng Tính Năng Đăng Nhập (Extensible Authentication)

Hiện tại, theo yêu cầu, ứng dụng sẽ **mở thẳng vào màn hình làm việc chính** (không bắt buộc đăng nhập) để kỹ sư trực ca thao tác nhanh nhất. Trên thanh thông tin ca trực (Header), trường **Người trực** cho phép chọn nhanh hoặc gõ tên kỹ sư trực ca.

### Cách bật lại tính năng Đăng nhập trong tương lai:
Chỉ cần mở file [`config/settings.py`](file:///d:/DuyData/APP/Developing/IT%20Incident%20Logger%20-%20test/config/settings.py), đổi:
```python
auth_enabled: bool = True
```
Ứng dụng sẽ tự động hiển thị màn hình `LoginView` trước khi vào ứng dụng chính, đồng thời hỗ trợ mã hóa mật khẩu bảo mật `PBKDF2-HMAC-SHA256` có khả năng tương thích ngược và nâng cấp tự động từ mật khẩu cũ.

---

## 5. Đóng Gói Thành File Thực Thi (.exe)

Sử dụng cấu hình PyInstaller spec đã được cập nhật:
```bash
pyinstaller IT_Error_Logger_v2.spec
```
File thực thi độc lập sẽ được tạo trong thư mục `dist/IT_Error_Logger_v2.exe`. Ứng dụng tự động tìm file `it_errors.db` đặt cùng thư mục file `.exe` khi vận hành.

---

## 2. Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

### Chạy ứng dụng:
```bash
python main.py
```

### Chạy kiểm thử tự động (Unit Tests):
```bash
python -m unittest discover tests
```

---

## 3. Khả Năng Mở Rộng Tính Năng Đăng Nhập (Extensible Authentication)

Hiện tại, theo yêu cầu, ứng dụng sẽ **mở thẳng vào màn hình làm việc chính** (không bắt buộc đăng nhập) để kỹ sư trực ca thao tác nhanh nhất. Trên thanh thông tin ca trực (Header), trường **Người trực** cho phép chọn nhanh hoặc gõ tên kỹ sư trực ca.

### Cách bật lại tính năng Đăng nhập trong tương lai:
Chỉ cần mở file [`config/settings.py`](file:///d:/DuyData/APP/Developing/IT%20Incident%20Logger%20-%20test/config/settings.py), đổi:
```python
auth_enabled: bool = True
```
Ứng dụng sẽ tự động hiển thị màn hình `LoginView` trước khi vào ứng dụng chính, đồng thời hỗ trợ mã hóa mật khẩu bảo mật `PBKDF2-HMAC-SHA256` có khả năng tương thích ngược và nâng cấp tự động từ mật khẩu cũ.

---

## 4. Đóng Gói Thành File Thực Thi (.exe)

Sử dụng cấu hình PyInstaller spec đã được cập nhật:
```bash
pyinstaller IT_Error_Logger_v2.spec
```
File thực thi độc lập sẽ được tạo trong thư mục `dist/IT_Error_Logger_v2.exe`. Ứng dụng tự động tìm file `it_errors.db` đặt cùng thư mục file `.exe` khi vận hành.

