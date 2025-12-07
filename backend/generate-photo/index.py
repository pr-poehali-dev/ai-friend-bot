import json
import os
from typing import Dict, Any
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def get_user_settings(telegram_id: int) -> Dict[str, Any]:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM telegram_users WHERE telegram_id = %s", (telegram_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return dict(user) if user else None

def generate_photo_prompt(nsfw_enabled: bool, spicy_level: int, style_variation: int = 1) -> str:
    """
    Генерирует промпт для FLUX с учетом настроек пользователя
    """
    
    base_character = "Beautiful 25-year-old woman named Alina, long dark brown hair, blue eyes, attractive face, natural makeup, realistic photo, high quality, professional photography, "
    
    casual_outfits = [
        "wearing casual jeans and white t-shirt, outdoor park setting, natural daylight, candid pose",
        "in cozy oversized sweater and leggings, home interior, soft window light, relaxed mood",
        "wearing elegant summer dress, city street background, golden hour lighting, walking pose",
        "in sporty outfit, gym or outdoor fitness setting, energetic pose, healthy lifestyle",
        "wearing business casual blazer and pants, office environment, confident professional look"
    ]
    
    medium_outfits = [
        "wearing elegant black cocktail dress, restaurant or bar setting, evening atmosphere, sophisticated look",
        "in tight jeans and crop top, rooftop terrace, sunset lighting, casual confidence",
        "wearing stylish swimsuit on beach, ocean background, summer vibes, vacation mood",
        "in short skirt and fitted top, nightclub interior, party atmosphere, dancing pose",
        "wearing silk robe, luxury bedroom, soft intimate lighting, morning mood"
    ]
    
    spicy_outfits = [
        "wearing beautiful lace lingerie, bedroom setting, sensual lighting, intimate atmosphere, artistic boudoir photography",
        "in elegant bikini, luxury pool background, seductive pose, vacation luxury mood",
        "wearing satin nightwear, bed with silk sheets, soft romantic lighting, intimate mood",
        "in revealing elegant dress, upscale lounge, dim lighting, confident seductive pose",
        "artistic implied nude style, wrapped in silk fabric, studio lighting, artistic photography"
    ]
    
    if not nsfw_enabled or spicy_level < 30:
        outfit_list = casual_outfits
    elif spicy_level < 60:
        outfit_list = medium_outfits
    else:
        outfit_list = spicy_outfits
    
    outfit_index = (style_variation - 1) % len(outfit_list)
    outfit = outfit_list[outfit_index]
    
    quality_tags = "4K resolution, sharp focus, bokeh background, instagram aesthetic, cinematic lighting"
    
    return f"{base_character}{outfit}, {quality_tags}"

def generate_image_flux(prompt: str) -> str:
    """
    Генерирует изображение через внешний API (заглушка для FLUX)
    В реальности здесь должен быть вызов к Replicate или другому сервису
    """
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return "https://via.placeholder.com/1024x1024.png?text=AI+Photo+Generation"
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "hd"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['data'][0]['url']
        else:
            return "https://via.placeholder.com/1024x1024.png?text=Generation+Error"
            
    except Exception as e:
        return "https://via.placeholder.com/1024x1024.png?text=API+Error"

def send_telegram_photo(chat_id: int, photo_url: str, caption: str = ""):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    response = requests.post(url, json={
        'chat_id': chat_id,
        'photo': photo_url,
        'caption': caption,
        'parse_mode': 'HTML'
    })
    
    return response.status_code == 200

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Генерация фото AI девушки для Telegram бота
    Создает изображения с учетом настроек пользователя (SFW/NSFW)
    """
    
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'Photo generation service', 'version': '1.0'}),
            'isBase64Encoded': False
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        
        telegram_id = body.get('telegram_id')
        chat_id = body.get('chat_id')
        style_variation = body.get('style_variation', 1)
        
        if not telegram_id or not chat_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'telegram_id and chat_id are required'}),
                'isBase64Encoded': False
            }
        
        user = get_user_settings(telegram_id)
        
        if not user:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'User not found'}),
                'isBase64Encoded': False
            }
        
        if user['nsfw_enabled'] and not user['is_premium']:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'NSFW content requires premium subscription'}),
                'isBase64Encoded': False
            }
        
        nsfw_enabled = user.get('nsfw_enabled', False)
        spicy_level = user.get('spicy_level', 30)
        
        prompt = generate_photo_prompt(nsfw_enabled, spicy_level, style_variation)
        
        photo_url = generate_image_flux(prompt)
        
        mood_emojis = {
            'friendly': '😊💕',
            'flirty': '😏💋',
            'playful': '😄✨',
            'spicy': '🔥😈'
        }
        
        personality = user.get('personality_mode', 'friendly')
        emoji = mood_emojis.get(personality, '😊')
        
        captions = [
            f"Вот моё фото для тебя {emoji}",
            f"Специально для тебя {emoji}",
            f"Как тебе? {emoji}",
            f"Надеюсь понравится {emoji}",
        ]
        
        import random
        caption = random.choice(captions)
        
        send_telegram_photo(chat_id, photo_url, caption)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'photo_url': photo_url,
                'prompt_used': prompt,
                'nsfw_mode': nsfw_enabled,
                'spicy_level': spicy_level
            }),
            'isBase64Encoded': False
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
