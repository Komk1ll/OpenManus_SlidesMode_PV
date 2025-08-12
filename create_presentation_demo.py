#!/usr/bin/env python3
"""
Demo script for creating presentations using OpenManus presentation tools
"""

import os
import sys
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockLLM:
    """Mock LLM for testing without API calls"""
    
    async def chat_completion(self, messages, **kwargs):
        """Mock chat completion that returns structured responses"""
        
        # Extract the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Mock response based on content
        if "структуру презентации" in user_message or "presentation structure" in user_message:
            # Mock structure generation
            if "искусственный интеллект" in user_message.lower():
                mock_response = {
                    "title": "Искусственный интеллект в образовании: возможности и вызовы",
                    "description": "Комплексный обзор применения ИИ в образовательной сфере",
                    "slides": [
                        {
                            "title": "Введение в ИИ в образовании",
                            "subtitle": "Определения и основные концепции",
                            "description": "Что такое искусственный интеллект и как он применяется в образовании",
                            "type": "title",
                            "keywords": ["искусственный интеллект", "образование", "технологии"],
                            "image_type": "technology"
                        },
                        {
                            "title": "Современные применения ИИ",
                            "subtitle": "Персонализация и адаптивное обучение",
                            "description": "Как ИИ помогает создавать персонализированные образовательные программы",
                            "type": "content",
                            "keywords": ["персонализация", "адаптивное обучение", "алгоритмы"],
                            "image_type": "education"
                        },
                        {
                            "title": "Вызовы и ограничения",
                            "subtitle": "Этические и технические проблемы",
                            "description": "Основные проблемы внедрения ИИ в образование",
                            "type": "content",
                            "keywords": ["этика", "приватность", "ограничения"],
                            "image_type": "challenge"
                        },
                        {
                            "title": "Будущее ИИ в образовании",
                            "subtitle": "Перспективы и рекомендации",
                            "description": "Куда движется развитие ИИ в образовательной сфере",
                            "type": "conclusion",
                            "keywords": ["будущее", "перспективы", "рекомендации"],
                            "image_type": "future"
                        }
                    ]
                }
            elif "блокчейн" in user_message.lower():
                mock_response = {
                    "title": "Блокчейн технологии: принципы работы и применение",
                    "description": "Подробное изучение технологии блокчейн и её практических применений",
                    "slides": [
                        {
                            "title": "Что такое блокчейн?",
                            "subtitle": "Основные принципы и концепции",
                            "description": "Введение в технологию распределённого реестра",
                            "type": "title",
                            "keywords": ["блокчейн", "криптография", "децентрализация"],
                            "image_type": "technology"
                        },
                        {
                            "title": "Как работает блокчейн",
                            "subtitle": "Техническая архитектура",
                            "description": "Детальное объяснение механизмов работы блокчейна",
                            "type": "content",
                            "keywords": ["хеширование", "консенсус", "майнинг"],
                            "image_type": "technical"
                        },
                        {
                            "title": "Применения блокчейна",
                            "subtitle": "Реальные случаи использования",
                            "description": "Где и как используется блокчейн сегодня",
                            "type": "content",
                            "keywords": ["криптовалюты", "смарт-контракты", "DeFi"],
                            "image_type": "business"
                        },
                        {
                            "title": "Перспективы развития",
                            "subtitle": "Будущее блокчейн технологий",
                            "description": "Тренды и направления развития блокчейна",
                            "type": "conclusion",
                            "keywords": ["Web3", "NFT", "метавселенная"],
                            "image_type": "future"
                        }
                    ]
                }
            else:
                mock_response = {
                    "title": "Демонстрационная презентация",
                    "description": "Пример структуры презентации",
                    "slides": [
                        {
                            "title": "Введение",
                            "subtitle": "Начало презентации",
                            "description": "Вводная информация",
                            "type": "title",
                            "keywords": ["введение"],
                            "image_type": "general"
                        }
                    ]
                }
            
            return type('MockResponse', (), {
                'choices': [type('Choice', (), {
                    'message': type('Message', (), {
                        'content': json.dumps(mock_response, ensure_ascii=False)
                    })()
                })()]
            })()
        
        elif "содержание слайда" in user_message or "slide content" in user_message:
            # Mock content generation
            mock_content = {
                "title": "Сгенерированный заголовок",
                "content": [
                    "• Первый важный пункт с подробным объяснением",
                    "• Второй ключевой момент для понимания темы",
                    "• Третий аспект, который необходимо рассмотреть",
                    "• Четвёртый элемент для полноты картины"
                ],
                "notes": "Дополнительные заметки для докладчика по данному слайду"
            }
            
            return type('MockResponse', (), {
                'choices': [type('Choice', (), {
                    'message': type('Message', (), {
                        'content': json.dumps(mock_content, ensure_ascii=False)
                    })()
                })()]
            })()
        
        # Default response
        return type('MockResponse', (), {
            'choices': [type('Choice', (), {
                'message': type('Message', (), {
                    'content': '{"result": "mock response"}'
                })()
            })()]
        })()

