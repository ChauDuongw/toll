import asyncio
import threading
import logging
import random
import tkinter as tk
from tkinter import ttk, scrolledtext
import time

from playwright.async_api import async_playwright, Playwright, BrowserContext, Page,expect

# --- Playwright automation functions (modified to send notifications to GUI) ---

async def perform_initial_login(GMAIL, MAT_KHAU, playwright: Playwright, log_callback, stop_event: threading.Event):
    FIXED_VIEWPORT = {'width': 1024, 'height': 768}
    def get_random_browser_config_inner():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
    try:
        browser = await playwright.chromium.launch(
                headless= False, # Chạy ở chế độ headless
                args=current_chrome_args)
        context = await browser.new_context(
                user_agent=current_user_agent,
                viewport=current_viewport)
        page = await context.new_page()

        log_callback("Đang truy cập tài khoản Google để đăng nhập...", "general")
        while True:
            await page.goto("https://accounts.google.com")
            if stop_event.is_set():
                log_callback("Đã nhận tín hiệu dừng. Đang dừng tải trang.", "general")
                return None, None
            try:
                # Using the timeout from the provided snippet, which is 30s
                await page.wait_for_load_state('domcontentloaded', timeout=30000)
                break
            except Exception:
                log_callback("Tải trang đăng nhập Google bị lỗi, đang reload...", "general")
                await page.reload()

        log_callback("Đang chờ form đăng nhập xuất hiện...", "general")
        max_retries = 3
        for attempt in range(max_retries):
            if stop_event.is_set():
                log_callback("Đã nhận tín hiệu dừng. Đang dừng chờ form đăng nhập.", "general")
                return None, None
            try:
                # Using the timeout from the provided snippet, which is 120s
                await expect(page.get_by_text("Sign inUse your Google Account")).to_be_visible(timeout=120000)
                break
            except Exception:
                log_callback(f"Không tìm thấy form đăng nhập (thử {attempt+1}/{max_retries}), đang thử goto lại...", "general")
                # Using specific URL from snippet
                await page.goto("https://accounts.google.com/v3/signin")
                if attempt == max_retries - 1:
                    raise Exception("Không thể tìm thấy form đăng nhập sau nhiều lần thử.")
        await asyncio.sleep(random.uniform(0.5, 3))
        await page.get_by_role("textbox", name="Email or phone").type(GMAIL, delay = random.uniform(0.5, 1))
        await asyncio.sleep(random.uniform(0.5, 3))
        await page.get_by_role("button", name="Next").click()

        log_callback("Đang chờ trường mật khẩu...", "general")

        try:
            if stop_event.is_set():
                log_callback("Đã nhận tín hiệu dừng. Đang dừng kiểm tra tài khoản.", "general")
                return None, None
            # Keep existing check for "Couldn't find your Google Account"
            await expect(page.locator('div[aria-live="assertive"]')).to_have_text("Couldn't find your Google Account", timeout=5000)
            log_callback("Lỗi: Không tìm thấy tài khoản Google của bạn.", "general")
            if browser:
                await browser.close()
            return None, None
        except Exception:
            pass # No error, continue

        # Using timeout from snippet for password fill (300s, will cap at Playwright default if too high)
        await asyncio.sleep(random.uniform(0.5, 3))
        await page.get_by_role("textbox", name="Enter your password").type(MAT_KHAU, delay = random.uniform(0.5, 1)  , timeout=300000)
        await asyncio.sleep(random.uniform(0.5, 3))
        await page.get_by_role("button", name="Next").click()

        try:
            if stop_event.is_set():
                log_callback("Đã nhận tín hiệu dừng. Đang dừng chờ thông báo chào mừng.", "general")
                return None, None
            # Using timeout from snippet for welcome message (100s)
            await expect(page.locator("span").filter(has_text="Welcome to your new Google Workspace for Education account")).to_be_visible(timeout=100000)
            log_callback("Phát hiện thông báo 'Chào mừng bạn đến với tài khoản', đang click 'Tôi hiểu'.", "general")
            # Using timeout from snippet for 'Tôi hiểu' button (100s)
            await asyncio.sleep(random.uniform(0.5, 3))
            await page.get_by_role("button", name="I understand").click(timeout=100000)
        except Exception:
            log_callback("Không có thông báo 'Chào mừng' hoặc đã xử lý, đang thử goto IDX.", "general")

        await page.close()
        log_callback(f"Đăng nhập Gmail '{GMAIL}' thành công và session đã được lưu vào context.", "general")
        log_callback("Đang chờ chuyển hướng tới IDX...", "general")
        return context, browser
    except Exception as e:
        log_callback(f"Lỗi trong quá trình đăng nhập Gmail '{GMAIL}': {e}", "general")
        if browser:
            await browser.close()
        return None, None
    finally:
        if stop_event.is_set() and browser:
            await browser.close() # Ensure browser is closed on stop signal

