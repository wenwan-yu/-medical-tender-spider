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
TENDER_SITES = [
    {"id": "ggzyzx", "name": "吉林省公共资源交易中心", "base_url": "http://www.ggzyzx.jl.gov.cn", "list_url": "http://www.ggzyzx.jl.gov.cn/jyxx/zfcg/zbgg/", "category": "省级-中标公告"},
    {"id": "ccgp-jilin", "name": "吉林省政府采购网", "base_url": "http://www.ccgp-jilin.gov.cn", "list_url": "http://www.ccgp-jilin.gov.cn/site/category?parentId=550068&childrenCode=ZcyAnnouncement", "category": "政府采购"},
    {"id": "zcy", "name": "政采云平台", "base_url": "https://www.zcygov.cn", "list_url": "https://www.zcygov.cn/", "category": "政采云"},
    {"id": "ccggzy", "name": "长春市公共资源交易中心", "base_url": "http://www.ccggzy.com.cn", "list_url": "http://www.ccggzy.com.cn/", "category": "长春市"},
    {"id": "jlsggzy", "name": "吉林市公共资源交易中心", "base_url": "http://www.jlsggzyjy.gov.cn", "list_url": "http://www.jlsggzyjy.gov.cn/", "category": "吉林市"},
    {"id": "spggzy", "name": "四平市公共资源交易中心", "base_url": "http://ggzy.siping.gov.cn", "list_url": "http://ggzy.siping.gov.cn/", "category": "四平市"},
    {"id": "ybzggzy", "name": "延边州公共资源交易中心", "base_url": "http://ggzy.yanbian.gov.cn", "list_url": "http://ggzy.yanbian.gov.cn/", "category": "延边州"},
    {"id": "thggzy", "name": "通化市公共资源交易中心", "base_url": "http://ggzy.tonghua.gov.cn", "list_url": "http://ggzy.tonghua.gov.cn/", "category": "通化市"},
    {"id": "syggzy", "name": "松原市公共资源交易中心", "base_url": "http://ggzy.songyuan.gov.cn", "list_url": "http://ggzy.songyuan.gov.cn/", "category": "松原市"},
    {"id": "bcggzy", "name": "白城市公共资源交易中心", "base_url": "http://ggzy.baicheng.gov.cn", "list_url": "http://ggzy.baicheng.gov.cn/", "category": "白城市"},
    {"id": "bsggzy", "name": "白山市公共资源交易中心", "base_url": "http://ggzy.baishan.gov.cn", "list_url": "http://ggzy.baishan.gov.cn/", "category": "白山市"},
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
