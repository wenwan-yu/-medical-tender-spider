"""
医疗招标信息爬虫 - 测试版（使用示例数据演示格式）
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from datetime import datetime
from notifier import EmailNotifier
from database import init_db, is_notification_sent, mark_notification_sent, get_record_count

# 爬取时间
CRAWL_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 测试数据 - 从之前搜索结果中获取的真实医疗招标
SAMPLE_TENDERS = [
    {
        'url': 'https://www.jl.gov.cn/ggzy/zfcg/cggg/202505/t20250506_9214827.html',
        'title': '4K3D荧光胸腔镜系统招标公告',
        'source': '吉林省公共资源交易网',
        'publish_type': '招标公告',
        'category': '设备类',
        'publish_date': '2025-04-30',
        'region': '吉林省',
    },
    {
        'url': 'https://www.jl.gov.cn/ggzy/zfcg/cggg/202509/t20250929_9330432.html',
        'title': '长春中医药大学附属第三临床医院电子胃肠镜系统等设备采购项目',
        'source': '吉林省公共资源交易网',
        'publish_type': '招标公告',
        'category': '设备类',
        'publish_date': '2025-09-29',
        'region': '长春市',
    },
    {
        'url': 'https://www.jl.gov.cn/ggzy/ybzggzy/ybzjyxx/ybzzfcg/ccszccggg/202509/t20250924_9327173.html',
        'title': '敦化市医院脊柱内窥镜手术系统采购项目',
        'source': '延边州公共资源交易中心',
        'publish_type': '竞争性谈判',
        'category': '设备类',
        'publish_date': '2025-09-24',
        'region': '延边州',
    },
    {
        'url': 'https://www.jl.gov.cn/ggzy/spsggzy/spsjyxx/spszfcg/ccszczbgs/202509/t20250905_9316252.html',
        'title': '双辽市中心医院紧密型县域医共体五大共享中心升级建设项目采购医疗设备及车辆等',
        'source': '四平市公共资源交易中心',
        'publish_type': '中标公告',
        'category': '设备类',
        'publish_date': '2025-09-05',
        'region': '四平市',
    },
    {
        'url': 'https://www.jl.gov.cn/ggzy/cbsbhkfqggzy/cbsbhkfqjyxx/cbsbhkfqzfcg/cbsbhkfqzccggg/202509/t20250916_9321765.html',
        'title': '池西医院医用X线设备采购',
        'source': '长白山公共资源交易中心',
        'publish_type': '招标公告',
        'category': '设备类',
        'publish_date': '2025-09-16',
        'region': '长白山',
    },
]

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

    for item in items:
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

    # 底部说明
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
    print("医疗招标信息监控爬虫 - 测试版")
    print(f"爬取时间: {CRAWL_TIME}")
    print("=" * 60)

    init_db()
    print(f"已跟踪 {get_record_count()} 条历史记录\n")

    # 使用示例数据
    items = SAMPLE_TENDERS

    # 过滤已发送的
    new_items = []
    for item in items:
        url = item.get('url', '')
        if url and not is_notification_sent(url):
            new_items.append(item)
            mark_notification_sent(url)

    print(f"新招标: {len(new_items)} 条")

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