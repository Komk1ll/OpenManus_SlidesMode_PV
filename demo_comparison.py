#!/usr/bin/env python3
"""
Демонстрация возможностей нашего софта для создания PDF презентаций
"""

import json
import os
from typing import Dict, Any

def create_demo_presentation() -> Dict[str, Any]:
    """Создает демонстрационную презентацию для сравнения"""
    
    presentation = {
        "title": "История Google",
        "description": "Путь от стартапа до технологического гиганта",
        "slides": [
            {
                "title": "История Google",
                "subtitle": "От исследовательского проекта до мирового феномена",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Компания Google была основана в 1998 году двумя студентами Стэнфордского университета и превратилась в одну из самых влиятельных технологических компаний мира."
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?w=800&h=600&fit=crop",
                "notes": "Титульный слайд с основной информацией о презентации"
            },
            {
                "title": "Истоки",
                "subtitle": "1996-1998: Рождение идеи",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "В 1996 году Ларри Пейдж и Сергей Брин начали работу над поисковой системой BackRub в Стэнфордском университете."
                    },
                    {
                        "type": "bullet_point",
                        "text": "1996: Начало проекта BackRub"
                    },
                    {
                        "type": "bullet_point",
                        "text": "1997: Регистрация домена google.com"
                    },
                    {
                        "type": "bullet_point",
                        "text": "1998: Официальное основание компании"
                    },
                    {
                        "type": "quote",
                        "text": "Наша миссия - организовать мировую информацию и сделать её универсально доступной и полезной",
                        "author": "Миссия Google"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop",
                "notes": "Рассказ о начале компании и её основателях"
            },
            {
                "title": "Рост и развитие",
                "subtitle": "1999-2010: Становление гиганта",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "В период с 1999 по 2010 год Google превратился из небольшого стартапа в технологического гиганта."
                    },
                    {
                        "type": "bullet_point",
                        "text": "2000: Запуск AdWords - рекламной платформы"
                    },
                    {
                        "type": "bullet_point",
                        "text": "2004: IPO и выход на биржу"
                    },
                    {
                        "type": "bullet_point",
                        "text": "2006: Приобретение YouTube за $1.65 млрд"
                    },
                    {
                        "type": "bullet_point",
                        "text": "2008: Запуск браузера Chrome"
                    },
                    {
                        "type": "code",
                        "language": "javascript",
                        "text": "// Пример поискового запроса\nfunction googleSearch(query) {\n    return fetch(`https://google.com/search?q=${query}`);\n}"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=800&h=600&fit=crop",
                "notes": "Ключевые моменты роста компании"
            },
            {
                "title": "Современная эпоха",
                "subtitle": "2011-настоящее время: Alphabet и инновации",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "С 2011 года Google продолжает инновации в области искусственного интеллекта, облачных технологий и мобильных платформ."
                    },
                    {
                        "type": "bullet_point",
                        "text": "2011: Запуск Google+"
                    },
                    {
                        "type": "bullet_point",
                        "text": "2015: Реорганизация в Alphabet Inc."
                    },
                    {
                        "type": "bullet_point",
                        "text": "2016: Запуск Google Assistant"
                    },
                    {
                        "type": "bullet_point",
                        "text": "2023: Интеграция AI в поисковую систему"
                    },
                    {
                        "type": "quote",
                        "text": "Искусственный интеллект - это одна из самых важных вещей, над которыми работает человечество",
                        "author": "Сундар Пичаи, CEO Google"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop",
                "notes": "Современные достижения и направления развития"
            },
            {
                "title": "Заключение",
                "subtitle": "Влияние на мир",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Google изменил способ поиска, обработки и использования информации, став неотъемлемой частью цифровой жизни миллиардов людей."
                    },
                    {
                        "type": "bullet_point",
                        "text": "Более 8.5 миллиардов поисковых запросов в день"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Присутствие в более чем 190 странах"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Инвестиции в будущие технологии: AI, квантовые вычисления"
                    },
                    {
                        "type": "quote",
                        "text": "Google не просто компания - это новый способ мышления об информации",
                        "author": "Технологический аналитик"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=600&fit=crop",
                "notes": "Подведение итогов и влияние на современный мир"
            }
        ],
        "metadata": {
            "created_by": "OpenManus SlidesMode v2.0",
            "topic": "История Google",
            "slide_count": 5,
            "language": "russian",
            "includes_images": True
        }
    }
    
    return presentation

