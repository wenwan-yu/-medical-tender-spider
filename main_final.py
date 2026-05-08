import os, re, smtplib
from datetime import datetime
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENT_FILE = "sent_urls.txt"
EMAIL_USER = os.environ.get('EMAIL_USER', '1192368708@qq.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', 'lyvcpezdrgeriegj')

sites = [
    ("吉林省人民政府公共资源专栏", "https://www.jl.gov.cn/ggzy/zbcg/zbgg/index.html"),
    ("中国采购与招标网", "https://www.chinabidding.cn/tg/sem/gg/index.html"),
    ("军队采购网", "https://www.plap.mil.cn/"),
    ("吉林省政府采购网", "http://www.ccgp-jilin.gov.cn/site/category?parentId=550068&childrenCode=ZcyAnnouncement"),
]

KW_MEDICAL = [
    "医疗", "医院", "医药", "卫生", "诊疗", "医用", 
    "CT", "DR", "B超", "彩超", "核磁", "MRI", "X光",
    "检验", "试剂", "耗材", "手术", "监护", "呼吸", "麻醉"
]

KW_BID = ["招标", "采购", "中标", "成交", "公告", "结果", "公示"]

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(l.strip() for l in f if l.strip())
    return set()

def save_sent(url):
    with open(SENT_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

print("=== 吉林医疗招标爬虫（稳定版）===")
sent = load_sent()
all_new = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    
    for site_name, url in sites:
        print(f"\n正在抓取：{site_name}")
        page = browser.new_page()
        matches = []

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            for a in soup.find_all("a", href=True):
                title = a.get_text(strip=True)
                href = a["href"].strip()
                if len(title) < 8 or not href:
                    continue
                if href.startswith(("javascript", "#", "mailto")):
                    continue

                link = urljoin(url, href)
                if not link.startswith("http"):
                    continue

                has_med = any(k in title for k in KW_MEDICAL)
                has_bid = any(k in title for k in KW_BID)
                
                has_medical_keyword = "医疗" in title or "医院" in title or "医药" in title
                
                if has_med and has_bid and has_medical_keyword:
                    print(f"  → {title[:50]}")
                    matches.append({"title": title, "url": link})

        except Exception as e:
            print(f"  异常：{str(e)[:60]}")
        
        page.close()

        new_items = [x for x in matches if x["url"] not in sent]
        for item in new_items:
            save_sent(item["url"])
            all_new.append(item)

    browser.close()

total = len(all_new)
print(f"\n本次抓取完成，新增：{total} 条")

try:
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER

    if total > 0:
        msg["Subject"] = f"【吉林医疗招标】{total} 条新信息"
        body = f"本次发现 {total} 条医疗招标：\n\n"
        for item in all_new:
            body += f"• {item['title']}\n  链接：{item['url']}\n\n"
    else:
        msg["Subject"] = "【吉林医疗招标】无新信息"
        body = "今日未抓取到新的医疗招标公告。"

    msg.attach(MIMEText(body, "plain", "utf-8"))
    with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    print("Email OK")
except Exception as e:
    print(f"Email Failed: {e}")
