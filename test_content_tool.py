#!/usr/bin/env python3
"""
Test script for enhanced GenerateSlideContentTool
"""

import json
import re


class GenerateSlideContentToolTest:
    """Isolated test version of GenerateSlideContentTool"""
    
    def _detect_language(self, text: str) -> str:
        """Detect if text contains Cyrillic characters (Russian) or is English"""
        cyrillic_pattern = re.compile(r'[а-яё]', re.IGNORECASE)
        if cyrillic_pattern.search(text):
            return "russian"
        return "english"

    def _get_enhanced_prompt(self, slide_info: dict, presentation_topic: str, presentation_context: str, language: str) -> str:
        """Generate enhanced language-specific prompt for slide content generation"""
        
        slide_title = slide_info.get('title', '')
        slide_description = slide_info.get('description', '')
        slide_type = slide_info.get('type', 'content')
        keywords = slide_info.get('keywords', [])
        
        if language == "russian":
            return f"""Сгенерируйте детальный контент для слайда презентации.

Тема презентации: {presentation_topic}
{f"Контекст: {presentation_context}" if presentation_context else ""}

Информация о слайде:
- Заголовок: {slide_title}
- Описание: {slide_description}
- Тип: {slide_type}
- Ключевые слова: {', '.join(keywords) if keywords else 'не указаны'}

Сгенерируйте контент в следующем JSON формате:
{{
    "title": "Заголовок слайда",
    "subtitle": "Дополнительный подзаголовок (опционально)",
    "content": [
        {{
            "type": "bullet_point",
            "text": "Основной пункт с детальным объяснением и конкретными фактами"
        }},
        {{
            "type": "paragraph", 
            "text": "Детальный параграф с конкретными данными, статистикой или примерами"
        }},
        {{
            "type": "quote",
            "text": "Релевантная цитата от эксперта или из авторитетного источника",
            "author": "Автор цитаты"
        }},
        {{
            "type": "code",
            "language": "python",
            "text": "# Пример кода, если релевантно к теме\\nprint('Пример')"
        }}
    ],
    "notes": "Заметки докладчика с дополнительным контекстом и конкретными фактами"
}}

Требования:
- Создайте всеобъемлющий, информативный контент
- Используйте подходящие типы контента (bullet_point, paragraph, quote, code)
- Включите 4-6 основных пунктов на слайд
- Обязательно включите конкретные факты, данные, статистику
- Добавьте релевантные цитаты от экспертов, если применимо
- Включите примеры кода для технических тем
- Сделайте контент увлекательным и профессиональным
- Добавьте заметки докладчика с дополнительным контекстом

Верните только JSON структуру, без дополнительного текста."""
        else:
            return f"""Generate detailed content for a presentation slide.

Presentation Topic: {presentation_topic}
{f"Context: {presentation_context}" if presentation_context else ""}

Slide Information:
- Title: {slide_title}
- Description: {slide_description}
- Type: {slide_type}
- Keywords: {', '.join(keywords) if keywords else 'not specified'}

Generate content in the following JSON format:
{{
    "title": "Slide Title",
    "subtitle": "Optional subtitle",
    "content": [
        {{
            "type": "bullet_point",
            "text": "Main point with detailed explanation and specific facts"
        }},
        {{
            "type": "paragraph", 
            "text": "Detailed paragraph with concrete data, statistics, or examples"
        }},
        {{
            "type": "quote",
            "text": "Relevant quote from expert or authoritative source",
            "author": "Quote author"
        }},
        {{
            "type": "code",
            "language": "python",
            "text": "# Code example if relevant to topic\\nprint('Example')"
        }}
    ],
    "notes": "Speaker notes with additional context and specific facts"
}}

Requirements:
- Create comprehensive, informative content
- Use appropriate content types (bullet_point, paragraph, quote, code)
- Include 4-6 main points per slide
- Must include specific facts, data, statistics
- Add relevant expert quotes when applicable
- Include code examples for technical topics
- Make content engaging and professional
- Add speaker notes with additional context

Return only the JSON structure, no additional text."""


def test_language_detection():
    """Test language detection functionality"""
    print("🧪 Testing language detection...")
    
    tool = GenerateSlideContentToolTest()
    
    # Test Russian detection
    russian_slide = {"title": "Введение в ИИ", "description": "Основы искусственного интеллекта"}
    combined_text = f"{russian_slide['title']} Искусственный интеллект"
    detected_lang = tool._detect_language(combined_text)
    assert detected_lang == "russian", f"Expected 'russian', got '{detected_lang}'"
    print("✅ Russian language detection works")
    
    # Test English detection
    english_slide = {"title": "Introduction to AI", "description": "Basics of artificial intelligence"}
    combined_text = f"{english_slide['title']} Artificial Intelligence"
    detected_lang = tool._detect_language(combined_text)
    assert detected_lang == "english", f"Expected 'english', got '{detected_lang}'"
    print("✅ English language detection works")
    
    return True