async def handle_idx_initial_setup(context, log_callback, stop_event: threading.Event):
    if stop_event.is_set():
        log_callback("Đã nhận tín hiệu dừng.", "general")
        return
    page = await context.new_page()
    try:
        log_callback("Đang kiểm tra thông báo chào mừng Firebase Studio", "general")
        await page.goto("https://idx.google.com", wait_until="domcontentloaded")
        try:
            if stop_event.is_set():
                log_callback("Đã nhận tín hiệu dừng.", "general")
                return
            await expect(page.get_by_role("heading", name="Welcome to Firebase Studio, a")).to_be_visible(timeout=150000)
            log_callback("Phát hiện thông báo .", "general")
            element_locator = page.get_by_text("I accept the terms and")
            await expect(element_locator).to_be_visible()
            box = await element_locator.bounding_box()
            if box:
                offset_x = 5  
                offset_y = 5  
                x_click = box['x'] + offset_x
                y_click = box['y'] + offset_y
                x_click = max(box['x'], min(x_click, box['x'] + box['width'] - 1))
                y_click = max(box['y'], min(y_click, box['y'] + box['height'] - 1))
                await asyncio.sleep(random.uniform(0.5, 3))
                await element_locator.click(position={'x': offset_x, 'y': offset_y}, force=True)
            await asyncio.sleep(random.uniform(0.5, 3))
            await page.get_by_role("button", name="Confirm").click()
            log_callback("Đã click nút 'Confirm'.", "general")
            log_callback("Hoàn tất ","general" )

        except Exception:
            log_callback("Không có thông báo chào mừng .", "general")

        log_callback("Đang điền thông tin hồ sơ nhà phát triển", "general")
        while True: 
            if stop_event.is_set():
                log_callback("Đã nhận tín hiệu dừng.", "general")
                return
            try:
                await page.goto("https://studio.firebase.google.com/devprofile", wait_until="load")
                await asyncio.sleep(random.uniform(0.5, 3))
                await page.get_by_role("textbox", name="City, Country").click()
                await asyncio.sleep(random.uniform(0.5, 3))
                await page.get_by_role("textbox", name="City, Country").type("han", delay = random.uniform(0.5, 1)) 
                await expect(page.get_by_text("HanoiVietnam")).to_be_visible(timeout=5000)
                await asyncio.sleep(random.uniform(0.5, 3))
                await page.get_by_text("HanoiVietnam").click()
                await page.get_by_role("combobox").select_option("Architect") 
                await asyncio.sleep(random.uniform(0.5, 3))
                await page.locator("label").filter(has_text="Stay up to date on new").click()
                log_callback("Đã điền thông tin và chọn các tùy chọn dev profile.", "general")
                break 
            except Exception as e:
                log_callback(f"Lỗi khi điền form dev profile: {e}", "general")
        try: 
            if stop_event.is_set():
                log_callback("Đã nhận tín hiệu dừng. Đang dừng click Continue (1).", "general")
                return
            await asyncio.sleep(random.uniform(0.5, 3))
            await page.get_by_role("button", name="Continue").click()
            log_callback("Đã click nút 'Continue' .", "general")
        except Exception as e:
            log_callback(f"Lỗi khi click nút 'Continue' (1) trong form dev profile: {e}", "general")
        try:
            if stop_event.is_set():
                log_callback("Đã nhận tín hiệu dừng. Đang dừng chờ thông báo earned.", "general")
                return
            await expect(page.get_by_role("heading", name="You earned your first")).to_be_visible(timeout=30000)
            log_callback("Đã nhận được thông báo 'You earned your first'.", "general")
            await asyncio.sleep(random.uniform(0.5, 3))
            await page.get_by_role("button", name="Continue").click()
            log_callback("Đã click nút 'Continue' (2).", "general")
        except Exception as e:
            log_callback(f"Thông báo 'You earned your first' không xuất hiện hoặc lỗi khi click 'Continue' (2): {e}", "general")
            try:
                if stop_event.is_set():
                    log_callback("Đã nhận tín hiệu dừng.", "general")
                    return
                await asyncio.sleep(random.uniform(0.5, 3))
                await page.get_by_role("button", name="Continue").click(timeout=5000)
                log_callback("Đã thử click nút 'Continue' (2) .", "general")
            except Exception:
                pass 
    except Exception as e:
        log_callback(f"Lỗi trong quá trình xử lý thiết lập ban đầu của IDX: {e}", "general")
    finally:
        if page:
            await page.close()
