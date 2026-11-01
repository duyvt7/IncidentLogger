# Kế Hoạch Tái Cấu Trúc Dự Án IT Incident Logger (Production-Ready)

## 1. Tổng quan (Overview)
Dự án là một ứng dụng Desktop (Tkinter) phục vụ ghi nhận sự cố IT (IT Incident Logger), kiểm tra hệ sinh thái HMI hàng ngày và xuất báo cáo ca trực theo chuẩn Excel (`Shift_Report_Full_Format.xlsx`).
Toàn bộ mã nguồn cũ tập trung trong 2 file nguyên khối:
- `database.py` (576 dòng): Quản lý SQLite, truy vấn sự cố, HMI và cả khối mã đồ sộ xuất báo cáo Excel (openpyxl).
- `main.py` (511 dòng): Chứa giao diện Tkinter nguyên khối với cú pháp nén (semicolon `;`), biến viết tắt khó đọc, thiếu tách biệt giữa giao diện, logic và dữ liệu.

**Yêu cầu điều chỉnh đặc biệt theo phản hồi của người dùng:**
- **Bỏ phần đăng nhập (Login Gate):** Ứng dụng sẽ mở thẳng vào không gian làm việc chính (Dashboard, Detail sự cố, HMI checking), không bắt người dùng phải đăng nhập hay gò bó bởi nút đăng xuất.
- **Thiết kế mở rộng (Extensible Architecture for Auth):** Tách riêng cơ chế quản lý phiên làm việc (`SessionService` / `AuthBackend`) với cờ bật/tắt `AUTH_ENABLED` trong `config/settings.py`. Khi cần kích hoạt lại hoặc tích hợp hệ thống xác thực nâng cao (LDAP, OAuth, mật khẩu hash, phân quyền RBAC), chỉ cần đổi cấu hình và cắm thêm màn hình login mà không phải viết lại bất kỳ logic nghiệp vụ hay UI nào khác.
- **Lựa chọn người trực (Operator Selection):** Trên thanh thông tin ca trực (Header), trường "User" được thiết kế dạng Combobox/Entry cho phép người trực linh hoạt chọn hoặc nhập tên mình (vd: các nhân sự trực ca: Hoàng Ngọc Huy, Nguyễn Mai Nghĩa, Vũ Thành Duy, Võ Đình Thủy...) để tự động gán vào trường `reporter` của sự cố.

---

## 2. Kiến trúc mục tiêu (Target Architecture)

```
IT Incident Logger - test/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Cấu hình app, đường dẫn DB, cờ AUTH_ENABLED (False), logging
│   └── constants.py         # Danh mục sự cố, lines HMI, nhân sự trực ca mặc định, bảng màu UI
├── database/
│   ├── __init__.py
│   ├── connection.py        # Context Manager kết nối SQLite an toàn, tự động commit/close
│   └── schema.py            # Khởi tạo bảng (incidents, hmi, daily, users) & bảo toàn 100% 53 sự cố
├── services/
│   ├── __init__.py
│   ├── session_service.py   # Quản lý phiên làm việc, extensible AuthBackend (sẵn sàng cắm Login sau này)
│   ├── incident_service.py  # Nghiệp vụ CRUD sự cố, lọc theo ngày/khoảng ngày, thống kê
│   ├── hmi_service.py       # Nghiệp vụ lưu & tải trạng thái HMI Monitoring
│   └── export_service.py    # Nghiệp vụ xuất file báo cáo Excel (tách riêng khỏi DB)
├── ui/
│   ├── styles.py            # Cấu hình theme ttk.Style hiện đại, đồng bộ
│   ├── components/          # Các UI component dùng lại (Reusable Widgets)
│   │   ├── stat_card.py     # Thẻ hiển thị KPI/thống kê Dashboard
│   │   ├── date_time_picker.py # Widget chọn ngày & giờ:phút kết hợp
│   │   └── data_table.py    # Bảng Treeview bọc sẵn thanh cuộn và căn lề
│   ├── dialogs/
│   │   └── incident_dialog.py # Hộp thoại Thêm/Sửa sự cố modular
│   └── views/               # Tách nhỏ từng màn hình chức năng
│       ├── header_view.py   # Thanh thông tin ca trực (Dept, Date, Shift, User selector)
│       ├── dashboard_view.py# Tab 1: Tổng quan số liệu thống kê
│       ├── detail_view.py   # Tab 2: Danh sách chi tiết sự cố & bộ lọc ngày
│       ├── hmi_view.py      # Tab 3: Bảng kiểm tra kết nối HMI theo chuyền
│       └── login_view.py    # (Extensible) Module đăng nhập sẵn có cho tương lai
├── tests/                   # Kiểm thử tự động (Unit Tests) trên SQLite in-memory
├── requirements.txt         # Khai báo các thư viện (openpyxl, tkcalendar, babel)
├── IT_Error_Logger_v2.spec  # Cấu hình đóng gói PyInstaller cập nhật
└── main.py                  # Entry point tinh gọn (~60 dòng code sạch)
```

---

## 3. Quyết định kỹ thuật & Tương thích (Architecture Decisions)