def test_enhanced_prompt_features():
    """Test enhanced prompt features"""
    print("🧪 Testing enhanced prompt features...")
    
    tool = GenerateSlideContentToolTest()
    
    # Test Russian prompt with all features
    russian_slide = {
        "title": "Машинное обучение",
        "description": "Алгоритмы и методы",
        "type": "content",
        "keywords": ["ML", "алгоритмы", "данные"]
    }
    
    russian_prompt = tool._get_enhanced_prompt(
        russian_slide, 
        "Искусственный интеллект", 
        "Обзор технологий ИИ", 
        "russian"
    )
    
    # Check for enhanced features in Russian prompt
    assert "quote" in russian_prompt, "Russian prompt should include quote type"
    assert "code" in russian_prompt, "Russian prompt should include code type"
    assert "конкретные факты" in russian_prompt, "Russian prompt should require specific facts"
    assert "статистику" in russian_prompt, "Russian prompt should mention statistics"
    assert "4-6 основных пунктов" in russian_prompt, "Russian prompt should specify 4-6 points"
    assert "author" in russian_prompt, "Russian prompt should include author field for quotes"
    print("✅ Russian enhanced prompt includes all required features")
    
    # Test English prompt with all features
    english_slide = {
        "title": "Machine Learning",
        "description": "Algorithms and methods",
        "type": "content",
        "keywords": ["ML", "algorithms", "data"]
    }
    
    english_prompt = tool._get_enhanced_prompt(
        english_slide, 
        "Artificial Intelligence", 
        "Overview of AI technologies", 
        "english"
    )
    
    # Check for enhanced features in English prompt
    assert "quote" in english_prompt, "English prompt should include quote type"
    assert "code" in english_prompt, "English prompt should include code type"
    assert "specific facts" in english_prompt, "English prompt should require specific facts"
    assert "statistics" in english_prompt, "English prompt should mention statistics"
    assert "4-6 main points" in english_prompt, "English prompt should specify 4-6 points"
    assert "author" in english_prompt, "English prompt should include author field for quotes"
    print("✅ English enhanced prompt includes all required features")
    
    return True


def test_content_types_validation():
    """Test that prompts include all required content types"""
    print("🧪 Testing content types validation...")
    
    tool = GenerateSlideContentToolTest()
    
    slide_info = {
        "title": "Test Slide",
        "description": "Test description",
        "type": "content",
        "keywords": ["test"]
    }
    
    # Test both languages include all content types
    for language in ["russian", "english"]:
        prompt = tool._get_enhanced_prompt(slide_info, "Test Topic", "Test Context", language)
        
        required_types = ["bullet_point", "paragraph", "quote", "code"]
        for content_type in required_types:
            assert content_type in prompt, f"{language} prompt missing content type: {content_type}"
        
        # Check for required fields in JSON structure
        required_fields = ["title", "subtitle", "content", "notes"]
        for field in required_fields:
            assert field in prompt, f"{language} prompt missing JSON field: {field}"
        
        print(f"✅ {language.capitalize()} prompt includes all content types and fields")
    
    return True


def test_json_structure_requirements():
    """Test JSON structure requirements in prompts"""
    print("🧪 Testing JSON structure requirements...")
    
    tool = GenerateSlideContentToolTest()
    
    slide_info = {
        "title": "Technical Slide",
        "description": "Technical content",
        "type": "content",
        "keywords": ["programming", "code"]
    }
    
    # Test that prompts specify proper JSON structure
    for language in ["russian", "english"]:
        prompt = tool._get_enhanced_prompt(slide_info, "Programming", "Code examples", language)
        
        # Check for JSON structure elements
        assert '"type":' in prompt, f"{language} prompt should show JSON type field"
        assert '"text":' in prompt, f"{language} prompt should show JSON text field"
        assert '"language":' in prompt, f"{language} prompt should show JSON language field for code"
        assert '"author":' in prompt, f"{language} prompt should show JSON author field for quotes"
        
        # Check for specific requirements
        if language == "russian":
            assert "JSON структуру" in prompt, "Russian prompt should mention JSON structure"
            assert "без дополнительного текста" in prompt, "Russian prompt should specify JSON only"
        else:
            assert "JSON structure" in prompt, "English prompt should mention JSON structure"
            assert "no additional text" in prompt, "English prompt should specify JSON only"
        
        print(f"✅ {language.capitalize()} prompt has proper JSON structure requirements")
    
    return True


def main():
    """Run all tests"""
    print("🚀 Starting enhanced GenerateSlideContentTool tests...\n")
    
    tests = [
        ("Language Detection", test_language_detection),
        ("Enhanced Prompt Features", test_enhanced_prompt_features),
        ("Content Types Validation", test_content_types_validation),
        ("JSON Structure Requirements", test_json_structure_requirements),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All GenerateSlideContentTool tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

