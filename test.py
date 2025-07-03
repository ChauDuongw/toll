from playwright.sync_api import sync_playwright
import random
def generate_ultra_diverse_chrome_user_agent():
    # Phần "Mozilla/5.0" luôn cố định
    mozilla_prefix = "Mozilla/5.0"

    # --- Các biến thể của Hệ điều hành và Nền tảng (Platform) ---
    platforms = [
        # Windows
        f"Windows NT 10.0; Win64; x64",
        f"Windows NT 10.0; WOW64",
        f"Windows NT 6.3; Win64; x64", # Windows 8.1
        f"Windows NT 6.1; Win64; x64", # Windows 7
        # macOS
        f"Macintosh; Intel Mac OS X 10_{random.randint(10, 15)}_{random.randint(0, 9)}",
        f"Macintosh; Intel Mac OS X 11_{random.randint(0, 7)}_{random.randint(0, 9)}", # Big Sur
        f"Macintosh; Intel Mac OS X 12_{random.randint(0, 7)}_{random.randint(0, 9)}", # Monterey
        f"Macintosh; Intel Mac OS X 13_{random.randint(0, 6)}_{random.randint(0, 9)}", # Ventura
        # Linux
        f"X11; Linux x86_64",
        f"X11; Ubuntu; Linux x86_64",
        f"X11; Fedora; Linux x86_64",
        # Android (phone and tablet variations)
        f"Linux; Android {random.randint(9, 13)}; SM-G{random.randint(900, 999)}F Build/SP1A.{random.randint(200000, 299999)}.0{random.randint(0,9)}",
        f"Linux; Android {random.randint(9, 13)}; Tablet Build/SP1A.{random.randint(200000, 299999)}.0{random.randint(0,9)}",
        # iOS (iPhone and iPad variations)
        f"iPhone; CPU iPhone OS {random.randint(14, 17)}_{random.randint(0,9)}_{random.randint(0,9)} like Mac OS X",
        f"iPad; CPU OS {random.randint(14, 17)}_{random.randint(0,9)}_{random.randint(0,9)} like Mac OS X",
    ]

    # --- Các biến thể của AppleWebKit và KHTML/Gecko ---
    # Chrome sử dụng AppleWebKit, và thường có (KHTML, like Gecko)
    webkit_version = f"{random.randint(537, 605)}.{random.randint(0, 99)}" # Phạm vi rộng hơn
    khtml_gecko = "(KHTML, like Gecko)" # Thường cố định

    # --- Các biến thể của Chrome Version ---
    # major.minor.build.patch
    chrome_major = random.randint(80, 126) # Phạm vi lớn hơn cho các phiên bản cũ và mới
    chrome_minor = random.randint(0, 9) # Minor version (ít biến đổi)
    chrome_build = random.randint(1000, 6000) # Build number
    chrome_patch = random.randint(0, 999) # Patch number

    # --- Các biến thể của Safari Version (trong User-Agent của Chrome) ---
    # Thường trùng với WebKit hoặc gần với nó
    safari_version_for_chrome = f"{random.randint(537, 605)}.{random.randint(0, 99)}"

    # --- Kết hợp các thành phần để tạo User-Agent ---
    user_agent = (
        f"{mozilla_prefix} ({random.choice(platforms)}) "
        f"AppleWebKit/{webkit_version} {khtml_gecko} "
        f"Chrome/{chrome_major}.{chrome_minor}.{chrome_build}.{chrome_patch} "
        f"Safari/{safari_version_for_chrome}"
    )

    return user_agent

def login_example_page():
    with sync_playwright() as p:

        user_agent_to_use = generate_ultra_diverse_chrome_user_agent()
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=user_agent_to_use)
        page = context.new_page()

        print("Truy cập trang đăng nhập giả định...")
        page.goto("https://accounts.google.com/signin") 

        print("Đang điền thông tin đăng nhập...")
        try:
            page.fill('input[type="email"]', "hoangsangdinhhung1382001@gmail.com")
            page.click('button:has-text("Next")') 
            page.wait_for_selector('input[type="password"]', state='visible')
            page.fill('input[type="password"]', "	dinhhung!2001") # THAY ĐỔI ĐỂ PHÙ HỢP

            # Nhấn nút "Next" hoặc "Đăng nhập"
            page.click('button:has-text("Next")') # Hoặc 'button:has-text("Đăng nhập")'

            print("Đã cố gắng đăng nhập. Chờ kết quả...")
            # Chờ một lúc để xem kết quả sau khi đăng nhập
            page.wait_for_timeout(7000) # Chờ 7 giây

            # In ra URL hiện tại sau khi đăng nhập để xem có thành công không
            print(f"URL hiện tại: {page.url}")

        except Exception as e:
            print(f"Đã xảy ra lỗi trong quá trình đăng nhập: {e}")
            print("Có thể do selectors không đúng hoặc trang đã phát hiện bot.")

        browser.close()

# Chạy ví dụ
login_example_page()
