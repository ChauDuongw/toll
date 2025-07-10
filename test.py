import asyncio
import time
import logging
import random
# Removed threading import as stop_event is no longer used
from playwright.async_api import Playwright, async_playwright, expect, BrowserContext, Page
NUM_IDX_PAGES = 10
LINK_GIT = " curl -sL https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/dao.sh | bash" # QUAN TRỌNG: Đặt lệnh Git thực tế của bạn tại đây, ví dụ: "git clone https://github.com/user/repo.git"

async def perform_initial_login(gmail_account: str, password: str, playwright: Playwright):
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
    browser = None
    context = None
    try:
        print("Đang khởi chạy trình duyệt để đăng nhập ban đầu...")
        browser = await playwright.chromium.launch(
                headless= True, # Chạy ở chế độ headless
                args=current_chrome_args)
        context = await browser.new_context(
                user_agent=current_user_agent,
                viewport=current_viewport)
        page = await context.new_page()

        async def Dangnhap():
            print("Đang thực hiện hành động đăng nhập gmail ")
            while True:
                try:
                    print("Truy nhap den trang https://accounts.google.com ")
                    await page.goto("https://accounts.google.com")
                    await page.wait_for_load_state('domcontentloaded', timeout=30000)
                    print("truy cap den trang https://accounts.google.com thanh cong Tien hanhnhap gmail")
                    await page.get_by_role("textbox", name="Email or phone").fill(gmail_account) # Sử dụng tham số
                    await page.get_by_role("button", name="Next").click()
                    print("Nhap gmail thanh cong chuyen qua truong nhap mat khau")
                    await page.get_by_role("textbox", name="Enter your password").fill(password, timeout=300000) # Sử dụng tham số
                    await page.get_by_role("button", name="Next").click()
                    print("nhap mat khau thanh cong hoan thanh hanh dong dang nhap")
                    break
                except Exception:
                    print("dang nhap that bai thuc hien lai hanh dong dang nhap gmail")
            print("Kiem tra thong bao (Chào mừng bạn đến với tài khoản)")
            try:
                await expect(page.locator("span").filter(has_text="Welcome to your new Google Workspace for Education account")).to_be_visible(timeout=120000)
                print("Da phat hien thong bao (Chào mừng bạn đến với tài khoản)")
                await page.get_by_role("button", name="I understand").click(timeout=100000)
                print("Da vuot qua thong bao(Chào mừng bạn đến với tài khoản)")
            except Exception:
                print("khong phat hien thong bao (Chào mừng bạn đến với tài khoản)")
            return 1

        async def idx():
            """Điều hướng đến IDX và xử lý các màn hình thiết lập/chào mừng ban đầu."""
            print("truy cap trang idx https://idx.google.com")
            while True:
                # kiem tra xem co thong bao
                try:
                    await page.goto("https://idx.google.com")
                    await expect(page.get_by_role("heading", name="Welcome to Firebase Studio, a")).to_be_visible(timeout=150000)
                    print("phat hien thong bao chao mung.")
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
                        await element_locator.click(position={'x': offset_x, 'y': offset_y}, force=True)
                    await page.get_by_role("button", name="Confirm").click()
                    try:
                        await expect(page.get_by_role("link", name="New Workspace")).to_be_visible(timeout=60000)
                        print("truy cap trang truy cap trang idx https://idx.google.com thanh cong ")
                        break
                    except Exception:
                        print("truy cap trang truy cap trang idx https://idx.google.com that bai dang thuc hien lai ")

                except Exception:
                    try:
                        await expect(page.get_by_role("link", name="New Workspace")).to_be_visible(timeout=60000)
                        print("truy cap trang truy cap trang idx https://idx.google.com thanh cong ")
                        break
                    except Exception:
                        print("truy cap trang truy cap trang idx https://idx.google.com that bai dang thuc hien lai ")
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
        await page_vm.goto(url, wait_until="load")
        while True:
          await asyncio.sleep(300)
          await page_vm.reload()
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
               await page_vm.reload()    

     
    return page_vm
async def main():
    # Lấy GMAIL từ người dùng
    user_gmail = input("Vui lòng nhập gmail: ")
    user_mat_khau = input("Vui lòng nhập Mật khẩu: ")
    url =  input("Vui lòng nhập link máy ảo: ")
    print(f"Bắt đầu với chuỗi hành động cho tài khoản {user_gmail} có mật khẩu {user_mat_khau}")

    async with async_playwright() as playwright:
        # Truyền GMAIL và MAT_KHAU đã lấy từ người dùng vào hàm perform_initial_login
        context, browser = await perform_initial_login(user_gmail, user_mat_khau, playwright,url)
        if not context:
            print("Đăng nhập thất bại. Không thể mở các trang IDX.")
            return

        tasks = []
        for i in range(NUM_IDX_PAGES):
            tasks.append(asyncio.create_task(open_single_idx_page(context,url, i+1)))
        idx_pages = await asyncio.gather(*tasks)
        print(f"Đã mở thành công {len(idx_pages)} trang IDX.")
        try:
            return
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Lỗi trong quá trình giữ trình duyệt mở: {e}")
        finally:
            if browser:
                print("Đang đóng trình duyệt...")
                await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
