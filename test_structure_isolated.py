#!/usr/bin/env python3
"""
Isolated test for GenerateStructureTool language detection and prompt generation
"""

import re
import json


class GenerateStructureToolTest:
    """Isolated test version of GenerateStructureTool"""
    
    def _detect_language(self, text: str) -> str:
        """Detect if text contains Cyrillic characters (Russian) or is English"""
        # Check for Cyrillic characters
        cyrillic_pattern = re.compile(r'[а-яё]', re.IGNORECASE)
        if cyrillic_pattern.search(text):
            return "russian"
        return "english"

    def _get_language_specific_prompt(self, topic: str, description: str, language: str) -> str:
        """Generate language-specific prompt for structure generation"""
        
        if language == "russian":
            return f"""Создайте комплексную структуру презентации на тему: "{topic}"
{f"Дополнительный контекст: {description}" if description else ""}

Сгенерируйте JSON структуру в следующем формате:
{{
    "title": "Название презентации",
    "description": "Краткое описание презентации",
    "slides": [
        {{
            "id": 1,
            "title": "Заголовок слайда",
            "description": "Что освещает этот слайд",
            "type": "intro|content|conclusion",
            "keywords": ["ключевое_слово1", "ключевое_слово2"],
            "image_type": "professional|general|technical",
            "image_query": "запрос для поиска изображения"
        }}
    ]
}}

Требования:
- Создайте 8-12 слайдов всего
- Включите введение, основные содержательные слайды и заключение
- Каждый слайд должен иметь четкую цель
- Включите актуальные аспекты и конкретные разделы темы
- Ключевые слова должны помочь с поиском изображений
- Обеспечьте логический поток и прогрессию
- Добавьте image_type: "professional" для введения/заключения, "general" для общих тем, "technical" для технических слайдов
- Добавьте image_query для более точного поиска изображений

Верните только JSON структуру, без дополнительного текста."""
        else:
            return f"""Create a comprehensive presentation structure for the topic: "{topic}"
{f"Additional context: {description}" if description else ""}

Generate a JSON structure with the following format:
{{
    "title": "Presentation Title",
    "description": "Brief description of the presentation",
    "slides": [
        {{
            "id": 1,
            "title": "Slide Title",
            "description": "What this slide covers",
            "type": "intro|content|conclusion",
            "keywords": ["keyword1", "keyword2"],
            "image_type": "professional|general|technical",
            "image_query": "image search query"
        }}
    ]
}}

Requirements:
- Create 8-12 slides total
- Include introduction, main content slides, and conclusion
- Each slide should have a clear purpose
- Include current aspects and specific sections of the topic
- Keywords should help with image search
- Ensure logical flow and progression
- Add image_type: "professional" for intro/conclusion, "general" for general topics, "technical" for technical slides
- Add image_query for more precise image search

Return only the JSON structure, no additional text."""


def test_language_detection():
    """Test language detection functionality"""
    print("🧪 Testing language detection...")
    
    tool = GenerateStructureToolTest()
    
    # Test Russian detection
    russian_text = "Искусственный интеллект в современном мире"
    detected_lang = tool._detect_language(russian_text)
    assert detected_lang == "russian", f"Expected 'russian', got '{detected_lang}'"
    print("✅ Russian language detection works")
    
    # Test English detection
    english_text = "Artificial Intelligence in Modern World"
    detected_lang = tool._detect_language(english_text)
    assert detected_lang == "english", f"Expected 'english', got '{detected_lang}'"
    print("✅ English language detection works")
    
    # Test mixed text (should detect Russian if any Cyrillic present)
    mixed_text = "AI and Искусственный интеллект"
    detected_lang = tool._detect_language(mixed_text)
    assert detected_lang == "russian", f"Expected 'russian' for mixed text, got '{detected_lang}'"
    print("✅ Mixed text detection works (prioritizes Russian)")
    
    return True


def test_prompt_generation():
    """Test prompt generation for different languages"""
    print("🧪 Testing prompt generation...")
    
    tool = GenerateStructureToolTest()
    
    # Test Russian prompt
    russian_topic = "Искусственный интеллект"
    russian_desc = "Обзор применения ИИ"
    russian_prompt = tool._get_language_specific_prompt(russian_topic, russian_desc, "russian")
    
    assert "Создайте комплексную структуру" in russian_prompt, "Russian prompt should be in Russian"
    assert russian_topic in russian_prompt, "Topic should be in prompt"
    assert russian_desc in russian_prompt, "Description should be in prompt"
    assert "image_type" in russian_prompt, "Prompt should include image_type field"
    assert "image_query" in russian_prompt, "Prompt should include image_query field"
    print("✅ Russian prompt generation works")
    
    # Test English prompt
    english_topic = "Artificial Intelligence"
    english_desc = "Overview of AI applications"
    english_prompt = tool._get_language_specific_prompt(english_topic, english_desc, "english")
    
    assert "Create a comprehensive presentation" in english_prompt, "English prompt should be in English"
    assert english_topic in english_prompt, "Topic should be in prompt"
    assert english_desc in english_prompt, "Description should be in prompt"
    assert "image_type" in english_prompt, "Prompt should include image_type field"
    assert "image_query" in english_prompt, "Prompt should include image_query field"
    print("✅ English prompt generation works")
    
    return True


def test_json_structure_requirements():
    """Test that prompts include all required JSON structure elements"""
    print("🧪 Testing JSON structure requirements...")
    
    tool = GenerateStructureToolTest()
    
    # Test Russian prompt structure
    russian_prompt = tool._get_language_specific_prompt("Тест", "", "russian")
    required_fields = ["title", "description", "slides", "id", "keywords", "image_type", "image_query"]
    
    for field in required_fields:
        assert field in russian_prompt, f"Russian prompt missing required field: {field}"
    
    print("✅ Russian prompt includes all required JSON fields")
    
    # Test English prompt structure
    english_prompt = tool._get_language_specific_prompt("Test", "", "english")
    
    for field in required_fields:
        assert field in english_prompt, f"English prompt missing required field: {field}"
    
    print("✅ English prompt includes all required JSON fields")
    
    return True


def main():
    """Run all tests"""
    print("🚀 Starting isolated GenerateStructureTool tests...\n")
    
    tests = [
        ("Language Detection", test_language_detection),
        ("Prompt Generation", test_prompt_generation),
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
        print("🎉 All GenerateStructureTool logic tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

