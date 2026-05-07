import os, re, smtplib
from datetime import datetime
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENT_FILE = "sent_urls.txt"

# 邮件配置 - 从环境变量读取
EMAIL_USER = os.environ.get('EMAIL_USER', '1192368708@qq.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', 'lyvcpezdrgeriegj')

sites = [
    ("吉林省人民政府公共资源专栏", "https://www.jl.gov.cn/ggzy/index.html"),
    ("中国采购与招标网", "https://www.chinabidding.cn/tg/sem/index.html"),
    ("军队采购网", "https://www.plap.mil.cn/"),
    ("吉林省政府采购网", "http://www.ccgp-jilin.gov.cn/site/category?parentId=550068&childrenCode=ZcyAnnouncement"),
]

KW = ["医疗", "设备", "仪器", "器械", "耗材", "试剂"]

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f: 
            return set(l.strip() for l in f if l.strip())
    return set()

def save_sent(url):
    with open(SENT_FILE, "a", encoding="utf-8") as f: f.write(url+"\n")

def get_stype(n):
    if "吉林省" in n and "政府" in n: return "省级采购"
    if "采购与招标" in n: return "招标门户"
    if "军队" in n: return "军队采购"
    return "其他"

def get_itype(t):
    for k,v in [('招标','招标'),('投标','投标'),('采购','采购'),('中标','中标'),('成交','成交'),('结果','结果')]:
        if k in t: return v
    return "公告"

def get_cat(t):
    for ks,c in [
        (['CT','核磁','MRI','X光','DR','B超','彩超','超声'],'设备类-大型影像'),
        (['心电','监护','脑电','血氧','血压'],'设备类-生命体征'),
        (['内窥镜','胃镜','肠镜','腹腔镜','胸腔镜'],'设备类-内窥镜'),
        (['生化','血球','血凝','免疫','PCR','核酸','检验'],'设备类-检验设备'),
        (['呼吸机','麻醉机','透析机','监护仪'],'设备类-治疗设备'),
        (['手术','无影灯','手术床','手术台'],'设备类-手术设备'),
        (['康复','理疗','按摩'],'设备类-康复设备'),
        (['耗材','试剂','敷料','针','管'],'耗材类'),
        (['口罩','防护','手套','隔离'],'耗材类-防护'),
    ]:
        if any(k in t for k in ks): return c
    return "其他"

def get_brand(t):
    for b in ['GE','西门子','飞利浦','Siemens','Philips','GE医疗','佳能','Sony','奥林巴斯','Pentax','富士','Fujifilm']:
        if b in t: return b
    return "-"

def get_model(t):
    return "-"

def get_supplier(t):
    return "-"

def get_reg_num(t):
    return "-"

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
        page.goto(url, timeout=30000)
        page.wait_for_timeout(3000)
        
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        print(f"  Links: {len(links)}")
        
        for a in links:
            title = a.get_text(strip=True)
            href = a.get("href", "")
            
            if len(title) < 8 or not href or href in ["#",""]: continue
            if href in ["javascript:;","javascript:void(0)"]: continue
            
            link_url = urljoin(url, href)
            if not link_url.startswith("http"): continue
            
            for k in KW:
                if k in title:
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
                    print(f"  + {title[:40]}")
                    break
                    break
        
        page.close()
        
        for i in items:
            if i['url'] not in sent: save_sent(i['url'])
        all_r[name] = items
        print(f"  => {len(items)}")
    
    b.close()

total = sum(len(v) for v in all_r.values())
print(f"\n[Total] {total}")

jl = len(all_r.get('吉林省人民政府公共资源专栏',[]))
cb = len(all_r.get('中国采购与招标网',[]))
jun = len(all_r.get('军队采购网',[]))
jl2 = len(all_r.get('吉林省政府采购网',[]))
print(f"[Check] 吉林省:{jl} | 招标网:{cb} | 军队:{jun} | 政府采购网:{jl2}")

if total > 0:
    print("[Email] Sending new data...")
    try:
        msg = MIMEMultipart()
        msg['From'] = "1192368708@qq.com"
        msg['To'] = "1192368708@qq.com"
        msg['Subject'] = f"吉林省医疗设备招标 - {total}条"
        
        body = f"发现{total}条医疗采购信息:\n\n"
        
        for name, items in all_r.items():
            if not items: continue
            body += f"【{name}】- {len(items)}条\n"
            body += "-"*40 + "\n"
            for i in items:
                body += f"标题: {i['title'][:60]}\n"
                body += f"  来源: {i['source_type']} | 类型: {i['info_type']} | 分类: {i['category']}\n"
                body += f"  品牌: {i['brand']} | 型号: {i['model']} | 供应商: {i['supplier']}\n"
                body += f"  注册证: {i['reg_num']} | 日期: {i['publish_date']} | 地区: {i['region']}\n"
                body += f"  链接: {i['url']}\n\n"
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print("[Email] OK")
    except Exception as e:
        print(f"[Email] Failed: {e}")
else:
    print("[Email] No new data")