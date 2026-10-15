import os
import json
import time
import threading
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ.get("TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

CATALOG_URL = "https://t.me/webappzconnectbot/temp_shop?startapp=shopidzxqawimv9o"
ABOUT_TEXT = (
    "Каталог PANDAMART - Привезу любой товар из Китая\n"
    "На этом сайте представлен пример товаров, который можно выкупить "
    "у поставщика и привезти вам\n\n"
    "Если интересует что-то, чего нет в каталоге, Отпишите в тг @mxcbjq\n"
    "Отправляете фото и размер - я нахожу товар и отправляю вам итоговую "
    "цену с учётом доставки"
)

# Нижняя (reply) клавиатура с 4 кнопками
MAIN_KEYBOARD = {
    "keyboard": [
        [{"text": "🗑 Очистить чат"}, {"text": "🛍 Открыть каталог"}],
        [{"text": "ℹ️ О магазине"}, {"text": "✉️ Написать мне"}],
    ],
    "resize_keyboard": True,
    "is_persistent": True,
}

# Inline-кнопки (для ссылок) — они не могут быть в нижней панели
INLINE_OPEN_CATALOG = {
    "inline_keyboard": [
        [{"text": "🛍 Открыть каталог", "url": CATALOG_URL}]
    ]
}
INLINE_WRITE_ME = {
    "inline_keyboard": [
        [{"text": "✉️ Написать мне", "url": "https://t.me/mxcbjq"}]
    ]
}


def api_call(method, **params):
    url = f"{API}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=60) as r:
        return json.loads(r.read().decode())


def send_message(chat_id, text, reply_markup=None):
    kwargs = {"chat_id": chat_id, "text": text}
    if reply_markup is not None:
        kwargs["reply_markup"] = json.dumps(reply_markup)
    api_call("sendMessage", **kwargs)


def show_menu(chat_id):
    """Показать приветствие + нижнюю клавиатуру."""
    send_message(chat_id, "Главное меню 👇", reply_markup=MAIN_KEYBOARD)


def send_about(chat_id):
    send_message(chat_id, ABOUT_TEXT, reply_markup=MAIN_KEYBOARD)


def send_open_catalog(chat_id):
    """Кнопка-ссылка на каталог в виде inline."""
    send_message(
        chat_id,
        "Нажми, чтобы открыть каталог:",
        reply_markup=INLINE_OPEN_CATALOG,
    )


def send_write_me(chat_id):
    """Кнопка-ссылка на личный чат."""
    send_message(
        chat_id,
        "Нажми, чтобы написать мне:",
        reply_markup=INLINE_WRITE_ME,
    )


def clear_chat(chat_id, last_message_id):
    """Удаляем сообщения бота с last_message_id назад (по одному)."""
    for msg_id in range(last_message_id, max(last_message_id - 100, 0), -1):
        try:
            api_call("deleteMessage", chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass


class Ping(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, *args, **kwargs):
        pass


def run_pinger():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), Ping).serve_forever()


def main():
    threading.Thread(target=run_pinger, daemon=True).start()
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
                msg_id = msg["message_id"]
                text = (msg.get("text") or "").strip()

                if text.startswith("/start") or text == "Меню":
                    show_menu(chat_id)
                elif text == "🗑 Очистить чат":
                    clear_chat(chat_id, msg_id)
                elif text == "🛍 Открыть каталог":
                    send_open_catalog(chat_id)
                elif text == "ℹ️ О магазине":
                    send_about(chat_id)
                elif text == "✉️ Написать мне":
                    send_write_me(chat_id)
        except KeyboardInterrupt:
            print("Остановлено")
            break
        except Exception as e:
            print("Ошибка:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
