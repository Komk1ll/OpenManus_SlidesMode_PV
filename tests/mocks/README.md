# OpenAI Mock System

Централизованная система мокирования OpenAI API для тестирования.

## Обзор

Эта система предоставляет автоматическое мокирование всех вызовов OpenAI API в тестах, обеспечивая:

- ✅ **Быстрые тесты** - без реальных API вызовов
- ✅ **Надежность** - независимость от внешних сервисов
- ✅ **Реалистичные ответы** - структура данных идентична OpenAI API
- ✅ **Простота использования** - автоматическая активация в тестах
- ✅ **Гибкость** - возможность настройки кастомных ответов

## Автоматическое мокирование

Моки автоматически активируются для всех тестов благодаря фикстурам в `conftest.py`:

```python
# Тесты автоматически используют моки
def test_my_function():
    import openai
    
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    # Получаем мок-ответ, не реальный API вызов
    assert response.model == "gpt-4"
    assert response.choices[0].message.content
```

## Доступные компоненты

### MockOpenAIClient

Синхронный мок-клиент OpenAI:

```python
from tests.mocks import MockOpenAIClient

client = MockOpenAIClient()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Test"}]
)
```

### MockAsyncOpenAIClient

Асинхронный мок-клиент:

```python
from tests.mocks import MockAsyncOpenAIClient

async def test_async():
    client = MockAsyncOpenAIClient()
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Test"}]
    )
```

### OpenAIResponseGenerator

Генератор реалистичных ответов:

```python
from tests.mocks import OpenAIResponseGenerator

# Генерация chat completion
response = OpenAIResponseGenerator.chat_completion(
    content="Custom response",
    model="gpt-4"
)

# Генерация embedding
embedding = OpenAIResponseGenerator.embedding(
    text="Sample text"
)

# Генерация ошибки
error = OpenAIResponseGenerator.error_response(
    error_type="rate_limit_exceeded",
    message="Too many requests"
)
```

## Поддерживаемые операции

### Chat Completions

```python
# Обычный ответ
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Стриминг
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True
)
for chunk in stream:
    print(chunk.choices[0].delta.content)

# Tool calls
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Search for something"}],
    tools=[{"type": "function", "function": {"name": "search"}}]
)
```

### Embeddings

```python
# Одиночный текст
response = client.embeddings.create(
    input="Text to embed",
    model="text-embedding-ada-002"
)

# Множественные тексты
response = client.embeddings.create(
    input=["Text 1", "Text 2", "Text 3"],
    model="text-embedding-ada-002"
)
```

### File Operations

```python
from io import StringIO

# Создание файла
file_obj = StringIO("file content")
file_obj.name = "test.txt"

response = client.files.create(
    file=file_obj,
    purpose="fine-tune"
)

# Список файлов
files = client.files.list()

# Удаление файла
client.files.delete(response.id)
```

## Кастомные ответы

Вы можете настроить специфические ответы для определенных сценариев:

```python
def test_custom_response(openai_mock_client):
    # Создаем кастомный ответ
    custom_response = OpenAIResponseGenerator.chat_completion(
        content="This is a custom response",
        model="gpt-3.5-turbo"
    )
    
    # Устанавливаем его для конкретной модели
    openai_mock_client.chat.completions.set_custom_response(
        custom_response,
        model="gpt-3.5-turbo"
    )
    
    # Теперь все вызовы с этой моделью вернут кастомный ответ
    response = openai_mock_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Any message"}]
    )
    
    assert response.choices[0].message.content == "This is a custom response"
```

## Отслеживание вызовов

Моки отслеживают количество вызовов:

```python
def test_call_tracking(openai_mock_client):
    # Изначально 0 вызовов
    assert openai_mock_client.chat.completions.call_count == 0
    
    # Делаем вызов
    openai_mock_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Test"}]
    )
    
    # Теперь 1 вызов
    assert openai_mock_client.chat.completions.call_count == 1
```

## Сброс состояния

Для очистки состояния между тестами:

```python
def test_reset_mocks(openai_mock_client):
    # Делаем несколько вызовов
    openai_mock_client.chat.completions.create(...)
    openai_mock_client.embeddings.create(...)
    
    # Сбрасываем все моки
    openai_mock_client.reset_all_mocks()
    
    # Счетчики обнулены
    assert openai_mock_client.chat.completions.call_count == 0
    assert openai_mock_client.embeddings.call_count == 0
```

## Доступные фикстуры

### Основные фикстуры

- `openai_mock_client` - экземпляр MockOpenAIClient
- `async_openai_mock_client` - экземпляр MockAsyncOpenAIClient
- `reset_openai_mocks` - автоматический сброс состояния после каждого теста

