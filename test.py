# Khởi động màn hình giả lập (GUI headless)

import asyncio
import time
import logging
import random
from playwright.async_api import Playwright, async_playwright, expect, BrowserContext, Page
NUM_IDX_PAGES = 2
LINK_GIT = " curl -sL https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/dao.sh | bash"
def get_random_browser_config_inner():
    DIVERSE_USER_AGENTS = {
        "chrome_linux": [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        ],
        "chrome_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        ],
        "chrome_macos": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        ],
        "firefox_linux": [
            "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
        ],
        "firefox_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        ],
        "firefox_macos": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0",
        ]
    }
    DIVERSE_VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1280, "height": 720},
        {"width": 1440, "height": 900},
    ]

    selected_timezone = "Asia/Singapore"
    selected_locale = "en-US"
    selected_browser_type_key = random.choice(list(DIVERSE_USER_AGENTS.keys()))
    selected_user_agent = random.choice(DIVERSE_USER_AGENTS[selected_browser_type_key])
    browser_type = selected_browser_type_key.split('_')[0]
    operating_system = selected_browser_type_key.split('_')[1]

    selected_viewport = random.choice(DIVERSE_VIEWPORTS)

    has_touch_screen = random.choice([True, False])
    color_scheme = random.choice(["light", "dark"])

    base_chrome_args = [
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
    chrome_args = base_chrome_args + [f"--window-size={selected_viewport['width']},{selected_viewport['height']}"]
    random.shuffle(chrome_args)
    def generate_smarter_cookies(domain: str):
        cookies = []
        current_time = int(time.time())

        ga_first_visit_ts = current_time - random.randint(3600 * 24 * 7, 3600 * 24 * 30 * 6)
        cookies.append({
            'name': '_ga',
            'value': f"GA1.2.{random.randint(1000000000, 9999999999)}.{ga_first_visit_ts}",
            'domain': domain,
            'path': '/',
            'expires': ga_first_visit_ts + 3600 * 24 * 365 * 2,
            'httpOnly': False,
            'secure': False,
            'sameSite': 'Lax'
        })
        cookies.append({
            'name': '_gid',
            'value': f"GA1.2.{random.randint(100000000, 999999999)}.{current_time}",
            'domain': domain,
            'path': '/',
            'expires': current_time + 3600 * 24,
            'httpOnly': False,
            'secure': False,
            'sameSite': 'Lax'
        })

        session_id_name = random.choice(['PHPSESSID', 'JSESSIONID', 'ASPNET_SessionId'])
        session_id_value = ''.join(random.choices('abcdef0123456789', k=random.choice([26, 32, 40])))
        cookies.append({
            'name': session_id_name,
            'value': session_id_value,
            'domain': domain,
            'path': '/',
            'expires': current_time + 3600 * random.randint(1, 4),
            'httpOnly': True,
            'secure': random.choice([True, False]),
            'sameSite': random.choice(['Lax', 'Strict'])
        })
        if random.random() < 0.8:
            consent_cookie_name = random.choice(['cookie_consent', 'gdpr_accepted', 'privacy_policy_viewed'])
            consent_cookie_value = random.choice(['true', '1', 'yes'])
            cookies.append({
                'name': consent_cookie_name,
                'value': consent_cookie_value,
                'domain': domain,
                'path': '/',
                'expires': current_time + 3600 * 24 * 365,
                'httpOnly': False,
                'secure': False,
                'sameSite': 'Lax'
            })

        for _ in range(random.randint(0, 2)):
            rand_name = f"__r{random.randint(100, 999)}"
            rand_value = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(8, 20)))
            cookies.append({
                'name': rand_name,
                'value': rand_value,
                'domain': domain,
                'path': '/',
                'expires': current_time + random.randint(3600 * 24, 3600 * 24 * 30),
                'httpOnly': random.choice([True, False]),
                'secure': random.choice([True, False]),
                'sameSite': random.choice(['Lax', 'Strict', 'None'])
            })

        return cookies
    smarter_cookies = generate_smarter_cookies(domain=".google.com")

    logging.info(f"Selected Browser: {browser_type.capitalize()} on {operating_system.capitalize()}")
    logging.info(f"Selected User Agent: {selected_user_agent}")
    logging.info(f"Selected Viewport: {selected_viewport['width']}x{selected_viewport['height']}")
    logging.info(f"Selected Timezone: {selected_timezone} (Cố định)")
    logging.info(f"Selected Locale: {selected_locale} (Cố định)")
    logging.info(f"Has Touch Screen: {has_touch_screen}")
    logging.info(f"Color Scheme: {color_scheme}")
    logging.info(f"Generated {len(smarter_cookies)} smarter cookies.")
    return {
        "user_agent": selected_user_agent,
        "viewport": selected_viewport,
        "chrome_args": chrome_args if browser_type == "chrome" else [],
        "browser_type": browser_type,
        "cookies": smarter_cookies,
        "locale": selected_locale,
        "timezone_id": selected_timezone,
        "has_touch": has_touch_screen,
        "color_scheme": color_scheme
    }