async def create_virtual_machine(LINK_GIT, context, app_name: str, log_callback, stop_event: threading.Event, app_type: str = "flutter"):
    page_vm = None
    page_vm = await context.new_page() 
    
    async def xoa(page_vm):
            url = page_vm.url
            parts = url.split('/')
            diemnhan = parts[-1]
            await page_vm.goto("https://idx.google.com/")
            await asyncio.sleep(random.uniform(0.5, 3))
            await page_vm.locator("workspace").filter(has_text=diemnhan).get_by_label("Workspace actions").click()
            await asyncio.sleep(random.uniform(0.5, 3))
            await page_vm.get_by_role("menuitem", name="Delete").click()
            await asyncio.sleep(random.uniform(0.5, 3))
            await page_vm.get_by_role("textbox", name="delete").click()
            await asyncio.sleep(random.uniform(0.5, 3))
            await page_vm.get_by_role("textbox", name="delete").type("delete", delay = random.uniform(0.5, 1))
            await asyncio.sleep(random.uniform(0.5, 3))
            await page_vm.get_by_role("button", name="Delete").click()
    async def Tao_may(page_vm):
     if stop_event.is_set():
        log_callback(f"[{app_name}] Đã nhận tín hiệu dừng. Bỏ qua tạo máy ảo.", app_name)

     try:
        if app_type == "flutter":
            log_callback(f"[{app_name}] Đang tạo máy ảo Flutter App tên '{app_name}'...", app_name)
            await page_vm.goto("https://idx.google.com/new/flutter", wait_until="load")
            await asyncio.sleep(random.uniform(0.5, 3))
            await page_vm.get_by_role("textbox", name="My Flutter App").type(app_name, delay = random.uniform(0.5, 1))
            await asyncio.sleep(random.uniform(0.5, 3))
            await page_vm.get_by_role("button", name="Create").click()
        else:
            log_callback(f"[{app_name}] Lỗi: Loại app không hợp lệ: {app_type}", app_name)
            return
        try:
            if stop_event.is_set():
                log_callback(f"[{app_name}] Đã nhận tín hiệu dừng. Đang dừng kiểm tra ban.", app_name)
                return
            await expect(page_vm.get_by_text("We've detected suspicious activity on one of your workspaces")).to_be_visible(timeout=2000)
            log_callback(f"[{app_name}] tài khoản đã bị ban", app_name) # As in snippet
            return
        except Exception:
            asss = 1 
        while True:
            if stop_event.is_set():
                log_callback(f"[{app_name}] Đã nhận tín hiệu dừng. Đang dừng chờ quá tải.", app_name)
                return
            try:
                await expect(page_vm.get_by_text("Rate limit exceeded. Please")).to_be_visible(timeout=20000) # As in snippet
                log_callback(f"[{app_name}] Máy ảo đang gặp quá tải máy ảo", app_name) # As in snippet
                await asyncio.sleep(300) 
                await asyncio.sleep(random.uniform(0.5, 3))
                await page_vm.get_by_role("button", name="Create").click()
            except Exception:
                try: 
                    await expect(page_vm.get_by_text("Setting up workspace")).to_be_visible(timeout=20000) # As in snippet
                    log_callback(f"[{app_name}] Máy ảo đang trong giai đoạn tạo máy ảo", app_name) # As in snippet
                    break
                except Exception:
                    continue
        import time 
        time_start = time.time()
        a = 0 
        while True:
            if a == 7:
                a = 0
                await xoa(page_vm)
                await Tao_may(page_vm)
                await Tem(page_vm)
                return
            if stop_event.is_set():
                log_callback(f"[{app_name}] Đã nhận tín hiệu dừng. Đang dừng chờ tải máy ảo.", app_name)
            try:
                await expect(page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("menuitem", name="Application Menu").locator("div")).to_be_visible(timeout=15000) # As in snippet
                log_callback(f"[{app_name}] Máy ảo '{app_name}' đã load và Files Explorer hiển thị.", app_name)
                break
            except Exception as e:
                time_end = time.time()
                if time_end - time_start >= 180: 
                    log_callback(f"[{app_name}] hết thời gian chờ cần load lại trang", app_name)
                    await page_vm.reload()
                    time_start = time.time()
                    continue
                try:
                    await expect(page_vm.get_by_text("Error opening workspace: We")).to_be_visible(timeout=10000) 
                    log_callback(f"[{app_name}] Phát hiện lỗi 'Error opening workspace' cho '{app_name}', đang reload...", app_name) 
                    await page_vm.reload() 
                    time_start = time.time()
                except Exception:
                    log_callback(f"[{app_name}] Đang chờ máy ảo '{app_name}' load hoặc không phát hiện lỗi đặc biệt, tiếp tục chờ...", app_name) # As in snippet
                    await asyncio.sleep(2) 
     except Exception as e:
        log_callback(f"Lỗi chung trong quá trình tạo máy ảo '{app_name}': {e}", app_name)
        return       
     await page_vm.wait_for_load_state('load')
         # hàm làm việc với tem   
    async def Tem(page_vm):  # 1 là xóa 2 thành công 4 là dừng
     so_lan_load = 0
     try:   
        while True: # mo tem
            log_callback(f"[{app_name}] Thực hiện vòng lặp 1.", app_name)
            if stop_event.is_set():
              log_callback("Đã nhận tín hiệu dừng. Bỏ qua đăng nhập.", "general")
              return 
              break
            if so_lan_load == 5:
              so_lan_load = 0
              await xoa(page_vm)
              await Tao_may(page_vm)
              await Tem(page_vm)
              return
            if stop_event.is_set():
                log_callback(f"[{app_name}] Đã nhận tín hiệu dừng. Đang dừng mở Terminal.", app_name)
                return
            try:
                await asyncio.sleep(random.uniform(0.5, 3))
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("menuitem", name="Application Menu").locator("div").click(force=True)
                log_callback(f"[{app_name}] đã click vào menu .", app_name)
            except Exception :   
                log_callback(f"[{app_name}] đã click vào menu nhưng thất bại.", app_name)
                so_lan_load = so_lan_load + 1
                await page_vm.reload()
                await page_vm.wait_for_load_state('load')
                continue
            try:    
                await asyncio.sleep(random.uniform(0.5, 3))
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("menuitem", name="Terminal", exact=True).click(force=True)           
                log_callback(f"[{app_name}] Bước 2 thành công.", app_name)
            except Exception : 
                log_callback(f"[{app_name}] bước 2 trong mở tem thất bại.", app_name)
                so_lan_load = so_lan_load + 1
                await page_vm.reload()
                await page_vm.wait_for_load_state('load')  
                continue
            try:     
                await asyncio.sleep(random.uniform(0.5, 3))
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("menuitem", name="New Terminal Ctrl+Shift+C").click(force=True) 
                log_callback(f"[{app_name}] đã click mơ tem.", app_name)
            except Exception : 
                log_callback(f"[{app_name}] click mở tem  nhưng thất bại.", app_name)
                so_lan_load = so_lan_load + 1
                await page_vm.reload()
                await page_vm.wait_for_load_state('load')  
                continue
            try:   
                await expect(page_vm.locator("#iframe-container iframe").first.content_frame.locator(".terminal-wrapper")).to_be_visible(timeout=30000) 
                
                log_callback(f"[{app_name}] Đã có tem.", app_name)
                await asyncio.sleep(5) 
                break
            except Exception :
                so_lan_load = so_lan_load + 1
                log_callback(f"[{app_name}] không tìm thấy tem.", app_name)
                await page_vm.reload()
                await page_vm.wait_for_load_state('load')
                continue
        so_lan_load = 0
        while True:# điền githup
            log_callback(f"[{app_name}] Thực hiện vòng lặp 2.", app_name)
            if stop_event.is_set():
             log_callback("Đã nhận tín hiệu dừng. Bỏ qua đăng nhập.", "general")
             return None
            if so_lan_load == 5:
                so_lan_load = 0
                await xoa(page_vm)
                await Tao_may(page_vm)
                await Tem(page_vm)
                return
            if stop_event.is_set():
                log_callback(f"[{app_name}] Đã nhận tín hiệu dừng. Đang dừng nhập lệnh Git.", app_name)
                return
            try: 
                await asyncio.sleep(random.uniform(0.5, 3))
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("textbox", name="Terminal 1, bash Run the").click(modifiers=["ControlOrMeta"],timeout = 30000)
                await asyncio.sleep(random.uniform(0.5, 3))
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("textbox", name="Terminal 1, bash Run the").click(modifiers=["ControlOrMeta"],timeout = 30000)
            except Exception as e:
                so_lan_load = so_lan_load + 1
                log_callback(f"[{app_name}] Không tìm thấy chỗ nhập", app_name)
                await page_vm.reload()    
                await page_vm.wait_for_load_state('load')  
                continue
            try:    
                await asyncio.sleep(random.uniform(0.5, 3))
                await page_vm.locator("#iframe-container iframe").first.content_frame.get_by_role("textbox", name="Terminal 1, bash Run the").type(LINK_GIT,delay = random.uniform(0.5, 1),timeout = 30000)
                await page_vm.keyboard.press("Enter",delay = 1) 
                log_callback(f"[{app_name}] đã nhập xong.", app_name)                
                await asyncio.sleep(10)        
                log_callback(f"[{app_name}] Đã hoàn thành hành động.", app_name)
                break
            except Exception as e:
                so_lan_load = so_lan_load + 1
                log_callback(f"[{app_name}] Lỗi khi nhập lệnh Git: {e}. Đang reload...", app_name)
                await page_vm.reload()
                await page_vm.wait_for_load_state('load')  
                continue
        return  
     except Exception as e:
        log_callback(f"Lỗi chung trong quá trình tạo máy ảo '{app_name}': {e}", app_name)
    try:
     await Tao_may(page_vm)
     await Tem(page_vm)
     while True:
         if stop_event.is_set():
          log_callback("Đã nhận tín hiệu dừng. Bỏ qua đăng nhập.", "general")
          return None
         await asyncio.sleep(120)
         return
         try:
             await expect(page_vm.get_by_text("Setting up workspace")).to_be_visible(timeout=20000)
             return
         except Exception as e:
             continue
   
    except Exception as e:
        log_callback(f"Lỗi chung trong quá trình tạo máy ảo '{app_name}': {e}", app_name)
        return 
