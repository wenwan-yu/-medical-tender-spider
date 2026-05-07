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
    ("军队采购网", "https://www.plap.mil.cn/index/noticeMore.html?category=3001"),
    ("军采网-医疗设备", "https://www.plap.mil.cn/index/noticeMore.html?category=3004"),
]

KW_MEDICAL = ["医疗", "医院", "医药"]
KW_EQUIPMENT = ["采购", "招标", "中标", "成交", "设备", "器械"]

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(l.strip() for l in f if l.strip())
    return set()

def save_sent(url):
    with open(SENT_FILE, "a", encoding="utf-8") as f: f.write(url+"\n")

def get_stype(n):
    if "军队" in n: return "军队采购"
    return "其他"

def get_itype(t):
    for k,v in [('招标','招标'),('中标','中标'),('成交','成交'),('采购','采购')]:
        if k in t: return v
    return "公告"

def get_cat(t):
    for ks,c in [
        (['CT','核磁','MRI','X光','DR'],'设备类-大型影像'),
        (['检验','生化','血球','免疫'],'设备类-检验设备'),
        (['手术','监护','呼吸','麻醉'],'设备类-治疗设备'),
        (['耗材','试剂','敷料'],'耗材类'),
    ]:
        if any(k in t for k in ks): return c
    return "其他"

def get_brand(t): return "-"
def get_model(t): return "-"
def get_supplier(t): return "-"
def get_reg_num(t): return "-"

def get_dt(u):
    for p in [r'/(\d{8})/',r'/(\d{4})(\d{2})(\d{2})/']:
        m = re.search(p,u)
        if m:
            g=m.groups()
            return f"{g[0][:4]}-{g[0][4:6]}-{g[0][6:8]}" if len(g[0])==8 else f"{g[0]}-{int(g[1]):02d}-{int(g[2]):02d}"
    return datetime.now().strftime('%Y-%m-%d')

def get_reg(t):
    for c in ['长春','吉林','四平','辽源','通化','白山','松原','白城','延边','延吉']:
        if c in t: return c
    return '-'

print("="*50)
print("Jilin Medical Spider")
print("="*50)

sent = load_sent()
all_r = {}

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)

    for name, url in sites:
        print(f"\n[->] {name}")
        items = []

        page = b.new_page()
        try:
            page.goto(url, timeout=10000)
            page.wait_for_timeout(1500)
        except Exception as e:
            print(f"  Failed: {str(e)[:50]}")
            page.close()
            continue

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        print(f"  Links: {len(links)}")

        for a in links:
            title = a.get_text(strip=True)
            href = a.get("href", "")

            if len(title) < 5: continue
            if not href or href in ["#",""]: continue
            if href in ["javascript:;","javascript:void(0)"]: continue

            link_url = urljoin(url, href)
            if not link_url.startswith("http"): continue

            has_medical = any(k in title for k in KW_MEDICAL)
            has_equipment = any(k in title for k in KW_EQUIPMENT)
            
            if has_medical or ("医院" in title):
                items.append({
                    "url": link_url, "title": title,
                    "source_type": get_stype(name),
                    "info_type": get_itype(title),
                    "category": get_cat(title),
                    "brand": get_brand(title),
                    "model": get_model(title),
                    "supplier": get_supplier(title),
                    "reg_num": get_reg_num(title),
                    "publish_date": get_dt(link_url),
                    "region": get_reg(title)
                })
                print(f"  + {title[:60]}")

        page.close()

        for i in items:
            if i['url'] not in sent: save_sent(i['url'])
        all_r[name] = items
        print(f"  => {len(items)}")

    b.close()

total = sum(len(v) for v in all_r.values())
print(f"\n[Total] {total}")

for name, cnt in all_r.items():
    print(f"  {name}: {cnt}")

print("[Email] Sending...")
try:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    
    if total > 0:
        msg['Subject'] = f"吉林省医疗设备招标 - {total}条"
        body = f"发现{total}条医疗采购信息:\n\n"
        for name, items in all_r.items():
            if not items: continue
            body += f"【{name}】- {len(items)}条\n"
            body += "-"*40 + "\n"
            for i in items:
                body += f"标题: {i['title'][:60]}\n"
                body += f"  来源: {i['source_type']} | 类型: {i['info_type']} | 分类: {i['category']}\n"
                body += f"  链接: {i['url']}\n\n"
    else:
        msg['Subject'] = "吉林省医疗设备招标 - 无匹配数据"
        body = f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n本次爬取未发现匹配的医疗采购信息。\n\n可能原因:\n1. 网站近期无医疗设备招标\n2. 关键词需要调整\n3. 网站结构变化\n\n如需调整关键词，请联系管理员。"

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
    server.quit()
    print("[Email] OK")
except Exception as e:
    print(f"[Email] Failed: {e}")
