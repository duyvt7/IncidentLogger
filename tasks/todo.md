# Danh Sách Nhiệm Vụ Tái Cấu Trúc Dự Án (Todo List)

## Giai đoạn 1: Nền tảng, Cấu hình & Dịch vụ (Foundation & Services)

### Task 1: Thiết lập cấu hình tập trung và định nghĩa dependencies
- [x] Tạo file `requirements.txt` với các thư viện: `openpyxl`, `tkcalendar`, `babel`.
- [x] Tạo `config/settings.py` chứa hàm xác định đường dẫn ứng dụng, đường dẫn DB (hỗ trợ cả môi trường script và PyInstaller frozen), cấu hình cửa sổ, cờ cấu hình `AUTH_ENABLED = False`, và cấu hình logging.
- [x] Tạo `config/constants.py` chứa toàn bộ hằng số nghiệp vụ: `DETAIL_STRUCTURE`, `HMI_LINES`, `HMI_COLS`, `CURRENT_SITUATION_OPTIONS`, danh sách kỹ sư trực mặc định (`DEFAULT_OPERATORS`), bảng mã màu UI (`BG`, `CARD_BG`, `PRIMARY`, v.v.), font chữ.
- **Acceptance criteria:**
  - [x] `config/settings.py` resolve chính xác đường dẫn file DB `dist/it_errors.db` hoặc thư mục gốc.
  - [x] `config/constants.py` gom toàn bộ hằng số từ `main.py` và `database.py` về một nơi duy nhất.
- **Verification:**
  - [x] Chạy script kiểm tra import và in ra đường dẫn DB hợp lệ: `python -c "from config.settings import get_db_path; print(get_db_path())"`
- **Dependencies:** None
- **Files touched:** `requirements.txt`, `config/__init__.py`, `config/settings.py`, `config/constants.py`
- **Scope:** Small (3-4 files)

---

### Task 2: Tách module kết nối và schema cơ sở dữ liệu
- [x] Tạo `database/connection.py` cung cấp context manager `get_connection()` an toàn với `sqlite3.Row`, tự động commit/rollback và đóng kết nối.
- [x] Tạo `database/schema.py` chứa hàm `init_db()` định nghĩa cấu trúc bảng: `incidents`, `hmi_monitoring`, `daily_inspection`, `users`, đảm bảo `IF NOT EXISTS` và bảo tồn dữ liệu cũ.
- **Acceptance criteria:**
  - [x] Không làm mất bất kỳ bản ghi nào trong `dist/it_errors.db`.
  - [x] Kết nối được quản lý an toàn qua context manager, không rò rỉ connection.
- **Verification:**
  - [x] Chạy kiểm tra kết nối và đếm số lượng bản ghi: `python -c "from database.connection import get_connection; from database.schema import init_db; init_db(); conn = get_connection(); print(conn.execute('SELECT COUNT(*) FROM incidents').fetchone()[0])"` trả về 53.
- **Dependencies:** Task 1
- **Files touched:** `database/__init__.py`, `database/connection.py`, `database/schema.py`
- **Scope:** Small (3 files)

---

### Task 3: Triển khai Session Service (Extensible Auth) & Domain Services
- [x] Tạo `services/session_service.py`: quản lý thông tin phiên làm việc của người trực hiện tại (`current_operator`), cung cấp interface trừu tượng `AuthBackend` để khi cần bật login trong tương lai chỉ cần implement mà không sửa UI/service khác.
- [x] Tạo `services/incident_service.py`: các hàm CRUD (`add_incident`, `get_incidents`, `get_incident_by_id`, `update_incident`, `delete_incident`, `get_incident_statistics`).
- [x] Tạo `services/hmi_service.py`: lưu và tải trạng thái HMI (`save_hmi_status`, `load_hmi_status`).
- **Acceptance criteria:**
  - [x] `session_service` cung cấp phương thức lấy và đổi operator hiện tại dễ dàng.
  - [x] Các hàm nghiệp vụ trả về đối tượng dữ liệu rõ ràng (dict/dataclass), có type hinting và docstrings.
- **Verification:**
  - [x] Viết script kiểm tra session và truy vấn danh sách sự cố thành công.
- **Dependencies:** Task 2
- **Files touched:** `services/__init__.py`, `services/session_service.py`, `services/incident_service.py`, `services/hmi_service.py`
- **Scope:** Medium (4 files)

---

### Task 4: Tách và chuẩn hóa Export Service (Excel)
- [x] Tạo `services/export_service.py` tách toàn bộ logic xuất Excel từ `database.py`.
- [x] Chuẩn hóa hàm `export_shift_report_to_excel(filepath, ...)`, tách nhỏ logic format header, environment, hardware inspection, facility, incidents, và HMI checking.
- [x] Xử lý ngoại lệ thân thiện khi thiếu thư viện `openpyxl` hoặc file bị khóa bởi ứng dụng khác (PermissionError).
- **Acceptance criteria:**
  - [x] File Excel xuất ra giữ nguyên 100% bố cục và định dạng giống file cũ của `Shift_Report_Full_Format.xlsx`.
  - [x] Xử lý trường hợp ghi đè an toàn khi file Excel đang mở.
