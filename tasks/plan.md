# Kế Hoạch Nâng Cấp: Lọc Sự Cố Hôm Nay, Xuất Sheet Excel Hàng Tháng & Tab Daily Inspection

## 1. Tổng quan (Overview)
Kế hoạch này thực hiện 4 yêu cầu cải tiến lớn của người dùng sau quá trình phỏng vấn chi tiết (`/grill-me`):
1. **Lọc mặc định sự cố trong ngày hôm nay tại Tab Detail:** Mở ứng dụng chỉ hiển thị các sự cố phát sinh trong ngày hôm nay; chỉ hiển thị danh sách mở rộng khi người dùng bấm "Lọc" theo khoảng ngày hoặc chọn "Xem tất cả".
2. **Cơ chế xuất Shift Report vào Tab mới trong file Excel tổng hợp (Hình 1, 2, 3):** Không xuất ra từng file đơn lẻ mà tự động mở/tạo file tháng `D:\Report\<Năm>\<Tháng>\Shift report <MM-YYYY>.xlsx` và ghi thêm tab theo định dạng chuẩn `DD-Mon-YYYY (Shift 1)` hoặc `DD-Mon-YYYY (Shift 2)`. Nếu tab đã có thì cập nhật lại tab đó.
3. **Chuẩn hóa cấu trúc Sheet Shift Report giống 100% Hình 1 & 2:**
   - Cập nhật dòng phòng ban: `Sect.: Dx Engineering Team`, nhóm trực `Group: B` (hoặc lấy từ Header).
   - Chuẩn hóa lại số thứ tự dòng (Detail từ dòng 19, Header bảng dòng 20, dữ liệu dòng 21-39).
   - Phần HMI Checking đóng khung từ dòng 41-48, gộp cột E:F cho `Application Link` và G:H cho `Remark`.
4. **Tích hợp Tab mới "4. Daily Inspection" trên giao diện & xuất Excel (Hình 4):**
   - Thêm tab `📋 4. Daily Inspection` trên giao diện Tkinter.
   - Hiển thị bảng lưới 24 khung giờ (Ca 1: 8h-20h, Ca 2: 20h-8h) cho toàn bộ danh mục kiểm tra (Server, Storage, Network, UPS, Air condition, Môi trường, PCCC, An ninh).
   - Nút tiện ích `⚡ Tạo dữ liệu mặc định hôm nay` (điền sẵn 22°C, 46%, tất cả V, tên người trực).
   - Lưu vào SQLite và nút `📤 Xuất Daily Inspection ra Excel` để ghi thêm tab ngày `DD-MM-YYYY` vào file `D:\Report\<Năm>\<Tháng>\Daily inspection <MM-YYYY>.xlsx`.

---

## 2. Kiến trúc và Luồng dữ liệu (Architecture & Data Flow)

```
[UI Views]
  ├── HeaderView (Dept, Date, Shift, Group, Operator)
  ├── DetailView (Mặc định hiển thị TODAY -> Lọc theo ngày -> Nút Xuất Excel vào Master File)
  ├── HmiView (Kiểm tra kết nối 6 chuyền)
  └── DailyInspectionView (MỚI: Bảng 24 mốc giờ, nút fill mặc định, Lưu DB & Xuất Excel)
        │
[Services Layer]
  ├── incident_service.py (Hỗ trợ get_today_incidents, query date range)
  ├── daily_inspection_service.py (MỚI: CRUD kiểm tra định kỳ 24 mốc giờ)
  └── export_service.py (NÂNG CẤP: Ghi tab vào file Excel có sẵn, format chuẩn Hình 1-2 & Hình 4)
        │
[File System Storage]
  └── D:\Report\<Năm>\<Tháng>\
        ├── Shift report <MM-YYYY>.xlsx       (Chứa các tab: 29-Oct-2026 (Shift 1), 29-Oct-2026 (Shift 2)...)
        └── Daily inspection <MM-YYYY>.xlsx   (Chứa các tab: 19-10-2026, 20-10-2026, ..., 29-10-2026...)
```

---

## 3. Quyết định kỹ thuật (Architecture Decisions)

