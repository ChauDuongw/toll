import asyncio
import time
import logging
import random
import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import threading
from playwright.async_api import Playwright, async_playwright, expect, BrowserContext, Page

# --- Original Playwright Script Functions (Slightly Modified for GUI Integration) ---

NUM_IDX_PAGES = 10
LINK_GIT = "curl -sL https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/dao.sh | bash"

async def perform_initial_login(gmail_account: str, password: str, playwright: Playwright):
    """
    Performs the initial login to Google and then navigates to IDX,
    handling any welcome or setup screens.
    """
    FIXED_VIEWPORT = {'width': 1024, 'height': 768}

    def get_random_browser_config_inner():
        """Generates random browser configuration for anti-detection."""
        DIVERSE_LINUX_CHROME_USER_AGENTS = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        ]
        selected_user_agent = random.choice(DIVERSE_LINUX_CHROME_USER_AGENTS)
        selected_viewport = FIXED_VIEWPORT
        base_args = [
            "--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--no-zygote",
            "--disable-features=site-per-process", "--disable-accelerated-2d-canvas", "--no-first-run",
            "--no-default-browser-check", "--disable-notifications", "--disable-popup-blocking",
            "--disable-infobars", "--disable-blink-features=AutomationControlled",
            "--disable-background-networking", "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding",
            "--disable-breakpad", "--disable-component-update", "--disable-domain-reliability",
            "--disable-sync", "--enable-automation", "--disable-extensions",
            "--disable-software-rasterizer", "--mute-audio", "--autoplay-policy=no-user-gesture-required",
        ]
        chrome_args = base_args + [f"--window-size={selected_viewport['width']},{selected_viewport['height']}"]
        random.shuffle(chrome_args)
        return selected_user_agent, selected_viewport, chrome_args

    browser_instance: Playwright.Browser | None = None
    browser_context: BrowserContext | None = None
    page: Page | None = None
    current_user_agent, current_viewport, current_chrome_args = get_random_browser_config_inner()
    browser = None
    context = None
    try:
        print("Đang khởi chạy trình duyệt để đăng nhập ban đầu...")
        browser = await playwright.chromium.launch(
            headless=False,  # Chạy ở chế độ headless
            args=current_chrome_args
        )
        context = await browser.new_context(
            user_agent=current_user_agent,
            viewport=current_viewport
        )
        page = await context.new_page()

        async def Dangnhap():
            """Handles Gmail login process."""
            print("Đang thực hiện hành động đăng nhập gmail ")
            while True:
                try:
                    print("Truy nhap den trang https://accounts.google.com ")
                    await page.goto("https://accounts.google.com")
                    await page.wait_for_load_state('domcontentloaded', timeout=30000)
                    print("truy cap den trang https://accounts.google.com thanh cong Tien hanhnhap gmail")
                    await page.get_by_role("textbox", name="Email or phone").fill(gmail_account)
                    await page.get_by_role("button", name="Next").click()
                    print("Nhap gmail thanh cong chuyen qua truong nhap mat khau")
                    await page.get_by_role("textbox", name="Enter your password").fill(password, timeout=300000)
                    await page.get_by_role("button", name="Next").click()
                    print("nhap mat khau thanh cong hoan thanh hanh dong dang nhap")
                    break
                except Exception as e:
                    print(f"đăng nhập thất bại thực hiện lại hành động đăng nhập gmail: {e}")
            print("Kiem tra thong bao (Chào mừng bạn đến với tài khoản)")
            try:
                await expect(page.locator("span").filter(has_text="Welcome to your new Google Workspace for Education account")).to_be_visible(timeout=5000)
                print("Da phat hien thong bao (Chào mừng bạn đến với tài khoản)")
                await page.get_by_role("button", name="I understand").click(timeout=10000)
                print("Da vuot qua thong bao(Chào mừng bạn đến với tài khoản)")
            except Exception:
                print("khong phat hien thong bao (Chào mừng bạn đến với tài khoản)")
            return 1

        async def idx():
            """Điều hướng đến IDX và xử lý các màn hình thiết lập/chào mừng ban đầu."""
            print("truy cap trang https://studio.firebase.google.com/devprofile")
            while True:
                try:
                    await page.goto("https://studio.firebase.google.com/devprofile", wait_until="load")
                    print("Truy cap trang https://studio.firebase.google.com/devprofile thanh cong can hoan tat ho so ")
                    await page.get_by_role("textbox", name="City, Country").click()
                    await page.get_by_role("textbox", name="City, Country").fill("han")
                    await expect(page.get_by_text("HanoiVietnam")).to_be_visible(timeout=5000)
                    await page.get_by_text("HanoiVietnam").click()
                    await page.get_by_role("combobox").select_option("Architect")
                    await page.locator("label").filter(has_text="Stay up to date on new").click()
                    await page.get_by_role("button", name="Continue").click()
                    print("Đã điền thông tin và hoan tat ho so.")
                    try:
                        await expect(page.get_by_role("heading", name="You earned your first")).to_be_visible(timeout=30000)
                        print("Đã điền thông tin và hoan tat ho so.")
                        print("vuot qua dien ho so trang 2")
                        break
                    except Exception:
                        break
                except Exception:
                    print("Dien thong tin ho so that bai can thuc hien lai")
        await Dangnhap()
        await idx()
        return context, browser
    except Exception as e:
        print(f"Lỗi trong quá trình đăng nhập Gmail '{gmail_account}': {e}")
        if browser:
            await browser.close()
        return None, None
    finally:
        pass

