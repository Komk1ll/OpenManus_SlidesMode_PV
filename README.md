# OpenManus SlidesMode - Система Генерации Презентаций

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-28/28_Passed-green.svg)](./tests/)
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](./tests/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Современная система автоматической генерации презентаций с поддержкой ИИ, многоязычности и профессионального экспорта.

## 🚀 Основные возможности

- **🌍 Многоязычность**: Автоматическое определение языка (русский/английский) и генерация контента
- **🎨 Богатый контент**: Поддержка параграфов, списков, цитат, кода и изображений
- **🖼️ Умный поиск изображений**: Интеграция с Unsplash и Tavily API с автоматическим выбором источника
- **📄 Экспорт в PDF**: Профессиональный экспорт в PDF с качественным оформлением
- **🔧 Гибкая настройка**: Настраиваемые параметры генерации и экспорта
- **🛡️ Надежность**: Комплексная обработка ошибок и резервные механизмы
- **✅ 100% покрытие тестами**: Полное тестирование всех компонентов

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Установка](#установка)
- [Настройка](#настройка)
- [Использование](#использование)
- [API документация](#api-документация)
- [Примеры](#примеры)
- [Тестирование](#тестирование)
- [Архитектура](#архитектура)
- [Участие в разработке](#участие-в-разработке)

## ⚡ Быстрый старт

```python
from app.agent.presentation_agent import create_presentation

# Создание простой презентации
result = await create_presentation("Искусственный интеллект в медицине", 8)

if result.get("success"):
    print(f"✅ Создана презентация: {result['presentation']['title']}")
    print(f"📊 Количество слайдов: {len(result['presentation']['slides'])}")
    print(f"📁 Форматы экспорта: {list(result['exports'].keys())}")
```

## 🔧 Установка

### Системные требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- wkhtmltopdf (для генерации PDF)
- Интернет-соединение (для API вызовов)

### Установка зависимостей

```bash
# Клонирование репозитория
git clone <repository-url>
cd openmanus_project

# Установка Python зависимостей
pip install -r requirements.txt

# Установка wkhtmltopdf (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install wkhtmltopdf

# Установка wkhtmltopdf (macOS)
brew install wkhtmltopdf

# Установка wkhtmltopdf (Windows)
# Скачайте с https://wkhtmltopdf.org/downloads.html
```

### Зависимости Python

```
pdfkit>=1.0.0          # Генерация PDF
requests>=2.25.0       # HTTP клиент для API
openai>=1.0.0          # Интеграция с LLM
pydantic>=2.0.0        # Валидация данных
tenacity>=8.0.0        # Механизмы повторных попыток
colorama>=0.4.0        # Форматирование вывода в консоль
```

## ⚙️ Настройка

### Настройка API ключей

Создайте файл `config/config.toml` с вашими API ключами:

```toml
[api]
# OpenAI/OpenRouter API ключ (обязательно)
openai_api_key = "your-openai-api-key"
openai_base_url = "https://openrouter.ai/api/v1"

# Tavily API ключ (обязательно для поиска изображений)
tavily_api_key = "your-tavily-api-key"

# Unsplash API ключ (опционально, для профессиональных изображений)
unsplash_access_key = "your-unsplash-access-key"

[presentation]
default_slide_count = 8
default_language = "auto"
default_output_dir = "./presentations"
```

### Получение API ключей

1. **OpenAI/OpenRouter**: Зарегистрируйтесь на [OpenRouter](https://openrouter.ai/) или [OpenAI](https://openai.com/)
2. **Tavily**: Получите ключ на [Tavily](https://tavily.com/)
3. **Unsplash** (опционально): Зарегистрируйтесь на [Unsplash Developers](https://unsplash.com/developers)

## 📖 Использование

### Основные способы использования

#### 1. Быстрое создание презентации

```python
import asyncio
from app.agent.presentation_agent import create_presentation

async def main():
    result = await create_presentation(
        topic="Машинное обучение в бизнесе",
        slide_count=6
    )
    
    if result.get("success"):
        print("Презентация создана успешно!")
    else:
        print(f"Ошибка: {result.get('error')}")

asyncio.run(main())
```

#### 2. Создание с PDF экспортом

```python
from app.agent.presentation_agent import create_presentation

result = await create_presentation(
    topic="Основы блокчейна",
    slide_count=8,
    include_pdf=True
)
```

#### 3. Настраиваемая конфигурация

```python
from app.agent.presentation_agent import PresentationConfig, create_custom_presentation

config = PresentationConfig(
    topic="Анализ данных в Python",
    slide_count=10,
    language="russian",  # или "english", "auto"
    include_images=True,
    export_formats=["markdown", "html", "pdf"],
    output_directory="./my_presentations"
)

result = await create_custom_presentation(config)
```

#### 4. Использование отдельных инструментов

```python
from app.tool.presentation_tools import (
    GenerateStructureTool,
    GenerateSlideContentTool,
    SearchImageTool,
    ExportPresentationTool
)

# Генерация структуры
structure_tool = GenerateStructureTool()
structure = await structure_tool.execute(
    topic="Кибербезопасность",
    slide_count=5,
    language="auto"
)

# Генерация контента для слайда
content_tool = GenerateSlideContentTool()
content = await content_tool.execute(
    slide_info=structure.output['slides'][0],
    presentation_topic="Кибербезопасность"
)

# Поиск изображения
image_tool = SearchImageTool()
image_url = await image_tool.execute(
    slide_title="Введение в кибербезопасность",
    slide_content="Основы защиты информации",
    image_type="professional"
)

# Экспорт презентации
export_tool = ExportPresentationTool()
exported = await export_tool.execute(
    presentation=presentation_data,
    format="pdf",
    output_path="./presentation.pdf"
)
```

### Параметры конфигурации

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `topic` | str | - | Тема презентации (обязательно) |
| `slide_count` | int | 10 | Количество слайдов |
| `language` | str | "auto" | Язык ("auto", "english", "russian") |
| `include_images` | bool | True | Включать ли поиск изображений |
| `export_formats` | List[str] | ["markdown", "html", "json"] | Форматы экспорта |
| `output_directory` | str | "./presentations" | Директория для сохранения |

### Поддерживаемые форматы экспорта

- **Markdown** (.md) - Для документации и простого просмотра
- **HTML** (.html) - Для веб-просмотра с интерактивными элементами
- **JSON** (.json) - Для программной обработки данных
- **PDF** (.pdf) - Для профессиональной печати и презентации

## 🧪 Тестирование

### Запуск всех тестов

```bash
# Запуск всех тестов с отчетом
python test_summary.py

# Запуск отдельных тестов
python test_structure_isolated.py    # Тесты генерации структуры
python test_content_tool.py          # Тесты генерации контента
python test_image_tool.py            # Тесты поиска изображений
python test_export_tool.py           # Тесты экспорта
python test_presentation_agent.py    # Интеграционные тесты
```

### Покрытие тестами

Проект имеет **100% покрытие тестами** (28/28 тестов):

- ✅ GenerateStructureTool: 3/3 тестов
- ✅ GenerateSlideContentTool: 4/4 тестов  
- ✅ SearchImageTool: 6/6 тестов
- ✅ ExportPresentationTool: 6/6 тестов
- ✅ PresentationAgent: 9/9 тестов

## 🏗️ Архитектура

### Компоненты системы

```
PresentationAgent (Оркестратор)
├── GenerateStructureTool (Генерация структуры)
├── GenerateSlideContentTool (Генерация контента)
├── SearchImageTool (Поиск изображений)
└── ExportPresentationTool (Экспорт в разные форматы)
```

### Принципы проектирования

1. **Модульность**: Каждый инструмент независим и может использоваться отдельно
2. **Расширяемость**: Легко добавлять новые типы контента, форматы экспорта или источники изображений
3. **Надежность**: Комплексная обработка ошибок с резервными механизмами
4. **Настраиваемость**: Гибкая система конфигурации для разных случаев использования
5. **Тестируемость**: Полное покрытие тестами с изолированными юнит-тестами

### Обработка ошибок

Система реализует многоуровневую обработку ошибок:

- **Уровень инструментов**: Каждый инструмент обрабатывает свои специфические ошибки
- **Уровень агента**: PresentationAgent управляет распространением ошибок и восстановлением
- **Graceful degradation**: Система продолжает работу даже при сбоях отдельных компонентов
- **Подробное логирование**: Детальное логирование для отладки и мониторинга

## 🔍 Устранение неполадок

### Частые проблемы

#### 1. Ошибка "No module named 'pdfkit'"
```bash
pip install pdfkit
sudo apt-get install wkhtmltopdf  # Linux
brew install wkhtmltopdf          # macOS
```

#### 2. Ошибка API ключей
- Проверьте правильность API ключей в `config/config.toml`
- Убедитесь, что у вас есть доступ к интернету
- Проверьте лимиты API на соответствующих платформах

#### 3. Проблемы с генерацией PDF
- Убедитесь, что wkhtmltopdf установлен и доступен в PATH
- Проверьте права доступа к директории вывода
- Попробуйте экспорт в другие форматы (HTML, Markdown)

#### 4. Медленная генерация
- Уменьшите количество слайдов для тестирования
- Отключите поиск изображений (`include_images=False`)
- Проверьте скорость интернет-соединения

### Логирование

Система использует стандартное логирование Python. Для включения подробного логирования:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🤝 Участие в разработке

### Структура проекта

```
openmanus_project/
├── app/                          # Основной код приложения
│   ├── agent/                    # Агенты и оркестраторы
│   │   ├── presentation_agent.py # Главный агент презентаций
│   │   └── enhanced_presentation_system.py # Устаревшая система
│   ├── tool/                     # Инструменты и утилиты
│   │   └── presentation_tools.py # Все инструменты презентаций
│   └── core/                     # Базовые классы
│       └── base_tool.py          # Базовый интерфейс инструментов
├── config/                       # Конфигурационные файлы
│   └── config.toml              # Основная конфигурация
├── tests/                        # Тесты
│   ├── test_*.py                # Различные тестовые файлы
│   └── test_summary.py          # Генератор отчетов по тестам
├── requirements.txt              # Python зависимости
├── README.md                     # Этот файл
├── MODERNIZATION_REPORT.md       # Отчет о модернизации
└── todo.md                       # Отслеживание задач проекта
```

### Добавление новых функций

1. **Новые типы контента**: Расширьте `GenerateSlideContentTool`
2. **Новые форматы экспорта**: Добавьте в `ExportPresentationTool`
3. **Новые источники изображений**: Расширьте `SearchImageTool`
4. **Новые языки**: Обновите логику определения языка

### Стиль кода

- Следуйте PEP 8 для Python кода
- Используйте type hints для всех функций
- Добавляйте docstrings для всех публичных методов
- Пишите тесты для новой функциональности

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🙏 Благодарности

- OpenAI за предоставление мощных языковых моделей
- Unsplash за качественные изображения
- Tavily за разнообразные источники изображений
- Сообществу Python за отличные библиотеки

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте [раздел устранения неполадок](#устранение-неполадок)
2. Просмотрите [существующие issues](../../issues)
3. Создайте новый issue с подробным описанием проблемы

---

**Версия**: 2.0.0  
**Последнее обновление**: Январь 2025  
**Статус**: ✅ Готов к продакшену

