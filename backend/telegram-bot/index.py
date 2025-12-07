import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, Optional
import requests
from datetime import datetime

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def get_or_create_user(telegram_id: int, username: str, first_name: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        "SELECT * FROM telegram_users WHERE telegram_id = %s",
        (telegram_id,)
    )
    user = cur.fetchone()
    
    if not user:
        cur.execute(
            """INSERT INTO telegram_users (telegram_id, username, first_name) 
               VALUES (%s, %s, %s) RETURNING *""",
            (telegram_id, username, first_name)
        )
        user = cur.fetchone()
        conn.commit()
    else:
        cur.execute(
            "UPDATE telegram_users SET last_active = CURRENT_TIMESTAMP WHERE telegram_id = %s",
            (telegram_id,)
        )
        conn.commit()
    
    cur.close()
    conn.close()
    return dict(user)

def save_message(telegram_id: int, role: str, content: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history (telegram_id, role, content) VALUES (%s, %s, %s)",
        (telegram_id, role, content)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_chat_history(telegram_id: int, limit: int = 10) -> list:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """SELECT role, content FROM chat_history 
           WHERE telegram_id = %s 
           ORDER BY created_at DESC LIMIT %s""",
        (telegram_id, limit)
    )
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(msg) for msg in reversed(messages)]

def update_user_settings(telegram_id: int, **kwargs):
    conn = get_db_connection()
    cur = conn.cursor()
    
    set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
    values = list(kwargs.values()) + [telegram_id]
    
    cur.execute(
        f"UPDATE telegram_users SET {set_clause} WHERE telegram_id = %s",
        values
    )
    conn.commit()
    cur.close()
    conn.close()

def generate_ai_response(user_message: str, personality_mode: str, chat_history: list) -> str:
    personalities = {
        'friendly': {
            'name': 'Алина',
            'style': 'дружелюбная, милая, поддерживающая девушка',
            'emoji': '😊💕',
        },
        'flirty': {
            'name': 'Алина',
            'style': 'кокетливая, игривая, флиртующая девушка',
            'emoji': '😏💋',
        },
        'playful': {
            'name': 'Алина',
            'style': 'веселая, озорная, жизнерадостная девушка',
            'emoji': '😄✨',
        },
        'spicy': {
            'name': 'Алина',
            'style': 'страстная, откровенная, пошлая девушка',
            'emoji': '🔥😈',
        }
    }
    
    personality = personalities.get(personality_mode, personalities['friendly'])
    
    responses_db = {
        'friendly': [
            f"Привет, милый! {personality['emoji']} Как твои дела сегодня?",
            f"Ой, интересно! Расскажи мне больше? {personality['emoji']}",
            f"Я так рада за тебя! {personality['emoji']} Ты молодец!",
            f"Понимаю тебя... {personality['emoji']} Я здесь, если хочешь поговорить",
            f"Звучит здорово! {personality['emoji']} А что дальше?",
        ],
        'flirty': [
            f"Ммм, интригующе... {personality['emoji']} Продолжай, мне нравится",
            f"Ты такой интересный... {personality['emoji']} Расскажи ещё",
            f"О, знаешь как растопить моё сердечко {personality['emoji']}",
            f"Хи-хи, ты меня смущаешь... {personality['emoji']} Но мне нравится",
            f"Какой ты... особенный {personality['emoji']} Люблю с тобой общаться",
        ],
        'playful': [
            f"Ха-ха-ха! {personality['emoji']} Ты такой забавный!",
            f"Ого! Вот это поворот! {personality['emoji']} А давай ещё!",
            f"Хи-хи, весело с тобой! {personality['emoji']} Что ещё придумаешь?",
            f"Ты просто супер! {personality['emoji']} Обожаю такое!",
            f"Вау! {personality['emoji']} Не ожидала от тебя такого!",
        ],
        'spicy': [
            f"Ммм, становится жарко здесь... {personality['emoji']} Продолжай",
            f"О боже... {personality['emoji']} Ты знаешь, как меня завести",
            f"Такой озорной сегодня... {personality['emoji']} Мне это нравится",
            f"Хочешь поиграть со мной? {personality['emoji']} Я не против...",
            f"Ты меня возбуждаешь своими словами... {personality['emoji']}",
        ]
    }
    
    import random
    responses = responses_db.get(personality_mode, responses_db['friendly'])
    return random.choice(responses)