async def create_presentation_demo(topic: str, output_dir: str = "./presentations"):
    """Create a demo presentation"""
    
    logger.info(f"Starting presentation creation for topic: {topic}")
    
    try:
        # Import tools
        from app.tool.presentation_tools import GenerateStructureTool, GenerateSlideContentTool
        from app.tool.base import ToolResult
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Mock LLM for testing
        mock_llm = MockLLM()
        
        # Step 1: Generate structure
        logger.info("Step 1: Generating presentation structure...")
        structure_tool = GenerateStructureTool()
        
        # Patch the LLM in the tool
        structure_tool.llm = mock_llm
        
        structure_result = await structure_tool.execute(topic=topic)
        
        if structure_result.error:
            logger.error(f"Structure generation failed: {structure_result.error}")
            return None
        
        structure = structure_result.output
        logger.info(f"✅ Generated structure with {len(structure.get('slides', []))} slides")
        
        # Step 2: Generate content for each slide
        logger.info("Step 2: Generating slide content...")
        content_tool = GenerateSlideContentTool()
        content_tool.llm = mock_llm
        
        slides_with_content = []
        
        for i, slide in enumerate(structure.get('slides', [])):
            logger.info(f"Generating content for slide {i+1}: {slide.get('title', 'Untitled')}")
            
            content_result = await content_tool.execute(
                slide_title=slide.get('title', ''),
                slide_description=slide.get('description', ''),
                slide_type=slide.get('type', 'content'),
                presentation_topic=topic
            )
            
            if content_result.error:
                logger.warning(f"Content generation failed for slide {i+1}: {content_result.error}")
                slide_content = {
                    "title": slide.get('title', 'Untitled'),
                    "content": ["Содержание не сгенерировано"],
                    "notes": "Заметки недоступны"
                }
            else:
                slide_content = content_result.output
            
            # Combine structure and content
            full_slide = {**slide, **slide_content}
            slides_with_content.append(full_slide)
        
        # Step 3: Create final presentation
        final_presentation = {
            "title": structure.get('title', 'Untitled Presentation'),
            "description": structure.get('description', ''),
            "created_at": datetime.now().isoformat(),
            "topic": topic,
            "slides": slides_with_content,
            "metadata": {
                "total_slides": len(slides_with_content),
                "generation_method": "OpenManus AI Agent",
                "language": "russian" if any(ord(c) > 127 for c in topic) else "english"
            }
        }
        
        # Step 4: Save presentation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"presentation_{safe_topic.replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(final_presentation, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Presentation saved to: {filepath}")
        
        # Generate HTML version
        html_content = generate_html_presentation(final_presentation)
        html_filepath = filepath.replace('.json', '.html')
        
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ HTML presentation saved to: {html_filepath}")
        
        return {
            "json_file": filepath,
            "html_file": html_filepath,
            "presentation": final_presentation
        }
        
    except Exception as e:
        logger.error(f"❌ Presentation creation failed: {e}")
        return None

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
        }}
        .presentation {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .slide {{
            padding: 40px;
            border-bottom: 1px solid #eee;
        }}
        .slide:last-child {{
            border-bottom: none;
        }}
        .slide h2 {{
            color: #667eea;
            font-size: 2em;
            margin: 0 0 10px 0;
        }}
        .slide h3 {{
            color: #666;
            font-size: 1.3em;
            margin: 0 0 20px 0;
            font-weight: normal;
        }}
        .slide-content {{
            font-size: 1.1em;
            line-height: 1.6;
        }}
        .slide-content ul {{
            padding-left: 0;
        }}
        .slide-content li {{
            list-style: none;
            padding: 8px 0;
            border-left: 3px solid #667eea;
            padding-left: 15px;
            margin: 10px 0;
        }}
        .slide-notes {{
            background: #f8f9fa;
            padding: 20px;
            margin-top: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .slide-notes h4 {{
            margin: 0 0 10px 0;
            color: #667eea;
        }}
        .metadata {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
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
            <p>Создано: {created_at} | Слайдов: {total_slides} | Генератор: OpenManus AI Agent</p>
        </div>
    </div>
</body>
</html>
"""
    
    slides_html = ""
    for i, slide in enumerate(presentation_data.get('slides', [])):
        content_html = ""
        if isinstance(slide.get('content'), list):
            content_html = "<ul>" + "".join(f"<li>{item}</li>" for item in slide['content']) + "</ul>"
        else:
            content_html = f"<p>{slide.get('content', '')}</p>"
        
        slide_html = f"""
        <div class="slide">
            <h2>{slide.get('title', 'Untitled')}</h2>
            <h3>{slide.get('subtitle', '')}</h3>
            <div class="slide-content">
                {content_html}
            </div>
            <div class="slide-notes">
                <h4>Заметки докладчика:</h4>
                <p>{slide.get('notes', 'Заметки отсутствуют')}</p>
            </div>
        </div>
        """
        slides_html += slide_html
    
    return html_template.format(
        title=presentation_data.get('title', 'Untitled Presentation'),
        description=presentation_data.get('description', ''),
        slides_html=slides_html,
        created_at=presentation_data.get('created_at', ''),
        total_slides=len(presentation_data.get('slides', []))
    )

async def main():
    """Main function to create demo presentations"""
    
    logger.info("🚀 Starting OpenManus Presentation Demo")
    
    # Create presentations directory
    presentations_dir = "./presentations"
    os.makedirs(presentations_dir, exist_ok=True)
    
    # Topics for presentations
    topics = [
        "Искусственный интеллект в образовании: возможности и вызовы",
        "Блокчейн технологии: принципы работы и применение"
    ]
    
    results = []
    
    for i, topic in enumerate(topics, 1):
        logger.info(f"\n📊 Creating presentation {i}/2: {topic}")
        
        result = await create_presentation_demo(topic, presentations_dir)
        
        if result:
            results.append(result)
            logger.info(f"✅ Presentation {i} completed successfully!")
        else:
            logger.error(f"❌ Presentation {i} failed!")
    
    # Summary
    logger.info(f"\n🎉 Demo completed! Created {len(results)} presentations:")
    for result in results:
        logger.info(f"  📄 JSON: {result['json_file']}")
        logger.info(f"  🌐 HTML: {result['html_file']}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())

