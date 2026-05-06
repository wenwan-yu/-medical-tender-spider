import requests
from bs4 import BeautifulSoup
import re
from config import TENDER_SITES, SPIDER_CONFIG

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 医疗关键词（用于分类）
MEDICAL_KEYWORDS = {
    '设备类': ['CT', 'MRI', '超声', 'X光', '心电图', '脑电图', '监护仪', '呼吸机', '麻醉机', '透析机', '内窥镜', '手术床', '检验设备', '生化仪', '血球仪', '免疫仪', 'PCR', '核酸仪'],
    '耗材类': ['耗材', '试剂', '导管', '支架', '输液', '针管', '敷料', '绷带', '口罩', '手套', '手术包', '缝线', '造影剂'],
    '药品类': ['药品', '医药', '疫苗', '抗生素', '中药', '西药', '生物制剂'],
    '服务类': ['维保', '维修', '保养', '租赁', '托管']
}

# 招标类型关键词
TENDER_TYPE_KEYWORDS = ['招标', '采购', '中标', '成交', '竞争性', '单一来源', '询价', '投标', '公告']

def extract_info(url, title):
    """提取8大类信息"""
    info = {
        '来源网站': '',
        '信息类型': '',
        '设备/耗材分类': '',
        '产品信息': '',
        '采购单位': '',
        '注册证号': '',
        '时间地域': '',
        '正文内容': ''
    }

    try:
        # 1. 来源网站
        if 'jl.gov.cn' in url:
            info['来源网站'] = '吉林省公共资源交易网'
        elif 'ggzyzx.jl.gov.cn' in url:
            info['来源网站'] = '吉林省公共资源交易中心'
        else:
            info['来源网站'] = url.split('/')[2] if 'http' in url else '未知'

        # 2. 信息类型
        for t in TENDER_TYPE_KEYWORDS:
            if t in title:
                if t in ['招标', '采购', '公告']:
                    info['信息类型'] = '招标信息'
                elif t in ['中标', '成交']:
                    info['信息类型'] = '中标结果'
                break

        # 3. 设备/耗材分类
        for category, keywords in MEDICAL_KEYWORDS.items():
            for kw in keywords:
                if kw in title:
                    info['设备/耗材分类'] = category
                    break

        # 4. 产品信息
        info['产品信息'] = title

        # 5. 尝试获取正文内容
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.encoding = r.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')

            # 获取文本内容
            text = soup.get_text(separator=' ', strip=True)[:2000]

            # 提取采购单位
            units = re.findall(r'(.{2,10}医院|.{2,10}卫生|.{2,10}医疗|.{2,10}疾控)', text)
            if units:
                info['采购单位'] = units[0]

            # 提取注册证号（最精准标识）
            reg_numbers = re.findall(r'(国械注\d+|国械注进\d+|国械备\d+|注册证号[：:]?\s*[A-Za-z0-9]+)', text)
            if reg_numbers:
                info['注册证号'] = reg_numbers[0][:50]

            # 提取时间
            dates = re.findall(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)', text)
            if dates:
                info['时间地域'] = dates[0]

            # 提取地域
            regions = re.findall(r'(吉林省|长春市|吉林市|四平市|辽源市|通化市|白山市|松原市|白城市|延边州)', text)
            if regions:
                info['时间地域'] += ' ' + regions[0]

            info['正文内容'] = text[:500] + '...'

        except Exception as e:
            pass

    except Exception as e:
        pass

    return info

# 爬取并提取信息
def crawl_medical_tenders():
    print("=" * 80)
    print("吉林省医疗招标信息爬取（8大类分类）")
    print("=" * 80)

    # 测试URL - 使用已知有效的医疗招标
    test_urls = [
        ('https://www.jl.gov.cn/ggzy/zfcg/cggg/202505/t20250506_9214827.html', '4K3D荧光胸腔镜系统招标公告'),
        ('https://www.jl.gov.cn/ggzy/zfcg/zbgg/202505/t20250520_9234642.html', '吉林省肿瘤医院医用设备及医院信息系统维保服务'),
        ('https://www.jl.gov.cn/ggzy/ccsggzy/ccsjyxx/ccszfcg/ccszccggg/202509/t20250928_9329395.html', '公主岭市第三人民医院医用激光仪器及设备采购项目'),
    ]

    all_info = []

    for url, title in test_urls:
        print(f"\n正在处理: {title}")
        info = extract_info(url, title)
        info['产品信息'] = title
        all_info.append(info)

    return all_info

def display_results(infos):
    """按8大类展示结果"""
    for i, info in enumerate(infos, 1):
        print(f"\n{'='*80}")
        print(f"第{i}条: {info['产品信息'][:60]}...")
        print(f"{'='*80}")

        fields = [
            ("① 来源网站类型", info['来源网站']),
            ("② 信息发布类型", info['信息类型']),
            ("③ 设备/耗材分类", info['设备/耗材分类']),
            ("④ 产品名+品牌+型号+参数", info['产品信息']),
            ("⑤ 厂家/供应商/医院采购单位", info['采购单位']),
            ("⑥ 医疗器械注册证编号", info['注册证号']),
            ("⑦ 时间+地域", info['时间地域']),
            ("⑧ 正文内容+关键词标签", info['正文内容'][:200] + '...'),
        ]

        for label, value in fields:
            if value:
                print(f"  {label}: {value}")

if __name__ == "__main__":
    results = crawl_medical_tenders()
    display_results(results)