def generate_photo_prompt(nsfw_enabled: bool, spicy_level: int) -> str:
    base_prompt = "Beautiful young woman, professional photo, high quality, realistic, "
    
    appearance = "long dark hair, blue eyes, attractive face, natural makeup, "
    
    if not nsfw_enabled or spicy_level < 30:
        outfits = [
            "casual street style outfit, jeans and sweater",
            "elegant dress, outdoor setting",
            "sporty outfit, gym clothes, fitness style",
            "cozy home clothes, comfortable style",
            "business casual, professional look"
        ]
    elif spicy_level < 60:
        outfits = [
            "tight dress, elegant evening style",
            "crop top and shorts, summer vibes",
            "swimsuit on beach, vacation mood",
            "lingerie style, boudoir photography",
            "short skirt and top, party style"
        ]
    else:
        outfits = [
            "seductive lingerie, bedroom setting",
            "bikini, sensual pose, beach vibes",
            "revealing outfit, intimate atmosphere",
            "provocative dress, nightclub style",
            "sensual pose, artistic nude style"
        ]
    
    import random
    outfit = random.choice(outfits)
    
    style = "soft lighting, portrait photography, instagram style, 4k quality"
    
    return f"{base_prompt}{appearance}{outfit}, {style}"

def send_telegram_message(chat_id: int, text: str):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    })

def send_telegram_photo(chat_id: int, photo_url: str, caption: str = ""):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    requests.post(url, json={
        'chat_id': chat_id,
        'photo': photo_url,
        'caption': caption
    })

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Telegram бот AI подруги с генерацией фото
    Обрабатывает webhook от Telegram и отвечает пользователям
    """
    
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'Bot is running', 'bot': 'AI Girlfriend'}),
            'isBase64Encoded': False
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        
        if 'message' not in body:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'ok': True}),
                'isBase64Encoded': False
            }
        
        message = body['message']
        chat_id = message['chat']['id']
        telegram_id = message['from']['id']
        username = message['from'].get('username', '')
        first_name = message['from'].get('first_name', 'User')
        text = message.get('text', '')
        
        user = get_or_create_user(telegram_id, username, first_name)
        
        if text.startswith('/start'):
            welcome_text = f"""Привет, {first_name}! 😊💕
            
Я Алина, твоя AI подруга. Со мной ты можешь:
💬 Общаться на любые темы
📸 Получать мои фото (команда /photo)
⚙️ Настроить мой характер (команда /settings)
👤 Посмотреть профиль (команда /profile)

Просто напиши мне что-нибудь, и я отвечу! 💕"""
            
            send_telegram_message(chat_id, welcome_text)
            
        elif text.startswith('/photo'):
            if not user['is_premium'] and user['nsfw_enabled']:
                send_telegram_message(chat_id, "🔒 Откровенные фото доступны только в Premium подписке!\n\nИспользуй /premium чтобы узнать больше")
            else:
                send_telegram_message(chat_id, "📸 Генерирую фото для тебя, подожди немного...")
                
                try:
                    photo_service_url = "https://functions.poehali.dev/generate-photo"
                    response = requests.post(photo_service_url, json={
                        'telegram_id': telegram_id,
                        'chat_id': chat_id,
                        'style_variation': 1
                    }, timeout=120)
                    
                    if response.status_code != 200:
                        send_telegram_message(chat_id, "😔 Извини, не смогла сгенерировать фото. Попробуй позже!")
                except Exception:
                    send_telegram_message(chat_id, "😔 Извини, произошла ошибка. Попробуй позже!")
                
        elif text.startswith('/settings'):
            settings_text = f"""⚙️ <b>Настройки</b>

