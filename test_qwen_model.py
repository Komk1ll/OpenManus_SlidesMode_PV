#!/usr/bin/env python3
"""
Тестирование новой модели qwen/qwen3-235b-a22b-thinking-2507
для создания презентации о VPN-сервере
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Настройка логирования
log_filename = f"/home/ubuntu/openmanus_project/logs/qwen_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
Path("/home/ubuntu/openmanus_project/logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

sys.path.append('/home/ubuntu/openmanus_project')

async def test_qwen_model():
    """Тестирует новую модель Qwen для создания презентации о VPN"""
    
    logger.info("🚀 Начало эксперимента с моделью qwen/qwen3-235b-a22b-thinking-2507")
    logger.info("📋 Тема презентации: Запуск собственного VPN-сервера, устойчивого к блокировкам РКН")
    
    start_time = time.time()
    
    try:
        # Импорт необходимых модулей
        logger.info("📦 Импорт модулей...")
        from app.tool.presentation_tools import (
            GenerateStructureTool,
            GenerateSlideContentTool,
            SearchImageTool,
            ExportPresentationTool
        )
        
        # Тема презентации
        topic = "Запуск собственного VPN-сервера, устойчивого к блокировкам РКН"
        slide_count = 8
        
        logger.info(f"🎯 Создание презентации: '{topic}'")
        logger.info(f"📊 Количество слайдов: {slide_count}")
        
        # Шаг 1: Генерация структуры
        logger.info("🏗️ Шаг 1: Генерация структуры презентации...")
        structure_tool = GenerateStructureTool()
        structure_result = await structure_tool.execute(
            topic=topic,
            slide_count=slide_count,
            language="auto"
        )
        
        if structure_result.error:
            logger.error(f"❌ Ошибка генерации структуры: {structure_result.error}")
            return None
            
        structure = structure_result.output
        logger.info(f"✅ Структура создана: {len(structure['slides'])} слайдов")
        
        # Логирование структуры
        for i, slide in enumerate(structure['slides'], 1):
            logger.info(f"   📄 Слайд {i}: {slide['title']}")
        
        # Шаг 2: Генерация контента для каждого слайда
        logger.info("📝 Шаг 2: Генерация контента слайдов...")
        content_tool = GenerateSlideContentTool()
        
        presentation = {
            "title": structure['title'],
            "description": structure.get('description', ''),
            "slides": [],
            "metadata": {
                "created_by": "OpenManus SlidesMode v2.0 + Qwen",
                "model": "qwen/qwen3-235b-a22b-thinking-2507",
                "topic": topic,
                "slide_count": len(structure['slides']),
                "language": structure.get('language', 'russian'),
                "created_at": datetime.now().isoformat()
            }
        }
        
        for i, slide_info in enumerate(structure['slides'], 1):
            logger.info(f"   🔄 Генерация контента для слайда {i}: {slide_info['title']}")
            
            content_result = await content_tool.execute(
                slide_info=slide_info,
                presentation_topic=topic
            )
            
            if content_result.error:
                logger.warning(f"   ⚠️ Ошибка генерации контента слайда {i}: {content_result.error}")
                # Используем базовый контент
                slide_content = {
                    "title": slide_info['title'],
                    "content": [{"type": "paragraph", "text": slide_info.get('description', 'Контент недоступен')}],
                    "notes": "Контент сгенерирован с ошибкой"
                }
            else:
                slide_content = content_result.output
                logger.info(f"   ✅ Контент слайда {i} создан ({len(slide_content.get('content', []))} элементов)")
            
            # Шаг 3: Поиск изображения для слайда
            logger.info(f"   🖼️ Поиск изображения для слайда {i}...")
            image_tool = SearchImageTool()
            
            image_result = await image_tool.execute(
                slide_title=slide_content['title'],
                slide_content=str(slide_content.get('content', [])),
                image_type="professional"
            )
            
            if image_result.error:
                logger.warning(f"   ⚠️ Ошибка поиска изображения для слайда {i}: {image_result.error}")
                image_url = None
            else:
                image_url = image_result.output
                logger.info(f"   ✅ Изображение найдено для слайда {i}")
            
            # Добавляем слайд в презентацию
            slide_content['image_url'] = image_url
            presentation['slides'].append(slide_content)
        
        # Шаг 4: Экспорт презентации
        logger.info("💾 Шаг 4: Экспорт презентации...")
        export_tool = ExportPresentationTool()
        
        # Экспорт в JSON
        json_result = await export_tool.execute(
            presentation=presentation,
            format="json",
            output_path="/home/ubuntu/openmanus_project/qwen_vpn_presentation.json"
        )
        
        # Экспорт в HTML
        html_result = await export_tool.execute(
            presentation=presentation,
            format="html",
            output_path="/home/ubuntu/openmanus_project/qwen_vpn_presentation.html"
        )
        
        # Экспорт в PDF
        pdf_result = await export_tool.execute(
            presentation=presentation,
            format="pdf",
            output_path="/home/ubuntu/openmanus_project/qwen_vpn_presentation.pdf"
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info("🎉 Эксперимент завершен успешно!")
        logger.info(f"⏱️ Общее время выполнения: {total_time:.2f} секунд")
        logger.info(f"📁 Файлы созданы:")
        logger.info(f"   📄 JSON: qwen_vpn_presentation.json")
        logger.info(f"   🌐 HTML: qwen_vpn_presentation.html")
        logger.info(f"   📋 PDF: qwen_vpn_presentation.pdf")
        logger.info(f"   📊 Лог: {log_filename}")
        
        # Анализ качества
        logger.info("📈 Анализ качества презентации:")
        logger.info(f"   📊 Слайдов создано: {len(presentation['slides'])}")
        
        content_types = {}
        for slide in presentation['slides']:
            for content_item in slide.get('content', []):
                content_type = content_item.get('type', 'unknown')
                content_types[content_type] = content_types.get(content_type, 0) + 1
        
        logger.info(f"   📝 Типы контента: {content_types}")
        
        images_found = sum(1 for slide in presentation['slides'] if slide.get('image_url'))
        logger.info(f"   🖼️ Изображений найдено: {images_found}/{len(presentation['slides'])}")
        
        return {
            "success": True,
            "presentation": presentation,
            "execution_time": total_time,
            "log_file": log_filename,
            "exports": {
                "json": json_result.output if not json_result.error else None,
                "html": html_result.output if not html_result.error else None,
                "pdf": pdf_result.output if not pdf_result.error else None
            }
        }
        
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {str(e)}")
        logger.exception("Детали ошибки:")
        return {
            "success": False,
            "error": str(e),
            "log_file": log_filename
        }

async def main():
    """Главная функция"""
    print("🧪 Запуск эксперимента с моделью Qwen...")
    result = await test_qwen_model()
    
    if result and result.get("success"):
        print("\n✅ Эксперимент завершен успешно!")
        print(f"📊 Время выполнения: {result['execution_time']:.2f} сек")
        print(f"📁 Лог файл: {result['log_file']}")
    else:
        print("\n❌ Эксперимент завершился с ошибкой!")
        if result:
            print(f"📁 Лог файл: {result['log_file']}")

if __name__ == "__main__":
    asyncio.run(main())