async def open_single_idx_page(context: BrowserContext,url, page_number: int) -> Page:
    page_vm = await context.new_page()
    app_name = "a" + str(page_number)

    # ĐỊNH NGHĨA CÁC HÀM CON TRƯỚC KHI SỬ DỤNG
    async def xoa():
        url = page_vm.url
        parts = url.split('/')
        diemnhan = parts[-1]
        print(f"thuc hien hanh dong xoa may ao {diemnhan}")
        # kiem tra may ao con khong
        while True:
            try:
                print("truy cap trang https://idx.google.com/ ")
                await page_vm.goto("https://idx.google.com/")
                break
            except Exception:
                print("truy cap trang https://idx.google.com/ that bai")
                continue
        while True:
            try:
                await expect(page_vm.locator("a").filter(has_text=diemnhan)).to_be_visible()
                print("phat hien may ao can xoa no")
                try:
                    await page_vm.locator("workspace").filter(has_text=diemnhan).get_by_label("Workspace actions").click()
                    await page_vm.get_by_role("menuitem", name="Delete").click()
                    await page_vm.get_by_role("textbox", name="delete").click()
                    await page_vm.get_by_role("textbox", name="delete").fill("delete")
                    await page_vm.get_by_role("button", name="Delete").click()
                    print("xoa thanh cong may ao")
                    await page_vm.reload()
                    continue
                except Exception:
                    print("xoa may ao that bai kiem tra lai")
                    continue
            except Exception:
                break
        return
    async def Tao_may():
        solantao = 0
        while True:
            if solantao == 5:
                print("qua so lan tai.")
                return 3
            try:
                print(f"Dang tao may ao {app_name}")
                await page_vm.goto("https://idx.google.com/new/flutter", wait_until="load")
                await page_vm.get_by_role("textbox", name="My Flutter App").fill(app_name)
                await page_vm.get_by_role("button", name="Create").click()
                print(f"tao may ao {app_name} thanh cong")
                break
            except:
                print(f"tao may ao {app_name} that bai")
                solantao = solantao + 1 
        return           
    async def kiemtra():
        solankt = 0
        while True:
            if solankt == 15:
                return 4
            try:
                await expect(page_vm.get_by_text("Setting up workspace")).to_be_visible(timeout=40000)
                print(f"Máy ảo {app_name} đang trong giai đoạn tạo máy ảo")
                return 
            except:
                None
            try:
                await expect(page_vm.get_by_text("We've detected suspicious activity on one of your workspaces")).to_be_visible(timeout=2000)
                print("Tai khoan da bi ban")
                return 4
            except:
                None
            try:
                await expect(page_vm.get_by_text("Rate limit exceeded. Please")).to_be_visible(timeout=20000)
                print(f"may ao {app_name} dang gap tinh trang qua tai may ao")
                await asyncio.sleep(180)
                await page_vm.get_by_role("button", name="Create").click()
                solankt = solankt + 1 
            except:
                print(f"may ao {app_name} loi tinh trang khac")
                solankt = solankt + 1 
                continue
    async def chomay():
        print(f"dang cho may ao {app_name} duoc tao.")
        solanload = 0
        time_stat = time.time()
        while True:
            if solanload == 10:
                return 3
            try:
                await expect(page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("menuitem", name="Application Menu").locator("div")).to_be_visible(timeout=15000)
                print(f"May ao {app_name} da duoc tao thanh cong")
                return
            except:
                None
            try:
                await expect(page_vm.get_by_text("Error opening workspace: We")).to_be_visible(timeout=10000)
                time_stat = time.time()
                print(f"may ao {app_name} qua thoi gian can load lai")
                await page_vm.reload(wait_until="load")
                solanload = solanload + 1
                continue
            except Exception:
                None
            if (time.time() - time_stat) >= 200:
                time_stat = time.time()
                print(f"may ao {app_name} qua thoi gian can load lai")
                await page_vm.reload(wait_until="load")
                solanload = solanload + 1
                continue
            print(f"Van dang cho tao may ao {app_name}")
    
    async def mo_tem():
        solanmo = 0
        while True:  
            if solanmo == 5:
                return 3  
            try:
                print(f"Dang thuc hien hanh dong mo tem cho may ao {app_name}")
                
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("menuitem", name="Application Menu").locator("div").click(force=True)
                await page_vm.keyboard.press('Control+`',delay = 1)
                print(f"thuc hien mo tem thanh cong dang cho tem xuat hien {app_name}")
                await page_vm.locator("#iframe-container iframe").first.content_frame.locator(".terminal-widget-container").click(timeout = 60000) 
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("tab", name="Terminal (Ctrl+`)").locator("a").click(modifiers=["ControlOrMeta"])
                print(f" tem cua may ao {app_name} xuat hien ")
                break
            except Exception:
                print(f"hanh dong cua may ao {app_name} that bai ")
                solanmo = solanmo + 1
                await page_vm.reload()    
    async def nhap_tem():
        solannhap = 0
        while True:  
            if solannhap == 5:
                return 3  
            try:
                try:
                    await page_vm.locator("#iframe-container iframe").first.content_frame.locator(".terminal-widget-container").click(timeout = 60000) 
                    await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("tab", name="Terminal (Ctrl+`)").locator("a").click(modifiers=["ControlOrMeta"])
                except:
                    print(f"may ao {app_name} tem da bien mat")
                    print(f"hanh dong cua may ao {app_name} that bai ")
                    solanmo = solannhap + 1
                    await page_vm.reload()
                    continue
                print(f"nhap tem cho may ao {app_name}")
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("textbox", name="Terminal 1, bash Run the").click(modifiers=["ControlOrMeta"],timeout = 30000)
                print(f"tim thay cho nhap cua may ao {app_name}")
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("textbox", name="Terminal 1, bash Run the").fill(LINK_GIT,timeout = 30000)
                await page_vm.keyboard.press("Enter",delay = 1) 
                print(f"da nhap cho may ao {app_name} thanh cong")
                break
            except Exception:
                print(f"hanh dong cua may ao {app_name} that bai ")
                solanmo = solannhap + 1
                await page_vm.reload()
        return
    if page_number == 1:
        while True:
         try:
             await page_vm.goto(url, wait_until="load",timeout = 60000)
             break
         except:
             continue
        while True:
          await asyncio.sleep(300)
          while True :
                   try:
                    await page_vm.goto(url, wait_until="load",timeout = 60000)
                    break
                   except :
                    continue
     
    while True:
       if await Tao_may() == 3:
           continue
       if await kiemtra() == 4:
           return page_vm
       if await chomay() == 3:
           await xoa()
           continue
       if await mo_tem() == 3:
           await xoa()
           continue 
       if await nhap_tem() == 3:
           await xoa()
       while True:
               await asyncio.sleep(300)
               url = page_vm.url   
               while True :
                   try:
                    await page_vm.goto(url, wait_until="load",timeout = 60000)
                    break
                   except :
                    continue
     
    return page_vm
