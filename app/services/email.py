from __future__ import annotations
import secrets
import redis.asyncio as aioredis
from emails import Message
from app.core.config import settings

VERIFY_CODE_TTL = 24 * 60 * 60
RESET_CODE_TTL = 60 * 60

# Тексты писем
EMAIL_TEXTS = {
    "verify": {
        "ru": {
            "subject": "Подтвердите email",
            "title": "Добро пожаловать в {app_name}!",
            "greeting": "Привет, {username}!",
            "body": "Пожалуйста, подтвердите ваш email нажав на кнопку ниже:",
            "button": "Подтвердить email",
            "expire": "Ссылка действительна 24 часа.",
            "ignore": "Если вы не создавали аккаунт — просто проигнорируйте это письмо.",
        },
        "uk": {
            "subject": "Підтвердіть email",
            "title": "Ласкаво просимо до {app_name}!",
            "greeting": "Привіт, {username}!",
            "body": "Будь ласка, підтвердіть вашу електронну адресу, натиснувши кнопку нижче:",
            "button": "Підтвердити email",
            "expire": "Посилання дійсне 24 години.",
            "ignore": "Якщо ви не створювали акаунт — просто проігноруйте цей лист.",
        },
        "en": {
            "subject": "Verify your email",
            "title": "Welcome to {app_name}!",
            "greeting": "Hi, {username}!",
            "body": "Please verify your email address by clicking the button below:",
            "button": "Verify Email",
            "expire": "This link expires in 24 hours.",
            "ignore": "If you did not create an account, please ignore this email.",
        },
    },
    "reset": {
        "ru": {
            "subject": "Сброс пароля",
            "title": "Сброс пароля — {app_name}",
            "greeting": "Привет, {username}!",
            "body": "Вы запросили сброс пароля. Нажмите на кнопку ниже:",
            "button": "Сбросить пароль",
            "expire": "Ссылка действительна 1 час.",
            "ignore": "Если вы не запрашивали сброс пароля — просто проигнорируйте это письмо.",
        },
        "uk": {
            "subject": "Скидання пароля",
            "title": "Скидання пароля — {app_name}",
            "greeting": "Привіт, {username}!",
            "body": "Ви запросили скидання пароля. Натисніть кнопку нижче:",
            "button": "Скинути пароль",
            "expire": "Посилання дійсне 1 годину.",
            "ignore": "Якщо ви не запитували скидання пароля — просто проігноруйте цей лист.",
        },
        "en": {
            "subject": "Password Reset",
            "title": "Password Reset — {app_name}",
            "greeting": "Hi, {username}!",
            "body": "You requested a password reset. Click the button below:",
            "button": "Reset Password",
            "expire": "This link expires in 1 hour.",
            "ignore": "If you did not request a password reset, please ignore this email.",
        },
    },
}


async def get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


def generate_code() -> str:
    return secrets.token_urlsafe(32)


async def save_verification_code(email: str, code: str) -> None:
    redis = await get_redis()
    await redis.setex(f"verify:{code}", VERIFY_CODE_TTL, email)
    await redis.aclose()


async def get_email_by_verification_code(code: str) -> str | None:
    redis = await get_redis()
    email = await redis.get(f"verify:{code}")
    await redis.aclose()
    return email


async def delete_verification_code(code: str) -> None:
    redis = await get_redis()
    await redis.delete(f"verify:{code}")
    await redis.aclose()


async def save_reset_code(email: str, code: str) -> None:
    redis = await get_redis()
    await redis.setex(f"reset:{code}", RESET_CODE_TTL, email)
    await redis.aclose()


async def get_email_by_reset_code(code: str) -> str | None:
    redis = await get_redis()
    email = await redis.get(f"reset:{code}")
    await redis.aclose()
    return email


async def delete_reset_code(code: str) -> None:
    redis = await get_redis()
    await redis.delete(f"reset:{code}")
    await redis.aclose()


def build_email_html(texts: dict, action_url: str, button_color: str) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>{texts['title']}</h2>
        <p>{texts['greeting']}</p>
        <p>{texts['body']}</p>
        <a href="{action_url}"
           style="background-color: {button_color}; color: white; padding: 14px 20px;
                  text-decoration: none; border-radius: 4px; display: inline-block;">
            {texts['button']}
        </a>
        <p style="color: #888; font-size: 13px;">{texts['expire']}</p>
        <p style="color: #888; font-size: 13px;">{texts['ignore']}</p>
    </div>
    """


def send_email(to: str, subject: str, html: str) -> None:
    message = Message(
        subject=subject,
        html=html,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    message.send(
        to=to,
        smtp={
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "user": settings.SMTP_USER,
            "password": settings.SMTP_PASSWORD,
            "tls": True,
        }
    )


async def send_verification_email(email: str, username: str, lang: str = "uk") -> None:
    if lang not in ("ru", "uk", "en"):
        lang = "uk"

    code = generate_code()
    await save_verification_code(email, code)

    texts = {
        k: v.format(app_name=settings.APP_NAME, username=username)
        for k, v in EMAIL_TEXTS["verify"][lang].items()
    }

    verify_url = f"http://localhost:3000/verify-email?code={code}"
    html = build_email_html(texts, verify_url, "#4CAF50")
    send_email(to=email, subject=texts["subject"], html=html)


async def send_reset_password_email(email: str, username: str, lang: str = "uk") -> None:
    if lang not in ("ru", "uk", "en"):
        lang = "uk"

    code = generate_code()
    await save_reset_code(email, code)

    texts = {
        k: v.format(app_name=settings.APP_NAME, username=username)
        for k, v in EMAIL_TEXTS["reset"][lang].items()
    }

    reset_url = f"http://localhost:3000/reset-password?code={code}"
    html = build_email_html(texts, reset_url, "#2196F3")
    send_email(to=email, subject=texts["subject"], html=html)