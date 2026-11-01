# IT Incident Logger & Shift Report Dashboard

Ứng dụng Desktop (Tkinter) chuyên nghiệp phục vụ quản lý, ghi nhận sự cố IT (IT Incident Logger), theo dõi kiểm tra đường truyền HMI chuyền sản xuất và kết xuất báo cáo ca trực định dạng Excel chuẩn (`Shift_Report_Full_Format.xlsx`).

Dự án đã được tái cấu trúc hoàn chỉnh theo chuẩn **Clean Modular Architecture**, sẵn sàng cho môi trường thực tế (Production-Ready) với khả năng mở rộng cao.

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
│   └── export_service.py    # Nghiệp vụ tạo và định dạng báo cáo Excel (openpyxl) chuẩn mẫu nhà máy
│
├── ui/                      # Tầng giao diện người dùng (Tkinter & ttk)
│   ├── styles.py            # Cấu hình theme clam và bảng màu hiện đại đồng bộ
│   ├── components/          # Các Reusable UI Component dùng lại
│   │   ├── stat_card.py     # Thẻ hiển thị số liệu KPI (Total, Today, Open issues)
│   │   ├── date_time_picker.py # Widget chọn ngày kết hợp giờ:phút chuyên dụng
│   │   └── data_table.py    # Bảng Treeview bọc sẵn thanh cuộn 2 chiều, định dạng cột linh hoạt
│   ├── dialogs/             # Các hộp thoại Modal
│   │   └── incident_dialog.py # Hộp thoại Thêm/Sửa sự cố chuẩn modular
│   └── views/               # Tách nhỏ từng màn hình chức năng
│       ├── header_view.py   # Thanh thông tin ca trực (Dept, Date, Shift, Người trực)
│       ├── dashboard_view.py# Tab 1: Tổng quan số liệu thống kê & phân bố sự cố
│       ├── detail_view.py   # Tab 2: Danh sách chi tiết sự cố, bộ lọc ngày & xuất Excel
│       ├── hmi_view.py      # Tab 3: Bảng kiểm tra kết nối HMI theo chuyền
│       └── login_view.py    # (Extensible) Module đăng nhập sẵn có cho tương lai
│
├── tests/                   # Bộ kiểm thử tự động (Unit Tests) độc lập
│   ├── test_database.py     # Kiểm thử kết nối, schema và rollback transaction
│   ├── test_session_service.py # Kiểm thử quản lý session, hash mật khẩu PBKDF2
│   ├── test_incident_service.py # Kiểm thử thêm, sửa, xóa, lọc sự cố & HMI
│   └── test_export_service.py # Kiểm thử xuất file Excel theo mẫu
│
├── dist/
│   └── it_errors.db         # Cơ sở dữ liệu SQLite chứa dữ liệu sự cố thực tế
├── requirements.txt         # Khai báo các thư viện phụ thuộc (openpyxl, tkcalendar, babel)
├── IT_Error_Logger_v2.spec  # Cấu hình đóng gói PyInstaller
└── main.py                  # Entry point tinh gọn (~100 dòng) khởi động ứng dụng
```

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