def generate_enhanced_html_for_pdf(presentation: Dict[str, Any]) -> str:
    """Генерирует улучшенный HTML для PDF экспорта"""
    title = presentation.get('title', 'Презентация')
    description = presentation.get('description', '')
    
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            margin: 2cm;
            size: A4 landscape;
            @bottom-center {{
                content: counter(page);
                font-family: 'Arial', sans-serif;
                font-size: 12px;
                color: #666;
            }}
        }}
        
        body {{ 
            font-family: 'Arial', 'Helvetica', sans-serif; 
            margin: 0; 
            padding: 0;
            line-height: 1.6; 
            color: #333;
            background: #f8f9fa;
        }}
        
        .title-page {{
            text-align: center;
            margin-bottom: 50px;
            page-break-after: always;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .title-page h1 {{
            font-size: 3.5em;
            font-weight: 700;
            margin-bottom: 30px;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        .title-page p {{
            font-size: 1.5em;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .slide {{ 
            margin-bottom: 40px; 
            page-break-after: always;
            min-height: 500px;
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .slide h2 {{ 
            color: #2c3e50; 
            border-bottom: 4px solid #3498db; 
            padding-bottom: 15px;
            font-size: 2.2em;
            margin-bottom: 25px;
            font-weight: 700;
        }}
        
        .slide h3 {{ 
            color: #34495e;
            font-size: 1.5em;
            margin-bottom: 20px;
            font-weight: 600;
            opacity: 0.8;
        }}
        
        .slide img {{ 
            max-width: 100%; 
            height: auto; 
            margin: 25px 0;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border: 3px solid #ecf0f1;
        }}
        
        .notes {{ 
            font-style: italic; 
            color: #7f8c8d; 
            margin-top: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left: 5px solid #3498db;
            border-radius: 8px;
            font-size: 0.95em;
        }}
        
        ul {{ 
            margin: 20px 0;
            padding-left: 0;
        }}
        
        li {{ 
            margin: 12px 0;
            line-height: 1.7;
            list-style: none;
            position: relative;
            padding-left: 30px;
        }}
        
        li:before {{
            content: "▶";
            color: #3498db;
            font-weight: bold;
            position: absolute;
            left: 0;
            top: 0;
        }}
        
        pre {{ 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
            color: #ecf0f1;
            padding: 25px; 
            border-radius: 12px; 
            overflow-x: auto;
            font-family: 'Courier New', 'Monaco', monospace;
            margin: 20px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            border: 1px solid #34495e;
        }}
        
        blockquote {{
            border-left: 5px solid #e74c3c;
            margin: 25px 0;
            padding: 20px 30px;
            background: linear-gradient(135deg, #fdf2f2 0%, #fce4ec 100%);
            font-style: italic;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.1);
        }}
        
        .quote-author {{
            text-align: right;
            font-weight: bold;
            color: #e74c3c;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        
        .content-item {{
            margin-bottom: 20px;
        }}
        
        .slide-number {{
            position: absolute;
            top: 20px;
            right: 30px;
            background: #3498db;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            align-items: start;
        }}
        
        .text-content {{
            padding-right: 20px;
        }}
        
        .image-content {{
            text-align: center;
        }}
        
        .highlight {{
            background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1>{title}</h1>
        {f'<p>{description}</p>' if description else ''}
        <div style="margin-top: 50px; font-size: 1.2em; opacity: 0.8;">
            Создано с помощью OpenManus SlidesMode v2.0
        </div>
    </div>
"""
    
    slides = presentation.get('slides', [])
    for i, slide in enumerate(slides, 1):
        html_content += f'    <div class="slide">\n'
        html_content += f'        <div class="slide-number">Слайд {i}</div>\n'
        html_content += f'        <h2>{slide.get("title", "Untitled")}</h2>\n'
        
        if slide.get('subtitle'):
            html_content += f'        <h3>{slide.get("subtitle")}</h3>\n'
        
        # Создаем сетку для контента и изображения
        has_image = slide.get('image_url')
        if has_image:
            html_content += '        <div class="content-grid">\n'
            html_content += '            <div class="text-content">\n'
        
        content_items = slide.get('content', [])
        for item in content_items:
            item_type = item.get('type', 'paragraph')
            text = item.get('text', '')
            
            html_content += '                <div class="content-item">\n'
            
            if item_type == 'bullet_point':
                html_content += f'                    <ul><li>{text}</li></ul>\n'
            elif item_type == 'paragraph':
                html_content += f'                    <p>{text}</p>\n'
            elif item_type == 'code':
                language = item.get('language', '')
                html_content += f'                    <pre><code class="{language}">{text}</code></pre>\n'
            elif item_type == 'quote':
                author = item.get('author', '')
                html_content += f'                    <blockquote>{text}'
                if author:
                    html_content += f'<div class="quote-author">— {author}</div>'
                html_content += '</blockquote>\n'
            
            html_content += '                </div>\n'
        
        if has_image:
            html_content += '            </div>\n'
            html_content += '            <div class="image-content">\n'
            html_content += f'                <img src="{slide.get("image_url")}" alt="Slide Image">\n'
            html_content += '            </div>\n'
            html_content += '        </div>\n'
        
        if slide.get('notes'):
            html_content += f'        <div class="notes"><strong>Заметки докладчика:</strong> {slide.get("notes")}</div>\n'
        
        html_content += '    </div>\n'
    
    html_content += '</body>\n</html>'
    
    return html_content

def save_demo_files():
    """Сохраняет демонстрационные файлы"""
    presentation = create_demo_presentation()
    
    # Сохраняем JSON
    with open('/home/ubuntu/openmanus_project/demo_google_history.json', 'w', encoding='utf-8') as f:
        json.dump(presentation, f, indent=2, ensure_ascii=False)
    
    # Сохраняем HTML
    html_content = generate_enhanced_html_for_pdf(presentation)
    with open('/home/ubuntu/openmanus_project/demo_google_history.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Демонстрационные файлы созданы:")
    print("   📄 demo_google_history.json - JSON данные презентации")
    print("   🌐 demo_google_history.html - HTML версия для просмотра")
    print("\n📊 Характеристики демо презентации:")
    print(f"   • Слайдов: {len(presentation['slides'])}")
    print(f"   • Язык: {presentation['metadata']['language']}")
    print(f"   • Изображения: {'Да' if presentation['metadata']['includes_images'] else 'Нет'}")
    print(f"   • Типы контента: параграфы, списки, цитаты, код")

if __name__ == "__main__":
    save_demo_files()