- **Verification:**
  - [x] Chạy test xuất file Excel ra thư mục tạm và xác nhận file tồn tại và mở được.
- **Dependencies:** Task 1, Task 3
- **Files touched:** `services/export_service.py`
- **Scope:** Small (1 file)

---

### Task 5: Viết bộ kiểm thử tự động (Unit Tests) cho Services & Database
- [x] Tạo thư mục `tests/` với các test case:
  - `tests/test_database.py`: Kiểm thử kết nối và schema.
  - `tests/test_session_service.py`: Kiểm thử quản lý session và extension points.
  - `tests/test_incident_service.py`: Kiểm thử thêm/sửa/xóa/lọc sự cố.
  - `tests/test_export_service.py`: Kiểm thử xuất file Excel.
- **Acceptance criteria:**
  - [x] 100% các unit test chạy độc lập trên cơ sở dữ liệu bộ nhớ (in-memory SQLite `:memory:`) không làm ảnh hưởng đến dữ liệu thực tế.
  - [x] Mọi test pass 100%.
- **Verification:**
  - [x] Chạy lệnh `python -m unittest discover tests` thành công (0 failure, 0 error).
- **Dependencies:** Task 1, Task 2, Task 3, Task 4
- **Files touched:** `tests/__init__.py`, `tests/test_database.py`, `tests/test_session_service.py`, `tests/test_incident_service.py`, `tests/test_export_service.py`
- **Scope:** Medium (5 files)

---

### 🏁 Checkpoint 1: Xác nhận tầng Foundation & Services
- [x] Tất cả các bài kiểm tra tự động `python -m unittest discover tests` đều PASSED.
- [x] Dữ liệu 53 sự cố trong `dist/it_errors.db` được bảo toàn nguyên vẹn.
- [x] Không còn bất kỳ mã nghiệp vụ hay export nào bị phụ thuộc lỏng lẻo.

---

## Giai đoạn 2: Reusable UI Components & Dialogs

### Task 6: Xây dựng UI Theme và Reusable UI Components
- [x] Tạo `ui/styles.py` cấu hình ttk.Style đồng bộ (Theme clam, Treeview styling, Notebook tab styling, combobox styling).
- [x] Tạo `ui/components/stat_card.py`: Widget hiển thị thẻ KPI/thống kê (Title, Value, Accent Color, Icon).
- [x] Tạo `ui/components/date_time_picker.py`: Widget chọn kết hợp DateEntry + Giờ + Phút có validation và method `get_datetime()`, `set_datetime()`.
- [x] Tạo `ui/components/data_table.py`: Bảng Treeview bọc sẵn thanh cuộn dọc/ngang, cấu hình cột tự động, bắt sự kiện click/double-click.
- **Acceptance criteria:**
  - [x] Các component kế thừa `tk.Frame` hoặc `ttk.Frame`, dễ dàng tái sử dụng ở bất kỳ view nào.
  - [x] Cung cấp API rõ ràng (`get_value()`, `set_value()`, `bind_event()`).
- **Verification:**
  - [x] Kiểm tra tạo component trong script test GUI mà không phát sinh lỗi.
- **Dependencies:** Task 1
- **Files touched:** `ui/__init__.py`, `ui/styles.py`, `ui/components/__init__.py`, `ui/components/stat_card.py`, `ui/components/date_time_picker.py`, `ui/components/data_table.py`
- **Scope:** Medium (5 files)

---

### Task 7: Tái cấu trúc IncidentDialog sử dụng Reusable Components
- [x] Tạo `ui/dialogs/incident_dialog.py` kế thừa `tk.Toplevel`.
- [x] Sử dụng `DateTimePicker` cho trường chọn thời gian.
- [x] Xây dựng form nhập liệu với các input rõ ràng, xử lý combobox category -> sub_category đồng bộ tự động.
- [x] Tự động gán người báo cáo (`reporter`) mặc định từ session hiện tại.
- [x] Validate dữ liệu đầu vào (báo lỗi nếu thiếu Failure hoặc thời gian không hợp lệ) trước khi gọi `incident_service`.
- **Acceptance criteria:**
  - [x] Hộp thoại hỗ trợ cả 2 chế độ: Thêm mới (`edit_id=None`) và Cập nhật (`edit_id=<id>`).
  - [x] Hiển thị thông báo thân thiện và tự động đóng dialog + kích hoạt callback reload sau khi lưu thành công.
- **Verification:**
  - [x] Mở dialog ở chế độ test thêm và sửa sự cố.
- **Dependencies:** Task 3, Task 6
- **Files touched:** `ui/dialogs/__init__.py`, `ui/dialogs/incident_dialog.py`
- **Scope:** Small (2 files)

---

### 🏁 Checkpoint 2: Xác nhận tầng Component & Dialog
- [x] Reusable components hoạt động độc lập và hiển thị phong cách phẳng hiện đại.
- [x] `IncidentDialog` mở lên, hiển thị đúng dữ liệu sự cố và lưu vào DB chính xác.

---

