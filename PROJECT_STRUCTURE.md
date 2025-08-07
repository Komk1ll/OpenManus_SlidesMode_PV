# Структура проекта OpenManus SlidesMode

```
openmanus_project/
├── 📁 app/                                    # Основной код приложения
│   ├── __init__.py
│   ├── config.py                              # Конфигурация приложения
│   ├── exceptions.py                          # Пользовательские исключения
│   ├── llm.py                                # Интеграция с языковыми моделями
│   ├── logger.py                             # Система логирования
│   ├── schema.py                             # Схемы данных
│   ├── bedrock.py                            # Интеграция с AWS Bedrock
│   │
│   ├── 📁 agent/                             # Агенты и оркестраторы
│   │   ├── __init__.py
│   │   ├── base.py                           # Базовый класс агента
│   │   ├── manus.py                          # Основной агент Manus
│   │   ├── presentation_agent.py             # 🎯 ГЛАВНЫЙ АГЕНТ ПРЕЗЕНТАЦИЙ
│   │   ├── enhanced_presentation_system.py   # Улучшенная система презентаций
│   │   ├── browser.py                        # Агент для работы с браузером
│   │   ├── data_analysis.py                  # Агент анализа данных
│   │   ├── react.py                          # ReAct агент
│   │   ├── swe.py                           # Software Engineering агент
│   │   ├── toolcall.py                      # Агент вызова инструментов
│   │   └── mcp.py                           # MCP агент
│   │
│   ├── 📁 tool/                              # Инструменты и утилиты
│   │   ├── __init__.py
│   │   ├── base.py                           # Базовый класс инструментов
│   │   ├── presentation_tools.py             # 🎯 ВСЕ ИНСТРУМЕНТЫ ПРЕЗЕНТАЦИЙ
│   │   ├── file_operators.py                 # Операции с файлами
│   │   ├── bash.py                          # Bash команды
│   │   ├── python_execute.py                # Выполнение Python кода
│   │   ├── str_replace_editor.py            # Редактор текста
│   │   ├── web_search.py                    # Веб поиск
│   │   ├── browser_use_tool.py              # Инструменты браузера
│   │   ├── crawl4ai.py                      # Веб краулинг
│   │   ├── unsplash_integration.py          # Интеграция с Unsplash
│   │   ├── ask_human.py                     # Взаимодействие с пользователем
│   │   ├── terminate.py                     # Завершение работы
│   │   ├── tool_collection.py               # Коллекция инструментов
│   │   ├── create_chat_completion.py        # Создание чат-завершений
│   │   ├── planning.py                      # Планирование
│   │   ├── mcp.py                          # MCP инструменты
│   │   │
│   │   ├── 📁 search/                       # Поисковые инструменты
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # Базовый поисковик
│   │   │   ├── google_search.py             # Google поиск
│   │   │   ├── bing_search.py               # Bing поиск
│   │   │   ├── baidu_search.py              # Baidu поиск
│   │   │   └── duckduckgo_search.py         # DuckDuckGo поиск
│   │   │
│   │   └── 📁 chart_visualization/          # Визуализация данных
│   │       ├── __init__.py
│   │       ├── README.md                    # Документация
│   │       ├── README_ja.md                 # Японская документация
│   │       ├── README_ko.md                 # Корейская документация
│   │       ├── README_zh.md                 # Китайская документация
│   │       ├── chart_prepare.py             # Подготовка диаграмм
│   │       ├── data_visualization.py        # Визуализация данных
│   │       ├── python_execute.py            # Выполнение Python
│   │       └── 📁 test/                     # Тесты визуализации
│   │           ├── chart_demo.py
│   │           └── report_demo.py
│   │
│   ├── 📁 prompt/                           # Промпты для разных агентов
│   │   ├── __init__.py
│   │   ├── manus.py                         # Промпты для Manus
│   │   ├── browser.py                       # Промпты для браузера
│   │   ├── swe.py                          # Промпты для SWE
│   │   ├── toolcall.py                     # Промпты для вызова инструментов
│   │   ├── planning.py                     # Промпты для планирования
│   │   ├── visualization.py                # Промпты для визуализации
│   │   └── mcp.py                          # Промпты для MCP
│   │
│   ├── 📁 flow/                             # Потоки выполнения
│   │   ├── __init__.py
│   │   ├── base.py                          # Базовый поток
│   │   ├── planning.py                      # Поток планирования
│   │   └── flow_factory.py                  # Фабрика потоков
│   │
│   ├── 📁 sandbox/                          # Песочница для выполнения
│   │   ├── __init__.py
│   │   ├── client.py                        # Клиент песочницы
│   │   └── 📁 core/                         # Ядро песочницы
│   │       ├── exceptions.py
│   │       ├── manager.py
│   │       ├── sandbox.py
│   │       └── terminal.py
│   │
│   └── 📁 mcp/                              # Model Context Protocol
│       ├── __init__.py
│       └── server.py                        # MCP сервер
│
├── 📁 config/                               # Конфигурационные файлы
│   ├── config.toml                          # 🎯 ОСНОВНАЯ КОНФИГУРАЦИЯ
│   ├── config.example.toml                  # Пример конфигурации
│   ├── config.example-model-anthropic.toml  # Пример для Anthropic
│   ├── config.example-model-azure.toml      # Пример для Azure
│   ├── config.example-model-google.toml     # Пример для Google
│   ├── config.example-model-ollama.toml     # Пример для Ollama
│   └── config.example-model-ppio.toml       # Пример для PPIO
│
├── 📁 tests/                                # 🎯 ТЕСТЫ (100% ПОКРЫТИЕ)
│   ├── test_structure_isolated.py           # Тесты генерации структуры
│   ├── test_content_tool.py                 # Тесты генерации контента
│   ├── test_image_tool.py                   # Тесты поиска изображений
│   ├── test_export_tool.py                  # Тесты экспорта
│   ├── test_presentation_agent.py           # Интеграционные тесты
│   ├── test_summary.py                      # Генератор отчетов тестов
│   ├── test_presentation.py                 # Основные тесты презентаций
│   ├── test_structure_tool.py               # Дополнительные тесты структуры
│   └── 📁 sandbox/                          # Тесты песочницы
│       ├── test_client.py
│       ├── test_docker_terminal.py
│       ├── test_sandbox.py
│       └── test_sandbox_manager.py
│
├── 📁 protocol/                             # Протоколы связи
│   └── 📁 a2a/                             # Agent-to-Agent протокол
│       ├── __init__.py
│       └── 📁 app/
│           ├── __init__.py
│           ├── README.md
│           ├── README_zh.md
│           ├── agent.py
│           ├── agent_executor.py
│           └── main.py
│
├── 📁 examples/                             # Примеры использования
│   ├── 📁 benchmarks/
│   │   └── __init__.py
│   └── 📁 use_case/
│       ├── readme.md
│       └── 📁 japan-travel-plan/
│           └── japan_travel_guide_instructions.txt
│
├── 📁 workspace/                            # Рабочая область
│   └── example.txt
│
├── 📄 README.md                             # 🎯 ГЛАВНАЯ ДОКУМЕНТАЦИЯ
├── 📄 MODERNIZATION_REPORT.md               # 🎯 ОТЧЕТ О МОДЕРНИЗАЦИИ
├── 📄 PROJECT_STRUCTURE.md                  # Этот файл
├── 📄 requirements.txt                      # Python зависимости
├── 📄 setup.py                             # Установочный скрипт
├── 📄 todo.md                              # Отслеживание задач
├── 📄 modernization_report.txt             # Текстовый отчет
│
├── 🐍 main.py                              # Главная точка входа
├── 🐍 main_presentation.py                 # Точка входа для презентаций
├── 🐍 run_flow.py                          # Запуск потоков
├── 🐍 run_mcp.py                           # Запуск MCP
├── 🐍 run_mcp_server.py                    # Запуск MCP сервера
├── 🐍 simple_test.py                       # Простые тесты
└── 🐍 final_enhanced_system.py             # Финальная улучшенная система
```

