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

# ========== 修复：正确的网站列表 ==========
sites = [
    ("吉林省人民政府公共资源专栏", "https://www.jl.gov.cn/ggzy/zbcg/zbgg/index.html"),
    ("中国采购与招标网", "https://www.chinabidding.cn/tg/sem/gg/index.html"),
    ("军队采购网", "https://www.plap.mil.cn/module/channel/jdcggg/index.html"),
    ("吉林省政府采购网", "http://www.ccgp-jilin.gov.cn/site/category?parentId=550068&childrenCode=ZcyAnnouncement"),
]

# ========== 修复：扩宽医疗关键词 ==========
KW_MEDICAL = [
    "医疗", "医院", "医药", "卫生", "诊疗", "医用", "检验", "防疫",
    "急救", "体检", "救治", "药材", "器械", "设备", "试剂", "耗材",
    "影像", "DR", "CT", "B超", "彩超", "心电", "监护", "手术", "康复"
]

KW_EQUIPMENT = ["采购", "招标", "中标", "成交", "公告", "结果", "公示", "谈判", "询价"]

# ========== 下面全部不动 ==========
def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(l.strip() for l in f if l.strip())
    return set()

def save_sent(url):
    with open(SENT_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

def get_stype(n):
    if "吉林省" in n: return "省级采购"
    if "招标" in n: return "招标门户"
    if "军队" in n: return "军队采购"
    return "其他"

def get_itype(t):
    for k, v in [('招标', '招标'), ('采购', '采购'), ('中标', '中标'), ('结果', '结果'), ('成交', '成交')]:
        if k in t: return v
    return "公告"

def get_cat(t):
    return "医疗设备"

def get_dt(u):
    m = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', u)
    if m:
        return f"{m.group(1)}-{m.group(2):0>2}-{m.group(3):0>2}"
    return datetime.now().strftime("%Y-%m-%d")

def get_reg(t):
    for c in ['长春', '吉林', '四平', '辽源', '通化', '白山', '松原', '白城', '延边']:
        if c in t: return c
    return "全国/军队"

print("=" * 50)
print("吉林医疗招标爬虫（修复漏抓版）")
print("=" * 50)

sent = load_sent()
all_r = {}

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for name, url in sites:
        print(f"\n[抓取] {name}")
        items = []
        page = b.new_page()
        try:
            page.goto(url, timeout=30000)
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f"  失败：{str(e)[:60]}")
            page.close()
            continue

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)

        for a in links:
            title = a.get_text(strip=True)
            href = a.get("href", "")
            if len(title) < 8 or not href or href.startswith(("javascript", "#")):
                continue
            link_url = urljoin(url, href)
            if not link_url.startswith("http"):
                continue

            has_med = any(k in title for k in KW_MEDICAL)
            has_bid = any(k in title for k in KW_EQUIPMENT)
            if has_med and has_bid:
                items.append({
                    "url": link_url, "title": title,
                    "source_type": get_stype(name),
                    "info_type": get_itype(title),
                    "category": get_cat(title),
                    "publish_date": get_dt(link_url),
                    "region": get_reg(title)
                })
                print(f"  ✅ {title[:50]}")

        page.close()
        new_items = [i for i in items if i['url'] not in sent]
        for i in new_items:
            save_sent(i['url'])
        all_r[name] = new_items
        print(f"  本次抓取：{len(items)} 条 | 新条目：{len(new_items)}")

    b.close()

total = sum(len(x) for x in all_r.values())
print(f"\n[总计] {total} 条新招标")

# 发送邮件
try:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    if total > 0:
        msg['Subject'] = f"【医疗招标】{total} 条新信息"
        body = f"共发现 {total} 条医疗采购信息：\n\n"
        for site_name, items in all_r.items():
            if items:
                body += f"【{site_name}】{len(items)} 条\n"
                for i in items:
                    body += f"• {i['title'][:60]}\n  链接：{i['url']}\n\n"
    else:
        msg['Subject'] = "【医疗招标】无新信息"
        body = "本次未抓取到新的医疗招标信息。"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    print("[邮件] 发送成功")
except Exception as e:
    print(f"[邮件] 失败：{e}")
