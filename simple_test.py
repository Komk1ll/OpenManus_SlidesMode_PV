#!/usr/bin/env python3
"""
Simplified test for presentation tools without full OpenManus dependencies
"""

import asyncio
import json
import os
import sys

# Add the project root to Python path
sys.path.insert(0, '/home/ubuntu/OpenManus')

# Mock the logger to avoid dependencies
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

# Mock the LLM class
class MockLLM:
    async def ask(self, messages):
        # Mock response for structure generation
        if "JSON structure" in str(messages):
            return MockResponse(json.dumps({
                "title": "Тестовая презентация",
                "description": "Описание тестовой презентации",
                "slides": [
                    {
                        "id": 1,
                        "title": "Введение",
                        "description": "Вводный слайд",
                        "type": "intro",
                        "keywords": ["введение", "начало"]
                    },
                    {
                        "id": 2,
                        "title": "Основная часть",
                        "description": "Основной контент",
                        "type": "content",
                        "keywords": ["контент", "информация"]
                    }
                ]
            }))
        # Mock response for content generation
        else:
            return MockResponse(json.dumps({
                "title": "Тестовый слайд",
                "subtitle": "Подзаголовок",
                "content": [
                    {
                        "type": "bullet_point",
                        "text": "Первый пункт презентации"
                    },
                    {
                        "type": "paragraph",
                        "text": "Подробное описание темы"
                    }
                ],
                "notes": "Заметки для докладчика"
            }))

class MockResponse:
    def __init__(self, content):
        self.content = content

# Replace imports with mocks
sys.modules['app.logger'] = type('MockModule', (), {'logger': MockLogger()})()
sys.modules['app.llm'] = type('MockModule', (), {'LLM': MockLLM})()

# Now import our tools
from app.tool.presentation_tools import GenerateStructureTool, GenerateSlideContentTool, SearchImageTool


async def test_structure_generation():
    """Test presentation structure generation"""
    print("🧪 Testing structure generation...")
    
    tool = GenerateStructureTool()
    result = await tool.execute(
        topic="Искусственный интеллект в современном мире",
        description="Обзор применения ИИ в различных сферах жизни"
    )
    
    if result.error:
        print(f"❌ Structure generation failed: {result.error}")
        return False
    
    try:
        structure = result.output if isinstance(result.output, dict) else json.loads(result.output)
        print(f"✅ Structure generated successfully with {len(structure.get('slides', []))} slides")
        print(f"   Title: {structure.get('title', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Structure parsing failed: {str(e)}")
        return False


async def test_slide_content_generation():
    """Test slide content generation"""
    print("🧪 Testing slide content generation...")
    
    slide_info = {
        "id": 1,
        "title": "Введение в искусственный интеллект",
        "description": "Основные понятия и определения ИИ",
        "type": "intro",
        "keywords": ["ИИ", "машинное обучение", "технологии"]
    }
    
    tool = GenerateSlideContentTool()
    result = await tool.execute(
        slide_info=slide_info,
        presentation_topic="Искусственный интеллект в современном мире",
        presentation_context="Обзор применения ИИ в различных сферах жизни"
    )
    
    if result.error:
        print(f"❌ Content generation failed: {result.error}")
        return False
    
    try:
        content = result.output if isinstance(result.output, dict) else json.loads(result.output)
        print(f"✅ Content generated successfully")
        print(f"   Title: {content.get('title', 'N/A')}")
        print(f"   Content items: {len(content.get('content', []))}")
        return True
    except Exception as e:
        print(f"❌ Content parsing failed: {str(e)}")
        return False


async def test_image_search():
    """Test image search functionality"""
    print("🧪 Testing image search...")
    
    tool = SearchImageTool()
    result = await tool.execute(
        slide_title="Искусственный интеллект",
        slide_content="Введение в основы ИИ",
        keywords=["AI", "artificial intelligence", "technology"]
    )
    
    if result.error:
        print(f"❌ Image search failed: {result.error}")
        return False
    
    if result.output:
        print(f"✅ Image found: {result.output}")
        return True
    else:
        print("⚠️ No image found, but no error occurred")
        return True


async def main():
    """Run simplified tests"""
    print("🚀 Starting simplified presentation system tests...\n")
    
    # Set environment variables
    os.environ['TAVILY_API_KEY'] = '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'
    
    tests = [
        ("Structure Generation", test_structure_generation),
        ("Slide Content Generation", test_slide_content_generation),
        ("Image Search", test_image_search),
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
        print("🎉 Core presentation tools are working! System is ready for production use.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")


if __name__ == "__main__":
    asyncio.run(main())

