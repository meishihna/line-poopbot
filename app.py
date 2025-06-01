from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json
from datetime import datetime
import os

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'poop_data.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    group_id = event.source.group_id if event.source.type == 'group' else None
    text = event.message.text.strip()

    if text == '💩' and group_id:
        data = load_data()
        current_month = datetime.now().strftime('%Y-%m')

        if group_id not in data:
            data[group_id] = {}
        if current_month not in data[group_id]:
            data[group_id][current_month] = {}
        if user_id not in data[group_id][current_month]:
            data[group_id][current_month][user_id] = 0

        data[group_id][current_month][user_id] += 1
        save_data(data)

    # 支援多個月份查詢：「大便統計 2025-05」、「大便統計 2025-05,2025-04」
    if text.startswith("大便統計"):
        # 解析多個月份，允許空白或逗號分隔
        import re
        pattern = r"大便統計[\s,]*(.*)"
        match = re.match(pattern, text)
        months_input = match.group(1) if match else ''
        months = []
        if months_input:
            months = re.split(r'[\s,]+', months_input.strip())
            months = [m for m in months if m]
        if not months:
            months = [datetime.now().strftime('%Y-%m')]

        data = load_data()
        reply_text = ''

        for month in months:
            reply_text += f"{month} 大便💩統計：\n"
            if group_id and group_id in data and month in data[group_id]:
                user_data = data[group_id][month]
                sorted_users = sorted(user_data.items(), key=lambda x: x[1], reverse=True)
                medals = ['🥇', '🥈', '🥉']

                last_count = None
                current_rank = 0
                medal_index = 0

                for idx, (uid, count) in enumerate(sorted_users):
                    if count != last_count:
                        current_rank += 1
                        last_count = count
                        if current_rank > 3:
                            medal_index = None
                        else:
                            medal_index = current_rank - 1  # medals index 0,1,2

                    try:
                        profile = line_bot_api.get_group_member_profile(group_id, uid)
                        name = profile.display_name
                    except Exception:
                        name = f"使用者 {uid[:5]}"

                    medal = medals[medal_index] if medal_index is not None and medal_index < 3 else ''
                    reply_text += f"{medal}{name}：{count} 次\n"
            else:
                reply_text += "這個月大家都還沒大便💩哦！\n"
            reply_text += '\n'

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text.strip())
        )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
