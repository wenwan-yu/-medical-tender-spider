# 医疗相关关键词
MEDICAL_KEYWORDS = [
    "医疗", "医药", "卫生", "医院", "药品", "器材", "耗材",
    "设备", "试剂", "疫苗", "防疫", "保健", "康复", "诊断",
    "检验", "监测", "监护", "手术", "医用", "器械", "X光",
    "CT", "核磁", "超声", "生化", "血球", "免疫", "核酸",
    "药房", "药材", "制药", "生物", "抗菌", "抗生素", "输液",
    "针管", "导管", "支架", "人工", "植入", "齿科", "牙科",
    "眼科", "耳鼻喉", "妇产", "儿科", "骨科", "神经", "心脑",
    "透析", "呼吸", "麻醉", "监护", "急救", "护理", "内窥镜"
]

# 招标类型关键词
TENDER_TYPE_KEYWORDS = ["采购", "招标", "中标", "成交", "投标", "供应商", "公告", "竞争", "单一来源"]

# 招标网站配置 - 直接指向采购公告页面
TENDER_SITES = [
    {
        "id": "jl-cggg",
        "name": "吉林省政府采购-采购公告",
        "base_url": "https://www.jl.gov.cn",
        "list_url": "https://www.jl.gov.cn/ggzy/zfcg/cggg/",
        "category": "采购公告",
    },
    {
        "id": "jl-zbgg",
        "name": "吉林省政府采购-中标公告",
        "base_url": "https://www.jl.gov.cn",
        "list_url": "https://www.jl.gov.cn/ggzy/zfcg/zbgg/",
        "category": "中标公告",
    },
]

EMAIL_CONFIG = {
    "enabled": True,
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender_email": "1192368708@qq.com",
    "sender_password": "lyvcpezdrgeriegj",
    "receiver_email": "1192368708@qq.com",
    "use_ssl": True,
}

# 爬虫配置
SPIDER_CONFIG = {
    "timeout": 30,
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
    "max_items": 50,
}

import os
LOCAL_MODE = os.environ.get('LOCAL_MODE', 'true').lower() == 'true'