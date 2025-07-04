import customtkinter as ctk
from tkinter import messagebox, simpledialog
import json
import os
import asyncio
from playwright.async_api import async_playwright, Playwright, BrowserContext, Page,expect
from playwright.sync_api import Error as PlaywrightError
import shutil
import logging
import random
import sys
import time
# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Cấu hình chung của ứng dụng ---
PROFILES_FILE = "profiles.json"
BASE_PROFILE_DIR = "playwright_profiles"
STATUS_COLOR = {
    "pending": "gray",
    "running": "blue",
    "success": "green",
    "error": "red",
    "closed": "orange",
    "paused": "purple",
    "hidden": "darkgreen",
}
CONCURRENT_BROWSERS_LIMIT = 4  # ĐÃ GIẢM: Số lượng trình duyệt tối đa chạy đồng thời (điều chỉnh theo cấu hình máy)

DEFAULT_TIMEOUT_MS = 30000 # Có thể giảm timeout mặc định nếu mạng ổn định
LONG_TIMEOUT_MS = 60000    # Giảm timeout dài hơn cho các thao tác tải trang

# --- Hàm tiện ích ---
def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                messagebox.showwarning("Lỗi đọc file", "File profiles.json bị lỗi định dạng. Tạo file mới.")
                logging.error("Lỗi đọc file profiles.json, có thể file bị hỏng.")
                return {}
    return {}

def save_profiles(profiles):
    with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=4)

def create_playwright_profile_dir(email):
    safe_email = email.replace("@", "_at_").replace(".", "_dot_").replace("/", "_slash_").replace("\\", "_backslash_").replace(" ", "_")
    profile_dir = os.path.join(BASE_PROFILE_DIR, safe_email)
    os.makedirs(profile_dir, exist_ok=True)
    return profile_dir

