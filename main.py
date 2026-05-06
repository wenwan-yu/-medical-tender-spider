"""
医疗招标信息爬虫 - 简化版
"""
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 读取环境变量配置
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.qq.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 465))
SMTP_USER = os.environ.get('SMTP_USER', '1192368708@qq.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'lyvcpezdrgeriegj')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL', '1192368708@qq.com')

CRAWL_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

MEDICAL_KEYWORDS = ['医院', '医疗', '卫生', '医用', '药品', '器械', '设备', '试剂', '耗材']

TENDER_SITES = [
    {"name": "吉林省公共资源交易中心", "url": "http://www.ggzyzx.jl.gov.cn/jyxx/zfcg/zbgg/"},
    {"name": "吉林省政府采购网", "url": "http://www.ccgp-jilin.gov.cn/"},
    {"name": "长春市公共资源交易中心", "url": "http://www.ccggzy.com.cn/"},
    {"name": "吉林市公共资源交易中心", "url": "http://www.jlsggzyjy.gov.cn/"},
    {"name": "四平市公共资源交易中心", "url": "http://ggzy.siping.gov.cn/"},
    {"name": "延边州公共资源交易中心", "url": "http://ggzy.yanbian.gov.cn/"},
    {"name": "通化市公共资源交易中心", "url": "http://ggzy.tonghua.gov.cn/"},
    {"name": "松原市公共资源交易中心", "url": "http://ggzy.songyuan.gov.cn/"},
    {"name": "白城市公共资源交易中心", "url": "http://ggzy.baicheng.gov.cn/"},
    {"name": "白山市公共资源交易中心", "url": "http://ggzy.baishan.gov.cn/"},
]

SENT_FILE = "sent_urls.txt"

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_sent(url):
    with open(SENT_FILE, 'a', encoding='utf-8') as f:
        f.write(url + '\n')

def is_medical(title):
    title_lower = title.lower()
    return any(k in title_lower for k in MEDICAL_KEYWORDS)

def crawl_site(site):
    items = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(site['url'], headers=headers, timeout=15)
        resp.encoding = resp.apparent_encoding or 'utf-8'
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            title = a.get_text(strip=True)
            
            if not title or len(title) < 10:
                continue
            if '.html' not in href:
                continue
            if not is_medical(title):
                continue
            
            if href.startswith('http'):
                url = href
            elif href.startswith('/'):
                url = site['url'].rstrip('/') + href
            else:
                continue
            
            items.append({'title': title, 'url': url, 'source': site['name']})
            print(f"  ✓ {title[:40]}")
            
    except Exception as e:
        print(f"  ✗ 错误: {e}")
    
    return items

def send_email(items):
    if not items:
        return
    
    html = f'<h3>爬取时间: {CRAWL_TIME}</h3><p>共获取 {len(items)} 条医疗招标信息</p><table border="1" cellpadding="5"><tr><th>来源</th><th>招标项目</th><th>链接</th></tr>'
    
    for item in items[:20]:
        html += f'<tr><td>{item["source"]}</td><td>{item["title"][:40]}...</td><td><a href="{item["url"]}">查看</a></td></tr>'
    
    html += '</table>'
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f'【{len(items)}条医疗招标】{CRAWL_TIME}'
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("邮件发送成功!")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def main():
    print(f"开始爬取 - {CRAWL_TIME}")
    
    sent_urls = load_sent()
    all_items = []
    
    for site in TENDER_SITES:
        print(f"\n正在爬取: {site['name']}")
        items = crawl_site(site)
        all_items.extend(items)
    
    print(f"\n共获取 {len(all_items)} 条医疗招标")
    
    new_items = []
    for item in all_items:
        if item['url'] not in sent_urls:
            new_items.append(item)
            save_sent(item['url'])
    
    print(f"新招标: {len(new_items)} 条")
    
    if new_items:
        send_email(new_items)
    else:
        print("没有新数据")

if __name__ == "__main__":
    main()
