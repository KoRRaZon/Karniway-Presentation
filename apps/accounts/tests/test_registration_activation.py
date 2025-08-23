import re

from django.core import mail

ACTIVATION_LINK_RE = re.compile(r"https?://[^\s]+/activate/[A-Za-z0-9_\-]+/[A-Za-z0-9\-]+/?")


def pop_last_email():
    """
    Забирает последнее письмо из локальной "почтовой корзины" (locmem backend).
    Удобно, чтобы не лазить в mail.outbox вручную в каждом тесте.
    """
    assert len(mail.outbox) >= 1, "Ожидалось отправленное письмо, но outbox пуст."
    return mail.outbox.pop()

def extract_activation_link(email_message):
    """
    Ищем ссылку активации как в HTML-части, так и в текстовой.
    Возвращаем первую найденную.
    """
    bodies = [email_message.body]
    for alt in getattr(email_message, 'alternatives', []):
        if alt[1] == 'text/html':
            bodies.append(alt[0])

    for body in bodies:
        m = ACTIVATION_LINK_RE.search(body)
        if m:
            return m.group(0)
    raise AssertionError("Ссылка активации не найдена в письме.")




