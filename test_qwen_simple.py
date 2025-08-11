#!/usr/bin/env python3
"""
Упрощенный тест модели qwen/qwen3-235b-a22b-thinking-2507
для создания презентации о VPN-сервере
"""

import asyncio
import json
import logging
import sys
import time
import requests
from datetime import datetime
from pathlib import Path

# Настройка логирования
log_filename = f"/home/ubuntu/openmanus_project/logs/qwen_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
Path("/home/ubuntu/openmanus_project/logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Конфигурация API
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/"
MODEL = "qwen/qwen3-235b-a22b-thinking-2507"

async def call_qwen_api(prompt: str, max_tokens: int = 4000) -> str:
    """Вызов API модели Qwen"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(f"{BASE_URL}chat/completions", headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        return f"Ошибка генерации: {e}"

async def generate_vpn_presentation():
    """Генерирует презентацию о VPN-сервере с помощью Qwen"""
    
    logger.info("🚀 Начало генерации презентации с моделью Qwen")
    start_time = time.time()
    
    # Шаг 1: Генерация структуры
    logger.info("🏗️ Генерация структуры презентации...")
    
    structure_prompt = """Создай структуру презентации на тему "Запуск собственного VPN-сервера, устойчивого к блокировкам РКН".

Требования:
- 8 слайдов
- Каждый слайд должен иметь заголовок и краткое описание
- Презентация должна быть практической и технической
- Включи информацию о протоколах, настройке, безопасности
- Ответ в формате JSON

Пример формата:
{
  "title": "Название презентации",
  "description": "Описание",
  "slides": [
    {
      "title": "Заголовок слайда",
      "description": "Краткое описание содержания",
      "keywords": ["ключевое", "слово"]
    }
  ]
}"""

    structure_response = await call_qwen_api(structure_prompt, 3000)
    logger.info("✅ Структура получена")
    
    # Попытка парсинга JSON
    try:
        # Извлекаем JSON из ответа
        start_idx = structure_response.find('{')
        end_idx = structure_response.rfind('}') + 1
        json_str = structure_response[start_idx:end_idx]
        structure = json.loads(json_str)
    except:
        logger.warning("⚠️ Не удалось распарсить JSON, создаем базовую структуру")
        structure = {
            "title": "Запуск собственного VPN-сервера",
            "description": "Устойчивого к блокировкам РКН",
            "slides": [
                {"title": "Введение в VPN", "description": "Основы и необходимость"},
                {"title": "Выбор протокола", "description": "Xray, VLESS-Reality"},
                {"title": "Выбор VPS", "description": "Провайдеры и характеристики"},
                {"title": "Установка сервера", "description": "Пошаговая настройка"},
                {"title": "Настройка клиентов", "description": "Подключение устройств"},
                {"title": "Безопасность", "description": "Защита и маскировка"},
                {"title": "Мониторинг", "description": "Отслеживание работы"},
                {"title": "Заключение", "description": "Итоги и рекомендации"}
            ]
        }
    
    logger.info(f"📊 Структура: {len(structure['slides'])} слайдов")
    
    # Шаг 2: Генерация контента для каждого слайда
    logger.info("📝 Генерация контента слайдов...")
    
    presentation = {
        "title": structure["title"],
        "description": structure.get("description", ""),
        "slides": [],
        "metadata": {
            "created_by": "OpenManus SlidesMode v2.0 + Qwen",
            "model": MODEL,
            "created_at": datetime.now().isoformat(),
            "topic": "VPN-сервер устойчивый к блокировкам РКН"
        }
    }
    
    for i, slide_info in enumerate(structure["slides"], 1):
        logger.info(f"   🔄 Слайд {i}: {slide_info['title']}")
        
        content_prompt = f"""Создай подробный контент для слайда презентации о VPN-сервере.

Заголовок слайда: {slide_info['title']}
Описание: {slide_info['description']}
Общая тема презентации: Запуск собственного VPN-сервера, устойчивого к блокировкам РКН

Требования:
- Создай практический и технический контент
- Включи конкретные примеры, команды, настройки где применимо
- Используй разные типы контента: параграфы, списки, цитаты, код
- Добавь заметки для докладчика
- Ответ в формате JSON

Формат ответа:
{{
  "title": "Заголовок слайда",
  "content": [
    {{"type": "paragraph", "text": "Текст параграфа"}},
    {{"type": "bullet_point", "text": "Пункт списка"}},
    {{"type": "code", "language": "bash", "text": "команда"}},
    {{"type": "quote", "text": "Цитата", "author": "Автор"}}
  ],
  "notes": "Заметки для докладчика"
}}"""

        content_response = await call_qwen_api(content_prompt, 2000)
        
        # Парсинг контента
        try:
            start_idx = content_response.find('{')
            end_idx = content_response.rfind('}') + 1
            json_str = content_response[start_idx:end_idx]
            slide_content = json.loads(json_str)
        except:
            logger.warning(f"   ⚠️ Ошибка парсинга контента слайда {i}")
            slide_content = {
                "title": slide_info['title'],
                "content": [
                    {"type": "paragraph", "text": slide_info['description']},
                    {"type": "paragraph", "text": content_response[:500] + "..."}
                ],
                "notes": "Контент сгенерирован с ошибкой парсинга"
            }
        
        # Добавляем изображение (заглушка)
        slide_content["image_url"] = f"https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=600&fit=crop"
        
        presentation["slides"].append(slide_content)
        logger.info(f"   ✅ Контент слайда {i} создан")
    
    # Шаг 3: Сохранение результатов
    logger.info("💾 Сохранение презентации...")
    
    # JSON
    json_path = "/home/ubuntu/openmanus_project/qwen_vpn_presentation.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(presentation, f, indent=2, ensure_ascii=False)
    
    # HTML
    html_content = generate_html(presentation)
    html_path = "/home/ubuntu/openmanus_project/qwen_vpn_presentation.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info("🎉 Презентация создана успешно!")
    logger.info(f"⏱️ Время выполнения: {total_time:.2f} секунд")
    logger.info(f"📁 Файлы:")
    logger.info(f"   📄 JSON: {json_path}")
    logger.info(f"   🌐 HTML: {html_path}")
    logger.info(f"   📊 Лог: {log_filename}")
    
    return {
        "success": True,
        "presentation": presentation,
        "execution_time": total_time,
        "log_file": log_filename,
        "files": {
            "json": json_path,
            "html": html_path
        }
    }

def generate_html(presentation):
    """Генерирует HTML из презентации"""
    
    title = presentation.get('title', 'Презентация')
    description = presentation.get('description', '')
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .title-page {{ text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 60px 40px; border-radius: 15px; margin-bottom: 30px; }}
        .title-page h1 {{ font-size: 2.5em; margin-bottom: 20px; }}
        .slide {{ background: white; margin: 20px 0; padding: 30px; border-radius: 10px; 
                  box-shadow: 0 4px 15px rgba(0,0,0,0.1); page-break-after: always; }}
        .slide h2 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .slide img {{ max-width: 100%; height: auto; margin: 20px 0; border-radius: 8px; }}
        .notes {{ background: #f8f9fa; padding: 15px; margin-top: 20px; border-left: 4px solid #3498db; 
                  font-style: italic; border-radius: 5px; }}
        ul {{ margin: 15px 0; }}
        li {{ margin: 8px 0; }}
        pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #e74c3c; margin: 20px 0; padding: 15px 20px; 
                      background: #fdf2f2; font-style: italic; }}
        .quote-author {{ text-align: right; font-weight: bold; color: #e74c3c; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1>{title}</h1>
        {f'<p>{description}</p>' if description else ''}
        <p style="margin-top: 30px; opacity: 0.8;">Создано с помощью OpenManus SlidesMode v2.0 + Qwen</p>
    </div>
"""
    
    for i, slide in enumerate(presentation.get('slides', []), 1):
        html += f'    <div class="slide">\n'
        html += f'        <h2>Слайд {i}: {slide.get("title", "Без названия")}</h2>\n'
        
        if slide.get('image_url'):
            html += f'        <img src="{slide.get("image_url")}" alt="Slide Image">\n'
        
        for item in slide.get('content', []):
            item_type = item.get('type', 'paragraph')
            text = item.get('text', '')
            
            if item_type == 'bullet_point':
                html += f'        <ul><li>{text}</li></ul>\n'
            elif item_type == 'paragraph':
                html += f'        <p>{text}</p>\n'
            elif item_type == 'code':
                language = item.get('language', '')
                html += f'        <pre><code class="{language}">{text}</code></pre>\n'
            elif item_type == 'quote':
                author = item.get('author', '')
                html += f'        <blockquote>{text}'
                if author:
                    html += f'<div class="quote-author">— {author}</div>'
                html += '</blockquote>\n'
        
        if slide.get('notes'):
            html += f'        <div class="notes"><strong>Заметки:</strong> {slide.get("notes")}</div>\n'
        
        html += '    </div>\n'
    
    html += '</body>\n</html>'
    return html

async def main():
    """Главная функция"""
    print("🧪 Запуск упрощенного эксперимента с Qwen...")
    result = await generate_vpn_presentation()
    
    if result and result.get("success"):
        print("\n✅ Эксперимент завершен успешно!")
        print(f"📊 Время: {result['execution_time']:.2f} сек")
        print(f"📁 Лог: {result['log_file']}")
    else:
        print("\n❌ Эксперимент завершился с ошибкой!")

if __name__ == "__main__":
    asyncio.run(main())