### Фикстуры ответов (в tests/fixtures/openai_fixtures.py)

- `chat_completion_response` - стандартный ответ chat completion
- `streaming_response` - стриминговый ответ
- `tool_call_response` - ответ с вызовом функции
- `embedding_response` - ответ embedding
- `file_object_response` - объект файла
- `error_response` - ответ с ошибкой
- `custom_openai_responses` - фабрика кастомных ответов

## Примеры использования

### Тестирование chat completion

```python
def test_chat_completion(openai_mock_client):
    response = openai_mock_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    assert response.model == "gpt-4"
    assert response.choices[0].message.role == "assistant"
    assert response.choices[0].message.content
    assert response.usage.total_tokens > 0
```

### Тестирование стриминга

```python
def test_streaming(openai_mock_client):
    stream = openai_mock_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Tell me a story"}],
        stream=True
    )
    
    chunks = list(stream)
    assert len(chunks) > 1
    assert chunks[-1].choices[0].finish_reason == "stop"
```

### Тестирование асинхронных операций

```python
@pytest.mark.asyncio
async def test_async_chat(async_openai_mock_client):
    response = await async_openai_mock_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello async"}]
    )
    
    assert response.model == "gpt-4"
    assert response.choices[0].message.content
```

### Тестирование ошибок

```python
def test_error_handling(openai_mock_client):
    error_response = OpenAIResponseGenerator.error_response(
        error_type="rate_limit_exceeded",
        message="Too many requests"
    )
    
    openai_mock_client.chat.completions.set_custom_response(
        error_response,
        model="gpt-4"
    )
    
    # Тест должен обработать ошибку
    with pytest.raises(Exception):
        openai_mock_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test"}]
        )
```

## Интеграция с существующим кодом

Мок система автоматически перехватывает все импорты OpenAI:

```python
# Ваш существующий код
import openai

def my_function():
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    return response.choices[0].message.content

# Тест автоматически использует моки
def test_my_function():
    result = my_function()
    assert result  # Получаем мок-ответ
```

## Переменные окружения

Система автоматически устанавливает тестовые переменные:

- `OPENAI_API_KEY=test-openai-key-for-testing`
- `TESTING=true`

## Структура файлов

```
tests/mocks/
├── __init__.py              # Экспорты основных классов
├── openai_mock.py           # Мок-клиенты OpenAI
├── responses.py             # Генератор ответов
└── README.md               # Эта документация

tests/fixtures/
└── openai_fixtures.py       # Дополнительные фикстуры

tests/
├── conftest.py             # Автоматические фикстуры
└── test_openai_mocks.py    # Тесты мок-системы
```

## Отключение моков

Для интеграционных тестов с реальным API:

```python
@pytest.mark.integration
def test_real_api():
    # Используйте реальный API ключ
    import openai
    
    client = openai.OpenAI(api_key="real-api-key")
    # Реальный вызов API
```

Запуск только unit тестов (с моками):
```bash
pytest -m "not integration"
```

Запуск интеграционных тестов:
```bash
pytest -m integration
```

## Лучшие практики

1. **Используйте автоматические моки** - не создавайте клиенты вручную
2. **Тестируйте поведение, а не реализацию** - проверяйте результат, а не API вызовы
3. **Используйте кастомные ответы для специфических сценариев**
4. **Сбрасывайте состояние между тестами** - используйте фикстуру `reset_openai_mocks`
5. **Тестируйте обработку ошибок** - используйте `error_response`

## Расширение системы

Для добавления новых методов API:

1. Добавьте метод в `OpenAIResponseGenerator`
2. Реализуйте мок в соответствующем классе
3. Добавьте тесты в `test_openai_mocks.py`
4. Обновите документацию

## Troubleshooting

### Проблема: Тесты все еще делают реальные API вызовы

**Решение**: Убедитесь, что:
- Файл `conftest.py` находится в корне папки `tests`
- Фикстуры `mock_openai_client` активны
- Переменная `OPENAI_API_KEY` установлена в тестовое значение

### Проблема: Кастомные ответы не работают

**Решение**: Проверьте:
- Правильность модели в `set_custom_response`
- Соответствие параметров `stream`
- Порядок вызовов (сначала `set_custom_response`, потом `create`)

### Проблема: Асинхронные тесты падают

**Решение**: Убедитесь, что:
- Используете `@pytest.mark.asyncio`
- Правильно ожидаете (`await`) асинхронные вызовы
- Используете `async_openai_mock_client` фикстуру