<b>Режим личности:</b> {user['personality_mode']}
{'🔓' if user['is_premium'] else '🔒'} Доступные режимы:
• friendly - Дружелюбная 😊
• flirty - Кокетливая 😏 {'✅' if user['is_premium'] else '(Premium)'}
• playful - Игривая 😄 {'✅' if user['is_premium'] else '(Premium)'}
• spicy - Пошлая 🔥 {'✅' if user['is_premium'] else '(Premium)'}

<b>18+ контент:</b> {'Включен ✅' if user['nsfw_enabled'] else 'Выключен ❌'}
<b>Уровень откровенности:</b> {user['spicy_level']}%

Чтобы изменить режим, используй:
/mode friendly
/mode flirty
/mode playful
/mode spicy

Чтобы включить 18+: /nsfw on
Чтобы выключить 18+: /nsfw off"""
            
            send_telegram_message(chat_id, settings_text)
            
        elif text.startswith('/profile'):
            profile_text = f"""👤 <b>Твой профиль</b>

<b>Имя:</b> {first_name}
<b>Username:</b> @{username if username else 'не указан'}
<b>Статус:</b> {'👑 Premium' if user['is_premium'] else 'Free'}
<b>С нами с:</b> {user['created_at'].strftime('%d.%m.%Y')}

<b>Статистика:</b>
• Сообщений отправлено: ❓
• Режим общения: {user['personality_mode']}
• 18+ режим: {'Вкл' if user['nsfw_enabled'] else 'Выкл'}

{'Спасибо за поддержку! 💕' if user['is_premium'] else 'Хочешь больше возможностей? /premium'}"""
            
            send_telegram_message(chat_id, profile_text)
            
        elif text.startswith('/premium'):
            premium_text = """👑 <b>Premium подписка</b>

<b>Что входит:</b>
✅ Безлимитные сообщения
✅ Все режимы личности (флирт, игривая, пошлая)
✅ 18+ фото генерация
✅ Настройка уровня откровенности
✅ Голосовые сообщения (скоро)
✅ Приоритетная поддержка

<b>Цена:</b> 599 ₽/месяц

Для подключения напиши @your_support"""
            
            send_telegram_message(chat_id, premium_text)
            
        elif text.startswith('/mode '):
            mode = text.split(' ')[1].lower()
            
            if mode not in ['friendly', 'flirty', 'playful', 'spicy']:
                send_telegram_message(chat_id, "❌ Неизвестный режим. Используй: friendly, flirty, playful или spicy")
            elif not user['is_premium'] and mode != 'friendly':
                send_telegram_message(chat_id, f"🔒 Режим '{mode}' доступен только в Premium!\n\nИспользуй /premium чтобы узнать больше")
            else:
                update_user_settings(telegram_id, personality_mode=mode)
                mode_names = {
                    'friendly': 'Дружелюбная 😊',
                    'flirty': 'Кокетливая 😏',
                    'playful': 'Игривая 😄',
                    'spicy': 'Пошлая 🔥'
                }
                send_telegram_message(chat_id, f"✅ Режим изменен на: {mode_names[mode]}")
                
        elif text.startswith('/nsfw '):
            action = text.split(' ')[1].lower()
            
            if not user['is_premium']:
                send_telegram_message(chat_id, "🔒 18+ режим доступен только в Premium подписке!\n\nИспользуй /premium чтобы узнать больше")
            else:
                nsfw_enabled = action == 'on'
                update_user_settings(telegram_id, nsfw_enabled=nsfw_enabled)
                send_telegram_message(chat_id, f"✅ 18+ режим {'включен 🔥' if nsfw_enabled else 'выключен'}")
        
        else:
            save_message(telegram_id, 'user', text)
            
            chat_history = get_chat_history(telegram_id)
            ai_response = generate_ai_response(text, user['personality_mode'], chat_history)
            
            save_message(telegram_id, 'assistant', ai_response)
            send_telegram_message(chat_id, ai_response)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': True}),
            'isBase64Encoded': False
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }