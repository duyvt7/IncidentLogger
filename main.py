"""
IT Error Logger - V4
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from tkcalendar import DateEntry
import database as db

BG="#F1F5F9"; CARD_BG="#FFFFFF"; BORDER="#E2E8F0"; PRIMARY="#6366F1"
TEXT_MAIN="#1E293B"; TEXT_DIM="#64748B"; SUCCESS="#10B981"
DANGER="#EF4444"; WARNING="#F59E0B"; HDR_BG="#CCFFFF"

FONT_MAIN=("Segoe UI",10); FONT_BOLD=("Segoe UI",10,"bold")
FONT_TITLE=("Segoe UI",14,"bold"); FONT_HEADER=("Segoe UI",18,"bold")
FONT_SM=("Segoe UI",9)

DETAIL_STRUCTURE = [
    ("Indoor Environment", ["Standard Temperature (19 - 25)", "Standard Humidity (35 - 55)"]),
    ("H/W Inspection", ["MES Server","CLTS Server","HMI Server","MES PC","CLTS PC","HMI PC","MES Printer","Storage","Network"]),
    ("Facility Inspection", ["UPS","Air conditioning","Fire, leaks","Fire extinguisher"]),
    ("Security Inspection", ["Locks (doors & windows)"]),
    ("MES Server Backup", []),
    ("MES Application", []),
    ("Remark / Other Issue", []),
]

HMI_LINES = ["PCM","CAL","FH-RCL","CR-RCL","PDS","CLTS"]
HMI_COLS  = ["MES link SCC","SCC Link PLC","Application Link","Remark"]

class ITErrorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        db.init_db()
        self.title("IT Operations Dashboard")
        self.geometry("1300x820")
        self.configure(bg=BG)
        self._setup_styles()
        self.show_login()

    def _setup_styles(self):
        s=ttk.Style(self); s.theme_use("clam")
        s.configure("TNotebook",background=BG,borderwidth=0)
        s.configure("TNotebook.Tab",background=BORDER,foreground=TEXT_DIM,padding=(20,8),font=FONT_BOLD)
        s.map("TNotebook.Tab",background=[("selected",PRIMARY)],foreground=[("selected","white")])
        s.configure("Treeview",background="white",fieldbackground="white",foreground=TEXT_MAIN,rowheight=32,borderwidth=0)
        s.configure("Treeview.Heading",background=HDR_BG,foreground=TEXT_MAIN,font=FONT_BOLD,relief="flat")
        s.map("Treeview",background=[("selected","#c7d2fe")],foreground=[("selected",TEXT_MAIN)])

    def show_login(self):
        # Refresh user list from DB every time we show login
        user_list = db.list_users()
        self.login_win=tk.Frame(self,bg=BG)
        self.login_win.place(relx=0.5,rely=0.5,anchor="center")
        card=tk.Frame(self.login_win,bg=CARD_BG,padx=40,pady=40,highlightthickness=1,highlightbackground=BORDER); card.pack()
        tk.Label(card,text="🔐 IT LOGIN",bg=CARD_BG,fg=PRIMARY,font=FONT_HEADER).pack(pady=(0,20))
        tk.Label(card,text="Username",bg=CARD_BG,fg=TEXT_DIM,font=FONT_MAIN).pack(anchor="w")
        self.ent_u=ttk.Combobox(card,values=user_list,width=28,font=FONT_MAIN,state="normal")
        self.ent_u.pack(pady=(5,15),ipady=6); self.ent_u.set("admin")
        tk.Label(card,text="Password",bg=CARD_BG,fg=TEXT_DIM,font=FONT_MAIN).pack(anchor="w")
        self.ent_p=tk.Entry(card,width=30,font=FONT_MAIN,show="*",relief="flat",highlightthickness=1,highlightbackground=BORDER)
        self.ent_p.pack(pady=(5,25),ipady=8)
        self.ent_p.bind("<Return>",lambda e:self.do_login())
        tk.Button(card,text="Sign In",bg=PRIMARY,fg="white",font=FONT_BOLD,relief="flat",cursor="hand2",command=self.do_login).pack(fill="x",ipady=10)

    def do_login(self):
        if db.verify_user(self.ent_u.get(),self.ent_p.get()):
            self.current_user=self.ent_u.get()
            self.login_win.destroy(); self.build_ui()
        else:
            messagebox.showerror("Error","Invalid credentials")

    def logout(self):
        if messagebox.askyesno("Đăng xuất","Bạn có muốn đăng xuất không?"):
            for w in self.winfo_children(): w.destroy()
            self.show_login()

    def build_ui(self):
        self.main_frame=tk.Frame(self,bg=BG); self.main_frame.pack(fill="both",expand=True)
        hdr=tk.Frame(self.main_frame,bg=CARD_BG,height=80,highlightthickness=1,highlightbackground=BORDER)
        hdr.pack(fill="x",padx=16,pady=(16,8))
        tk.Label(hdr,text="🚀 IT Shift Report",bg=CARD_BG,fg=TEXT_MAIN,font=FONT_HEADER).pack(side="left",padx=20)
        tk.Button(hdr,text="🚪 Đăng xuất",bg=DANGER,fg="white",font=FONT_BOLD,relief="flat",
                  padx=10,pady=4,cursor="hand2",command=self.logout).pack(side="right",padx=12,pady=10)
        info_p=tk.Frame(hdr,bg=CARD_BG); info_p.pack(side="right",padx=8)

        self.shift_data={"Dept":tk.StringVar(value="IT"),
                         "Date":tk.StringVar(value=datetime.now().strftime("%Y-%m-%d")),
                         "Shift":tk.StringVar(value="Ca Ngày"),
                         "User":tk.StringVar(value=self.current_user)}

        for k,v in self.shift_data.items():
            f=tk.Frame(info_p,bg=CARD_BG); f.pack(side="left",padx=8)
            tk.Label(f,text=k.upper(),bg=CARD_BG,fg=TEXT_DIM,font=("Segoe UI",8)).pack()
            if k=="Shift":
                cb=ttk.Combobox(f,textvariable=v,values=["Ca Ngày","Ca Đêm"],state="readonly",width=10,font=FONT_BOLD,justify="center")
                cb.pack()
            elif k=="Date":
                de=DateEntry(f,textvariable=v,width=12,font=FONT_BOLD,date_pattern="yyyy-mm-dd",
                             background=PRIMARY,foreground="white",headersbackground=PRIMARY)
                de.pack()
            else:
                tk.Entry(f,textvariable=v,width=12,font=FONT_BOLD,bg=CARD_BG,relief="flat",justify="center").pack()

        nb=ttk.Notebook(self.main_frame); nb.pack(fill="both",expand=True,padx=16,pady=8)
        self.tab_dashboard=tk.Frame(nb,bg=BG)
        self.tab_detail=tk.Frame(nb,bg=BG)
        self.tab_hmi=tk.Frame(nb,bg=BG)
        nb.add(self.tab_dashboard,text="  📊 Dashboard  ")
        nb.add(self.tab_detail,text="  📝 2. Detail  ")
        nb.add(self.tab_hmi,text="  ✅ 3. HMI Checking  ")
        if self.current_user=="admin":
            self.tab_users=tk.Frame(nb,bg=BG)
            nb.add(self.tab_users,text="  👤 Quản lý User  ")
            self._build_users_tab()

        self._build_dashboard_tab()
        self._build_detail_tab()
        self._build_hmi_tab()
        self._load_hmi_into_ui()

    # ══════════════════════════════════════════════════════════════
    # TAB: Quản lý User (admin only)
    # ══════════════════════════════════════════════════════════════
    def _build_users_tab(self):
        p=self.tab_users
        tk.Label(p,text="👤 Quản lý User",bg=BG,fg=TEXT_MAIN,font=FONT_TITLE).pack(anchor="w",padx=16,pady=(12,4))
        # Form tạo user mới
        form=tk.Frame(p,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER,padx=20,pady=16)
        form.pack(fill="x",padx=16,pady=8)
        tk.Label(form,text="Tạo user mới:",bg=CARD_BG,fg=TEXT_MAIN,font=FONT_BOLD).grid(row=0,column=0,columnspan=4,sticky="w",pady=(0,8))
        tk.Label(form,text="Username:",bg=CARD_BG,fg=TEXT_DIM,font=FONT_MAIN).grid(row=1,column=0,sticky="w",padx=(0,6))
        self.new_uname=tk.Entry(form,width=22,font=FONT_MAIN,relief="flat",highlightthickness=1,highlightbackground=BORDER)
        self.new_uname.grid(row=1,column=1,ipady=5,padx=(0,16))
        tk.Label(form,text="Password:",bg=CARD_BG,fg=TEXT_DIM,font=FONT_MAIN).grid(row=1,column=2,sticky="w",padx=(0,6))
        self.new_pwd=tk.Entry(form,width=18,font=FONT_MAIN,relief="flat",highlightthickness=1,highlightbackground=BORDER)
        self.new_pwd.grid(row=1,column=3,ipady=5,padx=(0,12))
        tk.Button(form,text="➕ Tạo user",bg=PRIMARY,fg="white",font=FONT_BOLD,relief="flat",padx=10,pady=4,
                  cursor="hand2",command=self._create_user).grid(row=1,column=4,padx=4)
        # Danh sách user
        lf=tk.Frame(p,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER)
        lf.pack(fill="both",expand=True,padx=16,pady=(0,16))
        
        # Header for list
        tk.Label(lf,text="Danh sách user:",bg=CARD_BG,fg=TEXT_MAIN,font=FONT_BOLD).pack(anchor="w",padx=12,pady=(8,4))
        
        # User selection and listbox
        list_f = tk.Frame(lf, bg=CARD_BG); list_f.pack(fill="both", expand=True, padx=12)
        self.user_lb=tk.Listbox(list_f,font=FONT_MAIN,bg="white",fg=TEXT_MAIN,selectbackground="#c7d2fe",relief="flat",height=10)
        self.user_lb.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(list_f, orient="vertical", command=self.user_lb.yview)
        sb.pack(side="right", fill="y"); self.user_lb.config(yscrollcommand=sb.set)

        # Actions for selected user
        af=tk.Frame(lf,bg=CARD_BG); af.pack(fill="x", padx=12, pady=8)
        tk.Label(af,text="Mật khẩu mới:",bg=CARD_BG,fg=TEXT_DIM,font=FONT_SM).pack(side="left")
        self.edit_pwd=tk.Entry(af,width=15,font=FONT_MAIN,relief="flat",highlightthickness=1,highlightbackground=BORDER)
        self.edit_pwd.pack(side="left", padx=8)
        tk.Button(af,text="🔄 Đổi mật khẩu",bg=WARNING,fg="white",font=FONT_BOLD,relief="flat",padx=10,pady=4,
                  cursor="hand2",command=self._change_password).pack(side="left",padx=4)
        tk.Button(af,text="🗑️ Xóa user",bg=DANGER,fg="white",font=FONT_BOLD,relief="flat",padx=10,pady=4,
                  cursor="hand2",command=self._delete_user).pack(side="right",padx=4)
        
        self._refresh_user_list()

    def _refresh_user_list(self):
        self.user_lb.delete(0,"end")
        for u in db.list_users(): self.user_lb.insert("end",u)

    def _change_password(self):
        sel=self.user_lb.curselection()
        if not sel: messagebox.showwarning("","Chọn một user để đổi mật khẩu."); return
        uname=self.user_lb.get(sel[0])
        pwd=self.edit_pwd.get().strip()
        if not pwd: messagebox.showwarning("","Nhập mật khẩu mới."); return
        ok,msg=db.update_user_password(uname,pwd)
        if ok: 
            self.edit_pwd.delete(0,"end")
            messagebox.showinfo("Thành công",msg)

    def _create_user(self):
        uname=self.new_uname.get().strip()
        pwd=self.new_pwd.get().strip()
        if not uname or not pwd: messagebox.showwarning("","Nhập đủ username và password."); return
        ok,msg=db.create_user(uname,pwd)
        if ok: 
            self.new_uname.delete(0,"end")
            self.new_pwd.delete(0,"end")
            self._refresh_user_list()
        messagebox.showinfo("Kết quả",msg) if ok else messagebox.showerror("Lỗi",msg)

    def _delete_user(self):
        sel=self.user_lb.curselection()
        if not sel: messagebox.showwarning("","Chọn một user để xóa."); return
        uname=self.user_lb.get(sel[0])
        if messagebox.askyesno("Xác nhận",f"Xóa user '{uname}'?"):
            ok,msg=db.delete_user(uname)
            if ok: self._refresh_user_list()
            messagebox.showinfo("Kết quả",msg) if ok else messagebox.showerror("Lỗi",msg)

    # ══════════════════════════════════════════════════════════════
    # TAB 1: Dashboard
    # ══════════════════════════════════════════════════════════════
    def _build_dashboard_tab(self):
        c=tk.Frame(self.tab_dashboard,bg=BG,padx=20,pady=20); c.pack(fill="both",expand=True)
        tk.Label(c,text="System Statistics",bg=BG,fg=TEXT_MAIN,font=FONT_TITLE).pack(anchor="w",pady=(0,15))
        kf=tk.Frame(c,bg=BG); kf.pack(fill="x")
        stats=db.get_stats()
        for title,val,color in [("Total Incidents",str(stats['total']),PRIMARY),("Today","OK",SUCCESS),("Open","0",WARNING)]:
            card=tk.Frame(kf,bg=CARD_BG,padx=20,pady=20,highlightthickness=1,highlightbackground=BORDER)
            card.pack(side="left",fill="both",expand=True,padx=10)
            tk.Label(card,text=title,bg=CARD_BG,fg=TEXT_DIM,font=FONT_MAIN).pack()
            tk.Label(card,text=val,bg=CARD_BG,fg=color,font=FONT_HEADER).pack()

    # ══════════════════════════════════════════════════════════════
    # TAB 2: Detail
    # ══════════════════════════════════════════════════════════════
    def _build_detail_tab(self):
        p=self.tab_detail
        tb=tk.Frame(p,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER)
        tb.pack(fill="x",padx=8,pady=(8,4))
        tk.Label(tb,text="2. Detail",bg=CARD_BG,fg=TEXT_MAIN,font=FONT_TITLE).pack(side="left",padx=12,pady=8)
        tk.Button(tb,text="📤 Export Excel",bg="#059669",fg="white",font=FONT_BOLD,relief="flat",padx=12,pady=4,cursor="hand2",
                  command=self.export_excel).pack(side="right",padx=8,pady=8)
        tk.Button(tb,text="➕ Thêm sự cố",bg=PRIMARY,fg="white",font=FONT_BOLD,relief="flat",padx=12,pady=4,cursor="hand2",
                  command=self.open_add_incident).pack(side="right",padx=4,pady=8)

        # Search bar with DateRange calendar
        sf=tk.Frame(p,bg=BG); sf.pack(fill="x",padx=8,pady=4)
        tk.Label(sf,text="📅 Từ ngày:",bg=BG,fg=TEXT_DIM,font=FONT_MAIN).pack(side="left",padx=(0,4))
        self.date_from=DateEntry(sf,width=12,font=FONT_MAIN,date_pattern="yyyy-mm-dd",
                                    background=PRIMARY,foreground="white",headersbackground=PRIMARY)
        self.date_from.pack(side="left",padx=(0,8))
        
        tk.Label(sf,text="đến ngày:",bg=BG,fg=TEXT_DIM,font=FONT_MAIN).pack(side="left",padx=(0,4))
        self.date_to=DateEntry(sf,width=12,font=FONT_MAIN,date_pattern="yyyy-mm-dd",
                                    background=PRIMARY,foreground="white",headersbackground=PRIMARY)
        self.date_to.pack(side="left",padx=(0,8))

        tk.Button(sf,text="🔍 Lọc",bg=PRIMARY,fg="white",font=FONT_BOLD,relief="flat",padx=15,pady=3,
                  cursor="hand2",command=self.refresh_detail).pack(side="left",padx=4)
        tk.Button(sf,text="↺ Xem tất cả",bg=BORDER,fg=TEXT_DIM,font=FONT_MAIN,relief="flat",padx=10,pady=3,
                  cursor="hand2",command=self._show_all).pack(side="left",padx=4)
        self.filter_active=False

        # Treeview
        cols=("id","category","sub_item","time","failure","reason","solution","situation","contact")
        heads=("ID","Category","Sub-Item","Time","Failure","Reason","Solution","Current Situation","Contact Number")
        widths=(40,130,160,100,150,100,180,140,110)
        tree_f=tk.Frame(p,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER)
        tree_f.pack(fill="both",expand=True,padx=8,pady=4)
        self.tree=ttk.Treeview(tree_f,columns=cols,show="headings",selectmode="browse")
        for c,h,w in zip(cols,heads,widths):
            self.tree.heading(c,text=h); self.tree.column(c,width=w,minwidth=30,anchor="center" if w<140 else "w")
        vsb=ttk.Scrollbar(tree_f,orient="vertical",command=self.tree.yview)
        hsb=ttk.Scrollbar(tree_f,orient="horizontal",command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        self.tree.grid(row=0,column=0,sticky="nsew"); vsb.grid(row=0,column=1,sticky="ns"); hsb.grid(row=1,column=0,sticky="ew")
        tree_f.rowconfigure(0,weight=1); tree_f.columnconfigure(0,weight=1)
        self.tree.bind("<Double-1>",lambda e:self._edit_selected())

        ab=tk.Frame(p,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER); ab.pack(fill="x",padx=8,pady=(0,8))
        self.lbl_count=tk.Label(ab,text="",bg=CARD_BG,fg=TEXT_DIM,font=FONT_MAIN)
        self.lbl_count.pack(side="left",padx=12,pady=6)
        tk.Button(ab,text="🗑️ Xóa",bg=DANGER,fg="white",font=FONT_BOLD,relief="flat",padx=10,pady=3,cursor="hand2",
                  command=self._delete_selected).pack(side="right",padx=8,pady=6)
        tk.Button(ab,text="✏️ Sửa",bg=WARNING,fg="white",font=FONT_BOLD,relief="flat",padx=10,pady=3,cursor="hand2",
                  command=self._edit_selected).pack(side="right",padx=4,pady=6)
        self._show_all()

    def refresh_detail(self):
        self.filter_active=True
        d1=self.date_from.get_date().strftime("%Y-%m-%d")
        d2=self.date_to.get_date().strftime("%Y-%m-%d")
        self.tree.delete(*self.tree.get_children())
        rows=db.get_incidents(start_date=d1, end_date=d2, current_user=self.current_user)
        for i, r in enumerate(rows, 1):
            self.tree.insert("","end",iid=str(r['id']),values=(
                i,r['category'],r['sub_category'] or "",r['time'],
                r['failure'],r['reason'] or "",r['solution'] or "",
                r['current_situation'] or "",r['contact'] or ""))
        db_name = db.DB_PATH.name
        self.lbl_count.configure(text=f"📅 {d1} ➔ {d2} — 📂 {db_name} — Tổng: {len(rows)} sự cố")

    def _show_all(self):
        self.filter_active=False
        self.tree.delete(*self.tree.get_children())
        try:
            rows=db.get_incidents(current_user=self.current_user)
            for i, r in enumerate(rows, 1):
                self.tree.insert("","end",iid=str(r['id']),values=(
                    i,r['category'],r['sub_category'] or "",r['time'],
                    r['failure'],r['reason'] or "",r['solution'] or "",
                    r['current_situation'] or "",r['contact'] or ""))
            db_name = db.DB_PATH.name
            self.lbl_count.configure(text=f"📂 DB: {db_name} | Tổng: {len(rows)} sự cố")
        except Exception as e:
            messagebox.showerror("Lỗi dữ liệu", f"Không thể tải dữ liệu: {e}")

    def _get_sel_id(self):
        sel=self.tree.selection()
        if not sel: messagebox.showwarning("","Chọn một bản ghi."); return None
        return int(sel[0])

    def _edit_selected(self):
        eid=self._get_sel_id()
        if eid: IncidentDialog(self,edit_id=eid,on_save=lambda:self._show_all())

    def _delete_selected(self):
        eid=self._get_sel_id()
        if eid and messagebox.askyesno("Xác nhận",f"Xóa sự cố ID {eid}?"):
            db.delete_incident(eid); self._show_all()

    def open_add_incident(self):
        IncidentDialog(self,on_save=lambda:self._show_all(),
                       default_reporter=self.shift_data["User"].get(),
                       default_shift=self.shift_data["Shift"].get())

    def _collect_hmi_data(self):
        """Collect HMI data from the HMI tab entries."""
        hmi={}
        for line in HMI_LINES:
            hmi[line]={}
            for col_name in HMI_COLS:
                val=self.hmi_entries[line][col_name].get()
                hmi[line][col_name]=val
        return hmi

    def export_excel(self):
        # Lấy dữ liệu đang hiển thị trên Treeview (đã lọc)
        d1=self.date_from.get_date().strftime("%Y-%m-%d")
        d2=self.date_to.get_date().strftime("%Y-%m-%d")
        
        # Nếu không ở chế độ lọc, lấy tất cả hoặc lấy theo ngày hiện tại
        if self.filter_active:
            rows = db.get_incidents(start_date=d1, end_date=d2, current_user=self.current_user)
            date_part = f"{d1}_to_{d2}"
        else:
            rows = db.get_incidents(current_user=self.current_user)
            date_part = self.shift_data["Date"].get()

        sel_shift = self.shift_data["Shift"].get()
        shift_tag = "DayShift" if "Ngày" in sel_shift else "NightShift"
        default_name = f"Shift Report_{date_part}_{shift_tag}.xlsx"
        
        path=filedialog.asksaveasfilename(defaultextension=".xlsx",
            filetypes=[("Excel files","*.xlsx")],
            initialfile=default_name)
        if not path: return
        
        incidents=[dict(r) for r in rows]
        hmi_data=self._collect_hmi_data()
        ok,msg=db.export_to_excel(path,
            dept=self.shift_data["Dept"].get(),
            prepared_by=self.shift_data["User"].get(),
            shift=sel_shift,
            incidents=incidents,
            hmi_data=hmi_data)
        if ok: messagebox.showinfo("Thành công",msg)
        else: messagebox.showerror("Lỗi",msg)

    # ══════════════════════════════════════════════════════════════
    # TAB 3: HMI Checking — options: OK / Stopped
    # ══════════════════════════════════════════════════════════════
    def _build_hmi_tab(self):
        c=tk.Frame(self.tab_hmi,bg=BG,padx=20,pady=20); c.pack(fill="both",expand=True)
        card=tk.Frame(c,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER,padx=20,pady=20)
        card.pack(fill="both",expand=True)
        tk.Label(card,text="3. HMI Checking",bg=CARD_BG,fg=TEXT_MAIN,font=FONT_TITLE).pack(anchor="w",pady=(0,16))
        gf=tk.Frame(card,bg=CARD_BG); gf.pack(fill="x")
        all_headers=["Line"]+HMI_COLS
        for i,h in enumerate(all_headers):
            tk.Label(gf,text=h,bg=HDR_BG,fg=TEXT_MAIN,font=FONT_BOLD,width=18,relief="flat",
                     highlightthickness=1,highlightbackground=BORDER).grid(row=0,column=i,padx=1,pady=1,sticky="ew")
        self.hmi_entries={}
        for ri,line in enumerate(HMI_LINES,1):
            tk.Label(gf,text=line,bg=CARD_BG,fg=TEXT_MAIN,font=FONT_MAIN,width=18,anchor="w").grid(row=ri,column=0,padx=1,pady=4)
            self.hmi_entries[line]={}
            for ci,col_name in enumerate(HMI_COLS,1):
                if col_name=="Remark":
                    w=tk.Entry(gf,width=16,font=FONT_MAIN,relief="flat",highlightthickness=1,highlightbackground=BORDER)
                else:
                    w=ttk.Combobox(gf,values=["OK","Stopped"],width=14,state="readonly"); w.set("OK")
                w.grid(row=ri,column=ci,padx=4,pady=4)
                self.hmi_entries[line][col_name]=w
        
        tk.Button(card, text="💾 Lưu trạng thái HMI", bg=PRIMARY, fg="white", font=FONT_BOLD, 
                  relief="flat", padx=20, pady=8, cursor="hand2", command=self._save_hmi).pack(anchor="e", pady=10)

    def _save_hmi(self):
        hmi_data = self._collect_hmi_data()
        db.save_hmi_status(hmi_data)
        messagebox.showinfo("Thành công", "Đã lưu trạng thái HMI vào database!")

    def _load_hmi_into_ui(self):
        hmi_data = db.load_hmi_status()
        for line, cols in hmi_data.items():
            if line in self.hmi_entries:
                for col_name, val in cols.items():
                    if col_name in self.hmi_entries[line]:
                        w = self.hmi_entries[line][col_name]
                        if isinstance(w, ttk.Combobox):
                            w.set(val if val else "OK")
                        else:
                            w.delete(0, "end")
                            w.insert(0, val if val else "")


# ══════════════════════════════════════════════════════════════
# DIALOG: Thêm / Sửa sự cố
# ══════════════════════════════════════════════════════════════
class IncidentDialog(tk.Toplevel):
    def __init__(self,parent,edit_id=None,on_save=None,default_reporter="",default_shift=""):
        super().__init__(parent)
        self.edit_id=edit_id; self.on_save=on_save
        self.default_reporter=default_reporter; self.default_shift=default_shift
        self.title("Sửa sự cố" if edit_id else "Thêm sự cố mới")
        self.configure(bg=BG); self.geometry("580x620"); self.resizable(False,False); self.grab_set()
        tk.Label(self,text="✏️ Thông tin sự cố",bg=BG,fg=PRIMARY,font=FONT_TITLE).pack(pady=(16,8))
        form=tk.Frame(self,bg=BG); form.pack(fill="both",expand=True,padx=24); form.columnconfigure(1,weight=1)
        cats=[c for c,_ in DETAIL_STRUCTURE]
        self.fields={}

        def add_row(r,label,key,wtype="entry",values=None):
            tk.Label(form,text=label,bg=BG,fg=TEXT_DIM,font=FONT_SM,anchor="e",width=18).grid(row=r,column=0,sticky="ne",pady=5,padx=(0,8))
            if wtype=="combo":
                w=ttk.Combobox(form,values=values or [],state="readonly",font=FONT_MAIN)
                if values: w.set(values[0])
            elif wtype=="text":
                w=tk.Text(form,height=3,wrap="word",font=FONT_MAIN,relief="flat",highlightthickness=1,highlightbackground=BORDER)
            else:
                w=tk.Entry(form,font=FONT_MAIN,relief="flat",highlightthickness=1,highlightbackground=BORDER)
            w.grid(row=r,column=1,sticky="ew",ipady=3 if wtype!="text" else 0,pady=3)
            self.fields[key]=w

        add_row(0,"Category *","category","combo",cats)
        self.fields["category"].bind("<<ComboboxSelected>>",self._on_cat_change)
        add_row(1,"Sub-Item","sub_category","combo",[])
        
        # Time picker with Date and Hour/Min
        tk.Label(form,text="Time *",bg=BG,fg=TEXT_DIM,font=FONT_SM,anchor="e",width=18).grid(row=2,column=0,sticky="ne",pady=5,padx=(0,8))
        tf=tk.Frame(form,bg=BG); tf.grid(row=2,column=1,sticky="w",pady=3)
        self.date_v = DateEntry(tf, width=12, background=PRIMARY, foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_v.pack(side="left", padx=(0,5))
        self.hour_v = ttk.Combobox(tf, values=[f"{i:02d}" for i in range(24)], width=3, state="readonly")
        self.hour_v.set(datetime.now().strftime("%H")); self.hour_v.pack(side="left")
        tk.Label(tf, text=":", bg=BG).pack(side="left")
        self.min_v = ttk.Combobox(tf, values=[f"{i:02d}" for i in range(60)], width=3, state="readonly")
        self.min_v.set(datetime.now().strftime("%M")); self.min_v.pack(side="left")

        add_row(3,"Failure *","failure")
        add_row(4,"Reason","reason")
        add_row(5,"Solution","solution","text")
        # Current Situation as dropdown
        sit_opts=["Running normal","Đang xử lí","Chờ hỗ trợ","Cần theo dõi","Tạm dừng"]
        add_row(6,"Current Situation","current_situation","combo",sit_opts)
        add_row(7,"Contact Number","contact")
        self._on_cat_change()

        bf=tk.Frame(self,bg=BG,pady=12); bf.pack()
        tk.Button(bf,text="💾 Lưu",bg=PRIMARY,fg="white",font=FONT_BOLD,relief="flat",padx=20,pady=8,cursor="hand2",command=self._save).pack(side="left",padx=8)
        tk.Button(bf,text="Hủy",bg=BORDER,fg=TEXT_DIM,font=FONT_MAIN,relief="flat",padx=14,pady=8,cursor="hand2",command=self.destroy).pack(side="left")
        if edit_id: self._load(edit_id)

    def _on_cat_change(self,*_):
        cat=self.fields["category"].get()
        subs=[]
        for c,s in DETAIL_STRUCTURE:
            if c==cat: subs=s; break
        self.fields["sub_category"].configure(values=subs,state="readonly" if subs else "disabled")
        if subs: self.fields["sub_category"].set(subs[0])
        else: self.fields["sub_category"].set("")

    def _load(self,eid):
        r=db.get_incident_by_id(eid)
        if not r: return
        self.fields["category"].set(r["category"]); self._on_cat_change()
        if r["sub_category"]: self.fields["sub_category"].set(r["sub_category"])
        
        # Load time
        try:
            dt = datetime.strptime(r["time"], "%Y-%m-%d %H:%M")
            self.date_v.set_date(dt.date())
            self.hour_v.set(f"{dt.hour:02d}")
            self.min_v.set(f"{dt.minute:02d}")
        except: pass

        self.fields["failure"].delete(0,"end"); self.fields["failure"].insert(0,r["failure"])
        self.fields["reason"].delete(0,"end"); self.fields["reason"].insert(0,r["reason"] or "")
        self.fields["solution"].insert("1.0",r["solution"] or "")
        self.fields["current_situation"].set(r["current_situation"] or "Running normal")
        self.fields["contact"].delete(0,"end"); self.fields["contact"].insert(0,r["contact"] or "")

    def _save(self):
        failure=self.fields["failure"].get().strip()
        time_v = f"{self.date_v.get_date()} {self.hour_v.get()}:{self.min_v.get()}"
        if not failure: messagebox.showwarning("","Nhập mô tả lỗi (Failure).",parent=self); return
        sol=self.fields["solution"].get("1.0","end").strip()
        data=dict(time=time_v,category=self.fields["category"].get(),
                  sub_category=self.fields["sub_category"].get(),
                  failure=failure,reason=self.fields["reason"].get().strip(),solution=sol,
                  current_situation=self.fields["current_situation"].get().strip(),
                  contact=self.fields["contact"].get().strip(),
                  reporter=self.default_reporter,shift=self.default_shift)
        if self.edit_id: db.update_incident(self.edit_id,data)
        else: db.add_incident(data)
        if self.on_save: self.on_save()
        self.destroy()

if __name__=="__main__":
    app=ITErrorApp(); app.mainloop()
