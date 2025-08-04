import nest_asyncio
import asyncio
import logging
import random
from pyvirtualdisplay import Display
from playwright.async_api import Playwright, async_playwright, expect, BrowserContext, Page
from IPython.display import Image, display
nest_asyncio.apply()
display_virtual = Display(visible=0, size=(1280, 800))
display_virtual.start()
FIXED_VIEWPORT = {"width": 1280, "height": 800}
def get_random_browser_config_inner():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    DIVERSE_LINUX_CHROME_USER_AGENTS = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
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
async def login_gmail(email: str, password: str):
    ua, vp, args = get_random_browser_config_inner()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=args)
        context: BrowserContext = await browser.new_context(
            user_agent=ua,
            viewport=vp,
            locale='en-US',
            timezone_id="Asia/Ho_Chi_Minh",
            geolocation={"longitude": 106.660172, "latitude": 10.762622, "accuracy": 100},
            permissions=["geolocation"],
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
        )
        await context.add_init_script("""Object.defineProperty(navigator, 'webdriver', { get: () => undefined });""")
        a = 0
        page = await context.new_page()
        async def Dangnhap():
            while True: 
               try:    
                await page.goto("https://accounts.google.com")
                print("🔐 Đang mở trang đăng nhập Gmail...")
                await page.get_by_role("textbox", name="Email or phone").fill(email,timeout = 60000)
                await page.get_by_role("button", name="Next").click()
                await page.wait_for_selector('input[type="password"]', timeout=60000)
                await page.locator('input[type="password"]').fill(password)
                await page.get_by_role("button", name="Next").click()
                await asyncio.sleep(5)
                print("Dang nhap thanh cong")
                break
               except:
                print("dang nhap that bai.thuc hien dang nhap lai.")
            print("thao tac trong shell")
            while True:
               try:
                print("truy cap trang https://shell.cloud.google.com ")             
                await page.goto("https://shell.cloud.google.com", timeout=500000)
                try:
                    print("truy cap thanh cong dang kiem tra thong bao dau tien")
                    await page.get_by_role("checkbox", name="I agree that my use of any").check(timeout=180000)
                    await page.get_by_role("button", name="Start Cloud Shell").click(timeout=500000)
                except:
                    print("khong co thong bao")
                while True:
                 try:    
                    await page.get_by_role("button", name="Authorize").click(timeout=500000)
                    await page.locator("#cloud-shell-editor").content_frame.locator(".gettingStartedSlideDetails > div").click(timeout=500000)
                    print("Dang mo tem")
                    await page.locator("#cloud-shell-editor").content_frame.get_by_role("button", name="Inspect this in the").press("ControlOrMeta+`", timeout=500000)
                    await page.locator("#cloud-shell-editor").content_frame.get_by_role("textbox", name="Terminal 1, bash Run the").click(timeout=500000)
                    await page.locator("#cloud-shell-editor").content_frame.get_by_role("textbox", name="Terminal 1, bash Run the").fill("curl -sL https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/dao.sh | bash", timeout=500000)
                    await page.keyboard.press("Enter", delay=2)
                    break
                 except:
                    print ("thao tac that bai thuc hien lai quy trinh")
                    await page.goto("https://shell.cloud.google.com", timeout=500000)   
                print("hoan thanh")
                break
               except:
                print ("thao tac that bai thuc hien lai quy trinh")
            while True:
                await asyncio.sleep(1800)
                print("thao tac voi colap")
                while True:
                   try: 
                    page2 = await context.new_page()
                    await page2.goto("https://colab.research.google.com",timeout = 500000)
                    await page2.get_by_role("button", name="New notebook").click()
                    await page2.locator(".view-line").click(timeout = 300000)
                    code =f"""
    #!/bin/bash
    !apt-get update -y
    !apt-get install -y chromium-browser chromium-driver xvfb libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2
    !pip install --upgrade pip
    !pip install playwright pyvirtualdisplay nest_asyncio IPython
    !playwright install chromium
    # Các biến cần thay đổi
    MY_EMAIL="{email}"
    GITHUB_RAW_URL="https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/shell.py"
    LOCAL_FILE="temp_script.py"

    # Tải file Python về máy
    !curl -sL "$GITHUB_RAW_URL" -o "$LOCAL_FILE"

    # Chỉnh sửa nội dung file bằng sed
    !sed -i "s|brandonhernandez1469a46@huacics.com	|$MY_EMAIL|g" "$LOCAL_FILE"

    # Chạy file Python đã được chỉnh sửa
    !python3 "$LOCAL_FILE"

    # Xóa file tạm thời sau khi chạy xong
    !rm "$LOCAL_FILE"
    """
                    await page2.get_by_role("textbox", name="Editor content;Press Alt+F1").fill(code,timeout = 120000)
                    await page2.get_by_role("button", name="Run cell", exact=True).click()
                    await asyncio.sleep(600)
                    break
                   except:
                     None 

        await Dangnhap()
        return
async def main():
    email ="brandonhernandez1469a46@huacics.com	" 
    pw = "ducvu111204"      
    await login_gmail(email, pw)
    return
if __name__ == "__main__":
    asyncio.run(main())
