# 医疗招标信息自动监控系统

自动爬取吉林省医疗招标信息，每小时更新，通过邮件通知。

## 功能特性

- ✅ 自动爬取医疗招标信息（医院、医疗设备、耗材等）
- ✅ 每小时自动运行
- ✅ 邮件自动推送新招标
- ✅ 自动过滤重复信息
- ✅ 8大类精准分类（来源、类型、分类、项目、时间等）

## 项目结构

```
tender-spider/
├── main.py           # 主程序
├── config.py         # 配置文件（网站、关键词、邮件等）
├── spider.py         # 爬虫逻辑
├── database.py      # 数据存储（去重）
├── notifier.py       # 邮件通知
├── requirements.txt  # Python依赖
├── sent_urls.txt     # 已发送URL记录（自动更新）
└── .github/
    └── workflows/
        └── run.yml  # GitHub Actions 自动部署
```

## 本地运行

```bash
pip install -r requirements.txt
python main.py
```

## 部署到 GitHub

### 1. 创建 GitHub 仓库

1. 登录 GitHub，创建新仓库（如 `medical-tender-spider`）
2. 上传本项目所有文件（不包括 `__pycache__`）

### 2. 配置 Secrets

在仓库 → Settings → Secrets and variables → Actions 中添加：

| Secret Name | 说明 | 示例值 |
|-------------|------|--------|
| SMTP_SERVER | SMTP服务器 | smtp.qq.com |
| SMTP_PORT | SMTP端口 | 465 |
| SMTP_USER | 发件人邮箱 | 1192368708@qq.com |
| SMTP_PASSWORD | SMTP授权码 | xxxxxxxxxxxx |
| RECEIVER_EMAIL | 收件人邮箱 | 1192368708@qq.com |

### 3. 启用自动运行

- 提交代码后，Actions 会自动运行
- 之后每小时自动运行一次
- 可以手动触发：在 Actions 页面点击 "Run workflow"

---

## 维护指南

### 如何修改配置

#### 1. 修改爬取网站

编辑 `config.py` 中的 `TENDER_SITES`：

```python
TENDER_SITES = [
    {
        "id": "jl-cggg",
        "name": "吉林省政府采购-采购公告",
        "base_url": "https://www.jl.gov.cn",
        "list_url": "https://www.jl.gov.cn/ggzy/zfcg/cggg/",
        "category": "采购公告",
    },
    # 添加更多网站...
]
```

#### 2. 修改医疗关键词

编辑 `config.py` 中的 `MEDICAL_KEYWORDS`：

```python
MEDICAL_KEYWORDS = [
    "医疗", "医院", "设备", "耗材", "试剂",
    # 添加更多关键词...
]
```

#### 3. 修改运行频率

编辑 `.github/workflows/run.yml`：

```yaml
# 每小时运行（当前）
- cron: '0 * * * *'

# 每6小时运行
- cron: '0 */6 * * *'

# 每天早上8点运行
- cron: '0 0 * * *'
```

### 常见维护任务

| 任务 | 操作 |
|------|------|
| 手动触发爬取 | GitHub → Actions → Run workflow |
| 查看运行日志 | GitHub → Actions → 点击具体运行 |
| 修改关键词 | 编辑 `config.py` 后提交 |
| 停止运行 | 删除仓库或修改 workflow |

### 调试本地运行

```bash
# 测试运行
python main.py

# 查看日志
# 邮件会显示爬取结果
```

---

## 字段说明（8大类）

| 字段 | 说明 |
|------|------|
| ① 来源网站类型 | 信息发布平台 |
| ② 信息发布类型 | 招标公告/中标公告/变更公告 |
| ③ 设备/耗材分类 | 设备类/耗材类/药品类/服务类 |
| ④ 招标项目 | 项目名称/产品名称 |
| ⑤ 发布时间 | 信息发布日期 |
| 爬取时间 | 抓取时的系统时间 |

---

## 问题排查

### Q: 邮件收不到？
A: 检查 SMTP 授权码是否正确，查看 GitHub Actions 日志

### Q: 爬取不到数据？
A: 可能目标网站有反爬措施，需要更新爬虫逻辑

### Q: 想增加其他网站？
A: 在 `config.py` 中添加新站点配置，修改 `spider.py` 适配页面结构

---

## 技术支持

如有问题，请查看：
1. GitHub Actions 运行日志
2. 本地运行测试 `python main.py`