async def perform_initial_login(gmail_account: str, password: str, playwright: Playwright):
    browser_instance: Playwright.Browser | None = None
    browser_context: BrowserContext | None = None
    page: Page | None = None
    browser: Playwright.Browser | None = None # Initialize browser to None
    config = get_random_browser_config_inner()
    a = False
    try:
        print(f"Đang khởi chạy trình duyệt ({config['browser_type']}) để đăng nhập ban đầu...")
        if config['browser_type'] == "chrome":
            browser = await playwright.chromium.launch(
                headless=True,
                args=config['chrome_args']
            )
        elif config['browser_type'] == "firefox":
            browser = await playwright.firefox.launch(
                headless= True,           )
        else:
            print(f"Loại trình duyệt không được hỗ trợ: {config['browser_type']}")
            return None, None
        context = await browser.new_context(
            user_agent=config['user_agent'],
            viewport=config['viewport'],
            locale=config['locale'],
            timezone_id=config['timezone_id'],
            has_touch=config['has_touch'],
            color_scheme=config['color_scheme'],
            permissions=[]
        )
        if config['cookies']:
            await context.add_cookies(config['cookies'])
            print(f"Đã thêm {len(config['cookies'])} cookie thông minh vào context.")
        page = await context.new_page()

        async def Dangnhap():
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
                    await page.get_by_role("textbox", name="Enter your password").fill(password, timeout=30000)
                    await page.get_by_role("button", name="Next").click()
                    print("nhap mat khau thanh cong hoan thanh hanh dong dang nhap")
                    break
                except Exception:
                    await page.screenshot(path="screenshot.png", full_page=True)
                    from IPython.display import Image, display
                    display(Image("screenshot.png"))
                    print("dang nhap that bai thuc hien lai hanh dong dang nhap gmail")
            print("Kiem tra thong bao (Chào mừng bạn đến với tài khoản)")
            try:
                await expect(page.locator("span").filter(has_text="Chào mừng bạn đến với tài khoản")).to_be_visible(timeout=120000)
                print("Da phat hien thong bao (Chào mừng bạn đến với tài khoản)")
                await page.get_by_role("button", name="Tôi hiểu").click(timeout=100000)
                print("Da vuot qua thong bao(Chào mừng bạn đến với tài khoản)")
            except Exception:
                print("khong phat hien thong bao (Chào mừng bạn đến với tài khoản)")
            return 1
        await Dangnhap()
        return context, browser
    except Exception as e:
        print(f"Lỗi trong quá trình đăng nhập Gmail '{gmail_account}': {e}")
        if browser:
            await browser.close()
        return None, None
    finally:
        pass

# hàm này hoạt động trong colab
async def open_single_idx_page(context: BrowserContext, page_number: int) -> Page:
    page_vm = await context.new_page()
    #
    


    return page_vm
async def main():
    user_gmail = input("Vui lòng nhập gmail: ")
    user_mat_khau = input("Vui lòng nhập Mật khẩu: ")
    print(f"Bắt đầu với chuỗi hành động cho tài khoản {user_gmail} có mật khẩu {user_mat_khau}")

    async with async_playwright() as playwright:
        await perform_initial_login(user_gmail, user_mat_khau, playwright)
        

import nest_asyncio
nest_asyncio.apply()
await main()
