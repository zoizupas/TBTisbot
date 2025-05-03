from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage"

# 預設模型，使用 OpenRouter 提供的免費模型
DEFAULT_MODEL = "deepseek/deepseek-chat:free"

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("收到 Telegram 訊息：", data)

    # 抽取訊息與 chat_id
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_text = message.get("text", "")

    if not chat_id or not user_text:
        return {"status": "no message"}

    # 發送至 OpenRouter
    ai_reply = ask_openrouter(user_text)

    # 回傳到 Telegram
    payload = {
        "chat_id": chat_id,
        "text": ai_reply,
    }
    requests.post(TELEGRAM_API_URL, json=payload)

    return {"status": "ok"}

def ask_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/zoizupas/TBTisbot",  # 可以改成你的 GitHub 專案連結
        "X-Title": "TBTisbot",
    }

    body = {
        "model": DEFAULT_MODEL,
        "messages": [
            {
            "role": "system",
            "content": "你是一個 Telegram AI 助理，請以繁體中文回答所有問題。。"
            },
            {
            "role": "user",
            "content": prompt
            }
        ]
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body, timeout=10)
        res.raise_for_status()
        data = res.json()
        print("API 回應：", data)  # 印出回應內容
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("OpenRouter 發生錯誤：", e)
        return "發生錯誤，請稍後再試～"