1. **Quản lý file Excel Master (Openpyxl Workbook Append/Update):**
   - Kiểm tra file Excel tháng có tồn tại không. Nếu có, mở bằng `openpyxl.load_workbook(filepath)`. Nếu chưa, tạo `Workbook()` mới.
   - Nếu sheet tab (`29-Oct-2026 (Shift 1)` hoặc `29-10-2026`) đã tồn tại, xóa sheet cũ đó và tạo lại sheet mới cùng tên để đảm bảo dữ liệu luôn được làm mới nguyên vẹn.
   - Thư mục đích `D:\Report\<Năm>\<Tháng>` được tạo tự động nếu chưa có.
2. **Cấu trúc Tab Shift Report (Hình 1 - 2):**
   - Section: `Sect.: Dx Engineering Team`.
   - Title: `Shift Report` (E1), Subtitle: `(DD-Mon-YYYY)` (E2).
   - Bảng 2. Detail: Header ở dòng 20, các mục chuẩn từ dòng 21 đến 39 (có mục `Remark` ở dòng 39).
   - Bảng 3. HMI Checking: Header ở dòng 41-42, các chuyền PCM -> CLTS ở dòng 43-48, gộp cột E:F (`Application Link`) và G:H (`Remark`).
3. **Cấu trúc Tab Daily Inspection (Hình 4):**
   - 28 hạng mục kiểm tra x 24 cột giờ (8:00 -> 7:00).
   - Tầng database lưu dữ liệu dưới dạng JSON hoặc bảng key-value theo ngày để việc đọc/ghi cực kỳ linh hoạt, nhanh chóng và không làm cồng kềnh database.
4. **Mặc định hiển thị sự cố hôm nay:**
   - Trong `DetailView`, khi khởi động gọi hàm `load_today_incidents()`.
   - Giữ lại nút `🔍 Lọc` và `↺ Xem tất cả` để người dùng linh hoạt xem lịch sử.

---

## 4. Phân đoạn nhiệm vụ (Task Breakdown)

### Giai đoạn 1: Lọc sự cố hôm nay & Cải tiến Exporter Shift Report theo tab (Hình 1, 2, 3)
- [x] **Task 1:** Điều chỉnh `DetailView` và `incident_service` để mặc định chỉ tải sự cố của ngày hôm nay.
- [x] **Task 2:** Cập nhật cấu trúc bố cục xuất Shift Report khớp 100% Hình 1 & 2 (`Sect.: Dx Engineering Team`, dòng 19-48, gộp cột HMI).
- [x] **Task 3:** Nâng cấp `export_service.py` để xuất/cập nhật tab vào file tổng `D:\Report\<Năm>\<Tháng>\Shift report <MM-YYYY>.xlsx`.
- [x] **Checkpoint 1:** Kiểm tra mở tab Detail chỉ thấy sự cố hôm nay; kiểm tra xuất Excel ghi thành công tab vào file Shift report tháng.

### Giai đoạn 2: Dịch vụ & Giao diện Tab Daily Inspection (Hình 4)
- [x] **Task 4:** Xây dựng `services/daily_inspection_service.py` quản lý dữ liệu kiểm tra 24 mốc giờ và hàm xuất Excel sheet Daily inspection.
- [x] **Task 5:** Xây dựng giao diện `ui/views/daily_inspection_view.py` với bảng 24 cột giờ, nút `⚡ Tạo dữ liệu mặc định`, nút lưu và nút xuất Excel.
- [x] **Task 6:** Tích hợp `DailyInspectionView` vào `main.py` làm Tab thứ 4 (`📋 4. Daily Inspection`).
- [x] **Checkpoint 2:** Mở app, thao tác trên Tab Daily Inspection, tạo mặc định, lưu vào DB và xuất tab Excel thành công vào file `Daily inspection MM-YYYY.xlsx`.

### Giai đoạn 3: Kiểm thử toàn diện & Hoàn thiện
- [x] **Task 7:** Viết Unit Tests cho các tính năng mới trong `tests/` (test lọc ngày hôm nay, test ghi tab file Excel có sẵn, test daily inspection).
- [x] **Task 8:** Cập nhật tài liệu `README.md`, đồng bộ Git repository lên GitHub.
- [x] **Checkpoint 3 (Final):** Chạy toàn bộ 100% tests pass, kiểm tra giao diện thực tế và cấu trúc các file Excel sinh ra.
