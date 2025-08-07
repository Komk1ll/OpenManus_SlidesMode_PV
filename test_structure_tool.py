#!/usr/bin/env python3
"""
Test script for enhanced GenerateStructureTool with language detection
"""

import asyncio
import sys
import os
import json
import re

# Add the project root to Python path
sys.path.insert(0, '/home/ubuntu/openmanus_project')

# Mock the dependencies to avoid import issues
class MockLLM:
    async def ask(self, messages):
        # Mock response for Russian topic
        if "Искусственный интеллект" in messages[0]["content"]:
            return MockResponse(json.dumps({
                "title": "Искусственный интеллект в современном мире",
                "description": "Обзор применения ИИ в различных сферах жизни",
                "slides": [
                    {
                        "id": 1,
                        "title": "Введение в ИИ",
                        "description": "Основные понятия и определения",
                        "type": "intro",
                        "keywords": ["ИИ", "машинное обучение"],
                        "image_type": "professional",
                        "image_query": "artificial intelligence concept"
                    },
                    {
                        "id": 2,
                        "title": "Применение ИИ",
                        "description": "Сферы использования ИИ",
                        "type": "content",
                        "keywords": ["применение", "технологии"],
                        "image_type": "general",
                        "image_query": "AI applications"
                    }
                ]
            }, ensure_ascii=False))
        else:
            # Mock response for English topic
            return MockResponse(json.dumps({
                "title": "Artificial Intelligence Overview",
                "description": "Introduction to AI concepts and applications",
                "slides": [
                    {
                        "id": 1,
                        "title": "Introduction to AI",
                        "description": "Basic concepts and definitions",
                        "type": "intro",
                        "keywords": ["AI", "machine learning"],
                        "image_type": "professional",
                        "image_query": "artificial intelligence concept"
                    }
                ]
            }))

class MockResponse:
    def __init__(self, content):
        self.content = content

class MockLogger:
    def error(self, msg):
        print(f"ERROR: {msg}")

class MockToolResult:
    def __init__(self, output=None, error=None):
        self.output = output
        self.error = error

# Mock the imports
sys.modules['app.llm'] = type('MockModule', (), {'LLM': MockLLM})()
sys.modules['app.logger'] = type('MockModule', (), {'logger': MockLogger()})()
sys.modules['app.tool.base'] = type('MockModule', (), {
    'BaseTool': object,
    'ToolResult': MockToolResult
})()

# Now import the tool
from app.tool.presentation_tools import GenerateStructureTool


async def test_language_detection():
    """Test language detection functionality"""
    print("🧪 Testing language detection...")
    
    tool = GenerateStructureTool()
    
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


async def test_russian_structure_generation():
    """Test structure generation with Russian topic"""
    print("🧪 Testing Russian structure generation...")
    
    tool = GenerateStructureTool()
    result = await tool.execute(
        topic="Искусственный интеллект в современном мире",
        description="Обзор применения ИИ в различных сферах жизни"
    )
    
    if result.error:
        print(f"❌ Russian structure generation failed: {result.error}")
        return False
    
    try:
        structure = result.output
        print(f"✅ Russian structure generated successfully")
        print(f"   Title: {structure.get('title', 'N/A')}")
        print(f"   Slides: {len(structure.get('slides', []))}")
        
        # Validate required fields
        assert "title" in structure, "Missing 'title' field"
        assert "slides" in structure, "Missing 'slides' field"
        assert isinstance(structure["slides"], list), "'slides' should be a list"
        
        # Check if slides have new fields
        if structure["slides"]:
            slide = structure["slides"][0]
            assert "image_type" in slide, "Missing 'image_type' field in slide"
            assert "image_query" in slide, "Missing 'image_query' field in slide"
            print(f"   First slide image_type: {slide.get('image_type')}")
            print(f"   First slide image_query: {slide.get('image_query')}")
        
        return True
    except Exception as e:
        print(f"❌ Russian structure validation failed: {str(e)}")
        return False


async def test_english_structure_generation():
    """Test structure generation with English topic"""
    print("🧪 Testing English structure generation...")
    
    tool = GenerateStructureTool()
    result = await tool.execute(
        topic="Artificial Intelligence Overview",
        description="Introduction to AI concepts and applications"
    )
    
    if result.error:
        print(f"❌ English structure generation failed: {result.error}")
        return False
    
    try:
        structure = result.output
        print(f"✅ English structure generated successfully")
        print(f"   Title: {structure.get('title', 'N/A')}")
        print(f"   Slides: {len(structure.get('slides', []))}")
        
        # Validate required fields
        assert "title" in structure, "Missing 'title' field"
        assert "slides" in structure, "Missing 'slides' field"
        
        return True
    except Exception as e:
        print(f"❌ English structure validation failed: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting GenerateStructureTool tests...\n")
    
    tests = [
        ("Language Detection", test_language_detection),
        ("Russian Structure Generation", test_russian_structure_generation),
        ("English Structure Generation", test_english_structure_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            success = await test_func()
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
        print("🎉 All GenerateStructureTool tests passed!")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")


if __name__ == "__main__":
    asyncio.run(main())

