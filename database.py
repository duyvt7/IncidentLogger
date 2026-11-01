"""
Database module for IT Error Logger
Updated to match Shift_Report_Full_Format.xlsx structure
"""
import sqlite3
import csv
import os
from datetime import datetime
from pathlib import Path

import sys

def get_db_path():
    # 1. Nếu chạy từ file .exe, ưu tiên file nằm cạnh file .exe
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        if (exe_dir / "it_errors.db").exists():
            return exe_dir / "it_errors.db"
    
    # 2. Kiểm tra ở thư mục gốc của code
    root_dir = Path(__file__).parent
    if (root_dir / "it_errors.db").exists():
        return root_dir / "it_errors.db"
        
    # 3. Kiểm tra trong thư mục dist (nếu lỡ để ở đó)
    dist_dir = root_dir / "dist"
    if (dist_dir / "it_errors.db").exists():
        return dist_dir / "it_errors.db"
    
    # 4. Mặc định tạo ở thư mục gốc của code
    return root_dir / "it_errors.db"

DB_PATH = get_db_path()

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Bảng Sự cố (Incidents) - khớp với cột "2. Detail" trong Excel
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            time             TEXT    NOT NULL,
            category         TEXT    NOT NULL,
            sub_category     TEXT,
            failure          TEXT    NOT NULL,
            reason           TEXT,
            solution         TEXT,
            current_situation TEXT,
            contact          TEXT,
            reporter         TEXT,
            shift            TEXT,
            created_at       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)
    
    # Bảng HMI Monitoring
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hmi_monitoring (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            line             TEXT    NOT NULL,
            mes_link_scc     TEXT,
            scc_link_plc     TEXT,
            app_link         TEXT,
            remark           TEXT,
            check_date       TEXT    NOT NULL DEFAULT (date('now'))
        )
    """)

    # Bảng Daily Inspection
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_inspection (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name        TEXT    NOT NULL,
            time_slot        TEXT    NOT NULL,
            status           TEXT    NOT NULL,
            check_date       TEXT    NOT NULL DEFAULT (date('now'))
        )
    """)
    
    # Bảng Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    
    # Chỉ tạo user mặc định nếu bảng users đang trống
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            ("admin", "admin123"),
            ("Hoàng Ngọc Huy", "123"),
            ("Nguyễn Mai Nghĩa", "123"),
            ("Vũ Thành Duy", "123"),
            ("Võ Đình Thủy", "123"),
        ]
        for uname, pwd in default_users:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (uname, pwd))
    
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users ORDER BY username")
    rows = cursor.fetchall()
    conn.close()
    return [r['username'] for r in rows]

def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True, "Tạo user thành công!"
    except Exception as e:
        conn.close()
        return False, f"Lỗi: {e}"

def update_user_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()
    return True, "Đã cập nhật mật khẩu."

def delete_user(username):
    if username == 'admin':
        return False, "Không thể xóa user admin!"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return True, "Đã xóa user."


# --- Incident Logic ---
def add_incident(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO incidents 
        (time, category, sub_category, failure, reason, solution, current_situation, contact, reporter, shift)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data['time'], data['category'], data.get('sub_category'), data['failure'], 
          data.get('reason'), data.get('solution'), data.get('current_situation'), 
          data.get('contact'), data.get('reporter'), data.get('shift')))
    conn.commit()
    conn.close()