# --- Hàm đăng nhập Gmail (bất đồng bộ) ---
async def login_gmail_async(playwright_instance: Playwright, email: str, password: str, profile_dir: str,
                            status_callback, active_browsers: dict, pause_event: asyncio.Event):
    """
    Sử dụng Playwright bất đồng bộ để đăng nhập Gmail.
    Luôn chạy ở chế độ NON-HEADLESS và quản lý ẩn/hiện cửa sổ.
    Giữ BrowserContext mở trong active_browsers.
    """
    status_callback(email, "running", "Đang xử lý...")
    browser_context = None
    page = None

    # CÁC ĐỐI SỐ TỐI ƯU HƠN CHO CHROMIUM
    chrome_args = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        # "--disable-gpu", # Giữ nếu không có GPU hoặc gặp vấn đề, xóa nếu muốn dùng GPU để tăng tốc rendering
        "--disable-dev-shm-usage",
        "--no-zygote",
        "--disable-features=site-per-process",
        "--disable-accelerated-2d-canvas",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-notifications",
        "--disable-popup-blocking",
        "--disable-infobars",
        "--disable-blink-features=AutomationControlled",
        "--window-size=800,600", # ĐÃ GIẢM KÍCH THƯỚC CỬA SỔ
        "--disable-background-networking",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-breakpad",
        "--disable-component-update",
        "--disable-domain-reliability",
        "--disable-sync",
        "--enable-automation",
        "--disable-extensions",
        "--disable-software-rasterizer",
        "--mute-audio",
        "--autoplay-policy=no-user-gesture-required", # Thêm để tắt autoplay video
        # "--remote-debugging-port=9222" # Chỉ dùng cho debug, không cho production
    ]

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

    try:
        logging.info(f"[{email}] Đang kiểm tra trình duyệt...")

        if email in active_browsers:
            browser_context = active_browsers[email]
            status_callback(email, "running", "Trình duyệt đang chạy, kiểm tra trạng thái.")
            logging.info(f"[{email}] Trình duyệt đã được tái sử dụng.")
        else:
            logging.info(f"[{email}] Khởi tạo persistent context mới tại {profile_dir} (NON-HEADLESS)...")
            browser_context = await playwright_instance.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False, # LUÔN CHẠY NON-HEADLESS
                args=chrome_args,
                timeout=LONG_TIMEOUT_MS,
                user_agent=user_agent,
                viewport={'width': 800, 'height': 600} # ĐÃ GIẢM KÍCH THƯỚC VIEWPORT
            )
            active_browsers[email] = browser_context # LƯU CONTEXT VÀO active_browsers
            logging.info(f"[{email}] Đã khởi tạo context.")

        # Lấy hoặc tạo trang đầu tiên trong context
        
        page = await browser_context.new_page() 
        # Bước 2: Điều hướng đến trang đăng nhập 
        logging.info(f"[{email}] Đi đến trang đăng nhập Google...") # thông báo
        await page.goto("https://accounts.google.com", timeout=0) # mơt trang đăng nhập
        await page.wait_for_timeout(random.uniform(300, 1000)) # GIẢM THỜI GIAN CHỜ NGẪU NHIÊN
        await page.fill('input[type="email"]', email, timeout=0) # nhập vào ô email
        await page.wait_for_timeout(random.uniform(300, 1000)) # GIẢM THỜI GIAN CHỜ NGẪU NHIÊN
        await page.click('#identifierNext', timeout=DEFAULT_TIMEOUT_MS) # click vào đồng ý
        # đây có nhập mã capcha 
        await page.wait_for_timeout(random.uniform(500, 1500)) # GIẢM THỜI GIAN CHỜ NGẪU NHIÊN
        logging.info(f"[{email}] Đã nhập email và click tiếp theo.") # thông báo hoàn thành 
        await page.fill('input[type="password"]', password, timeout=0) # nhập ô mật khẩu 
        await page.wait_for_timeout(random.uniform(300, 1000)) # delay ngẫu nhiên
        await page.wait_for_selector('#passwordNext', state='visible', timeout=0) 
        await page.click('#passwordNext', timeout=0)
        await page.wait_for_timeout(random.uniform(500, 1500)) # GIẢM THỜI GIAN CHỜ NGẪU NHIÊN
        logging.info(f"[{email}] Đã nhập mật khẩu và click tiếp theo.")
        try:
            await page.get_by_role("button", name="I understand").click(timeout=5000) # nhập nút chưa hiểu 
        except Exception:
            logging.info(f"[{email}] Không tìm thấy nút 'Tôi hiểu' hoặc đã bỏ qua.")
            await page.wait_for_timeout(random.uniform(300, 1000))
            pass
        await asyncio.sleep(5)
        page = await browser_context.new_page()
        await page.goto("https://idx.google.com")# mở idx  
        await page.locator("label").filter(has_text="I accept the terms and").click(position={"x": 5, "y": 5})
        await asyncio.sleep(random.uniform(1,3))
        await page.get_by_role("button", name="Confirm").click()
        await page.goto("https://idx.google.com/devprofile")
        await asyncio.sleep(random.uniform(1,3))
        await page.get_by_role("textbox", name="City, Country").click()
        await asyncio.sleep(random.uniform(1,3))
        await page.get_by_role("textbox", name="City, Country").fill("ha")
        await page.get_by_text("HanoiVietnam").click()
        await asyncio.sleep(random.uniform(1,3))
        await page.get_by_role("combobox").select_option("Architect")
        await asyncio.sleep(random.uniform(1,3))
        await page.locator("label").filter(has_text="Stay up to date on new").click()
        await asyncio.sleep(random.uniform(1,3))
        await page.get_by_role("button", name="Continue").click()    
        await asyncio.sleep(10)             
        await page.get_by_role("button", name="Continue").click()
        # đồng ý điều khoản 
        await page.close()
        page1 = await browser_context.new_page()
        await page1.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page1.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page1.get_by_role("textbox", name="My Flutter App").fill(f"a1")
        await asyncio.sleep(1)
        await page1.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        # tao may 2
        page2 = await browser_context.new_page()
        await page2.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page2.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page2.get_by_role("textbox", name="My Flutter App").fill(f"a2")
        await asyncio.sleep(1)
        await page2.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        # tao may 3
        page3 = await browser_context.new_page()
        await page3.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page3.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page3.get_by_role("textbox", name="My Flutter App").fill(f"a3")
        await asyncio.sleep(1)
        await page3.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        # tao may 4
        page4 = await browser_context.new_page()
        await page4.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page4.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page4.get_by_role("textbox", name="My Flutter App").fill(f"a4")
        await asyncio.sleep(1)
        await page4.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        # tao may 5
        page5 = await browser_context.new_page()
        await page5.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page5.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page5.get_by_role("textbox", name="My Flutter App").fill(f"a5")
        await asyncio.sleep(1)
        await page5.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        # tao may 6
        page6 = await browser_context.new_page()
        await page6.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page6.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page6.get_by_role("textbox", name="My Flutter App").fill(f"a6")
        await asyncio.sleep(1)
        await page6.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        # tao may 7
        page7 = await browser_context.new_page()
        await page7.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page7.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page1.reload()
        await page2.reload()
        await page3.reload()
        await page4.reload()
        await page5.reload()
        await page7.get_by_role("textbox", name="My Flutter App").fill(f"a7")
        await asyncio.sleep(300)
        await page6.reload()
        await page7.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        #tao may 8 
        page8 = await browser_context.new_page()
        await page8.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page8.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page1.reload()
        await page2.reload()
        await page3.reload()
        await page4.reload()
        await page5.reload()
        await page6.reload()
        await page8.get_by_role("textbox", name="My Flutter App").fill(f"a8")
        await asyncio.sleep(300)
        await page7.reload()
        await page8.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        #tao may 9
        page9 = await browser_context.new_page()
        await page9.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page9.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page1.reload()
        await page2.reload()
        await page3.reload()
        await page4.reload()
        await page5.reload()
        await page6.reload()
        await page7.reload()
        await page9.get_by_role("textbox", name="My Flutter App").fill(f"a9")
        await asyncio.sleep(300)
        await page8.reload()
        await page9.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        # tao may 10
        page10 = await browser_context.new_page()
        await page10.goto("https://idx.google.com/new/flutter")
        await asyncio.sleep(1)
        await page10.get_by_role("textbox", name="My Flutter App").click()
        await asyncio.sleep(1)
        await page1.reload()
        await page2.reload()
        await page3.reload()
        await page4.reload()
        await page5.reload()
        await page6.reload()
        await page7.reload()
        await page8.reload()
        await page10.get_by_role("textbox", name="My Flutter App").fill(f"a10")
        await asyncio.sleep(300)
        await page9.reload()
        await page10.get_by_role("button", name="Create").click()
        await asyncio.sleep(1)
        while True:
            await asyncio.sleep(120)
            await page1.reload()
            await page2.reload()
            await page3.reload()
            await page4.reload()
            await page5.reload()
            await page6.reload()
            await page7.reload()
            await page8.reload()   
            await page9.reload()
            await page10.reload()
            
        
        # tạo máy ảo       

    except Exception as e:
        logging.info(email, "error", f"[{email}] Lỗi hệ thống không mong muốn: {e}")
        logging.critical(f"[{email}] Lỗi hệ thống không mong muốn: {e}", exc_info=True)
    finally:
        pass