async def run_automation(accounts, LINK_GIT, num_flutter_apps, log_callback, status_callback, create_vm_log_sections_callback, stop_event: threading.Event):
    """
    Main function to orchestrate the entire automation process for multiple accounts.
    Args:
        accounts (list): List of (email, password) tuples.
        LINK_GIT (str): Git command.
        num_flutter_apps (int): Number of Flutter VMs to create per account.
        log_callback (callable): Function to send messages to the GUI.
        status_callback (callable): Function to update the overall application status.
        create_vm_log_sections_callback (callable): Function to create VM log sections in the GUI.
        stop_event (threading.Event): Event to signal stopping the automation.
    """
    status_callback("Bắt đầu tự động hóa...", "blue")
    
    for i, (gmail, password) in enumerate(accounts):
        if stop_event.is_set():
            log_callback(f"Đã nhận tín hiệu dừng. Dừng xử lý tài khoản '{gmail}'.", "general")
            status_callback("Đã dừng.", "red")
            break

        log_callback(f"--- Bắt đầu xử lý tài khoản {i+1}/{len(accounts)}: {gmail} ---", "general")
        status_callback(f"Đang xử lý tài khoản {i+1}/{len(accounts)}: {gmail}", "orange")

        browser = None
        logged_in_context = None
        try:
            async with async_playwright() as playwright:
                log_callback("Bắt đầu quá trình đăng nhập Google và thiết lập ban đầu...", "general")
                logged_in_context, browser = await perform_initial_login(gmail, password, playwright, log_callback, stop_event)

                if stop_event.is_set():
                    log_callback(f"Đã nhận tín hiệu dừng trong quá trình đăng nhập tài khoản '{gmail}'.", "general")
                    status_callback("Đã dừng.", "red")
                    break # Exit account loop
                
                if not logged_in_context:
                    log_callback(f"Đăng nhập tài khoản '{gmail}' thất bại. Bỏ qua tài khoản này.", "general")
                    continue # Skip to next account

                status_callback(f"Đăng nhập tài khoản '{gmail}' thành công, bắt đầu thiết lập IDX.", "orange")
                await handle_idx_initial_setup(logged_in_context, log_callback, stop_event)
                
                if stop_event.is_set():
                    log_callback(f"Đã nhận tín hiệu dừng trong quá trình thiết lập IDX cho tài khoản '{gmail}'.", "general")
                    status_callback("Đã dừng.", "red")
                    break # Exit account loop

                status_callback(f"Thiết lập IDX cho tài khoản '{gmail}' hoàn tất, bắt đầu tạo máy ảo.", "orange")

                # Create VM log sections in the GUI BEFORE starting actual VM creation
                # Only create if they don't exist yet for this run
                create_vm_log_sections_callback(num_flutter_apps)

                tasks = []
                for j in range(1, num_flutter_apps + 1):
                    app_name = f"a{j}" # VM names are "a1", "a2", etc.
                    # Create tasks for each VM to run in parallel
                    tasks.append(asyncio.create_task(create_virtual_machine(LINK_GIT, logged_in_context, app_name, log_callback, stop_event, "flutter")))

                log_callback(f"Đang chuẩn bị tạo {len(tasks)} máy ảo song song cho tài khoản '{gmail}'...", "general")
                status_callback(f"Tạo {len(tasks)} máy ảo cho '{gmail}'...", "orange")
                await asyncio.gather(*tasks) # Run all tasks in parallel

                log_callback(f"Đã hoàn thành tạo {len(tasks)} máy ảo song song và thực hiện nhiệm vụ cho tài khoản '{gmail}'.", "general")

        except Exception as e:
            log_callback(f"Lỗi không mong muốn khi xử lý tài khoản '{gmail}': {e}", "general")
            status_callback(f"Lỗi khi xử lý tài khoản '{gmail}'!", "red")
        finally:
            if logged_in_context:
                await logged_in_context.close()
                log_callback(f"Đã đóng ngữ cảnh trình duyệt cho tài khoản '{gmail}'.", "general")
            if browser:
                await browser.close()
                log_callback(f"Đã đóng trình duyệt cho tài khoản '{gmail}'.", "general")
        
    if not stop_event.is_set():
        status_callback("Hoàn thành tất cả tác vụ cho tất cả tài khoản!", "green")
    else:
        status_callback("Đã dừng quá trình tự động hóa.", "red")