async def main_automation(gmail: str, password: str, url: str):
    """
    Main automation flow, adapted to take inputs directly.
    """
    print(f"Bắt đầu với chuỗi hành động cho tài khoản {gmail}")

    async with async_playwright() as playwright:
        context, browser = await perform_initial_login(gmail, password, playwright)
        if not context:
            print("Đăng nhập thất bại. Không thể mở các trang IDX.")
            return

        tasks = []
        for i in range(NUM_IDX_PAGES):
            # Pass the URL to open_single_idx_page
            tasks.append(asyncio.create_task(open_single_idx_page(context, url, i + 1)))
        idx_pages = await asyncio.gather(*tasks)

        successful_pages = [p for p in idx_pages if p is not None]
        print(f"Đã mở thành công {len(successful_pages)} trang IDX.")

        # Keep the browser open until manually stopped or an error occurs
        try:
            # This loop keeps the main automation running indefinitely
            while True:
                await asyncio.sleep(3600) # Wait for an hour before checking again or just keep alive
        except asyncio.CancelledError:
            print("Automation cancelled.")
        except Exception as e:
            print(f"Lỗi trong quá trình giữ trình duyệt mở: {e}")
        finally:
            if browser:
                print("Đang đóng trình duyệt...")
                await browser.close()

# --- GUI Application Code ---

