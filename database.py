import os
import sys

SENT_URLS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sent_urls.txt")

def init_db():
    print(f"数据库文件: {SENT_URLS_FILE}")
    if not os.path.exists(SENT_URLS_FILE):
        with open(SENT_URLS_FILE, 'w', encoding='utf-8') as f:
            f.write("# 已发送的招标URL列表\n")
    return None

def load_sent_urls():
    sent_urls = set()
    if os.path.exists(SENT_URLS_FILE):
        with open(SENT_URLS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):
                    sent_urls.add(url)
    return sent_urls

def is_notification_sent(url):
    sent_urls = load_sent_urls()
    return url in sent_urls

def mark_notification_sent(url):
    with open(SENT_URLS_FILE, 'a', encoding='utf-8') as f:
        f.write(url + '\n')

def get_record_count():
    sent_urls = load_sent_urls()
    return len(sent_urls) - 1  # 减去标题行