# 🎯 OpenManus SlidesMode v2.0 - Модернизированная система создания презентаций

> **Автоматическое создание профессиональных презентаций с помощью ИИ**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI%20%7C%20OpenRouter-green.svg)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Возможности системы

### ✨ **Основные функции**
- 🧠 **ИИ-генерация контента** с поддержкой русского и английского языков
- 🖼️ **Автоматический поиск изображений** через Unsplash и Tavily API
- 📄 **Множественные форматы экспорта**: JSON, HTML, PDF
- 🎨 **Профессиональное оформление** с адаптивным дизайном
- ⚡ **Быстрая генерация** (менее 1 секунды для 8 слайдов)
- 🔧 **Гибкая настройка** через конфигурационные файлы

### 🎯 **Поддерживаемые модели ИИ**
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **OpenRouter**: Qwen, Claude, Llama и другие
- **Настраиваемые параметры**: температура, токены, базовый URL

### 📊 **Типы контента**
- 📝 Параграфы и текстовые блоки
- 🔸 Маркированные списки
- 💻 Блоки кода с подсветкой синтаксиса
- 💬 Цитаты с указанием авторов
- 🖼️ Интеграция изображений
- 📋 Заметки для докладчика

## 🛠️ Быстрый старт

### 1. **Установка зависимостей**

```bash
# Клонирование репозитория
git clone <repository-url>
cd openmanus_project

# Установка Python зависимостей
pip3 install -r requirements.txt

# Установка wkhtmltopdf для PDF экспорта
sudo apt-get update
sudo apt-get install -y wkhtmltopdf
```

### 2. **Настройка конфигурации**

```bash
# Копирование примера конфигурации
cp config/config.example.toml config/config.toml

# Редактирование конфигурации
nano config/config.toml
```

**Основные параметры в config.toml:**
```toml
[llm]
model = "qwen/qwen3-235b-a22b-thinking-2507"  # Модель ИИ
base_url = "https://openrouter.ai/api/v1/"     # API endpoint
api_key = "your-api-key-here"                  # API ключ
max_tokens = 8192                              # Максимум токенов
temperature = 0.7                              # Креативность (0.0-1.0)

[presentation]
tavily_api_key = "your-tavily-key"            # Для поиска изображений
unsplash_access_key = "your-unsplash-key"     # Для Unsplash API
default_slide_count = 10                       # Количество слайдов по умолчанию
export_formats = ["json", "html", "pdf"]      # Форматы экспорта
```

### 3. **Создание первой презентации**

```python
#!/usr/bin/env python3
import asyncio
from app.agent.presentation_agent import create_presentation

async def main():
    result = await create_presentation(
        topic="Искусственный интеллект в образовании",
        slide_count=8,
        include_pdf=True
    )
    
    if result.get('success'):
        print(f"✅ Презентация создана!")
        print(f"📁 Файлы: {list(result['exports'].keys())}")
    else:
        print(f"❌ Ошибка: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📋 Подробное руководство

### 🔧 **Использование инструментов презентации**

#### 1. **Генерация структуры**
```python
from app.tool.presentation_tools import GenerateStructureTool

structure_tool = GenerateStructureTool()
result = await structure_tool.execute(
    topic="Машинное обучение",
    slide_count=6,
    language="auto"  # auto, russian, english
)
```

#### 2. **Создание контента слайдов**
```python
from app.tool.presentation_tools import GenerateSlideContentTool

content_tool = GenerateSlideContentTool()
result = await content_tool.execute(
    slide_info={
        "title": "Введение в нейронные сети",
        "description": "Основы и принципы работы"
    },
    presentation_topic="Машинное обучение"
)
```

#### 3. **Поиск изображений**
```python
from app.tool.presentation_tools import SearchImageTool

image_tool = SearchImageTool()
result = await image_tool.execute(
    slide_title="Нейронные сети",
    slide_content="Искусственные нейронные сети",
    image_type="professional"  # professional, illustration, diagram
)
```

#### 4. **Экспорт презентации**
```python
from app.tool.presentation_tools import ExportPresentationTool

export_tool = ExportPresentationTool()
result = await export_tool.execute(
    presentation=presentation_data,
    format="pdf",  # json, html, pdf
    output_path="/path/to/output.pdf"
)
```

### 🎨 **Настройка стилей презентации**

Стили можно настроить в функции `generate_professional_html()` в файле генератора:

```css
/* Основные цвета */
--primary-color: #2c3e50;
--secondary-color: #3498db;
--accent-color: #e74c3c;

/* Шрифты */
--main-font: 'Arial', 'Helvetica', sans-serif;
--code-font: 'Courier New', 'Monaco', monospace;

/* Размеры */
--slide-padding: 30px;
--border-radius: 10px;
```

## 🧪 Тестирование системы

### **Запуск всех тестов**
```bash
# Тест структуры презентации
python3 test_structure_tool.py

# Тест генерации контента
python3 test_content_tool.py

# Тест поиска изображений
python3 test_image_tool.py

# Тест экспорта
python3 test_export_tool.py

