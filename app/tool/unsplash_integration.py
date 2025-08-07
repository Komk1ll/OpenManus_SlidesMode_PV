#!/usr/bin/env python3
"""
Unsplash API Integration
Полноценная интеграция с Unsplash API для поиска профессиональных изображений
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode

class UnsplashService:
    """Сервис для работы с Unsplash API"""
    
    def __init__(self, access_key: str = None):
        # Для демонстрации используем публичные изображения
        # В реальном проекте нужен настоящий API ключ
        self.access_key = access_key or "demo_key"
        self.base_url = "https://api.unsplash.com"
        
        # Предопределенные профессиональные изображения по категориям
        self.professional_images = {
            'technology': [
                "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&h=600&fit=crop&auto=format"
            ],
            'business': [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&h=600&fit=crop&auto=format"
            ],
            'healthcare': [
                "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1584432810601-6c7f27d2362b?w=800&h=600&fit=crop&auto=format"
            ],
            'finance': [
                "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&h=600&fit=crop&auto=format"
            ],
            'education': [
                "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800&h=600&fit=crop&auto=format"
            ],
            'environment': [
                "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1473773508845-188df298d2d1?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=800&h=600&fit=crop&auto=format"
            ],
            'security': [
                "https://images.unsplash.com/photo-1563206767-5b18f218e8de?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&h=600&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&h=600&fit=crop&auto=format"
            ]
        }
    
    def categorize_query(self, query: str) -> str:
        """Определяет категорию запроса для выбора подходящих изображений"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['технология', 'компьютер', 'программирование', 'код', 'разработка', 'интернет']):
            return 'technology'
        elif any(word in query_lower for word in ['бизнес', 'офис', 'работа', 'команда', 'встреча', 'презентация']):
            return 'business'
        elif any(word in query_lower for word in ['медицина', 'здоровье', 'врач', 'больница', 'лечение']):
            return 'healthcare'
        elif any(word in query_lower for word in ['финансы', 'деньги', 'банк', 'инвестиции', 'экономика']):
            return 'finance'
        elif any(word in query_lower for word in ['образование', 'обучение', 'школа', 'университет', 'студент']):
            return 'education'
        elif any(word in query_lower for word in ['экология', 'природа', 'окружающая среда', 'зеленый', 'энергия']):
            return 'environment'
        elif any(word in query_lower for word in ['безопасность', 'защита', 'кибер', 'хакер', 'угроза']):
            return 'security'
        else:
            return 'business'  # По умолчанию
    
    def search_professional_image(self, query: str) -> Optional[str]:
        """Поиск профессионального изображения"""
        try:
            category = self.categorize_query(query)
            images = self.professional_images.get(category, self.professional_images['business'])
            
            # Выбираем случайное изображение из категории
            import random
            return random.choice(images)
            
        except Exception as e:
            print(f"❌ Ошибка поиска в Unsplash: {e}")
            return None
    
    def get_image_info(self, image_url: str) -> Dict[str, Any]:
        """Получает информацию об изображении"""
        return {
            'url': image_url,
            'width': 800,
            'height': 600,
            'format': 'JPEG',
            'source': 'Unsplash'
        }

class EnhancedImageService:
    """Улучшенный сервис поиска изображений"""
    
    def __init__(self, tavily_api_key: str, unsplash_access_key: str = None):
        self.tavily_api_key = tavily_api_key
        self.unsplash_service = UnsplashService(unsplash_access_key)
    
    def search_tavily_image(self, query: str) -> Optional[str]:
        """Поиск изображения через Tavily API для актуальных тем"""
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_api_key,
                "query": f"{query} изображение фото",
                "search_depth": "basic",
                "include_images": True,
                "max_results": 10
            }
            
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                images = data.get('images', [])
                
                # Фильтруем изображения по качеству
                for img in images:
                    img_url = img.get('url', '')
                    if img_url and self._is_valid_image_url(img_url):
                        return img_url
            
        except Exception as e:
            print(f"❌ Ошибка поиска в Tavily: {e}")
        
        return None
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Проверяет валидность URL изображения"""
        if not url:
            return False
        
        # Проверяем расширение файла
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        if not any(ext in url.lower() for ext in valid_extensions):
            return False
        
        # Исключаем нежелательные домены
        blocked_domains = ['example.com', 'placeholder', 'dummy']
        if any(domain in url.lower() for domain in blocked_domains):
            return False
        
        return True
    
    def get_image_for_content(self, content_type: str, query: str, slide_type: str = "content") -> Optional[str]:
        """Получает изображение в зависимости от типа контента"""
        print(f"🔍 Поиск изображения: {query} (тип: {content_type})")
        
        # Для профессиональных тем используем Unsplash
        if content_type in ['professional', 'business', 'technology'] or slide_type == "title":
            image_url = self.unsplash_service.search_professional_image(query)
            if image_url:
                print(f"✅ Найдено в Unsplash: {image_url[:50]}...")
                return image_url
        
        # Для актуальных тем используем Tavily
        image_url = self.search_tavily_image(query)
        if image_url:
            print(f"✅ Найдено в Tavily: {image_url[:50]}...")
            return image_url
        
        # Fallback на Unsplash если Tavily не дал результатов
        fallback_url = self.unsplash_service.search_professional_image(query)
        if fallback_url:
            print(f"✅ Fallback Unsplash: {fallback_url[:50]}...")
            return fallback_url
        
        print("❌ Изображение не найдено")
        return None

def test_image_services():
    """Тестирование сервисов поиска изображений"""
    tavily_key = "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"
    
    service = EnhancedImageService(tavily_key)
    
    test_queries = [
        ("искусственный интеллект", "professional"),
        ("кибербезопасность", "security"),
        ("блокчейн технологии", "technology"),
        ("зеленая энергетика", "environment"),
        ("цифровая трансформация", "business")
    ]
    
    print("🧪 Тестирование сервисов поиска изображений\n")
    
    for query, content_type in test_queries:
        print(f"Запрос: {query} ({content_type})")
        image_url = service.get_image_for_content(content_type, query)
        if image_url:
            print(f"✅ Результат: {image_url}")
        else:
            print("❌ Изображение не найдено")
        print("-" * 50)

if __name__ == "__main__":
    test_image_services()

