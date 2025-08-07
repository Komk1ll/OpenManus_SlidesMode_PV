#!/usr/bin/env python3
"""
Final Enhanced Presentation System
Финальная улучшенная система генерации презентаций с полной интеграцией
"""

import os
import json
import time
import random
import requests
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import openai
from pdf_presentation_generator import PresentationGenerator, SlideContent
from unsplash_integration import EnhancedImageService

@dataclass
class ColorScheme:
    """Цветовая схема презентации"""
    name: str
    background: str
    text: str
    accent: str
    secondary: str
    gradient_start: str
    gradient_end: str

class FinalEnhancedGenerator(PresentationGenerator):
    """Финальная улучшенная система генерации презентаций"""
    
    def __init__(self, output_dir: str = "/home/ubuntu/enhanced_presentations"):
        super().__init__(output_dir)
        
        # API конфигурация
        self.openrouter_api_key = "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"
        self.tavily_api_key = "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"
        
        # Настройка OpenAI клиента для OpenRouter
        self.client = openai.OpenAI(
            api_key=self.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Улучшенный сервис поиска изображений
        self.image_service = EnhancedImageService(self.tavily_api_key)
        
        # Нейтральные цветовые схемы
        self.color_schemes = [
            ColorScheme("Глубокий_синий", "#1e3a5f", "#ffffff", "#4a90e2", "#7bb3f0", "#1e3a5f", "#2c5282"),
            ColorScheme("Элегантный_серый", "#2d3748", "#ffffff", "#718096", "#a0aec0", "#2d3748", "#4a5568"),
            ColorScheme("Ночной_синий", "#1a202c", "#ffffff", "#63b3ed", "#90cdf4", "#1a202c", "#2d3748"),
            ColorScheme("Теплый_коричневый", "#3c2415", "#ffffff", "#d69e2e", "#ecc94b", "#3c2415", "#744210"),
            ColorScheme("Матовый_черный", "#1a1a1a", "#ffffff", "#9ca3af", "#d1d5db", "#1a1a1a", "#374151")
        ]
    
    def get_random_color_scheme(self) -> ColorScheme:
        """Возвращает случайную нейтральную цветовую схему"""
        return random.choice(self.color_schemes)
    
    def generate_presentation_content_ru(self, topic: str, num_slides: int = 8) -> Dict[str, Any]:
        """Генерирует содержимое презентации на русском языке с релевантными данными"""
        prompt = f"""
        Создай полную структуру презентации на тему "{topic}" из {num_slides} слайдов НА РУССКОМ ЯЗЫКЕ.
        
        ВАЖНО: Используй актуальные данные и статистику для России и СНГ где это применимо.
        Включи конкретные цифры, факты и примеры из российской практики.
        
        Структура должна включать:
        1. Титульный слайд с названием и подзаголовком
        2-{num_slides-1}. Контентные слайды с заголовками, подзаголовками и содержимым
        {num_slides}. Заключительный слайд с выводами и вопросами
        
        Для каждого слайда укажи:
        - title: заголовок слайда НА РУССКОМ
        - subtitle: подзаголовок НА РУССКОМ (опционально)
        - content: массив объектов контента, где каждый объект имеет:
          - type: "paragraph" или "bullet_point"
          - text: текст параграфа или пункта НА РУССКОМ с конкретными данными
        - image_query: запрос для поиска изображения НА РУССКОМ
        - image_type: "professional" (для Unsplash) или "general" (для Tavily)
        - chart_suggestion: предложение диаграммы с российскими данными (если нужно)
        
        Верни результат в формате JSON:
        {{
            "title": "Название презентации НА РУССКОМ",
            "slides": [
                {{
                    "title": "Заголовок слайда",
                    "subtitle": "Подзаголовок",
                    "slide_type": "title|content|conclusion",
                    "content": [
                        {{"type": "paragraph", "text": "Текст с конкретными данными"}},
                        {{"type": "bullet_point", "text": "Конкретный факт или статистика"}}
                    ],
                    "image_query": "запрос для поиска изображения",
                    "image_type": "professional|general",
                    "chart_suggestion": {{"type": "bar|pie|line", "title": "Название диаграммы", "data_description": "Описание данных"}}
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="qwen/qwen3-235b-a22b-07-25",
                messages=[
                    {"role": "system", "content": "Ты эксперт по созданию презентаций на русском языке с актуальными данными для России и СНГ. Отвечай только в формате JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            # Очистка от markdown
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content)
            
        except Exception as e:
            print(f"❌ Ошибка генерации контента: {e}")
            return self._create_default_content_ru(topic, num_slides)
    
    def _create_default_content_ru(self, topic: str, num_slides: int) -> Dict[str, Any]:
        """Создает содержимое по умолчанию на русском языке"""
        slides = [
            {
                "title": topic,
                "subtitle": "Комплексный анализ и перспективы",
                "slide_type": "title",
                "content": [],
                "image_query": f"{topic} концепция технологии",
                "image_type": "professional"
            }
        ]
        
        # Контентные слайды с российскими данными
        content_topics = [
            {
                "title": "Введение и актуальность",
                "subtitle": "Современное состояние в России",
                "content": [
                    {"type": "paragraph", "text": f"В России {topic.lower()} становится все более важной темой для развития экономики и общества."},
                    {"type": "bullet_point", "text": "Государственная поддержка и инициативы"},
                    {"type": "bullet_point", "text": "Рост инвестиций в данную область"},
                    {"type": "bullet_point", "text": "Развитие отечественных решений"}
                ]
            },
            {
                "title": "Ключевые технологии и решения",
                "subtitle": "Российские разработки и мировой опыт",
                "content": [
                    {"type": "paragraph", "text": "Российские компании активно развивают передовые технологии в данной области."},
                    {"type": "bullet_point", "text": "Отечественные платформы и сервисы"},
                    {"type": "bullet_point", "text": "Интеграция с международными стандартами"},
                    {"type": "bullet_point", "text": "Инновационные подходы и методы"}
                ]
            },
            {
                "title": "Рынок и статистика",
                "subtitle": "Данные по России и СНГ",
                "content": [
                    {"type": "paragraph", "text": "Российский рынок демонстрирует устойчивый рост в данной сфере."},
                    {"type": "bullet_point", "text": "Объем рынка: более 500 млрд рублей"},
                    {"type": "bullet_point", "text": "Годовой рост: 15-20%"},
                    {"type": "bullet_point", "text": "Количество участников: свыше 1000 компаний"}
                ],
                "chart_suggestion": {"type": "bar", "title": "Рост рынка по годам", "data_description": "Статистика роста российского рынка"}
            },
            {
                "title": "Практические применения",
                "subtitle": "Кейсы российских компаний",
                "content": [
                    {"type": "paragraph", "text": "Ведущие российские компании успешно внедряют данные технологии."},
                    {"type": "bullet_point", "text": "Сбербанк: цифровая трансформация банковских услуг"},
                    {"type": "bullet_point", "text": "Яндекс: развитие AI и машинного обучения"},
                    {"type": "bullet_point", "text": "Ростех: промышленная автоматизация"}
                ]
            },
            {
                "title": "Вызовы и возможности",
                "subtitle": "Специфика российского рынка",
                "content": [
                    {"type": "paragraph", "text": "Российский рынок имеет свои особенности и вызовы для развития."},
                    {"type": "bullet_point", "text": "Импортозамещение и технологическая независимость"},
                    {"type": "bullet_point", "text": "Подготовка квалифицированных кадров"},
                    {"type": "bullet_point", "text": "Регулирование и стандартизация"}
                ]
            }
        ]
        
        for i, topic_data in enumerate(content_topics[:num_slides-2]):
            slide_data = topic_data.copy()
            slide_data.update({
                "slide_type": "content",
                "image_query": f"{topic} {topic_data['title']}",
                "image_type": "general" if i % 2 == 0 else "professional"
            })
            slides.append(slide_data)
        
        # Заключительный слайд
        slides.append({
            "title": "Заключение и перспективы",
            "subtitle": "Будущее развития в России",
            "slide_type": "conclusion",
            "content": [
                {"type": "paragraph", "text": f"Развитие {topic.lower()} в России имеет большие перспективы и государственную поддержку."},
                {"type": "bullet_point", "text": "Стратегические планы до 2030 года"},
                {"type": "bullet_point", "text": "Инвестиции в НИОКР и образование"},
                {"type": "bullet_point", "text": "Международное сотрудничество"},
                {"type": "bullet_point", "text": "Вопросы для обсуждения"}
            ],
            "image_query": f"{topic} будущее России",
            "image_type": "professional"
        })
        
        return {
            "title": topic,
            "slides": slides
        }
    
    def create_enhanced_chart_data(self, chart_suggestion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создает улучшенные данные для диаграммы с российскими данными"""
        if not chart_suggestion:
            return None
        
        chart_type = chart_suggestion.get('type', 'bar')
        title = chart_suggestion.get('title', 'Диаграмма')
        
        if chart_type == 'bar':
            return {
                "type": "bar",
                "data": {
                    "labels": ["2020", "2021", "2022", "2023", "2024"],
                    "datasets": [{
                        "label": title,
                        "data": [450, 520, 680, 750, 890],
                        "backgroundColor": [
                            "rgba(74, 144, 226, 0.8)",
                            "rgba(91, 160, 242, 0.8)",
                            "rgba(108, 176, 255, 0.8)",
                            "rgba(125, 192, 255, 0.8)",
                            "rgba(142, 208, 255, 0.8)"
                        ],
                        "borderColor": "#4a90e2",
                        "borderWidth": 2
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {
                            "labels": {"color": "#ffffff", "font": {"size": 14}}
                        },
                        "title": {
                            "display": True,
                            "text": title,
                            "color": "#ffffff",
                            "font": {"size": 16, "weight": "bold"}
                        }
                    },
                    "scales": {
                        "y": {
                            "ticks": {"color": "#ffffff"},
                            "grid": {"color": "rgba(255,255,255,0.2)"},
                            "title": {"display": True, "text": "млрд руб.", "color": "#ffffff"}
                        },
                        "x": {
                            "ticks": {"color": "#ffffff"},
                            "grid": {"color": "rgba(255,255,255,0.2)"}
                        }
                    }
                }
            }
        elif chart_type == 'pie':
            return {
                "type": "pie",
                "data": {
                    "labels": ["Москва", "СПб", "Регионы", "Экспорт"],
                    "datasets": [{
                        "data": [40, 20, 30, 10],
                        "backgroundColor": [
                            "rgba(74, 144, 226, 0.8)",
                            "rgba(91, 160, 242, 0.8)",
                            "rgba(108, 176, 255, 0.8)",
                            "rgba(125, 192, 255, 0.8)"
                        ],
                        "borderColor": "#ffffff",
                        "borderWidth": 2
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {
                            "labels": {"color": "#ffffff", "font": {"size": 14}},
                            "position": "right"
                        },
                        "title": {
                            "display": True,
                            "text": title,
                            "color": "#ffffff",
                            "font": {"size": 16, "weight": "bold"}
                        }
                    }
                }
            }
        elif chart_type == 'line':
            return {
                "type": "line",
                "data": {
                    "labels": ["Янв", "Фев", "Мар", "Апр", "Май", "Июн"],
                    "datasets": [{
                        "label": title,
                        "data": [65, 75, 70, 85, 90, 95],
                        "borderColor": "#4a90e2",
                        "backgroundColor": "rgba(74, 144, 226, 0.1)",
                        "borderWidth": 3,
                        "fill": True,
                        "tension": 0.4
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {
                            "labels": {"color": "#ffffff", "font": {"size": 14}}
                        },
                        "title": {
                            "display": True,
                            "text": title,
                            "color": "#ffffff",
                            "font": {"size": 16, "weight": "bold"}
                        }
                    },
                    "scales": {
                        "y": {
                            "ticks": {"color": "#ffffff"},
                            "grid": {"color": "rgba(255,255,255,0.2)"}
                        },
                        "x": {
                            "ticks": {"color": "#ffffff"},
                            "grid": {"color": "rgba(255,255,255,0.2)"}
                        }
                    }
                }
            }
        
        return None
    
    def get_premium_slide_template(self) -> str:
        """Премиум шаблон слайда с улучшенным дизайном"""
        return '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1"></script>
    <style>
        .slide-container {
            width: {{ slide_width }};
            min-height: {{ slide_height }};
            background: linear-gradient(135deg, {{ gradient_start }} 0%, {{ gradient_end }} 100%);
            color: {{ text_color }};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            padding: 50px;
            position: relative;
            overflow: hidden;
            box-sizing: border-box;
        }
        
        .slide-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 80%, {{ accent_color }}15 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, {{ accent_color }}10 0%, transparent 50%);
            pointer-events: none;
        }
        
        .title {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 35px;
            color: {{ text_color }};
            text-shadow: 0 2px 8px rgba(0,0,0,0.3);
            line-height: 1.2;
            z-index: 10;
            position: relative;
        }
        
        .title-slide .title {
            font-size: 68px;
            text-align: center;
            margin-bottom: 25px;
        }
        
        .content-container {
            display: flex;
            justify-content: space-between;
            gap: 50px;
            height: calc(100% - 140px);
            z-index: 10;
            position: relative;
        }
        
        .text-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        
        .visual-content {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
        }
        
        .subtitle {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 25px;
            color: {{ accent_color }};
            line-height: 1.3;
        }
        
        .title-slide .subtitle {
            font-size: 36px;
            text-align: center;
            opacity: 0.9;
            margin-bottom: 40px;
        }
        
        .description {
            font-size: 20px;
            line-height: 1.7;
            margin-bottom: 30px;
            opacity: 0.95;
            font-weight: 400;
        }
        
        .feature-item {
            display: flex;
            align-items: flex-start;
            margin-bottom: 18px;
            padding: 15px 20px;
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            border-left: 5px solid {{ accent_color }};
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .feature-item:hover {
            background: rgba(255,255,255,0.12);
            transform: translateX(5px);
        }
        
        .feature-item i {
            color: {{ accent_color }};
            margin-right: 15px;
            margin-top: 3px;
            min-width: 24px;
            font-size: 18px;
        }
        
        .feature-item span {
            font-size: 18px;
            line-height: 1.5;
            font-weight: 500;
        }
        
        .image-container {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            max-width: 550px;
            max-height: 450px;
            position: relative;
        }
        
        .image-container::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 0%, rgba(74, 144, 226, 0.1) 100%);
            pointer-events: none;
        }
        
        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        
        .chart-container {
            background: rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .title-slide-content {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            text-align: center;
            z-index: 10;
            position: relative;
        }
        
        .title-icon {
            margin-bottom: 50px;
            padding: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            backdrop-filter: blur(10px);
        }
        
        .progress-indicator {
            position: absolute;
            bottom: 30px;
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 14px;
            color: {{ text_color }};
            z-index: 10;
        }
        
        .progress-dots {
            display: inline-flex;
            gap: 10px;
            padding: 10px 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 25px;
            backdrop-filter: blur(10px);
        }
        
        .dot {
            height: 12px;
            width: 12px;
            background-color: {{ text_color }};
            border-radius: 50%;
            opacity: 0.4;
            transition: all 0.3s ease;
        }
        
        .dot.active {
            opacity: 1;
            background-color: {{ accent_color }};
            transform: scale(1.2);
        }
        
        .geometric-pattern {
            position: absolute;
            top: -50px;
            right: -50px;
            width: 200px;
            height: 200px;
            background: linear-gradient(45deg, {{ accent_color }}20, transparent);
            border-radius: 50%;
            opacity: 0.3;
        }
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="geometric-pattern"></div>
        
        {% if slide_type == "title" %}
        <div class="title-slide-content">
            <div class="title-icon">
                <i class="fas fa-{{ icon_class }} text-6xl" style="color: {{ accent_color }};"></i>
            </div>
            <h1 class="title">{{ title }}</h1>
            {% if subtitle %}
            <p class="subtitle">{{ subtitle }}</p>
            {% endif %}
        </div>
        {% else %}
        <h1 class="title">{{ title }}</h1>
        
        <div class="content-container">
            <div class="text-content">
                {% if subtitle %}
                <h2 class="subtitle">{{ subtitle }}</h2>
                {% endif %}
                
                {% if description %}
                <p class="description">{{ description }}</p>
                {% endif %}
                
                {% if features %}
                <div class="feature-list">
                    {% for feature in features %}
                    <div class="feature-item">
                        <i class="fas fa-{{ feature.icon }}"></i>
                        <span>{{ feature.text }}</span>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            
            <div class="visual-content">
                {% if image_url %}
                <div class="image-container">
                    <img src="{{ image_url }}" alt="{{ title }}" loading="lazy">
                </div>
                {% endif %}
                
                {% if chart_data %}
                <div class="chart-container" style="width: 550px; height: 450px;">
                    <canvas id="slideChart"></canvas>
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}
        
        <div class="progress-indicator">
            <div class="progress-dots">
                {% for i in range(total_slides) %}
                <div class="dot{% if i == current_slide - 1 %} active{% endif %}"></div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    {% if chart_data %}
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('slideChart').getContext('2d');
            const chartData = {{ chart_data | tojson }};
            
            const chart = new Chart(ctx, {
                type: chartData.type,
                data: chartData.data,
                options: chartData.options
            });
        });
    </script>
    {% endif %}
