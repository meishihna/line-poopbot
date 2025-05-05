
# 💩 line-poopbot

這是一個用 Python 開發的 LINE Bot，用來統計群組成員傳送 💩 emoji 的次數。

## 📦 專案內容

- `app.py`：主程式，處理 LINE Webhook，記錄 💩 數據。
- `poop_data.json`：存放每個用戶的 💩 統計資料。
- `requirements.txt`：需要安裝的 Python 套件。
- `Procfile`：Render 部署所需的啟動指令。
- `render.yaml`：Render 平台的設定檔（可選）。
- `keep_alive.py`：定時喚醒主服務的背景 worker（可選）。

## 🚀 如何部署

### 1. 安裝需求套件
```
pip install -r requirements.txt
```

### 2. 啟動主程式
```
gunicorn app:app
```

### 3. 在 Render 部署

- Build Command:
  ```
  pip install -r requirements.txt
  ```
- Start Command:
  ```
  gunicorn app:app
  ```

如果需要用 Render Worker 定時喚醒：
- Worker Start Command:
  ```
  python keep_alive.py
  ```

## ⚙️ 環境變數

請在 Render 或本地 `.env` 中設定：
- `LINE_CHANNEL_SECRET`：LINE Channel Secret
- `LINE_CHANNEL_ACCESS_TOKEN`：LINE Channel Access Token

## 📱 LINE Webhook 設定

到 LINE Developers → Messaging API → Webhook URL 填入：
```
https://line-poopbot.onrender.com/callback
```

## 💡 功能說明

- 接收群組內的 💩 emoji 訊息
- 更新並儲存到 `poop_data.json`
- 回覆群組當前 💩 排名

## 🙌 貢獻者

- meishihna