# --- Giao diện ứng dụng CustomTkinter ---

class GmailLoginApp(ctk.CTk):
    def __init__(self, loop):
        super().__init__()

        self.loop = loop
        self.semaphore = asyncio.Semaphore(CONCURRENT_BROWSERS_LIMIT)

        self.title("Ứng dụng Đăng nhập Gmail Đa hồ sơ")
        self.geometry("1200x750")

        self.grid_columnconfigure(0, weight=1, minsize=400)
        self.grid_columnconfigure(1, weight=1, minsize=600)
        self.grid_rowconfigure(0, weight=1)

        self.profiles = load_profiles()
        self.active_browsers: dict[str, BrowserContext] = {}
        self.profile_tasks: dict[str, asyncio.Task] = {}
        self.pause_events: dict[str, asyncio.Event] = {}
        self.playwright_global_instance: Playwright | None = None

        os.makedirs(BASE_PROFILE_DIR, exist_ok=True)

        self.create_widgets()
        self.update_profile_listbox()

    def create_widgets(self):
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=0)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        add_bulk_frame = ctk.CTkFrame(self.left_frame)
        add_bulk_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        ctk.CTkLabel(add_bulk_frame, text="Thêm nhiều hồ sơ (Tài khoản Mật khẩu, mỗi dòng một cặp):",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(padx=10, pady=(10, 5), anchor="w")
        self.bulk_entry = ctk.CTkTextbox(add_bulk_frame, height=100)
        self.bulk_entry.pack(padx=10, pady=5, fill="x", expand=True)

        add_bulk_button = ctk.CTkButton(add_bulk_frame, text="Thêm hồ sơ hàng loạt", command=self.add_bulk_profiles,
                                        corner_radius=8, fg_color="#27AE60", hover_color="#2ECC71")
        add_bulk_button.pack(padx=10, pady=10, anchor="e")

        self.saved_profiles_frame = ctk.CTkFrame(self.left_frame)
        self.saved_profiles_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.saved_profiles_frame.grid_columnconfigure(0, weight=1)
        self.saved_profiles_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.saved_profiles_frame, text="Các hồ sơ đã lưu:",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        self.profile_list_frame = ctk.CTkScrollableFrame(self.saved_profiles_frame, height=200)
        self.profile_list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        button_frame_left = ctk.CTkFrame(self.saved_profiles_frame, fg_color="transparent")
        button_frame_left.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        button_frame_left.grid_columnconfigure((0, 1, 2), weight=1)

        run_all_button = ctk.CTkButton(button_frame_left, text="Chạy tất cả hồ sơ", command=self.run_all_profiles,
                                       corner_radius=8, fg_color="#3498DB", hover_color="#2980B9")
        run_all_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        delete_selected_button = ctk.CTkButton(button_frame_left, text="Xóa hồ sơ đã chọn", command=self.delete_selected_profile,
                                               fg_color="#E74C3C", hover_color="#C0392B", corner_radius=8)
        delete_selected_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        delete_all_button = ctk.CTkButton(button_frame_left, text="Xóa tất cả hồ sơ", command=self.delete_all_profiles,
                                          fg_color="#C0392B", hover_color="#A93226", corner_radius=8)
        delete_all_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.right_frame, text="Trạng thái trình duyệt:",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.running_status_frame = ctk.CTkScrollableFrame(self.right_frame)
        self.running_status_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        close_all_browsers_button = ctk.CTkButton(self.right_frame, text="Đóng tất cả trình duyệt",
                                                  command=self.close_all_active_browsers_command,
                                                  fg_color="#8E44AD", hover_color="#9B59B6", corner_radius=8)
        close_all_browsers_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.profile_status_labels = {}

    def update_profile_listbox(self):
        for widget in self.profile_list_frame.winfo_children():
            widget.destroy()

        if not self.profiles:
            ctk.CTkLabel(self.profile_list_frame, text="Chưa có hồ sơ nào được lưu.").pack(padx=10, pady=10)
            return

        for email, data in self.profiles.items():
            profile_row_frame = ctk.CTkFrame(self.profile_list_frame, fg_color="transparent")
            profile_row_frame.pack(fill="x", padx=5, pady=2)
            profile_row_frame.grid_columnconfigure(0, weight=1)
            profile_row_frame.grid_columnconfigure(1, weight=0)

            ctk.CTkLabel(profile_row_frame, text=email, anchor="w").grid(row=0, column=0, padx=5, pady=2, sticky="ew")

            run_single_button = ctk.CTkButton(profile_row_frame, text="Chạy", width=60,
                                              command=lambda e=email: self.run_single_profile(e),
                                              corner_radius=6, fg_color="#28B463", hover_color="#2ECC71")
            run_single_button.grid(row=0, column=1, padx=5, pady=2)

            if email not in self.profile_status_labels:
                 self.update_status_label(email, "pending", "Chưa chạy.")

    def add_bulk_profiles(self):
        raw_text = self.bulk_entry.get("1.0", "end-1c").strip()
        if not raw_text:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Tài khoản và Mật khẩu vào ô.")
            return

        new_profiles_added = 0
        lines = raw_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(maxsplit=1)

            if len(parts) == 2:
                email = parts[0].strip()
                password = parts[1].strip()

                if "@" not in email or "." not in email:
                    messagebox.showwarning("Email không hợp lệ", f"Email '{email}' không đúng định dạng. Bỏ qua.")
                    logging.warning(f"Email '{email}' không đúng định dạng. Bỏ qua.")
                    continue

                if email in self.profiles:
                    logging.info(f"Hồ sơ {email} đã tồn tại, bỏ qua.")
                    continue

                profile_dir = create_playwright_profile_dir(email)
                self.profiles[email] = {
                    "password": password,
                    "playwright_profile_dir": profile_dir
                }
                new_profiles_added += 1
            else:
                messagebox.showwarning("Lỗi định dạng", f"Dòng '{line}' không đúng định dạng 'Tài khoản Mật khẩu'. Bỏ qua.")
                logging.warning(f"Dòng '{line}' không đúng định dạng 'Tài khoản Mật khẩu'. Bỏ qua.")

        if new_profiles_added > 0:
            save_profiles(self.profiles)
            self.update_profile_listbox()
            messagebox.showinfo("Thành công", f"Đã thêm {new_profiles_added} hồ sơ mới.")
            self.bulk_entry.delete("1.0", "end")
            logging.info(f"Đã thêm {new_profiles_added} hồ sơ mới.")
        else:
            messagebox.showinfo("Hoàn tất", "Không có hồ sơ mới nào được thêm (có thể đã tồn tại hoặc lỗi định dạng).")
            logging.info("Không có hồ sơ mới nào được thêm.")

    def delete_selected_profile(self):
        email_to_delete = simpledialog.askstring("Xóa hồ sơ", "Nhập email của hồ sơ bạn muốn xóa:", parent=self)
        if email_to_delete and email_to_delete in self.profiles:
            if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa hồ sơ '{email_to_delete}' không?"):
                logging.info(f"Đang xóa hồ sơ {email_to_delete}...")

                if email_to_delete in self.profile_tasks and not self.profile_tasks[email_to_delete].done():
                    self.profile_tasks[email_to_delete].cancel()
                    logging.info(f"Đã hủy tác vụ đang chạy cho {email_to_delete}.")
                    del self.profile_tasks[email_to_delete]

                if email_to_delete in self.active_browsers:
                    self.loop.create_task(self._close_single_browser_context_task(email_to_delete, self.active_browsers[email_to_delete]))

                profile_data = self.profiles.pop(email_to_delete, None)
                if profile_data and "playwright_profile_dir" in profile_data:
                    profile_dir = profile_data["playwright_profile_dir"]
                    if os.path.exists(profile_dir):
                        try:
                            shutil.rmtree(profile_dir)
                            messagebox.showinfo("Thành công", f"Thư mục hồ sơ Playwright của '{email_to_delete}' đã được xóa.")
                            logging.info(f"Thư mục hồ sơ Playwright của '{email_to_delete}' đã được xóa.")
                        except Exception as e:
                            messagebox.showwarning("Cảnh báo", f"Không thể xóa thư mục hồ sơ Playwright: {e}. Vui lòng xóa thủ công.")
                            logging.error(f"Không thể xóa thư mục hồ sơ Playwright cho {email_to_delete}: {e}")

                save_profiles(self.profiles)
                self.update_profile_listbox()

                if email_to_delete in self.profile_status_labels and self.profile_status_labels[email_to_delete]["frame"].winfo_exists():
                    self.profile_status_labels[email_to_delete]["frame"].destroy()
                    del self.profile_status_labels[email_to_delete]
                if email_to_delete in self.pause_events:
                    del self.pause_events[email_to_delete]

                messagebox.showinfo("Thành công", f"Hồ sơ '{email_to_delete}' đã được xóa.")
                logging.info(f"Hồ sơ '{email_to_delete}' đã được xóa khỏi danh sách.")
        elif email_to_delete:
            messagebox.showerror("Lỗi", "Email không tồn tại trong danh sách hồ sơ.")
            logging.warning(f"Người dùng cố gắng xóa email '{email_to_delete}' không tồn tại.")

    def delete_all_profiles(self):
        if not self.profiles:
            messagebox.showinfo("Thông báo", "Không có hồ sơ nào để xóa.")
            return

        if messagebox.askyesno("Xác nhận xóa tất cả", "Bạn có chắc chắn muốn xóa TẤT CẢ hồ sơ và dữ liệu Playwright của chúng không? Hành động này không thể hoàn tác."):
            logging.info("Đang xóa tất cả hồ sơ và trình duyệt liên quan.")
            self.loop.create_task(self.close_all_active_browsers())

            for email, task in list(self.profile_tasks.items()):
                if not task.done():
                    task.cancel()
                    logging.info(f"Đã hủy tác vụ {email} trong quá trình xóa tất cả.")
                del self.profile_tasks[email]

            for email, data in list(self.profiles.items()):
                profile_dir = data.get("playwright_profile_dir")
                if profile_dir and os.path.exists(profile_dir):
                    try:
                        shutil.rmtree(profile_dir)
                        logging.info(f"Đã xóa thư mục hồ sơ Playwright của '{email}'.")
                    except Exception as e:
                        messagebox.showwarning("Cảnh báo", f"Không thể xóa thư mục hồ sơ Playwright của '{email}': {e}. Vui lòng xóa thủ công.")
                        logging.error(f"Không thể xóa thư mục hồ sơ Playwright của '{email}': {e}")
                self.profiles.pop(email)
                if email in self.profile_status_labels and self.profile_status_labels[email]["frame"].winfo_exists():
                    self.profile_status_labels[email]["frame"].destroy()
                    del self.profile_status_labels[email]
                if email in self.pause_events:
                    del self.pause_events[email]

            save_profiles(self.profiles)
            self.update_profile_listbox()
            messagebox.showinfo("Thành công", "Tất cả hồ sơ và dữ liệu Playwright đã được xóa.")
            logging.info("Đã xóa tất cả hồ sơ và dữ liệu Playwright.")

    def run_single_profile(self, email: str):
        if email not in self.profiles:
            messagebox.showerror("Lỗi", f"Hồ sơ '{email}' không tồn tại.")
            logging.error(f"Không thể chạy hồ sơ '{email}': không tồn tại.")
            return

        if email in self.profile_tasks and not self.profile_tasks[email].done():
            self.profile_tasks[email].cancel()
            logging.info(f"Đã hủy tác vụ đang chạy cho {email} để chạy lại.")

        profile_data = self.profiles[email]
        self.update_status_label(email, "pending", "Đang chờ...")

        if email not in self.pause_events:
            self.pause_events[email] = asyncio.Event()
        self.pause_events[email].set()

        task = self.loop.create_task(self._run_single_profile_task(email, profile_data, self.pause_events[email]))
        self.profile_tasks[email] = task
        logging.info(f"Đã tạo tác vụ chạy đơn cho {email}.")

    async def _run_single_profile_task(self, email, profile_data, pause_event: asyncio.Event):
        try:
            async with self.semaphore:
                if self.playwright_global_instance is None:
                    logging.info("Khởi tạo Playwright global instance.")
                    self.playwright_global_instance = await async_playwright().start()

                await login_gmail_async(
                    self.playwright_global_instance,
                    email,
                    profile_data["password"],
                    profile_data["playwright_profile_dir"],
                    self.update_status_label,
                    self.active_browsers,
                    pause_event
                )

                if email in self.active_browsers:
                    current_status = self.profile_status_labels[email]["current_status"]
                    if current_status != "error":
                        self.update_status_label(email, "hidden", "Đã đăng nhập thành công (đang ẩn).")
                    else:
                        self.update_status_label(email, current_status, self.profile_status_labels[email]["message_label"].cget("text"))
                logging.info(f"Tác vụ chạy đơn cho {email} đã hoàn thành.")
        except asyncio.CancelledError:
            self.update_status_label(email, "error", "Tác vụ đã bị hủy.")
            logging.info(f"Tác vụ cho {email} đã bị hủy.")
        except Exception as e:
            self.update_status_label(email, "error", f"Lỗi tác vụ: {e}")
            logging.error(f"Lỗi trong tác vụ chạy đơn cho {email}: {e}", exc_info=True)
        finally:
            if email in self.profile_tasks:
                del self.profile_tasks[email]

    def run_all_profiles(self):
        if not self.profiles:
            messagebox.showwarning("Không có hồ sơ", "Vui lòng thêm hồ sơ trước khi chạy.")
            return

        for email, task in list(self.profile_tasks.items()):
            if not task.done():
                task.cancel()
                logging.info(f"Đã hủy tác vụ {email} khi chạy tất cả hồ sơ.")
                del self.profile_tasks[email]

        self.loop.create_task(self._run_all_profiles_task())
        logging.info("Đã tạo tác vụ chạy tất cả hồ sơ.")

    async def _run_all_profiles_task(self):
        tasks_to_run = []
        if self.playwright_global_instance is None:
            logging.info("Khởi tạo Playwright global instance cho chạy tất cả hồ sơ.")
            self.playwright_global_instance = await async_playwright().start()

        for email, data in self.profiles.items():
            self.update_status_label(email, "pending", "Đang chờ...")
            if email not in self.pause_events:
                self.pause_events[email] = asyncio.Event()
            self.pause_events[email].set()

            task = self.loop.create_task(self._constrained_login_task(email, data, self.pause_events[email]))
            self.profile_tasks[email] = task
            tasks_to_run.append(task)
            logging.info(f"Đã thêm tác vụ cho {email} vào hàng đợi.")

        if tasks_to_run:
            await asyncio.gather(*tasks_to_run, return_exceptions=True)
            messagebox.showinfo("Hoàn tất chạy", "Đã hoàn thành chạy tất cả hồ sơ.")
            logging.info("Tất cả tác vụ chạy hồ sơ đã hoàn thành.")
        else:
            messagebox.showinfo("Hoàn tất", "Không có hồ sơ mới nào để chạy.")
            logging.info("Không có hồ hồ sơ mới nào để chạy.")

    async def _constrained_login_task(self, email, data, pause_event: asyncio.Event):
        try:
            async with self.semaphore:
                await login_gmail_async(
                    self.playwright_global_instance,
                    email,
                    data["password"],
                    data["playwright_profile_dir"],
                    self.update_status_label,
                    self.active_browsers,
                    pause_event
                )
                if email in self.active_browsers:
                    current_status = self.profile_status_labels[email]["current_status"]
                    if current_status != "error":
                        self.update_status_label(email, "hidden", "Đã đăng nhập thành công (đang ẩn).")
                    else:
                        self.update_status_label(email, current_status, self.profile_status_labels[email]["message_label"].cget("text"))
        except asyncio.CancelledError:
            self.update_status_label(email, "error", "Tác vụ đã bị hủy.")
            logging.info(f"Tác vụ bị hủy cho {email} trong constrained login task.")
        except Exception as e:
            self.update_status_label(email, "error", f"Lỗi tác vụ: {e}")
            logging.error(f"Lỗi trong constrained login task cho {email}: {e}", exc_info=True)
        finally:
            if email in self.profile_tasks:
                del self.profile_tasks[email]

    def update_status_label(self, email, status, message):
        self.after(0, self._update_status_label_ui, email, status, message)

    def _update_status_label_ui(self, email, status, message):
        if email not in self.profile_status_labels:
            status_row_frame = ctk.CTkFrame(self.running_status_frame, fg_color="transparent")
            status_row_frame.pack(fill="x", padx=5, pady=2)

            status_row_frame.grid_columnconfigure(0, weight=1)
            status_row_frame.grid_columnconfigure(1, weight=2)
            status_row_frame.grid_columnconfigure(2, weight=0)

            email_label = ctk.CTkLabel(status_row_frame, text=email, anchor="w", font=ctk.CTkFont(weight="bold"))
            email_label.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

            message_label = ctk.CTkLabel(status_row_frame, text=message, anchor="w",
                                        text_color=STATUS_COLOR.get(status, "white"))
            message_label.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

            control_buttons_frame = ctk.CTkFrame(status_row_frame, fg_color="transparent")
            control_buttons_frame.grid(row=0, column=2, padx=5, pady=2, sticky="e")
            control_buttons_frame.grid_columnconfigure((0,1,2), weight=0)

            pause_resume_button = ctk.CTkButton(control_buttons_frame, text="Tạm dừng", width=70,
                                                command=lambda e=email: self.toggle_pause_resume(e),
                                                fg_color="#8E44AD", hover_color="#9B59B6", corner_radius=6)
            pause_resume_button.grid(row=0, column=0, padx=3, pady=2)

            view_hide_button = ctk.CTkButton(control_buttons_frame, text="Hiện", width=50,
                                                command=lambda e=email: self.loop.create_task(self.toggle_browser_visibility(e)),
                                                fg_color="#2980B9", hover_color="#3498DB", corner_radius=6)
            view_hide_button.grid(row=0, column=1, padx=3, pady=2)

            close_button = ctk.CTkButton(control_buttons_frame, text="Đóng", width=50,
                                         command=lambda e=email: self.close_single_browser_command(e),
                                         fg_color="#E74C3C", hover_color="#C0392B", corner_radius=6)
            close_button.grid(row=0, column=2, padx=3, pady=2)


            self.profile_status_labels[email] = {
                "frame": status_row_frame,
                "message_label": message_label,
                "pause_resume_button": pause_resume_button,
                "view_hide_button": view_hide_button,
                "current_status": status
            }
            logging.info(f"Đã tạo hiển thị trạng thái cho {email}: {message} ({status}).")
        else:
            label_data = self.profile_status_labels[email]
            if label_data["frame"].winfo_exists():
                label_data["message_label"].configure(text=message, text_color=STATUS_COLOR.get(status, "white"))
                label_data["current_status"] = status
                if status == "paused":
                    label_data["pause_resume_button"].configure(text="Tiếp tục", fg_color="#2ECC71", hover_color="#28B463")
                else:
                    label_data["pause_resume_button"].configure(text="Tạm dừng", fg_color="#8E44AD", hover_color="#9B59B6")

                if email in self.active_browsers and (status == "running" or status == "success" or status == "paused" or status == "hidden"):
                    label_data["view_hide_button"].configure(state="normal")
                    if status == "hidden":
                        label_data["view_hide_button"].configure(text="Hiện", fg_color="#2980B9", hover_color="#3498DB")
                    elif status in ["running", "success", "paused"]:
                        label_data["view_hide_button"].configure(text="Ẩn", fg_color="#F39C12", hover_color="#E67E22")
                else:
                    label_data["view_hide_button"].configure(state="disabled", text="Hiện", fg_color="gray", hover_color="gray")

                logging.debug(f"Cập nhật trạng thái cho {email}: {message} ({status}).")
            else:
                logging.warning(f"Frame trạng thái cho {email} không tồn tại khi cố gắng cập nhật. Tạo lại.")
                del self.profile_status_labels[email]
                self._update_status_label_ui(email, status, message)

    def toggle_pause_resume(self, email: str):
        if email not in self.pause_events:
            logging.warning(f"Không tìm thấy sự kiện tạm dừng cho {email}.")
            return

        event = self.pause_events[email]
        if event.is_set():
            event.clear()
            self.update_status_label(email, "paused", "Đã tạm dừng.")
            logging.info(f"Đã tạm dừng tác vụ cho {email}.")
        else:
            event.set()
            current_displayed_status = self.profile_status_labels[email]["current_status"]
            if current_displayed_status == "hidden":
                 self.update_status_label(email, "hidden", "Đang tiếp tục (đang ẩn).")
            else:
                 self.update_status_label(email, "running", "Đang tiếp tục.")
            logging.info(f"Đã tiếp tục tác vụ cho {email}.")


    async def toggle_browser_visibility(self, email: str):
        if email not in self.active_browsers:
            messagebox.showwarning("Thông báo", f"Trình duyệt cho '{email}' hiện không hoạt động.")
            return

        browser_context = self.active_browsers[email]
        if not browser_context.pages:
            messagebox.showwarning("Thông báo", f"Không tìm thấy trang nào trong trình duyệt cho '{email}'.")
            return

        page = browser_context.pages[0]
        label_data = self.profile_status_labels.get(email)
        if not label_data: return

        current_status = label_data["current_status"]
        logging.info(f"[{email}] Yêu cầu chuyển đổi hiển thị. Trạng thái hiện tại: {current_status}")

        label_data["view_hide_button"].configure(state="disabled", text="...", fg_color="gray")

        try:
            if current_status == "hidden":
                logging.info(f"[{email}] Đang hiện cửa sổ trình duyệt...")
                await page.evaluate("window.moveTo(10, 10);")
                await page.bring_to_front()
                self.update_status_label(email, "running", "Đã hiện trình duyệt.")
                logging.info(f"[{email}] Đã hiện trình duyệt.")
            else:
                logging.info(f"[{email}] Đang ẩn cửa sổ trình duyệt...")
                await page.evaluate("window.moveTo(20000, 20000);")
                # Đảm bảo làm mất focus nếu có thể
                if sys.platform == "win32":
                    try:
                        # Thử dùng win32api nếu có, cần cài đặt: pip install pywin32
                        import win32gui
                        import win32con
                        hwnd = win32gui.GetForegroundWindow()
                        # Thu nhỏ cửa sổ hiện tại (nếu là cửa sổ trình duyệt)
                        # Có thể cần tìm cửa sổ của chromium.exe/msedge.exe
                        # win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                        # Hoặc gửi tín hiệu mất focus
                        # win32gui.SetForegroundWindow(self.winfo_id()) # Đưa cửa sổ app lên trước
                    except ImportError:
                        pass # Không có pywin32, bỏ qua
                await page.main_frame.evaluate("window.blur();") # Chỉ làm mất focus trên tab
                self.update_status_label(email, "hidden", "Đã ẩn trình duyệt.")
                logging.info(f"[{email}] Đã ẩn trình duyệt.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chuyển đổi hiển thị cho '{email}': {e}.")
            logging.error(f"Lỗi khi chuyển đổi hiển thị cho '{email}': {e}", exc_info=True)
            self.update_status_label(email, "error", f"Lỗi hiển thị: {e}")
        finally:
            if email in self.profile_status_labels and self.profile_status_labels[email]["frame"].winfo_exists():
                final_status = self.profile_status_labels[email]["current_status"]
                if final_status == "hidden":
                    label_data["view_hide_button"].configure(state="normal", text="Hiện", fg_color="#2980B9", hover_color="#3498DB")
                elif final_status in ["running", "success", "paused"]:
                    label_data["view_hide_button"].configure(state="normal", text="Ẩn", fg_color="#F39C12", hover_color="#E67E22")
                else:
                    label_data["view_hide_button"].configure(state="disabled", text="Hiện", fg_color="gray", hover_color="gray")

    def close_single_browser_command(self, email: str):
        if email not in self.active_browsers:
            messagebox.showinfo("Thông báo", f"Trình duyệt cho '{email}' hiện không mở hoặc đã bị đóng.")
            self.update_status_label(email, "closed", "Trình duyệt đã đóng.")
            return

        if messagebox.askyesno("Xác nhận đóng", f"Bạn có muốn đóng trình duyệt cho '{email}' không?"):
            if email in self.profile_tasks and not self.profile_tasks[email].done():
                self.profile_tasks[email].cancel()
                logging.info(f"Đã hủy tác vụ {email} để đóng trình duyệt.")
                del self.profile_tasks[email]

            browser_context = self.active_browsers[email]
            self.loop.create_task(self._close_single_browser_context_task(email, browser_context))
            logging.info(f"Yêu cầu đóng trình duyệt cho {email}.")

    def close_all_active_browsers_command(self):
        if not self.active_browsers:
            messagebox.showinfo("Thông báo", "Không có trình duyệt nào đang mở để đóng.")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có muốn đóng tất cả các trình duyệt Gmail đang mở không?"):
            for email, task in list(self.profile_tasks.items()):
                if not task.done():
                    task.cancel()
                    logging.info(f"Đã hủy tác vụ {email} khi đóng tất cả trình duyệt.")
                del self.profile_tasks[email]

            self.loop.create_task(self.close_all_active_browsers())
            logging.info("Yêu cầu đóng tất cả trình duyệt đang hoạt động.")

    async def close_all_active_browsers(self):
        closed_count = 0
        tasks = []
        emails_to_close_and_remove = list(self.active_browsers.keys())

        for email in emails_to_close_and_remove:
            if email in self.active_browsers:
                browser_context = self.active_browsers[email]
                tasks.append(self._close_single_browser_context_task(email, browser_context))
                logging.info(f"Đã thêm tác vụ đóng cho {email}.")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            closed_count = len(emails_to_close_and_remove)

        if self.playwright_global_instance:
            try:
                if not self.playwright_global_instance.is_stopped:
                    await self.playwright_global_instance.stop()
                    self.playwright_global_instance = None
                    logging.info("Playwright global instance stopped.")
            except Exception as e:
                logging.error(f"Lỗi khi dừng Playwright instance: {e}", exc_info=True)

        if closed_count > 0:
            messagebox.showinfo("Thành công", f"Đã đóng {closed_count} trình duyệt.")
            logging.info(f"Đã đóng {closed_count} trình duyệt.")
        else:
            messagebox.showinfo("Hoàn tất", "Không có trình duyệt nào được đóng (có thể đã đóng trước đó).")
            logging.info("Không có trình duyệt nào được đóng.")

    async def _close_single_browser_context_task(self, email, browser_context: BrowserContext):
        try:
            await browser_context.close()
            logging.info(f"Đã đóng trình duyệt cho: {email}")
        except PlaywrightError as e:
            logging.warning(f"Trình duyệt cho {email} có thể đã đóng hoặc mất kết nối: {e}")
        except Exception as e:
            logging.error(f"Lỗi khi đóng trình duyệt cho {email}: {e}", exc_info=True)
            self.update_status_label(email, "error", f"Lỗi đóng: {e}")
        finally:
            if email in self.active_browsers:
                del self.active_browsers[email]
            self.update_status_label(email, "closed", "Trình duyệt đã đóng.")


# --- Chạy ứng dụng ---
async def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app = GmailLoginApp(loop)
    logging.info("Ứng dụng GUI đã khởi tạo.")

    async def main_loop_task():
        while True:
            if not app.winfo_exists():
                logging.info("Cửa sổ Tkinter đã đóng, dừng vòng lặp UI.")
                break
            try:
                app.update_idletasks()
                app.update()
            except ctk.CTK.TclError as e:
                logging.warning(f"Lỗi khi cập nhật UI, có thể cửa sổ đã đóng: {e}")
                break
            await asyncio.sleep(0.01)

    def on_closing():
        logging.info("Người dùng đã yêu cầu đóng ứng dụng.")
        asyncio.create_task(app.close_all_active_browsers())
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        await main_loop_task() 
    except asyncio.CancelledError:
        logging.info("Vòng lặp sự kiện đã bị hủy.")
    except Exception as e:
        logging.critical(f"Ứng dụng gặp lỗi nghiêm trọng: {e}", exc_info=True)
    finally:
        if app.playwright_global_instance:
            try:
                if not app.playwright_global_instance.is_stopped:
                    await app.playwright_global_instance.stop()
                    logging.info("Playwright global instance stopped during final cleanup.")
            except Exception as e:
                logging.error(f"Lỗi khi dừng Playwright global instance trong finally: {e}", exc_info=True)
        logging.info("Ứng dụng đã thoát hoàn toàn.")


if __name__ == "__main__":
    logging.info("Khởi động ứng dụng bằng asyncio.run().")
    asyncio.run(main())