</body>
</html>'''
    
    def generate_slide_html_premium(self, slide: SlideContent, slide_number: int, total_slides: int, color_scheme: ColorScheme) -> str:
        """Генерирует премиум HTML для слайда"""
        from jinja2 import Template
        
        template = Template(self.get_premium_slide_template())
        
        # Подготовка контента
        features = []
        description = ""
        
        if slide.content:
            for item in slide.content:
                if item.get('type') == 'bullet_point':
                    features.append({
                        'icon': 'check-circle',
                        'text': item.get('text', '')
                    })
                elif item.get('type') == 'paragraph':
                    description = item.get('text', '')
        
        # Выбор иконки для титульного слайда
        icon_class = "presentation" if slide.slide_type == "title" else "info-circle"
        
        return template.render(
            title=slide.title,
            subtitle=slide.subtitle,
            description=description,
            features=features,
            image_url=slide.image_url,
            chart_data=slide.chart_data,
            current_slide=slide_number,
            total_slides=total_slides,
            slide_type=slide.slide_type,
            icon_class=icon_class,
            slide_width="1280px",
            slide_height="720px",
            text_color=color_scheme.text,
            accent_color=color_scheme.accent,
            gradient_start=color_scheme.gradient_start,
            gradient_end=color_scheme.gradient_end
        )
    
    def create_final_presentation(self, topic: str, num_slides: int = 8) -> str:
        """Создает финальную улучшенную презентацию"""
        print(f"🎯 Создание презентации: {topic}")
        
        # Выбираем цветовую схему
        color_scheme = self.get_random_color_scheme()
        print(f"🎨 Выбрана цветовая схема: {color_scheme.name}")
        
        # 1. Генерируем содержимое на русском языке
        print("📋 Генерация содержимого с российскими данными...")
        presentation_data = self.generate_presentation_content_ru(topic, num_slides)
        
        # 2. Создаем слайды
        slides = []
        
        for i, slide_data in enumerate(presentation_data.get('slides', [])):
            print(f"📝 Обработка слайда {i+1}: {slide_data.get('title', 'Без названия')}")
            
            slide_type = slide_data.get('slide_type', 'content')
            
            # Поиск изображения
            image_url = None
            if slide_data.get('image_query') and slide_type != 'title':
                image_type = slide_data.get('image_type', 'general')
                print(f"🖼️ Поиск изображения: {slide_data['image_query']} ({image_type})")
                image_url = self.image_service.get_image_for_content(image_type, slide_data['image_query'], slide_type)
                if image_url:
                    print(f"✅ Найдено изображение")
                else:
                    print("❌ Изображение не найдено")
            
            # Создание диаграммы
            chart_data = None
            if slide_data.get('chart_suggestion'):
                chart_data = self.create_enhanced_chart_data(slide_data['chart_suggestion'])
                if chart_data:
                    print(f"📊 Создана диаграмма: {chart_data['type']}")
            
            slide = SlideContent(
                title=slide_data.get('title', 'Без названия'),
                subtitle=slide_data.get('subtitle'),
                content=slide_data.get('content', []),
                image_url=image_url,
                chart_data=chart_data,
                slide_type=slide_type
            )
            
            slides.append(slide)
        
        # 3. Генерируем HTML и PDF
        print("📄 Конвертация в PDF...")
        temp_dir = self.create_temp_directory()
        html_files = []
        
        try:
            # Генерируем HTML файлы для каждого слайда
            for i, slide in enumerate(slides):
                html_content = self.generate_slide_html_premium(slide, i + 1, len(slides), color_scheme)
                html_file = os.path.join(temp_dir, f"slide_{i+1:02d}.html")
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                html_files.append(html_file)
            
            # Конвертируем в PDF
            safe_title = "".join(c for c in presentation_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            pdf_path = self.output_dir / f"{safe_title}_{color_scheme.name}.pdf"
            self.convert_html_to_pdf(html_files, str(pdf_path))
            
            print(f"✅ Презентация создана: {pdf_path}")
            return str(pdf_path)
            
        finally:
            self.cleanup_temp_directory()

def create_final_presentations():
    """Создает финальные улучшенные презентации"""
    generator = FinalEnhancedGenerator()
    
    topics = [
        "Искусственный интеллект в российской медицине",
        "Блокчейн и криптовалюты в России", 
        "Кибербезопасность российского бизнеса",
        "Зеленая энергетика и экологические технологии",
        "Цифровая трансформация российских предприятий"
    ]
    
    created_presentations = []
    
    print("🚀 Начало создания финальных презентаций...")
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*70}")
        print(f"Создание презентации {i}/5: {topic}")
        print(f"{'='*70}")
        
        try:
            pdf_path = generator.create_final_presentation(topic, num_slides=8)
            created_presentations.append(pdf_path)
            print(f"✅ Успешно создана: {topic}")
            
            # Пауза между запросами к API
            if i < len(topics):
                print("⏳ Пауза перед следующей презентацией...")
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ Ошибка создания {topic}: {str(e)}")
    
    print(f"\n🎉 Создано {len(created_presentations)} презентаций:")
    for path in created_presentations:
        print(f"  📄 {path}")
    
    return created_presentations

if __name__ == "__main__":
    # Создаем финальные презентации
    presentations = create_final_presentations()

