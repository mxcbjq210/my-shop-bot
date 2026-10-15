import json
import time
import urllib.request
import urllib.parse

TOKEN = "8638546684:AAE4l2_gI6BECvCdguiSqjr9elTqqrfmMNI"
API = f"https://api.telegram.org/bot{TOKEN}"
SHOP_URL = "https://t.me/webappzconnectbot/temp_shop?startapp=shopidzxqawimv9o"

# Нижняя (reply) клавиатура
REPLY_KEYBOARD = {
    "keyboard": [
        [{"text": "🛍 Магазин"}]
    ],
    "resize_keyboard": True,
    "is_persistent": True,
}


def api_call(method, **params):
    url = f"{API}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=60) as r:
        return json.loads(r.read().decode())


def send_message(chat_id, text, reply_markup=None):
    kwargs = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_markup is not None:
        kwargs["reply_markup"] = json.dumps(reply_markup)
    api_call("sendMessage", **kwargs)


def show_shop_button(chat_id):
    """Показывает нижнюю reply-клавиатуру + сообщение с inline-кнопкой."""
    inline = {
        "inline_keyboard": [
            [{"text": "🛍 Открыть магазин", "url": SHOP_URL}]
        ]
    }
    # Нижняя клавиатура
    send_message(chat_id, "КАТАЛОГ ТОВАРОВ", reply_markup=REPLY_KEYBOARD)
    # Inline-кнопка со ссылкой
    send_message(chat_id, "Нажми, чтобы открыть каталог:", reply_markup=inline)


def main():
    print("Бот запущен")
    offset = None
    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset
            resp = api_call("getUpdates", **params)

            for upd in resp.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message") or upd.get("edited_message")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = (msg.get("text") or "").strip()

                # /start или нажатие на нижнюю кнопку «🛍 Магазин»
                if text.startswith("/start") or text == "🛍 Магазин":
                    show_shop_button(chat_id)
        except KeyboardInterrupt:
            print("Остановлено")
            break
        except Exception as e:
            print("Ошибка:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()