def start_automation_thread(accounts, LINK_GIT, num_flutter_apps, log_callback, status_callback, create_vm_log_sections_callback, stop_event: threading.Event):
    """
    Wrapper function to run async tasks in a separate thread.
    Creates a new event loop for this thread.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_automation(accounts, LINK_GIT, num_flutter_apps, log_callback, status_callback, create_vm_log_sections_callback, stop_event))
    except Exception as e:
        log_callback(f"Lỗi trong luồng tự động hóa: {e}", "general")
        status_callback("Lỗi trong luồng!", "red")
    finally:
        loop.close()


# --- Tkinter GUI ---

class PlaywrightGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Công Cụ Tự Động Hóa IDX")
        self.root.geometry("1200x800")
        self.root.option_add("*Font", "Arial 10") 

        self.log_widgets = {} 
        self.vm_log_frames = []
        self.automation_thread = None 
        self.stop_event = threading.Event()

        self.create_widgets()

    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(padx=10, pady=10, fill="x")
        input_frame = ttk.LabelFrame(top_frame, text="Thông Tin Đăng Nhập & Cấu Hình", padding=10)
        input_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Label(input_frame, text="Danh sách tài khoản (Gmail:Mật khẩu):").grid(row=0, column=0, padx=5, pady=2, sticky="nw")
        self.accounts_entry = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=50, height=5, font=("Arial", 9))
        self.accounts_entry.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")
        # Example accounts (replace with your actual accounts)
        self.accounts_entry.insert(tk.END, "email1@gmail.com:Ducngocvs123\n")

        input_frame.grid_rowconfigure(0, weight=1) # Allow accounts_entry to expand
        input_frame.grid_columnconfigure(1, weight=1)


        # Git Link Entry
        ttk.Label(input_frame, text="Lệnh Git:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.git_link_entry = ttk.Entry(input_frame, width=40)
        self.git_link_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.git_link_entry.insert(0, "curl -sL https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/dao.sh | bash")

        # Number of Flutter Apps Entry
        ttk.Label(input_frame, text="Số lượng máy ảo Flutter (tối đa 10):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.num_apps_entry = ttk.Entry(input_frame, width=10)
        self.num_apps_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        self.num_apps_entry.insert(0, "10") # Default to 3 VMs for quick testing

        input_frame.columnconfigure(1, weight=1)

        control_frame = ttk.Frame(top_frame, padding=10)
        control_frame.pack(side="right", fill="y", padx=5, pady=5)

        self.start_button = ttk.Button(control_frame, text="Bắt Đầu Tự Động Hóa", command=self.start_automation)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(control_frame, text="Dừng Tự Động Hóa", command=self.stop_automation, state="disabled")
        self.stop_button.pack(pady=5)

        self.clear_log_button = ttk.Button(control_frame, text="Xóa Nhật Ký", command=self.clear_log)
        self.clear_log_button.pack(pady=5)

        self.status_label = ttk.Label(control_frame, text="Trạng thái: Sẵn sàng", font=("Arial", 10, "bold"), foreground="black")
        self.status_label.pack(pady=5)

        # Main Log Area
        self.main_log_frame = ttk.LabelFrame(self.root, text="Nhật Ký Hoạt Động", padding=10)
        self.main_log_frame.pack(padx=10, pady=10, expand=True, fill="both")

        # General Log
        self.general_log_label = ttk.Label(self.main_log_frame, text="Nhật Ký Chung:", font=("Arial", 9, "bold"))
        self.general_log_label.grid(row=0, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        self.general_log_text = scrolledtext.ScrolledText(self.main_log_frame, wrap=tk.WORD, height=8, font=("Consolas", 8))
        self.general_log_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.general_log_text.config(state="disabled")
        self.log_widgets["general"] = self.general_log_text

        # Configure main_log_frame grid for log areas
        self.main_log_frame.grid_rowconfigure(1, weight=1) # General log can expand vertically
        self.main_log_frame.grid_columnconfigure(0, weight=1)
        self.main_log_frame.grid_columnconfigure(1, weight=1)

    def log_message(self, message, vm_name="general"):
        """
        Adds a message to the corresponding log area.
        Uses `self.root.after` to ensure updates are on the main GUI thread.
        Args:
            message (str): The message to log.
            vm_name (str): VM name (e.g., "a1", "a2") or "general" for the general log.
        """
        self.root.after(0, self._append_log, message, vm_name)

    def _append_log(self, message, vm_name):
        """Internal function to append message to log."""
        if vm_name in self.log_widgets:
            target_text = self.log_widgets[vm_name]
            target_text.config(state="normal") # Enable editing
            target_text.insert(tk.END, message + "\n") # Append message
            target_text.see(tk.END) # Auto-scroll to end
            target_text.config(state="disabled") # Disable editing
        else:
            print(f"Lỗi: Không tìm thấy widget nhật ký cho '{vm_name}'. Tin nhắn: {message}") # Log to console if widget not found

    def update_status(self, message, color="black"):
        """
        Updates the status label.
        Uses `self.root.after` to ensure updates are on the main GUI thread.
        """
        self.root.after(0, self._set_status, message, color)

    def _set_status(self, message, color):
        """Internal function to update the status label."""
        self.status_label.config(text=f"Trạng thái: {message}", foreground=color)

    def clear_log(self):
        """Clears all messages in all log areas and resets status."""
        # Clear all existing log widgets
        for vm_name, text_widget in self.log_widgets.items():
            text_widget.config(state="normal")
            text_widget.delete(1.0, tk.END)
            text_widget.config(state="disabled")
        self.update_status("Sẵn sàng", "black")

        # Destroy all dynamically created VM log frames
        for frame in self.vm_log_frames:
            frame.destroy()
        self.vm_log_frames.clear()

        # Reset log_widgets, keeping only "general"
        self.log_widgets = {"general": self.general_log_text}

    def create_vm_log_sections(self, num_apps):
        """
        Creates new log sections for each virtual machine.
        This function is called from the Playwright thread via root.after().
        """
        self.root.after(0, self._create_vm_log_sections_gui, num_apps)

    def _create_vm_log_sections_gui(self, num_apps):
        """Internal function to create VM log sections in the GUI."""
        # Ensure that previous VM logs are cleared before creating new ones
        for frame in self.vm_log_frames:
            frame.destroy()
        self.vm_log_frames.clear()
        
        # Re-initialize log_widgets to only include general log before adding VM logs
        self.log_widgets = {"general": self.general_log_text}

        # Start creating VM logs from row 2 onwards, in 2 columns
        current_row = 2
        for i in range(num_apps):
            app_name = f"a{i+1}"
            col = i % 2
            
            # Create a LabelFrame for each VM log section
            vm_frame = ttk.LabelFrame(self.main_log_frame, text=f"VM {app_name} Log", padding=5)
            vm_frame.grid(row=current_row, column=col, padx=5, pady=5, sticky="nsew")
            self.vm_log_frames.append(vm_frame) # Keep track of frames to destroy later

            vm_log_text = scrolledtext.ScrolledText(vm_frame, wrap=tk.WORD, height=6, font=("Consolas", 8)) # Smaller height for VMs
            vm_log_text.pack(expand=True, fill="both")
            vm_log_text.config(state="disabled")
            self.log_widgets[app_name] = vm_log_text # Store reference to widget

            # Configure grid weight for vm_frame to expand
            vm_frame.columnconfigure(0, weight=1)
            vm_frame.rowconfigure(0, weight=1)

            if col == 1: # Move to next row after placing two columns
                current_row += 1
        
        # Ensure that the rows where VM logs are placed can expand
        for r in range(2, current_row + 1):
            self.main_log_frame.grid_rowconfigure(r, weight=1)


    def start_automation(self):
        """
        Starts the automation process in a separate thread.
        Retrieves input information from the GUI.
        """
        accounts_text = self.accounts_entry.get("1.0", tk.END).strip()
        accounts = []
        for line in accounts_text.split('\n'):
            line = line.strip()
            if line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    accounts.append((parts[0], parts[1]))
                else:
                    self.log_message(f"Lỗi định dạng tài khoản: '{line}'. Vui lòng sử dụng 'Gmail:Mật khẩu'.", "general")
                    self.update_status("Lỗi đầu vào tài khoản!", "red")
                    return
        
        if not accounts:
            self.log_message("Vui lòng nhập ít nhất một tài khoản Gmail:Mật khẩu.", "general")
            self.update_status("Lỗi đầu vào!", "red")
            return

        git_link = self.git_link_entry.get()
        try:
            num_apps = int(self.num_apps_entry.get())
            if num_apps <= 0 or num_apps > 10: # Limit to 10 VMs as per request
                self.log_message("Số lượng máy ảo phải là số nguyên dương và không quá 10.", "general")
                self.update_status("Lỗi đầu vào!", "red")
                return
        except ValueError:
            self.log_message("Số lượng máy ảo không hợp lệ. Vui lòng nhập một số nguyên.", "general")
            self.update_status("Lỗi đầu vào!", "red")
            return

        # Clear existing logs and VM log sections before starting a new run
        self.clear_log()
        self.log_message("Bắt đầu quá trình tự động hóa...", "general")
        self.update_status("Đang chạy...", "orange")
        self.start_button.config(state="disabled") # Disable Start button while running
        self.stop_button.config(state="normal") # Enable Stop button

        self.stop_event.clear() # Clear any previous stop signals

        # Initialize a new thread to run the automation
        self.automation_thread = threading.Thread(
            target=start_automation_thread,
            args=(accounts, git_link, num_apps, self.log_message, self.update_status, self.create_vm_log_sections, self.stop_event)
        )
        self.automation_thread.daemon = True # Allow the thread to exit with the main program
        self.automation_thread.start()

        # Check the thread status periodically to re-enable the button
        self.check_thread_status()

    def stop_automation(self):
        """
        Signals the automation thread to stop.
        """
        self.stop_event.set() # Set the stop signal
        self.log_message("Đang gửi tín hiệu dừng tự động hóa...", "general")
        self.update_status("Đang dừng...", "red")
        self.stop_button.config(state="disabled") # Disable Stop button once clicked

    def check_thread_status(self):
        """
        Checks the status of the automation thread and updates the GUI.
        """
        if self.automation_thread and self.automation_thread.is_alive():
            # If the thread is still running, check again after 100ms
            self.root.after(100, self.check_thread_status)
        else:
            # If the thread has finished, re-enable the Start button and disable Stop button
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            # Status is updated by the automation thread itself

if __name__ == "__main__":
    # Create the root Tkinter window
    root = tk.Tk()
    # Create an instance of the GUI application
    app = PlaywrightGUI(root)
    # Start the Tkinter event loop
    root.mainloop()
