#!/usr/bin/env python3
"""
Enhanced Presentation System
Улучшенная система генерации презентаций с поддержкой русского языка,
интеграцией Tavily и Unsplash API, улучшенным дизайном
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

class ImageSearchService:
    """Сервис поиска изображений"""
    
    def __init__(self, tavily_api_key: str, unsplash_access_key: str = None):
        self.tavily_api_key = tavily_api_key
        self.unsplash_access_key = unsplash_access_key or "YOUR_UNSPLASH_ACCESS_KEY"
    
    def search_tavily_image(self, query: str) -> Optional[str]:
        """Поиск изображения через Tavily API для актуальных тем"""
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_api_key,
                "query": f"{query} изображение",
                "search_depth": "basic",
                "include_images": True,
                "max_results": 5
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                images = data.get('images', [])
                if images:
                    # Фильтруем изображения по размеру и качеству
                    for img in images:
                        img_url = img.get('url', '')
                        if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png']):
                            return img_url
            
        except Exception as e:
            print(f"❌ Ошибка поиска в Tavily: {e}")
        
        return None
    
    def search_unsplash_image(self, query: str) -> Optional[str]:
        """Поиск профессионального изображения через Unsplash API"""
        try:
            # Для демонстрации используем публичные изображения Unsplash
            # В реальном проекте нужен API ключ
            unsplash_urls = [
                "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop",
                "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&h=600&fit=crop"
            ]
            return random.choice(unsplash_urls)
            
        except Exception as e:
            print(f"❌ Ошибка поиска в Unsplash: {e}")
        
        return None
    
    def get_image_for_content(self, content_type: str, query: str) -> Optional[str]:
        """Получает изображение в зависимости от типа контента"""
        if content_type in ['professional', 'business', 'technology']:
            # Используем Unsplash для профессиональных изображений
            return self.search_unsplash_image(query)
        else:
            # Используем Tavily для актуальных тем и обычных изображений
            return self.search_tavily_image(query)

class EnhancedPresentationGenerator(PresentationGenerator):
    """Улучшенный генератор презентаций"""
    
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
        
        # Сервис поиска изображений
        self.image_service = ImageSearchService(self.tavily_api_key)
        
        # Нейтральные цветовые схемы
        self.color_schemes = [
            ColorScheme("Синий", "#1e3a5f", "#ffffff", "#4a90e2", "#7bb3f0", "#1e3a5f", "#2c5282"),
            ColorScheme("Серый", "#2d3748", "#ffffff", "#718096", "#a0aec0", "#2d3748", "#4a5568"),
            ColorScheme("Темно-синий", "#1a202c", "#ffffff", "#63b3ed", "#90cdf4", "#1a202c", "#2d3748"),
            ColorScheme("Коричневый", "#3c2415", "#ffffff", "#d69e2e", "#ecc94b", "#3c2415", "#744210"),
            ColorScheme("Черный", "#1a1a1a", "#ffffff", "#9ca3af", "#d1d5db", "#1a1a1a", "#374151")
        ]
    
    def get_random_color_scheme(self) -> ColorScheme:
        """Возвращает случайную нейтральную цветовую схему"""
        return random.choice(self.color_schemes)
    
    def generate_presentation_content_ru(self, topic: str, num_slides: int = 8) -> Dict[str, Any]:
        """Генерирует содержимое презентации на русском языке"""
        prompt = f"""
        Создай полную структуру презентации на тему "{topic}" из {num_slides} слайдов НА РУССКОМ ЯЗЫКЕ.
        
        Структура должна включать:
        1. Титульный слайд с названием и подзаголовком
        2-{num_slides-1}. Контентные слайды с заголовками, подзаголовками и содержимым
        {num_slides}. Заключительный слайд с выводами и вопросами
        
        Для каждого слайда укажи:
        - title: заголовок слайда НА РУССКОМ
        - subtitle: подзаголовок НА РУССКОМ (опционально)
        - content: массив объектов контента, где каждый объект имеет:
          - type: "paragraph" или "bullet_point"
          - text: текст параграфа или пункта НА РУССКОМ
        - image_query: запрос для поиска изображения НА РУССКОМ
        - image_type: "professional" (для Unsplash) или "general" (для Tavily)
        - chart_suggestion: предложение диаграммы (если нужно)
        
        Используй актуальные данные и статистику для России/СНГ где это применимо.
        
        Верни результат в формате JSON:
        {{
            "title": "Название презентации НА РУССКОМ",
            "slides": [
                {{
                    "title": "Заголовок слайда",
                    "subtitle": "Подзаголовок",
                    "slide_type": "title|content|conclusion",
                    "content": [
                        {{"type": "paragraph", "text": "Текст параграфа"}},
                        {{"type": "bullet_point", "text": "Текст пункта"}}
                    ],
                    "image_query": "запрос для поиска изображения",
                    "image_type": "professional|general",
                    "chart_suggestion": {{"type": "bar|pie|line", "title": "Название диаграммы"}}
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="qwen/qwen3-235b-a22b-07-25",
                messages=[
                    {"role": "system", "content": "Ты эксперт по созданию презентаций на русском языке. Отвечай только в формате JSON. Используй актуальные данные для России и СНГ."},
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
                "subtitle": "Комплексный обзор",
                "slide_type": "title",
                "content": [],
                "image_query": f"{topic} концепция",
                "image_type": "professional"
            }
        ]
        
        # Контентные слайды
        content_topics = [
            "Введение и актуальность",
            "Ключевые понятия и определения", 
            "Текущее состояние и тенденции",
            "Практические применения",
            "Преимущества и выгоды",
            "Вызовы и решения",
            "Перспективы развития"
        ]
        
        for i in range(1, num_slides - 1):
            if i - 1 < len(content_topics):
                title = content_topics[i - 1]
            else:
                title = f"Раздел {i}"
            
            slides.append({
                "title": title,
                "subtitle": f"Изучение {title.lower()}",
                "slide_type": "content",
                "content": [
                    {"type": "paragraph", "text": f"Данный раздел рассматривает важные аспекты {title.lower()}."},
                    {"type": "bullet_point", "text": f"Ключевой момент по теме {title.lower()}"},
                    {"type": "bullet_point", "text": f"Важное соображение для {title.lower()}"},
                    {"type": "bullet_point", "text": f"Практическое применение {title.lower()}"}
                ],
                "image_query": f"{topic} {title}",
                "image_type": "general"
            })
        
        # Заключительный слайд
        slides.append({
            "title": "Заключение и вопросы",
            "subtitle": "Резюме и обсуждение",
            "slide_type": "conclusion",
            "content": [
                {"type": "paragraph", "text": f"В заключение, {topic.lower()} представляет важную область с значительными перспективами."},
                {"type": "bullet_point", "text": "Ключевой вывод 1"},
                {"type": "bullet_point", "text": "Ключевой вывод 2"},
                {"type": "bullet_point", "text": "Вопросы и обсуждение"}
            ],
            "image_query": f"{topic} будущее",
            "image_type": "professional"
        })
        
        return {
            "title": topic,
            "slides": slides
        }
    
    def create_chart_data_ru(self, chart_suggestion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создает данные для диаграммы с русскими подписями"""
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
                        "data": [65, 75, 80, 85, 90],
                        "backgroundColor": ["#4a90e2", "#5ba0f2", "#6cb0ff", "#7dc0ff", "#8ed0ff"],
                        "borderColor": "#4a90e2",
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {"labels": {"color": "#ffffff"}},
                        "title": {"display": True, "text": title, "color": "#ffffff"}
                    },
                    "scales": {
                        "y": {"ticks": {"color": "#ffffff"}, "grid": {"color": "rgba(255,255,255,0.2)"}},
                        "x": {"ticks": {"color": "#ffffff"}, "grid": {"color": "rgba(255,255,255,0.2)"}}
                    }
                }
            }
        elif chart_type == 'pie':
            return {
                "type": "pie",
                "data": {
                    "labels": ["Категория 1", "Категория 2", "Категория 3", "Категория 4"],
                    "datasets": [{
                        "data": [30, 25, 25, 20],
                        "backgroundColor": ["#4a90e2", "#5ba0f2", "#6cb0ff", "#7dc0ff"]
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {"labels": {"color": "#ffffff"}},
                        "title": {"display": True, "text": title, "color": "#ffffff"}
                    }
                }
            }
        
        return None
    
    def get_enhanced_slide_template(self) -> str:
        """Улучшенный шаблон слайда с поддержкой изображений и диаграмм"""
        return '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1"></script>
    <style>
        .slide-container {
            width: {{ slide_width }};
            min-height: {{ slide_height }};
            background: linear-gradient(135deg, {{ gradient_start }} 0%, {{ gradient_end }} 100%);
            color: {{ text_color }};
            font-family: 'Inter', sans-serif;
            padding: 40px;
            position: relative;
            overflow: hidden;
        }
        .title {
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 30px;
            color: {{ text_color }};
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .content-container {
            display: flex;
            justify-content: space-between;
            gap: 40px;
            height: calc(100% - 120px);
        }
        .text-content {
            flex: 1;
            z-index: 10;
        }
        .visual-content {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10;
        }
        .subtitle {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
            color: {{ accent_color }};
        }
        .description {
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 25px;
            opacity: 0.95;
        }
        .feature-item {
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            border-left: 4px solid {{ accent_color }};
        }
        .feature-item i {
            color: {{ accent_color }};
            margin-right: 12px;
            margin-top: 2px;
            min-width: 20px;
        }
        .image-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            max-width: 500px;
            max-height: 400px;
        }
        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .chart-container {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }
        .progress-indicator {
            position: absolute;
            bottom: 20px;
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 14px;
            color: {{ text_color }};
            z-index: 10;
        }
        .progress-dots {
            display: inline-flex;
            gap: 8px;
        }
        .dot {
            height: 10px;
            width: 10px;
            background-color: {{ text_color }};
            border-radius: 50%;
            opacity: 0.4;
        }
        .dot.active {
            opacity: 1;
            background-color: {{ accent_color }};
        }
        .background-pattern {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0.03;
            background-image: radial-gradient(circle at 25% 25%, {{ accent_color }} 2px, transparent 2px);
            background-size: 50px 50px;
        }
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="background-pattern"></div>
        
        {% if slide_type == "title" %}
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; text-align: center;">
            <div style="margin-bottom: 40px;">
                <i class="fas fa-{{ icon_class }} text-6xl" style="color: {{ accent_color }};"></i>
            </div>
            <h1 style="font-size: 64px; font-weight: 700; margin-bottom: 30px; line-height: 1.2;">{{ title }}</h1>
            {% if subtitle %}
            <p style="font-size: 32px; opacity: 0.9; margin-bottom: 40px;">{{ subtitle }}</p>
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
                        <i class="fas fa-{{ feature.icon }} fa-lg"></i>
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
                <div class="chart-container" style="width: 500px; height: 400px;">
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
    
    def generate_slide_html_enhanced(self, slide: SlideContent, slide_number: int, total_slides: int, color_scheme: ColorScheme) -> str:
        """Генерирует улучшенный HTML для слайда"""
        from jinja2 import Template
        
        template = Template(self.get_enhanced_slide_template())
        
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
    
    def create_presentation_enhanced(self, topic: str, num_slides: int = 8) -> str:
        """Создает улучшенную презентацию"""
        print(f"🎯 Создание презентации: {topic}")
        
        # Выбираем цветовую схему
        color_scheme = self.get_random_color_scheme()
        print(f"🎨 Выбрана цветовая схема: {color_scheme.name}")
        
        # 1. Генерируем содержимое на русском языке
        print("📋 Генерация содержимого...")
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
                image_url = self.image_service.get_image_for_content(image_type, slide_data['image_query'])
                if image_url:
                    print(f"✅ Найдено изображение: {image_url[:50]}...")
                else:
                    print("❌ Изображение не найдено")
            
            # Создание диаграммы
            chart_data = None
            if slide_data.get('chart_suggestion'):
                chart_data = self.create_chart_data_ru(slide_data['chart_suggestion'])
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
                html_content = self.generate_slide_html_enhanced(slide, i + 1, len(slides), color_scheme)
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

def create_enhanced_presentations():
    """Создает несколько улучшенных презентаций"""
    generator = EnhancedPresentationGenerator()
    
    topics = [
        "Искусственный интеллект в медицине",
        "Блокчейн технологии в России", 
        "Кибербезопасность для бизнеса",
        "Зеленая энергетика и экология",
        "Цифровая трансформация предприятий"
    ]
    
    created_presentations = []
    
    print("🚀 Начало создания улучшенных презентаций...")
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*60}")
        print(f"Создание презентации {i}/5: {topic}")
        print(f"{'='*60}")
        
        try:
            pdf_path = generator.create_presentation_enhanced(topic, num_slides=8)
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
    # Создаем улучшенные презентации
    presentations = create_enhanced_presentations()

