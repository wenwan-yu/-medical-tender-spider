import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG

class EmailNotifier:
    def __init__(self):
        self.config = EMAIL_CONFIG

    def send(self, subject, content):
        if not self.config.get("enabled", False):
            print("邮件通知未启用")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config["sender_email"]
            msg['To'] = self.config["receiver_email"]
            msg['Subject'] = subject

            # HTML格式邮件
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background: #1890ff; color: white; padding: 15px; }}
                    .content {{ padding: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                    th {{ background: #f5f5f5; }}
                    a {{ color: #1890ff; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>📢 招标信息监控通知</h2>
                </div>
                <div class="content">
                    {content}
                </div>
                <p style="color: #888; font-size: 12px;">
                    本邮件由自动监控系统发送
                </p>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 连接邮件服务器
            if self.config.get("use_ssl", True):
                server = smtplib.SMTP_SSL(
                    self.config["smtp_server"],
                    self.config["smtp_port"]
                )
            else:
                server = smtplib.SMTP(
                    self.config["smtp_server"],
                    self.config["smtp_port"]
                )
                server.starttls()

            # 登录并发送
            server.login(
                self.config["sender_email"],
                self.config["sender_password"]
            )
            server.sendmail(
                self.config["sender_email"],
                self.config["receiver_email"],
                msg.as_string()
            )
            server.quit()

            print(f"邮件发送成功: {subject}")
            return True

        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False

    def send_new_tenders(self, items):
        if not items:
            return

        content = f"""
        <p>发现 <strong>{len(items)}</strong> 条新招标信息：</p>
        <table>
            <tr>
                <th>来源</th>
                <th>标题</th>
                <th>链接</th>
            </tr>
        """

        for item in items[:20]:  # 最多显示20条
            content += f"""
            <tr>
                <td>{item.get('source', '')}</td>
                <td>{item['title']}</td>
                <td><a href="{item['url']}">查看详情</a></td>
            </tr>
            """

        content += "</table>"

        if len(items) > 20:
            content += f"<p>...还有 {len(items) - 20} 条未显示</p>"

        sources = list(set(item['source'] for item in items))
        source_str = ', '.join(sources) if len(sources) <= 2 else f"{sources[0]}等{len(sources)}个网站"
        subject = f"【{len(items)}条新招标】{source_str}"
        self.send(subject, content)