def get_incidents(search="", start_date=None, end_date=None, current_user=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM incidents WHERE 1=1"
    params = []
    
    # Quyền riêng tư: User chỉ thấy lỗi của mình, admin thấy hết
    if current_user and current_user != 'admin':
        query += " AND reporter = ?"
        params.append(current_user)
        
    if search:
        query += " AND (failure LIKE ? OR reason LIKE ? OR contact LIKE ?)"
        lk = f"%{search}%"
        params.extend([lk, lk, lk])
        
    if start_date and end_date:
        query += " AND SUBSTR(time, 1, 10) BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    elif start_date:
        query += " AND SUBSTR(time, 1, 10) >= ?"
        params.append(start_date)
    elif end_date:
        query += " AND SUBSTR(time, 1, 10) <= ?"
        params.append(end_date)
        
    query += " ORDER BY time DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_incident_by_id(iid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents WHERE id = ?", (iid,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_incident(iid, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE incidents SET
            time = ?, category = ?, sub_category = ?, failure = ?,
            reason = ?, solution = ?, current_situation = ?, contact = ?
        WHERE id = ?
    """, (data['time'], data['category'], data.get('sub_category'), data['failure'],
          data.get('reason'), data.get('solution'), data.get('current_situation'),
          data.get('contact'), iid))
    conn.commit()
    conn.close()

def delete_incident(iid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM incidents WHERE id = ?", (iid,))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    stats = {}
    cursor.execute("SELECT COUNT(*) FROM incidents")
    stats['total'] = cursor.fetchone()[0]
    cursor.execute("SELECT category, COUNT(*) FROM incidents GROUP BY category")
    stats['by_category'] = cursor.fetchall()
    conn.close()
    return stats

def export_to_excel(filepath, dept="IT", section="IT Management", 
                    prepared_by="", group="", shift="",
                    incidents=None, inspection_data=None, hmi_data=None):
    """Export to Excel matching Shift_Report_Full_Format.xlsx layout."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    except ImportError:
        return False, "openpyxl chưa được cài đặt"
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Shift Report"
    
    # Column widths matching original
    ws.column_dimensions['A'].width = 5
    ws.column_dimensions['B'].width = 19
    ws.column_dimensions['C'].width = 29
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 25
    ws.column_dimensions['H'].width = 20
    ws.column_dimensions['I'].width = 16
    ws.column_dimensions['J'].width = 20
    
    # Styles
    header_font = Font(name="Calibri", size=14, bold=True)
    bold_font = Font(name="Calibri", size=11, bold=True)
    normal_font = Font(name="Calibri", size=11)
    header_fill = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_align = Alignment(horizontal='left', vertical='top', wrap_text=True)
    
    # ── Row 1-3: Header ──
    ws.merge_cells('B1:C1')
    ws.merge_cells('E1:J3')
    ws['E1'] = "Shift Report"
    ws['E1'].font = header_font
    ws['E1'].alignment = center_align
    
    ws.merge_cells('B2:C2')
    ws['B2'] = f"Dept.: {dept}"
    ws['B2'].alignment = Alignment(horizontal='left')
    
    ws.merge_cells('B3:C3')
    ws['B3'] = f"Sect.: {section}"
    ws['B3'].alignment = Alignment(horizontal='left')
    
    # Row 4-5
    ws['B4'] = f"Prepared by: {prepared_by}"
    ws['B5'] = f"Group: {group}"
    
    # ── Row 6-18: General Task Description ──
    ws.merge_cells('B6:J18')
    ws['B6'] = (
        "1. General Task Description:\n"
        "- Make a roll call of the computer room\n"
        "- Monitor status lights of Hardware Attention and Fault\n"
        "- Monitoring for Servers, Switch, Router, MES PC, MES Printer\n"
        "- Report after shift about status and any problem in Shift\n"
        "- Check Environment and all equipments in Server Room\n"
        "- Stop/Start Server and equipment when PoscoCenter order\n"
        "- Check equipment 2hours/time and Clean equipment 01 time/month\n"
        "- Managing\n"
        "+ Restore and backup OS System\n"
        "+ Hardware error\n"
        "+ Visitor\n"
        "+ Equipment In/out\n"
        "+ Improve IT Device in IT Room (Server, UPS)\n"
        "+ Control equipment in IT Warehouse in Server Room."
    )
    ws['B6'].alignment = left_align
    ws['B6'].font = normal_font
    
    # ── Row 20: "2. Detail" ──
    ws.merge_cells('B20:J20')
    ws['B20'] = "2. Detail"
    ws['B20'].font = bold_font
    
    # ── Row 21: Detail Headers ──
    detail_headers = {
        'B': 'Category', 'D': 'Time', 'E': 'Failure', 'F': 'Reason',
        'G': 'Solution', 'H': 'Current Situation', 'I': 'Contact Number'
    }
    ws.merge_cells('B21:C21')
    for col, text in detail_headers.items():
        cell = ws[f'{col}21']
        cell.value = text
        cell.font = bold_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    # Also border C21
    ws['C21'].border = thin_border
    ws['C21'].fill = header_fill
    
    # ── Row 22-23: Indoor Environment ──
    ws.merge_cells('B22:B23')
    ws['B22'] = "Indoor Environment"
    ws['B22'].font = bold_font
    ws['B22'].fill = header_fill
    ws['B22'].alignment = center_align
    ws['B22'].border = thin_border
    
    env_items = [
        (22, "Standard Temperature (19 - 25)", inspection_data.get('temperature', '22℃') if inspection_data else '22℃'),
        (23, "Standard Humidity (35 - 55)", inspection_data.get('humidity', '46%') if inspection_data else '46%'),
    ]
    for row_n, label, val in env_items:
        ws[f'C{row_n}'] = label
        ws[f'C{row_n}'].font = bold_font
        ws[f'C{row_n}'].fill = header_fill
        ws[f'C{row_n}'].border = thin_border
        ws[f'H{row_n}'] = val
        ws[f'H{row_n}'].font = normal_font
        ws[f'H{row_n}'].border = thin_border
        for c in ['D', 'E', 'F', 'G', 'I']:
            ws[f'{c}{row_n}'].border = thin_border
    
    # ── Row 24-32: H/W Inspection ──
    ws.merge_cells('B24:B32')
    ws['B24'] = "H/W Inspection"
    ws['B24'].font = bold_font
    ws['B24'].fill = header_fill
    ws['B24'].alignment = center_align
    ws['B24'].border = thin_border
    
    hw_items = [
        "MES Server", "CLTS Server", "HMI Server", "MES PC",
        "CLTS PC", "HMI PC", "MES Printer", "Storage", "Network"
    ]
    for i, item in enumerate(hw_items):
        row_n = 24 + i
        ws[f'C{row_n}'] = item
        ws[f'C{row_n}'].font = bold_font
        ws[f'C{row_n}'].fill = header_fill
        ws[f'C{row_n}'].border = thin_border
        status = "Running normal"
        if inspection_data and item in inspection_data:
            status = inspection_data[item]
        ws[f'H{row_n}'] = status
        ws[f'H{row_n}'].font = normal_font
        ws[f'H{row_n}'].border = thin_border
        for c in ['D', 'E', 'F', 'G', 'I']:
            ws[f'{c}{row_n}'].border = thin_border
    
    # ── Row 33-36: Facility Inspection ──
    ws.merge_cells('B33:B36')
    ws['B33'] = "Facility Inspection"
    ws['B33'].font = bold_font
    ws['B33'].fill = header_fill
    ws['B33'].alignment = center_align
    ws['B33'].border = thin_border
    
    facility_items = [
        (33, "UPS", "Running normal"),
        (34, "Air conditioning", "None"),
        (35, "Fire, leaks", "OK"),
        (36, "Fire extinguisher", "OK"),
    ]
    for row_n, label, default_val in facility_items:
        ws[f'C{row_n}'] = label
        ws[f'C{row_n}'].font = bold_font
        ws[f'C{row_n}'].fill = header_fill
        ws[f'C{row_n}'].border = thin_border
        val = default_val
        if inspection_data and label in inspection_data:
            val = inspection_data[label]
        ws[f'H{row_n}'] = val
        ws[f'H{row_n}'].font = normal_font
        ws[f'H{row_n}'].border = thin_border
        for c in ['D', 'E', 'F', 'G', 'I']:
            ws[f'{c}{row_n}'].border = thin_border
    
    # ── Row 37: Security Inspection ──
    ws['B37'] = "Security Inspection"
    ws['B37'].font = bold_font
    ws['B37'].fill = header_fill
    ws['B37'].border = thin_border
    ws['C37'] = "Locks (doors & windows)"
    ws['C37'].font = bold_font
    ws['C37'].fill = header_fill
    ws['C37'].border = thin_border
    ws['H37'] = inspection_data.get('Locks (doors & windows)', 'OK') if inspection_data else 'OK'
    ws['H37'].border = thin_border
    for c in ['D', 'E', 'F', 'G', 'I']:
        ws[f'{c}37'].border = thin_border
    
    # ── Row 38: MES Server Backup ──
    ws.merge_cells('B38:C38')
    ws['B38'] = "MES Server Backup"
    ws['B38'].font = bold_font
    ws['B38'].fill = header_fill
    ws['B38'].border = thin_border
    ws['C38'].border = thin_border
    ws['H38'] = inspection_data.get('MES Server Backup', 'OK') if inspection_data else 'OK'
    ws['H38'].border = thin_border
    for c in ['D', 'E', 'F', 'G', 'I']:
        ws[f'{c}38'].border = thin_border
    
    # ── Row 39: MES Application ──
    ws.merge_cells('B39:C39')
    ws['B39'] = "MES Application"
    ws['B39'].font = bold_font
    ws['B39'].fill = header_fill
    ws['B39'].border = thin_border
    ws['C39'].border = thin_border
    ws['H39'] = inspection_data.get('MES Application', 'OK') if inspection_data else 'OK'
    ws['H39'].border = thin_border
    for c in ['D', 'E', 'F', 'G', 'I']:
        ws[f'{c}39'].border = thin_border
    
    # ── Row 40: Remark / Other Issue ──
    ws.merge_cells('B40:C40')
    ws['B40'] = "Remark / Other Issue"
    ws['B40'].font = bold_font
    ws['B40'].fill = header_fill
    ws['B40'].border = thin_border
    ws['C40'].border = thin_border
    for c in ['D', 'E', 'F', 'G', 'H', 'I']:
        ws[f'{c}40'].border = thin_border
    
    # ── Write incidents into rows 22-40 ──
    if incidents:
        # Initial row mapping
        item_map = {
            "Standard Temperature (19 - 25)": 22, "Standard Humidity (35 - 55)": 23,
            "MES Server": 24, "CLTS Server": 25, "HMI Server": 26, "MES PC": 27,
            "CLTS PC": 28, "HMI PC": 29, "MES Printer": 30, "Storage": 31, "Network": 32,
            "UPS": 33, "Air conditioning": 34, "Fire, leaks": 35, "Fire extinguisher": 36,
            "Locks (doors & windows)": 37, "MES Server Backup": 38, "MES Application": 39,
            "Remark / Other Issue": 40
        }
        cat_map = {
            'Indoor Environment': 22, 'H/W Inspection': 24, 'Facility Inspection': 33,
            'Security Inspection': 37, 'MES Server Backup': 38, 'MES Application': 39,
            'Remark / Other Issue': 40
        }

        for inc in incidents:
            cat = inc.get('category', '')
            sub = inc.get('sub_category', '')
            target_row = item_map.get(sub) or cat_map.get(cat, 40)

            # Columns to fill
            data_map = {
                'D': inc.get('time', ''),
                'E': inc.get('failure', ''),
                'F': inc.get('reason', ''),
                'G': inc.get('solution', ''),
                'H': inc.get('current_situation', ''),
                'I': inc.get('contact', '')
            }

            for col, val in data_map.items():
                cell = ws[f'{col}{target_row}']
                old_val = str(cell.value) if cell.value is not None else ""
                if old_val:
                    cell.value = old_val + "\n" + str(val)
                else:
                    cell.value = str(val)
                
                # Formatting
                cell.font = normal_font
                cell.border = thin_border
                cell.alignment = center_align

    # ── Row 42: "3. HMI checking" ──
    ws.merge_cells('B42:J42')
    ws['B42'] = "3. HMI checking"
    ws['B42'].font = bold_font
    
    hmi_header_row = 43
    hmi_headers = {'B': 'Line', 'C': 'MES link SCC', 'D': 'SCC Link PLC', 
                   'E': 'Application Link', 'F': 'Remark'}
    for col, text in hmi_headers.items():
        cell = ws[f'{col}{hmi_header_row}']
        cell.value = text
        cell.font = bold_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    
    hmi_lines = ["PCM", "CAL", "FH-RCL", "CR-RCL", "PDS", "CLTS"]
    for i, line in enumerate(hmi_lines):
        row_n = hmi_header_row + 1 + i
        ws[f'B{row_n}'] = line
        ws[f'B{row_n}'].font = normal_font
        ws[f'B{row_n}'].border = thin_border
        for c in ['C', 'D', 'E', 'F']:
            ws[f'{c}{row_n}'].border = thin_border
            if hmi_data and line in hmi_data:
                col_map = {'C': 'MES link SCC', 'D': 'SCC Link PLC', 'E': 'Application Link', 'F': 'Remark'}
                ws[f'{c}{row_n}'] = hmi_data[line].get(col_map[c], '')
                ws[f'{c}{row_n}'].font = normal_font
    
    wb.save(filepath)
    return True, f"Đã xuất thành công: {filepath}"

# --- HMI Persistence ---
def save_hmi_status(hmi_dict):
    conn = get_connection()
    cursor = conn.cursor()
    # Clear old and insert new
    cursor.execute("DELETE FROM hmi_monitoring")
    for line, cols in hmi_dict.items():
        cursor.execute("""
            INSERT INTO hmi_monitoring (line, mes_link_scc, scc_link_plc, app_link, remark)
            VALUES (?, ?, ?, ?, ?)
        """, (line, cols.get('MES link SCC'), cols.get('SCC Link PLC'), 
              cols.get('Application Link'), cols.get('Remark')))
    conn.commit()
    conn.close()

def load_hmi_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hmi_monitoring")
    rows = cursor.fetchall()
    conn.close()
    res = {}
    for r in rows:
        res[r['line']] = {
            'MES link SCC': r['mes_link_scc'],
            'SCC Link PLC': r['scc_link_plc'],
            'Application Link': r['app_link'],
            'Remark': r['remark']
        }
    return res
