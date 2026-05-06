"""
医疗招标爬虫 - 完整版（12个网站）
"""
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CRAWL_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

TENDER_SITES = [
    {"name": "吉林省公共资源交易中心", "url": "http://www.ggzyzx.jl.gov.cn/jyxx/zfcg/zbgg/"},
    {"name": "吉林省政府采购网", "url": "http://www.ccgp-jilin.gov.cn/"},
    {"name": "政采云平台", "url": "https://www.zcygov.cn/"},
    {"name": "中国政府采购网", "url": "http://www.ccgp.gov.cn/"},
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
    kw = ['医疗设备', '医疗器械', '医用耗材', '检验试剂', '骨科', '介入', '超声', 'CT', '监护仪', '康复', '保健', '手术室', '超声设备', '检验设备', '医用设备', '医疗仪器', '透析', '呼吸机', '麻醉机', '内窥镜', '胃肠镜', '胸腔镜', '肠镜', '胃镜', '生化仪', '血球仪', '免疫仪', 'PCR', '心电图', '脑电图', '彩超', 'B超', 'DR', 'X光']
    return any(k in title for k in kw)

def crawl_site(site):
    items = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(site['url'], headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            title = a.get_text(strip=True)
            if not title or len(title) < 8:
                continue
            if '.html' not in href and 'http' not in href:
                continue
            if href.startswith('http'):
                url = href
            elif href.startswith('/'):
                url = site['url'].rstrip('/') + '/' + href.lstrip('/')
            else:
                continue
            if is_medical(title):
                items.append({'title': title, 'url': url, 'source': site['name']})
                print(f"  ✓ {title[:45]}")
    except Exception as e:
        print(f"  ✗ 无法访问")
    return items

def send_email(all_results):
    total = sum(len(items) for items in all_results.values())
    if total == 0:
        print("没有医疗招标")
        return
    html = f'<html><body><h3>爬取时间: {CRAWL_TIME}</h3><p>共获取 <b>{total}</b> 条精准医疗招标</p><ul>'
    for site_name, items in all_results.items():
        if items:
            html += f'<li><b>{site_name}</b>: {len(items)} 条</li>'
    html += '</ul><table border="1" cellpadding="5"><tr><th>来源</th><th>招标项目</th><th>链接</th></tr>'
    all_items = []
    for items in all_results.values():
        all_items.extend(items)
    for item in all_items[:50]:
        html += f'<tr><td>{item["source"]}</td><td>{item["title"][:40]}</td><td><a href="{item["url"]}">查看</a></td></tr>'
    html += '</table></body></html>'
    msg = MIMEMultipart()
    msg['From'] = '1192368708@qq.com'
    msg['To'] = '1192368708@qq.com'
    msg['Subject'] = f'【{total}条医疗招标】{CRAWL_TIME}'
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login('1192368708@qq.com', 'lyvcpezdrgeriegj')
        server.sendmail('1192368708@qq.com', '1192368708@qq.com', msg.as_string())
        server.quit()
        print("\n✓ 邮件已发送!")
    except Exception as e:
        print(f"\n✗ 邮件失败: {e}")

def main():
    print(f"开始爬取 - {CRAWL_TIME}\n")
    all_results = {}
    for site in TENDER_SITES:
        print(f"【{site['name']}】")
        items = crawl_site(site)
        all_results[site['name']] = items
        if items:
            print(f"  -> {len(items)} 条")
    total = sum(len(items) for items in all_results.values())
    print(f"\n总计: {total} 条")
    sent_urls = load_sent()
    new_items = []
    for items in all_results.values():
        for item in items:
            if item['url'] not in sent_urls:
                new_items.append(item)
                save_sent(item['url'])
    print(f"新招标: {len(new_items)} 条")
    send_email(all_results)

if __name__ == "__main__":
    main()
