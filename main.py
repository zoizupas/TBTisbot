from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

# 讀取環境變數
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_API_KEY}"
DEFAULT_MODEL = "deepseek/deepseek-chat:free"

# Telegram Webhook Endpoint
@app.post("/webhook")
async def telegram_webhook(request: Request):
    payload = await request.json()
    message = payload.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_message = message.get("text")

    if not chat_id or not user_message:
        return {"status": "ignored"}

    # Step 1: 呼叫 OpenRouter API 取得 AI 回覆
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://tbtisbot.onrender.com",
        "Content-Type": "application/json"
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
            "content": user_message
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=body,
                timeout=30
            )
            response.raise_for_status()
            reply_text = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        reply_text = f"❗ AI 回覆失敗：{str(e)}"

    # Step 2: 回傳 AI 回覆到 Telegram 使用者
    send_message_url = f"{TELEGRAM_API_URL}/sendMessage"
    await httpx.post(
        send_message_url,
        json={"chat_id": chat_id, "text": reply_text}
    )

    return {"status": "ok"}