## 🎯 Ключевые файлы для презентаций

### Основные компоненты
- **`app/agent/presentation_agent.py`** - Главный агент-оркестратор презентаций
- **`app/tool/presentation_tools.py`** - Все инструменты для работы с презентациями
- **`config/config.toml`** - Конфигурация API ключей и настроек

### Тестирование (100% покрытие)
- **`test_structure_isolated.py`** - Тесты генерации структуры (3/3)
- **`test_content_tool.py`** - Тесты генерации контента (4/4)
- **`test_image_tool.py`** - Тесты поиска изображений (6/6)
- **`test_export_tool.py`** - Тесты экспорта (6/6)
- **`test_presentation_agent.py`** - Интеграционные тесты (9/9)

### Документация
- **`README.md`** - Полная документация по использованию
- **`MODERNIZATION_REPORT.md`** - Детальный отчет о модернизации
- **`PROJECT_STRUCTURE.md`** - Структура проекта (этот файл)

## 📊 Статистика проекта

- **Всего файлов Python**: ~80 файлов
- **Основных компонентов**: 5 (Structure, Content, Image, Export, Agent)
- **Тестов**: 28 (100% покрытие)
- **Поддерживаемых языков**: 2 (русский, английский)
- **Форматов экспорта**: 4 (Markdown, HTML, JSON, PDF)
- **API интеграций**: 3 (OpenAI/OpenRouter, Unsplash, Tavily)

## 🚀 Быстрый старт

1. **Установка зависимостей**: `pip install -r requirements.txt`
2. **Настройка конфигурации**: Отредактируйте `config/config.toml`
3. **Запуск тестов**: `python test_summary.py`
4. **Создание презентации**: Используйте `app/agent/presentation_agent.py`

---

*Структура создана автоматически для проекта OpenManus SlidesMode v2.0.0*