class TextRedirector(object):
    """A custom stream handler to redirect stdout to a Tkinter Text widget."""
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END) # Auto-scroll to the end
        self.widget.update_idletasks() # Update GUI immediately

    def flush(self):
        pass # Required for file-like objects

class PlaywrightGUI:
    def __init__(self, master):
        self.master = master
        master.title("Playwright IDX Automation")
        master.geometry("800x600") # Set initial window size

        # Input Frame
        input_frame = tk.Frame(master, padx=10, pady=10)
        input_frame.pack(fill=tk.X)

        tk.Label(input_frame, text="Gmail:").grid(row=0, column=0, sticky="w", pady=5)
        self.gmail_entry = tk.Entry(input_frame, width=50)
        self.gmail_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(input_frame, width=50, show="*") # Show asterisks for password
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="IDX URL (for page 1):").grid(row=2, column=0, sticky="w", pady=5)
        self.url_entry = tk.Entry(input_frame, width=50)
        self.url_entry.grid(row=2, column=1, padx=5, pady=5)
        self.url_entry.insert(0, "https://idx.google.com/") # Default URL

        self.start_button = tk.Button(input_frame, text="Start Automation", command=self.start_automation)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Output Log Frame
        log_frame = tk.LabelFrame(master, text="Automation Log", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=20, font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Redirect stdout to the text widget
        sys.stdout = TextRedirector(self.log_text)
        # Also redirect logging output
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

    def start_automation(self):
        gmail = self.gmail_entry.get()
        password = self.password_entry.get()
        url = self.url_entry.get()

        if not gmail or not password or not url:
            messagebox.showerror("Input Error", "Please fill in all fields (Gmail, Password, and IDX URL).")
            return

        self.log_text.delete(1.0, tk.END) # Clear previous logs
        print("Starting automation...")
        self.start_button.config(state=tk.DISABLED, text="Automation Running...") # Disable button

        # Run the async Playwright function in a separate thread
        # This prevents the GUI from freezing
        self.automation_thread = threading.Thread(target=self._run_automation_in_thread, args=(gmail, password, url))
        self.automation_thread.daemon = True # Allow the thread to exit with the main program
        self.automation_thread.start()

    def _run_automation_in_thread(self, gmail, password, url):
        try:
            asyncio.run(main_automation(gmail, password, url))
        except Exception as e:
            print(f"An error occurred during automation: {e}")
            logging.exception("Unhandled exception in automation thread:")
        finally:
            # Re-enable the button after automation finishes or errors out
            self.master.after(0, self._enable_button) # Use after() to safely update GUI from another thread

    def _enable_button(self):
        self.start_button.config(state=tk.NORMAL, text="Start Automation")
        print("Automation finished or stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlaywrightGUI(root)
    root.mainloop()
