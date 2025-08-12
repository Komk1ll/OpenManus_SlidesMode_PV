#!/usr/bin/env python3
"""
Standalone script for creating presentations without complex dependencies
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_ai_education_presentation():
    """Create presentation about AI in education"""
    
    presentation = {
        "title": "Искусственный интеллект в образовании: возможности и вызовы",
        "description": "Комплексный обзор применения ИИ в образовательной сфере, включая современные технологии, практические применения и этические вопросы",
        "created_at": datetime.now().isoformat(),
        "topic": "Искусственный интеллект в образовании",
        "slides": [
            {
                "id": 1,
                "title": "Искусственный интеллект в образовании",
                "subtitle": "Возможности и вызовы современных технологий",
                "type": "title",
                "content": [
                    "• Обзор современного состояния ИИ в образовании",
                    "• Ключевые технологии и их применение",
                    "• Анализ возможностей и ограничений",
                    "• Этические аспекты и будущие перспективы"
                ],
                "notes": "Вводный слайд, который задает тон всей презентации. Подчеркнуть актуальность темы и важность понимания роли ИИ в современном образовании.",
                "keywords": ["искусственный интеллект", "образование", "технологии"],
                "image_type": "professional"
            },
            {
                "id": 2,
                "title": "Что такое ИИ в образовании?",
                "subtitle": "Определения и основные концепции",
                "type": "content",
                "content": [
                    "• Машинное обучение для анализа образовательных данных",
                    "• Обработка естественного языка для автоматической проверки",
                    "• Компьютерное зрение для анализа поведения студентов",
                    "• Экспертные системы для персонализированного обучения",
                    "• Чат-боты и виртуальные ассистенты для поддержки студентов"
                ],
                "notes": "Объяснить основные технологии ИИ, которые применяются в образовании. Привести конкретные примеры каждой технологии.",
                "keywords": ["машинное обучение", "NLP", "компьютерное зрение"],
                "image_type": "technical"
            },
            {
                "id": 3,
                "title": "Персонализированное обучение",
                "subtitle": "Адаптация под индивидуальные потребности",
                "type": "content",
                "content": [
                    "• Анализ стиля обучения каждого студента",
                    "• Автоматическая корректировка сложности материала",
                    "• Рекомендации по дополнительным ресурсам",
                    "• Прогнозирование трудностей в обучении",
                    "• Создание индивидуальных образовательных траекторий"
                ],
                "notes": "Подчеркнуть, как ИИ помогает создавать уникальный опыт обучения для каждого студента. Привести примеры успешных платформ.",
                "keywords": ["персонализация", "адаптивное обучение", "индивидуальный подход"],
                "image_type": "education"
            },
            {
                "id": 4,
                "title": "Автоматизация оценивания",
                "subtitle": "Эффективность и объективность",
                "type": "content",
                "content": [
                    "• Автоматическая проверка тестов и заданий",
                    "• Анализ письменных работ на плагиат и качество",
                    "• Оценка устных ответов и презентаций",
                    "• Мгновенная обратная связь для студентов",
                    "• Снижение нагрузки на преподавателей"
                ],
                "notes": "Обсудить преимущества автоматизации оценивания: скорость, объективность, консистентность. Также упомянуть ограничения.",
                "keywords": ["автоматизация", "оценивание", "обратная связь"],
                "image_type": "technical"
            },
            {
                "id": 5,
                "title": "Интеллектуальные обучающие системы",
                "subtitle": "Виртуальные наставники и помощники",
                "type": "content",
                "content": [
                    "• Чат-боты для ответов на вопросы студентов 24/7",
                    "• Виртуальные репетиторы для дополнительной помощи",
                    "• Системы раннего предупреждения о проблемах в обучении",
                    "• Интеллектуальные рекомендательные системы",
                    "• Адаптивные учебные платформы"
                ],
                "notes": "Показать, как ИИ может дополнить работу преподавателей, а не заменить их. Подчеркнуть важность человеческого фактора.",
                "keywords": ["чат-боты", "виртуальные помощники", "ITS"],
                "image_type": "technology"
            },
            {
                "id": 6,
                "title": "Этические вызовы",
                "subtitle": "Приватность, справедливость и прозрачность",
                "type": "content",
                "content": [
                    "• Защита персональных данных студентов",
                    "• Предотвращение алгоритмической дискриминации",
                    "• Обеспечение прозрачности принятия решений ИИ",
                    "• Сохранение человеческого контроля над образованием",
                    "• Равный доступ к технологиям для всех студентов"
                ],
                "notes": "Критически важная тема. Обсудить реальные риски и способы их минимизации. Подчеркнуть ответственность разработчиков и педагогов.",
                "keywords": ["этика", "приватность", "справедливость"],
                "image_type": "challenge"
            },
            {
                "id": 7,
                "title": "Практические примеры",
                "subtitle": "Успешные внедрения ИИ в образовании",
                "type": "content",
                "content": [
                    "• Khan Academy - персонализированные рекомендации",
                    "• Coursera - автоматическое оценивание заданий",
                    "• Duolingo - адаптивное изучение языков",
                    "• Carnegie Learning - интеллектуальные математические системы",
                    "• Российские проекты: Яндекс.Учебник, Учи.ру"
                ],
                "notes": "Привести конкретные примеры успешного использования ИИ. Показать разнообразие применений и достигнутые результаты.",
                "keywords": ["Khan Academy", "Coursera", "Duolingo", "практика"],
                "image_type": "business"
            },
            {
                "id": 8,
                "title": "Будущее ИИ в образовании",
                "subtitle": "Тренды и перспективы развития",
                "type": "conclusion",
                "content": [
                    "• Развитие более совершенных алгоритмов персонализации",
                    "• Интеграция с виртуальной и дополненной реальностью",
                    "• Создание полностью адаптивных образовательных экосистем",
                    "• Развитие эмоционального ИИ для лучшего понимания студентов",
                    "• Формирование новых педагогических подходов"
                ],
                "notes": "Заключительный слайд должен вдохновлять на дальнейшее изучение темы. Подчеркнуть важность баланса между технологиями и человеческим фактором.",
                "keywords": ["будущее", "тренды", "перспективы"],
                "image_type": "future"
            }
        ],
        "metadata": {
            "total_slides": 8,
            "generation_method": "OpenManus AI Agent (Standalone)",
            "language": "russian",
            "estimated_duration": "20-25 minutes",
            "target_audience": "Педагоги, администраторы образовательных учреждений, исследователи"
        }
    }
    
    return presentation

def create_blockchain_presentation():
    """Create presentation about blockchain technology"""
    
    presentation = {
        "title": "Блокчейн технологии: принципы работы и применение",
        "description": "Подробное изучение технологии блокчейн, её технических основ и практических применений в различных сферах",
        "created_at": datetime.now().isoformat(),
        "topic": "Блокчейн технологии",
        "slides": [
            {
                "id": 1,
                "title": "Блокчейн технологии",
                "subtitle": "Принципы работы и практическое применение",
                "type": "title",
                "content": [
                    "• Фундаментальные принципы технологии блокчейн",
                    "• Техническая архитектура и механизмы работы",
                    "• Реальные применения в различных отраслях",
                    "• Преимущества, ограничения и перспективы развития"
                ],
                "notes": "Вводный слайд, который представляет тему и структуру презентации. Подчеркнуть революционный характер технологии.",
                "keywords": ["блокчейн", "криптография", "децентрализация"],
                "image_type": "professional"
            },
            {
                "id": 2,
                "title": "Что такое блокчейн?",
                "subtitle": "Основные концепции и определения",
                "type": "content",
                "content": [
                    "• Распределённый реестр транзакций",
                    "• Криптографическая защита данных",
                    "• Децентрализованная архитектура без единого центра управления",
                    "• Неизменяемость записей после подтверждения",
                    "• Прозрачность и публичная верификация"
                ],
                "notes": "Объяснить базовые концепции простым языком. Использовать аналогии для лучшего понимания.",
                "keywords": ["распределённый реестр", "криптография", "децентрализация"],
                "image_type": "technical"
            },
            {
                "id": 3,
                "title": "Техническая архитектура",
                "subtitle": "Как работает блокчейн изнутри",
                "type": "content",
                "content": [
                    "• Структура блока: заголовок, хеш, транзакции",
                    "• Криптографические хеш-функции (SHA-256)",
                    "• Цепочка блоков и связи между ними",
                    "• Цифровые подписи для аутентификации",
                    "• Merkle Tree для эффективной верификации"
                ],
                "notes": "Технический слайд, требующий детального объяснения. Использовать диаграммы и схемы для визуализации.",
                "keywords": ["хеширование", "цифровые подписи", "Merkle Tree"],
                "image_type": "technical"
            },
            {
                "id": 4,
                "title": "Алгоритмы консенсуса",
                "subtitle": "Как сеть достигает согласия",
                "type": "content",
                "content": [
                    "• Proof of Work (PoW) - доказательство работы",
                    "• Proof of Stake (PoS) - доказательство доли",
                    "• Delegated Proof of Stake (DPoS)",
                    "• Practical Byzantine Fault Tolerance (pBFT)",
                    "• Сравнение энергоэффективности и безопасности"
                ],
                "notes": "Объяснить различные механизмы консенсуса и их применение в разных блокчейн-сетях. Обсудить компромиссы.",
                "keywords": ["консенсус", "PoW", "PoS", "майнинг"],
                "image_type": "technical"
            },
            {
                "id": 5,
                "title": "Криптовалюты",
                "subtitle": "Первое и самое известное применение",
                "type": "content",
                "content": [
                    "• Bitcoin - первая успешная криптовалюта",
                    "• Ethereum и концепция смарт-контрактов",
                    "• Стейблкоины для стабильности стоимости",
                    "• Центральные банковские цифровые валюты (CBDC)",
                    "• DeFi - децентрализованные финансовые услуги"
                ],
                "notes": "Рассказать об эволюции криптовалют от Bitcoin до современных DeFi протоколов. Объяснить практическую ценность.",
                "keywords": ["Bitcoin", "Ethereum", "DeFi", "смарт-контракты"],
                "image_type": "business"
            },
            {
                "id": 6,
                "title": "Смарт-контракты",
                "subtitle": "Программируемые соглашения",
                "type": "content",
                "content": [
                    "• Автоматическое исполнение условий договора",
                    "• Устранение необходимости в посредниках",
                    "• Программирование на Solidity и других языках",
                    "• Применение в страховании, недвижимости, логистике",
                    "• Ограничения и потенциальные уязвимости"
                ],
                "notes": "Показать практические примеры смарт-контрактов. Обсудить как преимущества, так и риски их использования.",
                "keywords": ["смарт-контракты", "Solidity", "автоматизация"],
                "image_type": "technology"
            },
            {
                "id": 7,
                "title": "Применения в различных отраслях",
                "subtitle": "Реальные случаи использования",
                "type": "content",
                "content": [
                    "• Логистика и цепочки поставок (Walmart, Maersk)",
                    "• Здравоохранение - безопасное хранение медицинских данных",
                    "• Недвижимость - прозрачные сделки и реестры",
                    "• Голосование - защищённые электронные выборы",
                    "• Интеллектуальная собственность и авторские права"
                ],
                "notes": "Привести конкретные примеры успешного внедрения блокчейна в различных сферах. Показать практическую ценность.",
                "keywords": ["логистика", "здравоохранение", "недвижимость"],
                "image_type": "business"
            },
            {
                "id": 8,
                "title": "Вызовы и ограничения",
                "subtitle": "Проблемы, которые нужно решить",
                "type": "content",
                "content": [
                    "• Масштабируемость - ограничения пропускной способности",
                    "• Энергопотребление при использовании PoW",
                    "• Регулятивная неопределённость в разных юрисдикциях",
                    "• Сложность интеграции с существующими системами",
                    "• Проблемы пользовательского опыта и удобства"
                ],
                "notes": "Честно обсудить текущие проблемы технологии. Показать, что блокчейн не является универсальным решением.",
                "keywords": ["масштабируемость", "энергопотребление", "регулирование"],
                "image_type": "challenge"
            },
            {
                "id": 9,
                "title": "Будущее блокчейн технологий",
                "subtitle": "Тренды и перспективы развития",
                "type": "conclusion",
                "content": [
                    "• Web3 и децентрализованный интернет",
                    "• Интеграция с IoT и искусственным интеллектом",
                    "• Развитие межблокчейновой совместимости",
                    "• Экологически устойчивые консенсус-алгоритмы",
                    "• Массовое внедрение в государственных услугах"
                ],
                "notes": "Заключительный слайд должен вдохновлять на дальнейшее изучение технологии. Подчеркнуть потенциал для трансформации общества.",
                "keywords": ["Web3", "IoT", "будущее", "инновации"],
                "image_type": "future"
            }
        ],
        "metadata": {
            "total_slides": 9,
            "generation_method": "OpenManus AI Agent (Standalone)",
            "language": "russian",
            "estimated_duration": "25-30 minutes",
            "target_audience": "IT-специалисты, предприниматели, студенты технических специальностей"
        }
    }
    
    return presentation

def generate_html_presentation(presentation_data):
    """Generate HTML version of the presentation"""
    
    html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}
        .presentation {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
            margin-bottom: 15px;
        }}
        .header p {{
            margin: 0;
            font-size: 1.3em;
            opacity: 0.9;
            max-width: 800px;
            margin: 0 auto;
        }}
        .slide {{
            padding: 50px 40px;
            border-bottom: 1px solid #eee;
            position: relative;
        }}
        .slide:last-child {{
            border-bottom: none;
        }}
        .slide-number {{
            position: absolute;
            top: 20px;
            right: 30px;
            background: #667eea;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .slide h2 {{
            color: #667eea;
            font-size: 2.2em;
            margin: 0 0 10px 0;
            font-weight: 600;
        }}
        .slide h3 {{
            color: #666;
            font-size: 1.4em;
            margin: 0 0 30px 0;
            font-weight: normal;
            font-style: italic;
        }}
        .slide-content {{
            font-size: 1.15em;
            line-height: 1.8;
            margin-bottom: 30px;
        }}
        .slide-content ul {{
            padding-left: 0;
            margin: 20px 0;
        }}
        .slide-content li {{
            list-style: none;
            padding: 12px 0 12px 25px;
            border-left: 4px solid #667eea;
            margin: 15px 0;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
            position: relative;
        }}
        .slide-content li:before {{
            content: "▶";
            color: #667eea;
            position: absolute;
            left: 8px;
            font-size: 0.8em;
        }}
        .slide-notes {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            margin-top: 30px;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .slide-notes h4 {{
            margin: 0 0 15px 0;
            color: #667eea;
            font-size: 1.1em;
            font-weight: 600;
        }}
        .slide-notes p {{
            margin: 0;
            color: #555;
            font-style: italic;
        }}
        .metadata {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 0.95em;
        }}
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .metadata-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .metadata-item strong {{
            color: #667eea;
            display: block;
            margin-bottom: 5px;
        }}
        .title-slide {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .title-slide h2, .title-slide h3 {{
            color: white;
        }}
        .conclusion-slide {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
        }}
        .conclusion-slide h2, .conclusion-slide h3 {{
            color: white;
        }}
        .conclusion-slide .slide-content li {{
            background: rgba(255,255,255,0.1);
            border-left-color: white;
        }}
        @media (max-width: 768px) {{
            .presentation {{
                margin: 10px;
                border-radius: 10px;
            }}
            .header, .slide {{
                padding: 30px 20px;
            }}
            .header h1 {{
                font-size: 2.2em;
            }}
            .slide h2 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation">
        <div class="header">
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        
        {slides_html}
        
        <div class="metadata">
            <h3>Информация о презентации</h3>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <strong>Создано:</strong>
                    {created_at}
                </div>
                <div class="metadata-item">
                    <strong>Количество слайдов:</strong>
                    {total_slides}
                </div>
                <div class="metadata-item">
                    <strong>Продолжительность:</strong>
                    {duration}
                </div>
                <div class="metadata-item">
                    <strong>Целевая аудитория:</strong>
                    {audience}
                </div>
                <div class="metadata-item">
                    <strong>Генератор:</strong>
                    OpenManus AI Agent
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    slides_html = ""
    for i, slide in enumerate(presentation_data.get('slides', [])):
        slide_class = ""
        if slide.get('type') == 'title':
            slide_class = "title-slide"
        elif slide.get('type') == 'conclusion':
            slide_class = "conclusion-slide"
        
        content_html = ""
        if isinstance(slide.get('content'), list):
            content_html = "<ul>" + "".join(f"<li>{item}</li>" for item in slide['content']) + "</ul>"
        else:
            content_html = f"<p>{slide.get('content', '')}</p>"
        
        slide_html = f"""
        <div class="slide {slide_class}">
            <div class="slide-number">Слайд {i+1}</div>
            <h2>{slide.get('title', 'Untitled')}</h2>
            <h3>{slide.get('subtitle', '')}</h3>
            <div class="slide-content">
                {content_html}
            </div>
            <div class="slide-notes">
                <h4>📝 Заметки докладчика:</h4>
                <p>{slide.get('notes', 'Заметки отсутствуют')}</p>
            </div>
        </div>
        """
        slides_html += slide_html
    
    metadata = presentation_data.get('metadata', {})
    
    return html_template.format(
        title=presentation_data.get('title', 'Untitled Presentation'),
        description=presentation_data.get('description', ''),
        slides_html=slides_html,
        created_at=presentation_data.get('created_at', ''),
        total_slides=len(presentation_data.get('slides', [])),
        duration=metadata.get('estimated_duration', 'Не указано'),
        audience=metadata.get('target_audience', 'Не указано')
    )

async def main():
    """Main function to create presentations"""
    
    logger.info("🚀 Starting OpenManus Presentation Generation")
    
    # Create presentations directory
    presentations_dir = "./presentations"
    os.makedirs(presentations_dir, exist_ok=True)
    
    # Create presentations
    presentations = [
        ("ai_education", create_ai_education_presentation()),
        ("blockchain", create_blockchain_presentation())
    ]
    
    results = []
    
    for i, (name, presentation) in enumerate(presentations, 1):
        logger.info(f"\n📊 Creating presentation {i}/2: {presentation['title']}")
        
        try:
            # Save JSON version
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"presentation_{name}_{timestamp}.json"
            json_filepath = os.path.join(presentations_dir, json_filename)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(presentation, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ JSON saved: {json_filepath}")
            
            # Generate and save HTML version
            html_content = generate_html_presentation(presentation)
            html_filename = f"presentation_{name}_{timestamp}.html"
            html_filepath = os.path.join(presentations_dir, html_filename)
            
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ HTML saved: {html_filepath}")
            
            results.append({
                "name": name,
                "title": presentation['title'],
                "json_file": json_filepath,
                "html_file": html_filepath,
                "slides_count": len(presentation['slides'])
            })
            
        except Exception as e:
            logger.error(f"❌ Failed to create presentation {name}: {e}")
    
    # Summary
    logger.info(f"\n🎉 Generation completed! Created {len(results)} presentations:")
    for result in results:
        logger.info(f"\n📋 {result['title']}")
        logger.info(f"   📄 JSON: {result['json_file']}")
        logger.info(f"   🌐 HTML: {result['html_file']}")
        logger.info(f"   📊 Slides: {result['slides_count']}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())

