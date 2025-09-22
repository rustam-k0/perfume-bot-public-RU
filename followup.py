# perfume-bot/followup.py
# Follow-up сообщение через 30 секунд, если пользователь не ответил.

import threading

FOLLOWUP_TEXT = "Ура! 🎉 Кажется, получилось. Хочешь, попробуем ещё разок?"

def schedule_followup_once(bot, chat_id, ts, last_user_ts, followup_sent):
    if followup_sent.get(chat_id):
        return
    def _send():
        if last_user_ts.get(chat_id, 0) == ts and not followup_sent.get(chat_id):
            bot.send_message(chat_id, FOLLOWUP_TEXT)
            followup_sent[chat_id] = True
    t = threading.Timer(30.0, _send)
    t.daemon = True
    t.start()