## Giai đoạn 3: Views, Controller & Hoàn thiện Production

### Task 8: Xây dựng các View chuyên biệt (Modular Views)
- [x] Tạo `ui/views/header_view.py`: Thanh Header chứa thông tin ca trực (Dept, Date, Shift, User selector dạng dropdown danh sách nhân sự trực).
- [x] Tạo `ui/views/dashboard_view.py`: Hiển thị số liệu thống kê (Total incidents, hôm nay, sự cố mở) qua `StatCard`.
- [x] Tạo `ui/views/detail_view.py`: Quản lý danh sách sự cố qua `DataTable`, thanh lọc ngày, nút Thêm/Sửa/Xóa và nút Xuất Excel.
- [x] Tạo `ui/views/hmi_view.py`: Bảng lưới theo dõi các chuyền HMI, có nút lưu trạng thái vào database qua `hmi_service`.
- [x] Tạo `ui/views/login_view.py`: (Sẵn sàng mở rộng) Khung đăng nhập hoàn chỉnh được đóng gói độc lập để khi cần bật lại chỉ việc kích hoạt từ `settings.AUTH_ENABLED = True`.
- **Acceptance criteria:**
  - [x] Mỗi View là một Frame độc lập, nhận callbacks và services qua dependency injection.
  - [x] Ứng dụng chạy trực tiếp vào các tab chính mà không bị chặn bởi màn hình login.
  - [x] Code sạch, không còn cú pháp nén `;`, có docstring mô tả công dụng.
- **Verification:**
  - [x] Từng view có thể khởi tạo độc lập và hiển thị đầy đủ các thành phần.
- **Dependencies:** Task 6, Task 7
- **Files touched:** `ui/views/__init__.py`, `ui/views/header_view.py`, `ui/views/dashboard_view.py`, `ui/views/detail_view.py`, `ui/views/hmi_view.py`, `ui/views/login_view.py`
- **Scope:** Medium (6 files)

---

### Task 9: Tái cấu trúc Application Controller và main.py
- [x] Tái cấu trúc `main.py`:
  - Khởi tạo ứng dụng `ITIncidentApp(tk.Tk)`.
  - Mở trực tiếp không gian làm việc chính (HeaderView + Notebook các tabs: Dashboard, 2. Detail, 3. HMI Checking).
  - Tích hợp hook kiểm tra `AUTH_ENABLED`: nếu `True` mới hiện login, nếu `False` vào thẳng app (khả năng mở rộng tối đa).
  - Khởi tạo cấu hình logging để ghi lại các lỗi chưa xử lý.
  - Tích hợp icon ứng dụng `app_icon.ico`.
- **Acceptance criteria:**
  - [x] `main.py` chỉ còn khoảng 60-80 dòng code sạch, vai trò điều phối ứng dụng.
  - [x] Vào ứng dụng ngay lập tức, chuyển tab, lưu dữ liệu, xuất Excel mượt mà.
- **Verification:**
  - [x] Khởi chạy `python main.py`, kiểm tra đầy đủ mọi tính năng.
- **Dependencies:** Task 8
- **Files touched:** `main.py`
- **Scope:** Small (1-2 files)

---

### Task 10: Tinh chỉnh PyInstaller Spec và Tài liệu hóa kiến trúc
- [x] Cập nhật file spec PyInstaller `IT_Error_Logger_v2.spec` để nhận diện cấu trúc thư mục mới (`config/`, `database/`, `services/`, `ui/`), icon và hidden imports (`openpyxl`, `tkcalendar`, `babel`).
- [x] Tạo tài liệu hướng dẫn dự án `README.md` giải thích chi tiết cấu trúc thư mục, chức năng từng module, cách mở rộng tính năng đăng nhập sau này (`AUTH_ENABLED`), cách cài đặt và build file exe.
- **Acceptance criteria:**
  - [x] File spec tương thích với cấu trúc mã nguồn mới.
  - [x] Tài liệu `README.md` mô tả rõ ràng cách bật lại tính năng Auth khi cần.
- **Verification:**
  - [x] Kiểm tra PyInstaller phân tích spec thành công: `pyinstaller --dry-run IT_Error_Logger_v2.spec` (hoặc kiểm tra cú pháp spec).
- **Dependencies:** Task 9
- **Files touched:** `IT_Error_Logger_v2.spec`, `README.md`
- **Scope:** Small (2 files)

---

### 🏁 Checkpoint 3 (Final): Kiểm tra toàn diện sẵn sàng Production
- [x] Tất cả unit tests đều PASS.
- [x] Ứng dụng mở trực tiếp không cần đăng nhập: Dashboard -> Quản lý sự cố -> Kiểm tra HMI -> Xuất báo cáo Excel.
- [x] Dữ liệu 53 bản ghi cũ không bị biến đổi bất thường.
- [x] Khả năng mở rộng Auth sẵn sàng: chỉ cần cấu hình `AUTH_ENABLED = True` là có thể tích hợp luồng đăng nhập mà không vỡ ứng dụng.
- [x] Code sạch, rõ ràng, không còn cú pháp nén và có đầy đủ docstring mô tả công dụng từng module.