1. **Khả năng mở rộng xác thực (Extensible Authentication Architecture):**
   - Tạo lớp `BaseAuthService` và `NoAuthService` (default): cho phép truy cập tự do, quản lý active operator qua danh sách nhân viên trực ca.
   - Chuẩn bị sẵn khung `DatabaseAuthService` và `LoginView`: lưu trữ sẵn sàng trong codebase. Khi tương lai cần kích hoạt, chỉ cần bật `AUTH_ENABLED = True` trong `settings.py`.
2. **Bảo tồn dữ liệu hiện có (`dist/it_errors.db`):**
   - Database hiện hữu chứa 53 sự cố. Module `database/` tự động nhận diện đúng file DB thực tế, bảo toàn mọi dữ liệu.
3. **Tách rời Excel Exporter:**
   - Độc lập 100% khỏi cơ sở dữ liệu và giao diện, nhận dữ liệu thuần dạng dict/list để xuất bảng Excel chuẩn.
4. **Clean Code & Khắc phục cú pháp nén:**
   - Loại bỏ hoàn toàn cú pháp viết tắt và dấu `;`, phân tách phương thức theo Single Responsibility Principle (SRP).

---

## 4. Danh sách nhiệm vụ (Task Breakdown)

### Giai đoạn 1: Nền tảng cấu hình, Kết nối DB & Dịch vụ nghiệp vụ (Foundation & Services)
- [ ] **Task 1:** Tạo `requirements.txt` và module cấu hình `config/settings.py` (với `AUTH_ENABLED = False`), `config/constants.py`.
- [ ] **Task 2:** Tách lớp cơ sở dữ liệu `database/connection.py` và `database/schema.py` an toàn với DB hiện hữu.
- [ ] **Task 3:** Triển khai `session_service.py` (kiến trúc mở rộng cho Auth) cùng `incident_service.py` và `hmi_service.py`.
- [ ] **Task 4:** Tách module xuất báo cáo Excel sang `services/export_service.py`.
- [ ] **Task 5:** Viết bộ kiểm thử tự động (Unit Tests) trong thư mục `tests/` kiểm thử 100% logic dịch vụ.

> **Checkpoint 1:** Toàn bộ test suite chạy thành công (`python -m unittest discover tests`), dữ liệu 53 sự cố được đọc chính xác, logic export Excel tạo file hoàn hảo.

---

### Giai đoạn 2: Thành phần giao diện dùng lại & Hộp thoại (UI Components & Dialogs)
- [ ] **Task 6:** Xây dựng module phong cách giao diện `ui/styles.py` và các Reusable UI Components: `StatCard`, `DateTimePicker`, `DataTable`.
- [ ] **Task 7:** Tái cấu trúc hộp thoại thêm/sửa sự cố `ui/dialogs/incident_dialog.py` sử dụng các Reusable Components.

> **Checkpoint 2:** Chạy thử nghiệm độc lập các component và dialog, đảm bảo giao diện đẹp, đồng bộ phong cách, tương tác mượt mà.

---

### Giai đoạn 3: Tách Views, Hoàn thiện ứng dụng & Đóng gói (Views & Production Assembly)
- [ ] **Task 8:** Xây dựng các View độc lập: `HeaderView` (với bộ chọn User linh hoạt), `DashboardView`, `DetailView`, `HmiView`, và `LoginView` (chế độ chờ mở rộng).
- [ ] **Task 9:** Tái cấu trúc `main.py` mở thẳng giao diện làm việc chính, kết nối mượt mà các views và quản lý ngoại lệ an toàn.
- [ ] **Task 10:** Cập nhật file đóng gói `IT_Error_Logger_v2.spec`, dọn dẹp file cũ không cần thiết và tạo tài liệu kiến trúc `README.md`.

> **Checkpoint 3 (Final):** Chạy kiểm thử toàn bộ luồng nghiệp vụ không cần đăng nhập: Mở app -> Xem Dashboard -> Thêm/Sửa/Xóa sự cố -> Lọc ngày -> Lưu HMI -> Xuất Excel -> Kiểm tra build exe.

---

## 5. Rủi ro & Giải pháp giảm thiểu (Risks & Mitigations)

| Rủi ro | Mức độ | Biện pháp giảm thiểu |
|---|---|---|
| Mất mát dữ liệu trong `dist/it_errors.db` | Cao | Đã tạo git tag khôi phục `restore-point-20261101`. Schema sử dụng `CREATE TABLE IF NOT EXISTS`. |
| Người dùng cần bật lại đăng nhập trong tương lai | Thấp | Cung cấp sẵn cờ `AUTH_ENABLED` trong `config/settings.py` và kiến trúc `SessionService` có thể cắm `LoginView` ngay lập tức. |
| Thư viện bên ngoài thiếu (openpyxl, tkcalendar) | Thấp | Khai báo trong `requirements.txt` và bắt lỗi import thân thiện. |
| Đường dẫn file khi đóng gói PyInstaller bị sai | Trung bình | `settings.py` xử lý chuẩn cả 2 môi trường: chạy script và chạy binary `.exe` (`sys.frozen`). |
