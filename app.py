from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json
from datetime import datetime
import os

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = '你的LINE_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = '你的LINE_SECRET'

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

    if text.startswith("大便統計"):
        parts = text.split()
        if len(parts) == 2:
            month = parts[1]
        else:
            month = datetime.now().strftime('%Y-%m')

        data = load_data()
        reply_text = f"{month} 大便💩統計：\n"

        if group_id and group_id in data and month in data[group_id]:
            user_data = data[group_id][month]
            sorted_users = sorted(user_data.items(), key=lambda x: x[1], reverse=True)
            medals = ['🥇', '🥈', '🥉']

            for idx, (uid, count) in enumerate(sorted_users):
                try:
                    profile = line_bot_api.get_group_member_profile(group_id, uid)
                    name = profile.display_name
                except Exception:
                    name = f"使用者 {uid[:5]}"

                medal = medals[idx] if idx < 3 else ''
                reply_text += f"{medal}{name}：{count} 次\n"
        else:
            reply_text += "這個月大家都還沒大便💩哦！"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