# Комплексный тест агента
python3 test_presentation_agent.py

# Сводка всех тестов
python3 test_summary.py
```

### **Создание демо-презентации**
```bash
# Быстрое создание демо
python3 qwen_vpn_generator.py

# Результат: JSON, HTML и PDF файлы
```

## 📊 Примеры использования

### **1. Техническая презентация**
```python
result = await create_presentation(
    topic="Настройка VPN-сервера с Xray",
    slide_count=8,
    include_images=True,
    include_code=True
)
```

### **2. Образовательная презентация**
```python
result = await create_presentation(
    topic="История развития интернета",
    slide_count=12,
    style="educational",
    language="russian"
)
```

### **3. Бизнес-презентация**
```python
result = await create_presentation(
    topic="Стратегия цифровой трансформации",
    slide_count=15,
    style="business",
    include_charts=True
)
```

## 🔍 Устранение неполадок

### **Частые проблемы и решения**

#### 1. **Ошибка API ключа**
```bash
# Проверьте конфигурацию
cat config/config.toml | grep api_key

# Убедитесь что ключ действителен
curl -H "Authorization: Bearer YOUR_KEY" https://openrouter.ai/api/v1/models
```

#### 2. **Проблемы с PDF генерацией**
```bash
# Проверьте установку wkhtmltopdf
wkhtmltopdf --version

# Переустановка если нужно
sudo apt-get install --reinstall wkhtmltopdf
```

#### 3. **Ошибки поиска изображений**
```bash
# Проверьте API ключи для изображений
echo $TAVILY_API_KEY
echo $UNSPLASH_ACCESS_KEY
```

#### 4. **Проблемы с зависимостями**
```bash
# Переустановка зависимостей
pip3 install -r requirements.txt --force-reinstall
```

## 📈 Производительность

### **Бенчмарки системы**
- ⚡ **Генерация структуры**: ~2-5 секунд
- 📝 **Создание контента**: ~3-8 секунд на слайд
- 🖼️ **Поиск изображений**: ~1-3 секунды на изображение
- 📄 **Экспорт PDF**: ~1-2 секунды
- 🎯 **Полная презентация (8 слайдов)**: ~30-60 секунд

### **Оптимизация производительности**
```toml
# Для быстрой генерации
[llm]
temperature = 0.3        # Меньше креативности = быстрее
max_tokens = 4096        # Меньше токенов = быстрее

# Для качественного результата
[llm]
temperature = 0.7        # Больше креативности
max_tokens = 8192        # Больше деталей
```

## 🔧 Расширенная настройка

### **Добавление новых моделей ИИ**
```toml
[llm]
model = "anthropic/claude-3-sonnet"
base_url = "https://openrouter.ai/api/v1/"
api_key = "your-key"
```

### **Настройка поиска изображений**
```toml
[presentation]
image_search_enabled = true
preferred_image_source = "unsplash"  # unsplash, tavily, both
image_quality = "high"               # low, medium, high
```

### **Кастомизация экспорта**
```toml
[presentation]
export_formats = ["json", "html", "pdf", "markdown"]
pdf_orientation = "landscape"        # portrait, landscape
pdf_page_size = "A4"                # A4, Letter, A3
```

## 📚 API Reference

### **PresentationAgent**
```python
async def create_presentation(
    topic: str,                    # Тема презентации
    slide_count: int = 10,         # Количество слайдов
    language: str = "auto",        # Язык (auto, russian, english)
    include_images: bool = True,   # Включать изображения
    include_pdf: bool = True,      # Создавать PDF
    style: str = "professional"   # Стиль (professional, educational, business)
) -> dict
```

### **GenerateStructureTool**
```python
async def execute(
    topic: str,                    # Тема презентации
    slide_count: int,              # Количество слайдов
    language: str = "auto"         # Язык генерации
) -> ToolResult
```

### **GenerateSlideContentTool**
```python
async def execute(
    slide_info: dict,              # Информация о слайде
    presentation_topic: str        # Общая тема презентации
) -> ToolResult
```

## 🤝 Вклад в проект

### **Структура проекта**
```
openmanus_project/
├── app/
│   ├── agent/              # ИИ агенты
│   ├── tool/               # Инструменты презентации
│   └── core/               # Основные компоненты
├── config/                 # Конфигурационные файлы
├── logs/                   # Логи выполнения
├── tests/                  # Тесты системы
└── examples/               # Примеры использования
```

### **Добавление новых функций**
1. Создайте новый инструмент в `app/tool/`
2. Добавьте тесты в корневую директорию
3. Обновите документацию
4. Создайте pull request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🆘 Поддержка

- 📧 **Email**: support@openmanus.ai
- 💬 **Discord**: [OpenManus Community](https://discord.gg/openmanus)
- 📖 **Документация**: [docs.openmanus.ai](https://docs.openmanus.ai)
- 🐛 **Баг-репорты**: [GitHub Issues](https://github.com/openmanus/issues)

---

**OpenManus SlidesMode v2.0** - Создавайте профессиональные презентации за секунды! 🚀

