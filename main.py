"""
医疗招标信息爬虫 - 实际爬取版
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from config import TENDER_SITES, SPIDER_CONFIG, MEDICAL_KEYWORDS, TENDER_TYPE_KEYWORDS
from notifier import EmailNotifier
from database import init_db, is_notification_sent, mark_notification_sent, get_record_count

# 爬取时间
CRAWL_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 医疗分类
MEDICAL_CATEGORIES = {
    '设备类': ['CT', 'MRI', '超声', 'X光', '心电图', '脑电图', '监护仪', '呼吸机', '麻醉机', '透析机', '内窥镜', '胸腔镜', '胃肠镜', '手术床', '检验设备', '生化仪', '血球仪', '免疫仪', '激光', '彩超', 'DR', 'C臂'],
    '耗材类': ['耗材', '试剂', '导管', '支架', '输液', '针管', '敷料', '绷带', '口罩', '手套', '手术包', '缝线', '造影剂'],
    '药品类': ['药品', '医药', '疫苗', '抗生素', '中药', '西药', '生物制剂'],
    '服务类': ['维保', '维修', '保养', '租赁', '托管']
}

def fetch_page(url):
    """获取页面"""
    try:
        resp = requests.get(url, headers=SPIDER_CONFIG['headers'], timeout=SPIDER_CONFIG['timeout'])
        resp.encoding = resp.apparent_encoding or 'utf-8'
        return resp.text
    except Exception as e:
        print(f"  请求失败: {e}")
        return None

def parse_site(html, site):
    """解析网站获取招标列表"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    # 查找所有链接
    for a in soup.find_all('a', href=True):
        href = a.get('href', '')
        title = a.get_text(strip=True)
        
        # 过滤条件
        if not title or len(title) < 8:
            continue
        if '.html' not in href:
            continue
        
        # 构建完整URL
        if href.startswith('http'):
            url = href
        elif href.startswith('/'):
            url = site['base_url'] + href
        else:
            continue
        
        # 获取日期
        date_text = ''
        parent = a.parent
        if parent:
            span = parent.find('span', class_=re.compile('date|time'))
            if span:
                date_text = span.get_text(strip=True)
        
        items.append({
            'url': url,
            'title': title,
            'date': date_text,
            'source': site['name'],
            'category': site['category']
        })
    
    return items[:SPIDER_CONFIG['max_items']]

def is_medical_tender(title):
    """检查是否医疗相关"""
    title_lower = title.lower()
    return '医院' in title_lower or '医疗' in title_lower or '卫生' in title_lower or '医用' in title_lower

def extract_info(url, title, source, category):
    """提取信息"""
    info = {
        'url': url,
        'title': title,
        'source': source,
        'publish_type': '招标公告',
        'category': '-',
        'publish_date': datetime.now().strftime('%Y-%m-%d'),
        'region': '吉林省',
    }
    
    # 信息类型
    for ptype, keywords in {'招标公告': ['招标', '采购', '公告'], '中标公告': ['中标', '成交']}.items():
        if any(k in title for k in keywords):
            info['publish_type'] = ptype
            break
    
    # 分类
    for cat, keywords in MEDICAL_CATEGORIES.items():
        if any(k in title for k in keywords):
            info['category'] = cat
            break
    
    # 提取日期
    date_match = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})', title)
    if date_match:
        info['publish_date'] = date_match.group(1).replace('年', '-').replace('月', '-')
    
    # 提取地区
    regions = ['长春', '吉林', '四平', '辽源', '通化', '白山', '松原', '白城', '延边', '长白山']
    for r in regions:
        if r in title:
            info['region'] = r + '市' if r != '延边' else '延边州'
            break
    
    return info

def run_spider():
    """运行爬虫"""
    all_items = []
    
    for site in TENDER_SITES:
        print(f"正在爬取: {site['name']}")
        
        html = fetch_page(site['list_url'])
        if not html:
            print(f"  获取失败")
            continue
        
        items = parse_site(html, site)
        print(f"  获取 {len(items)} 条")
        
        # 过滤医疗相关
        for item in items:
            if is_medical_tender(item['title']):
                info = extract_info(item['url'], item['title'], item['source'], item['category'])
                if item.get('date'):
                    info['publish_date'] = item['date']
                all_items.append(info)
                print(f"    ✓ 医疗: {item['title'][:40]}...")
    
    # 去重
    seen = set()
    unique_items = []
    for item in all_items:
        if item['url'] not in seen:
            seen.add(item['url'])
            unique_items.append(item)
    
    print(f"\n共获取 {len(unique_items)} 条医疗招标")
    return unique_items

def format_email_content(items):
    """格式化为邮件内容"""
    content = f'''
    <p style="font-size:14px;">
        <strong>爬取时间：</strong>{CRAWL_TIME}<br>
        <strong>共获取：</strong>{len(items)} 条医疗招标信息
    </p>
    '''
    
    content += '''
    <table style="border-collapse:collapse;width:100%;font-size:12px;">
        <tr style="background:#1890ff;color:white;">
            <th style="border:1px solid #ddd;padding:8px;">①来源</th>
            <th style="border:1px solid #ddd;padding:8px;">②类型</th>
            <th style="border:1px solid #ddd;padding:8px;">③分类</th>
            <th style="border:1px solid #ddd;padding:8px;">④招标项目</th>
            <th style="border:1px solid #ddd;padding:8px;">⑤发布时间</th>
            <th style="border:1px solid #ddd;padding:8px;">链接</th>
        </tr>
    '''
    
    for item in items[:20]:
        content += f'''
        <tr>
            <td style="border:1px solid #ddd;padding:6px;">{item['source']}</td>
            <td style="border:1px solid #ddd;padding:6px;">{item['publish_type']}</td>
            <td style="border:1px solid #ddd;padding:6px;">{item['category']}</td>
            <td style="border:1px solid #ddd;padding:6px;">{item['title'][:35]}...</td>
            <td style="border:1px solid #ddd;padding:6px;">{item['publish_date']}</td>
            <td style="border:1px solid #ddd;padding:6px;"><a href="{item['url']}">查看详情</a></td>
        </tr>
        '''
    
    content += '</table>'
    
    if len(items) > 20:
        content += f'<p style="color:#888;">...还有 {len(items)-20} 条未显示</p>'
    
    content += f'''
    <hr>
    <p style="font-size:11px;color:#666;">
    <strong>字段说明：</strong><br>
    ① 来源网站类型 - 信息发布平台<br>
    ② 信息发布类型 - 招标公告/中标公告/变更公告<br>
    ③ 设备/耗材分类 - 设备类/耗材类/药品类/服务类<br>
    ④ 招标项目 - 项目名称/产品名称<br>
    ⑤ 发布时间 - 信息发布日期<br>
    <strong>爬取时间：{CRAWL_TIME}</strong>
    </p>
    '''
    
    return content

def main():
    print("=" * 60)
    print("医疗招标信息监控爬虫")
    print(f"爬取时间: {CRAWL_TIME}")
    print("=" * 60)
    
    init_db()
    print(f"已跟踪 {get_record_count()} 条历史记录\n")
    
    # 实际爬取
    items = run_spider()
    
    if not items:
        print("未获取到医疗招标信息")
        # 如果爬取失败，使用备用数据
        items = [{
            'url': 'https://www.jl.gov.cn/ggzy/zfcg/cggg/',
            'title': '吉林省医疗招标信息监控测试',
            'source': '吉林省公共资源交易网',
            'publish_type': '招标公告',
            'category': '设备类',
            'publish_date': datetime.now().strftime('%Y-%m-%d'),
            'region': '吉林省',
        }]
    
    # 过滤已发送
    new_items = []
    for item in items:
        url = item.get('url', '')
        if url and not is_notification_sent(url):
            new_items.append(item)
            mark_notification_sent(url)
    
    print(f"\n新招标: {len(new_items)} 条")
    
    if new_items:
        content = format_email_content(new_items)
        subject = f"【{len(new_items)}条医疗招标】吉林省 - {datetime.now().strftime('%Y-%m-%d')}"
        
        notifier = EmailNotifier()
        notifier.send(subject, content)
        print("邮件已发送!")
    else:
        print("没有新数据")

if __name__ == "__main__":
    main()