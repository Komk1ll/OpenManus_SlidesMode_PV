import json
import os
from typing import Any, Dict, List, Optional
import requests
import asyncio

from app.tool.base import BaseTool, ToolResult
from app.logger import logger
from app.llm import LLM


class GenerateStructureTool(BaseTool):
    """Tool for generating presentation structure with language detection"""
    
    name = "generate_structure"
    description = "Generate a structured outline for a presentation including slide titles, descriptions, and flow"
    parameters = {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Main topic of the presentation"
            },
            "description": {
                "type": "string", 
                "description": "Additional description or context for the presentation"
            }
        },
        "required": ["topic"]
    }

    def _detect_language(self, text: str) -> str:
        """Detect if text contains Cyrillic characters (Russian) or is English"""
        import re
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

    async def execute(self, topic: str, description: str = "") -> ToolResult:
        """Generate presentation structure using LLM with language detection"""
        try:
            llm = LLM()
            
            # Detect language from topic and description
            combined_text = f"{topic} {description}"
            language = self._detect_language(combined_text)
            
            # Get language-specific prompt
            prompt = self._get_language_specific_prompt(topic, description, language)

            messages = [{"role": "user", "content": prompt}]
            response = await llm.ask(messages)
            
            if response and response.content:
                # Try to parse as JSON
                try:
                    structure = json.loads(response.content)
                    # Validate required fields
                    if not isinstance(structure, dict) or "title" not in structure or "slides" not in structure:
                        return ToolResult(error="Generated structure missing required fields 'title' or 'slides'")
                    return ToolResult(output=structure)
                except json.JSONDecodeError:
                    # If not valid JSON, try to extract JSON from response
                    content = response.content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    
                    structure = json.loads(content.strip())
                    return ToolResult(output=structure)
            else:
                return ToolResult(error="Failed to generate presentation structure")
                
        except Exception as e:
            logger.error(f"Error in GenerateStructureTool: {str(e)}")
            return ToolResult(error=f"Structure generation failed: {str(e)}")


class GenerateSlideContentTool(BaseTool):
    """Tool for generating detailed content for individual slides with enhanced capabilities"""
    
    name = "generate_slide_content"
    description = "Generate detailed content for a specific slide including title, bullet points, explanations, quotes, and code examples"
    parameters = {
        "type": "object",
        "properties": {
            "slide_info": {
                "type": "object",
                "description": "Information about the slide from the structure"
            },
            "presentation_topic": {
                "type": "string",
                "description": "Overall presentation topic for context"
            },
            "presentation_context": {
                "type": "string",
                "description": "Additional context about the presentation"
            }
        },
        "required": ["slide_info"]
    }

    def _detect_language(self, text: str) -> str:
        """Detect if text contains Cyrillic characters (Russian) or is English"""
        import re
        cyrillic_pattern = re.compile(r'[а-яё]', re.IGNORECASE)
        if cyrillic_pattern.search(text):
            return "russian"
        return "english"

    def _get_enhanced_prompt(self, slide_info: Dict, presentation_topic: str, presentation_context: str, language: str) -> str:
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

    async def execute(self, slide_info: Dict, presentation_topic: str = "", presentation_context: str = "") -> ToolResult:
        """Generate detailed slide content with enhanced capabilities"""
        try:
            llm = LLM()
            
            # Detect language from slide info and presentation topic
            combined_text = f"{slide_info.get('title', '')} {presentation_topic} {presentation_context}"
            language = self._detect_language(combined_text)
            
            # Get enhanced language-specific prompt
            prompt = self._get_enhanced_prompt(slide_info, presentation_topic, presentation_context, language)

            # Use increased max_tokens for larger content generation
            messages = [{"role": "user", "content": prompt}]
            response = await llm.ask(messages, max_tokens=12000)  # Increased from default
            
            if response and response.content:
                try:
                    content = json.loads(response.content)
                    # Validate required fields
                    if not isinstance(content, dict):
                        return ToolResult(error="Generated content is not a valid JSON object")
                    
                    required_fields = ["title", "content", "notes"]
                    missing_fields = [field for field in required_fields if field not in content]
                    if missing_fields:
                        return ToolResult(error=f"Generated content missing required fields: {', '.join(missing_fields)}")
                    
                    # Validate content structure
                    if not isinstance(content.get("content"), list):
                        return ToolResult(error="Content field must be a list of content items")
                    
                    return ToolResult(output=content)
                except json.JSONDecodeError as e:
                    # Enhanced JSON parsing with better error handling
                    try:
                        content_text = response.content.strip()
                        
                        # Remove markdown code blocks
                        if content_text.startswith('```json'):
                            content_text = content_text[7:]
                        elif content_text.startswith('```'):
                            content_text = content_text[3:]
                        
                        if content_text.endswith('```'):
                            content_text = content_text[:-3]
                        
                        # Try to find JSON within the response
                        import re
                        json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
                        if json_match:
                            content_text = json_match.group()
                        
                        content = json.loads(content_text.strip())
                        
                        # Validate parsed content
                        required_fields = ["title", "content", "notes"]
                        missing_fields = [field for field in required_fields if field not in content]
                        if missing_fields:
                            return ToolResult(error=f"Parsed content missing required fields: {', '.join(missing_fields)}")
                        
                        return ToolResult(output=content)
                    except (json.JSONDecodeError, AttributeError) as parse_error:
                        logger.error(f"JSON parsing failed: {str(parse_error)}")
                        logger.error(f"Raw response: {response.content[:500]}...")
                        return ToolResult(error=f"Failed to parse JSON response: {str(parse_error)}")
            else:
                return ToolResult(error="Failed to generate slide content - no response from LLM")
                
        except Exception as e:
            logger.error(f"Error in GenerateSlideContentTool: {str(e)}")
            return ToolResult(error=f"Content generation failed: {str(e)}")


class SearchImageTool(BaseTool):
    """Tool for searching relevant images for slides using Unsplash and Tavily APIs"""
    
    name = "search_image"
    description = "Search for relevant images for presentation slides using multiple sources"
    parameters = {
        "type": "object",
        "properties": {
            "slide_title": {
                "type": "string",
                "description": "Title of the slide"
            },
            "slide_content": {
                "type": "string", 
                "description": "Content of the slide for context"
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Keywords for image search"
            },
            "use_unsplash": {
                "type": "boolean",
                "description": "Whether to use Unsplash API (default: True for professional images)"
            },
            "image_type": {
                "type": "string",
                "description": "Type of image needed (professional, general, technical)"
            }
        },
        "required": ["slide_title"]
    }

    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL points to a valid image file"""
        if not url:
            return False
        
        # Check for direct image extensions
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        url_lower = url.lower()
        
        # Direct extension check
        if any(url_lower.endswith(ext) for ext in valid_extensions):
            return True
        
        # Unsplash URLs are valid even without extensions
        if 'unsplash.com' in url_lower or 'images.unsplash.com' in url_lower:
            return True
        
        # Check for image parameters in URL (common in APIs)
        if any(param in url_lower for param in ['w=', 'h=', 'format=', 'fm=jpg', 'fm=png']):
            return True
        
        return False

    def _search_unsplash(self, query: str, unsplash_key: str) -> Optional[str]:
        """Search for images using Unsplash API"""
        try:
            url = "https://api.unsplash.com/photos/random"
            params = {
                "query": query,
                "client_id": unsplash_key,
                "count": 1,
                "orientation": "landscape"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle both single photo and array responses
                if isinstance(data, list) and len(data) > 0:
                    photo = data[0]
                elif isinstance(data, dict):
                    photo = data
                else:
                    return None
                
                # Get the best quality URL
                urls = photo.get('urls', {})
                image_url = urls.get('regular') or urls.get('full') or urls.get('raw')
                
                if image_url and self._is_valid_image_url(image_url):
                    logger.info(f"Found Unsplash image for query '{query}': {image_url}")
                    return image_url
                
            else:
                logger.warning(f"Unsplash API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Unsplash search error: {str(e)}")
        
        return None

    def _search_tavily(self, query: str, tavily_key: str) -> Optional[str]:
        """Search for images using Tavily API"""
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": tavily_key,
                "query": query,
                "search_depth": "basic",
                "include_images": True,
                "include_answer": False,
                "max_results": 5
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                images = data.get('images', [])
                
                # Filter for valid image URLs
                for image in images:
                    image_url = image.get('url', '')
                    if self._is_valid_image_url(image_url):
                        logger.info(f"Found Tavily image for query '{query}': {image_url}")
                        return image_url
                
                logger.warning(f"No valid images found in Tavily results for query: {query}")
            else:
                logger.error(f"Tavily API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
        
        return None

    def _determine_use_unsplash(self, slide_title: str, keywords: List[str], image_type: str) -> bool:
        """Determine whether to use Unsplash based on slide content"""
        if image_type:
            # Use Unsplash for professional and general images
            if image_type.lower() in ['professional', 'general']:
                return True
            # Use Tavily for technical images (more likely to find specific technical content)
            elif image_type.lower() == 'technical':
                return False
        
        # Check for professional keywords
        professional_keywords = ['business', 'professional', 'corporate', 'presentation', 'meeting']
        if keywords:
            for keyword in keywords:
                if any(prof_word in keyword.lower() for prof_word in professional_keywords):
                    return True
        
        # Check slide title for professional terms
        if any(prof_word in slide_title.lower() for prof_word in professional_keywords):
            return True
        
        # Default to Unsplash for general use
        return True

    async def execute(self, slide_title: str, slide_content: str = "", keywords: List[str] = None, 
                     use_unsplash: bool = None, image_type: str = "") -> ToolResult:
        """Search for relevant images using Unsplash and Tavily APIs"""
        try:
            from app.config import config
            
            # Get API keys from config
            tavily_api_key = None
            unsplash_access_key = None
            
            if config.presentation_config:
                tavily_api_key = config.presentation_config.tavily_api_key
                unsplash_access_key = config.presentation_config.unsplash_access_key
            
            # Fallback to environment variables
            if not tavily_api_key:
                tavily_api_key = os.getenv('TAVILY_API_KEY', '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')
            
            if not unsplash_access_key:
                unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY')
            
            # Prepare search query
            search_query = slide_title
            if keywords:
                search_query += " " + " ".join(keywords[:3])  # Use top 3 keywords
            
            # Determine which source to use
            if use_unsplash is None:
                use_unsplash = self._determine_use_unsplash(slide_title, keywords or [], image_type)
            
            image_url = None
            
            # Try Unsplash first if requested and key is available
            if use_unsplash and unsplash_access_key and unsplash_access_key != "YOUR_UNSPLASH_ACCESS_KEY":
                logger.info(f"Searching Unsplash for: {search_query}")
                image_url = self._search_unsplash(search_query, unsplash_access_key)
                
                if image_url:
                    logger.info(f"Successfully found image from Unsplash source")
                    return ToolResult(output=image_url)
            
            # Fallback to Tavily if Unsplash failed or wasn't used
            if not image_url and tavily_api_key:
                logger.info(f"Searching Tavily for: {search_query}")
                image_url = self._search_tavily(search_query, tavily_api_key)
                
                if image_url:
                    logger.info(f"Successfully found image from Tavily source")
                    return ToolResult(output=image_url)
            
            # No image found from either source
            logger.warning(f"No images found for query: {search_query}")
            return ToolResult(output=None)
                
        except Exception as e:
            logger.error(f"Error in SearchImageTool: {str(e)}")
            return ToolResult(error=f"Image search failed: {str(e)}")


class ExportPresentationTool(BaseTool):
    """Tool for exporting presentations to various formats including PDF"""
    
    name = "export_presentation"
    description = "Export presentation to markdown, HTML, JSON, or PDF format"
    parameters = {
        "type": "object",
        "properties": {
            "presentation": {
                "type": "object",
                "description": "Complete presentation data"
            },
            "format": {
                "type": "string",
                "enum": ["markdown", "html", "json", "pdf"],
                "description": "Export format"
            },
            "output_path": {
                "type": "string",
                "description": "Output file path (optional)"
            }
        },
        "required": ["presentation", "format"]
    }

    async def execute(self, presentation: Dict, format: str = "markdown", output_path: str = None) -> ToolResult:
        """Export presentation to specified format"""
        try:
            if format == "markdown":
                content = self._export_to_markdown(presentation)
            elif format == "html":
                content = self._export_to_html(presentation)
            elif format == "json":
                content = json.dumps(presentation, indent=2, ensure_ascii=False)
            elif format == "pdf":
                return await self._export_to_pdf(presentation, output_path)
            else:
                return ToolResult(error=f"Unsupported format: {format}")
            
            # Save to file if path provided (for non-PDF formats)
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return ToolResult(output=f"Presentation exported to {output_path}")
            else:
                return ToolResult(output=content)
                
        except Exception as e:
            logger.error(f"Error in ExportPresentationTool: {str(e)}")
            return ToolResult(error=f"Export failed: {str(e)}")

    async def _export_to_pdf(self, presentation: Dict, output_path: str = None) -> ToolResult:
        """Export presentation to PDF format using HTML as intermediate"""
        try:
            import pdfkit
            
            # Generate HTML content first
            html_content = self._export_to_html(presentation)
            
            # Configure PDF options for better presentation formatting
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
                'print-media-type': None
            }
            
            # Determine output path
            if not output_path:
                output_path = 'presentation.pdf'
            
            # Generate PDF from HTML
            pdfkit.from_string(html_content, output_path, options=options)
            
            logger.info(f"Successfully exported presentation to PDF: {output_path}")
            return ToolResult(output=f"Presentation PDF saved to {output_path}")
            
        except ImportError:
            error_msg = "pdfkit library not found. Please install it with: pip install pdfkit"
            logger.error(error_msg)
            return ToolResult(error=error_msg)
        except OSError as e:
            if "wkhtmltopdf" in str(e):
                error_msg = "wkhtmltopdf not found. Please install it: sudo apt-get install wkhtmltopdf"
                logger.error(error_msg)
                return ToolResult(error=error_msg)
            else:
                logger.error(f"PDF generation OS error: {str(e)}")
                return ToolResult(error=f"PDF generation failed: {str(e)}")
        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}")
            return ToolResult(error=f"PDF generation failed: {str(e)}")

    def _get_enhanced_html_for_pdf(self, presentation: Dict) -> str:
        """Generate enhanced HTML specifically optimized for PDF export"""
        title = presentation.get('title', 'Presentation')
        description = presentation.get('description', '')
        
        html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            margin: 2cm;
            @bottom-center {{
                content: counter(page);
            }}
        }}
        body {{ 
            font-family: 'Arial', sans-serif; 
            margin: 0; 
            padding: 20px;
            line-height: 1.6; 
            color: #333;
        }}
        .title-page {{
            text-align: center;
            margin-bottom: 50px;
            page-break-after: always;
        }}
        .title-page h1 {{
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        .title-page p {{
            font-size: 1.2em;
            color: #7f8c8d;
        }}
        .slide {{ 
            margin-bottom: 40px; 
            page-break-after: always;
            min-height: 500px;
        }}
        .slide h2 {{ 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 10px;
            font-size: 1.8em;
            margin-bottom: 20px;
        }}
        .slide h3 {{ 
            color: #34495e;
            font-size: 1.3em;
            margin-bottom: 15px;
        }}
        .slide img {{ 
            max-width: 100%; 
            height: auto; 
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .notes {{ 
            font-style: italic; 
            color: #7f8c8d; 
            margin-top: 30px;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
        }}
        ul {{ 
            margin: 15px 0;
            padding-left: 25px;
        }}
        li {{ 
            margin: 8px 0;
            line-height: 1.5;
        }}
        pre {{ 
            background: #2c3e50; 
            color: #ecf0f1;
            padding: 20px; 
            border-radius: 8px; 
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            margin: 15px 0;
        }}
        blockquote {{
            border-left: 4px solid #e74c3c;
            margin: 15px 0;
            padding: 10px 20px;
            background-color: #fdf2f2;
            font-style: italic;
        }}
        .quote-author {{
            text-align: right;
            font-weight: bold;
            color: #e74c3c;
            margin-top: 10px;
        }}
        .content-item {{
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1>{title}</h1>
        {f'<p>{description}</p>' if description else ''}
    </div>
"""
        
        slides = presentation.get('slides', [])
        for i, slide in enumerate(slides, 1):
            html_content += f'    <div class="slide">\n'
            html_content += f'        <h2>Слайд {i}: {slide.get("title", "Untitled")}</h2>\n'
            
            if slide.get('subtitle'):
                html_content += f'        <h3>{slide.get("subtitle")}</h3>\n'
            
            content_items = slide.get('content', [])
            for item in content_items:
                item_type = item.get('type', 'paragraph')
                text = item.get('text', '')
                
                html_content += '        <div class="content-item">\n'
                
                if item_type == 'bullet_point':
                    html_content += f'            <ul><li>{text}</li></ul>\n'
                elif item_type == 'paragraph':
                    html_content += f'            <p>{text}</p>\n'
                elif item_type == 'code':
                    language = item.get('language', '')
                    html_content += f'            <pre><code class="{language}">{text}</code></pre>\n'
                elif item_type == 'quote':
                    author = item.get('author', '')
                    html_content += f'            <blockquote>{text}'
                    if author:
                        html_content += f'<div class="quote-author">— {author}</div>'
                    html_content += '</blockquote>\n'
                
                html_content += '        </div>\n'
            
            if slide.get('image_url'):
                html_content += f'        <img src="{slide.get("image_url")}" alt="Slide Image">\n'
            
            if slide.get('notes'):
                html_content += f'        <div class="notes"><strong>Заметки докладчика:</strong> {slide.get("notes")}</div>\n'
            
            html_content += '    </div>\n'
        
        html_content += '</body>\n</html>'
        
        return html_content

    def _export_to_markdown(self, presentation: Dict) -> str:
        """Export presentation to markdown format"""
        md_content = []
        
        # Title and description
        title = presentation.get('title', 'Presentation')
        description = presentation.get('description', '')
        
        md_content.append(f"# {title}\n")
        if description:
            md_content.append(f"{description}\n")
        
        # Slides
        slides = presentation.get('slides', [])
        for i, slide in enumerate(slides, 1):
            md_content.append(f"\n---\n\n## Слайд {i}: {slide.get('title', 'Untitled')}\n")
            
            if slide.get('subtitle'):
                md_content.append(f"### {slide.get('subtitle')}\n")
            
            # Content
            content_items = slide.get('content', [])
            for item in content_items:
                item_type = item.get('type', 'paragraph')
                text = item.get('text', '')
                
                if item_type == 'bullet_point':
                    md_content.append(f"- {text}\n")
                elif item_type == 'paragraph':
                    md_content.append(f"{text}\n")
                elif item_type == 'code':
                    language = item.get('language', '')
                    md_content.append(f"```{language}\n{text}\n```\n")
                elif item_type == 'quote':
                    md_content.append(f"> {text}\n")
            
            # Image
            if slide.get('image_url'):
                md_content.append(f"\n![Slide Image]({slide.get('image_url')})\n")
            
            # Notes
            if slide.get('notes'):
                md_content.append(f"\n*Заметки докладчика: {slide.get('notes')}*\n")
        
        return '\n'.join(md_content)

    def _export_to_html(self, presentation: Dict) -> str:
        """Export presentation to HTML format"""
        html_content = []
        
        title = presentation.get('title', 'Presentation')
        description = presentation.get('description', '')
        
        html_content.append(f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .slide {{ margin-bottom: 50px; page-break-after: always; }}
        .slide h2 {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
        .slide h3 {{ color: #666; }}
        .slide img {{ max-width: 100%; height: auto; margin: 20px 0; }}
        .notes {{ font-style: italic; color: #666; margin-top: 20px; }}
        ul {{ margin: 10px 0; }}
        li {{ margin: 5px 0; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>{title}</h1>""")
        
        if description:
            html_content.append(f"    <p>{description}</p>")
        
        slides = presentation.get('slides', [])
        for i, slide in enumerate(slides, 1):
            html_content.append(f'    <div class="slide">')
            html_content.append(f'        <h2>Слайд {i}: {slide.get("title", "Untitled")}</h2>')
            
            if slide.get('subtitle'):
                html_content.append(f'        <h3>{slide.get("subtitle")}</h3>')
            
            content_items = slide.get('content', [])
            for item in content_items:
                item_type = item.get('type', 'paragraph')
                text = item.get('text', '')
                
                if item_type == 'bullet_point':
                    html_content.append(f'        <ul><li>{text}</li></ul>')
                elif item_type == 'paragraph':
                    html_content.append(f'        <p>{text}</p>')
                elif item_type == 'code':
                    language = item.get('language', '')
                    html_content.append(f'        <pre><code class="{language}">{text}</code></pre>')
                elif item_type == 'quote':
                    html_content.append(f'        <blockquote>{text}</blockquote>')
            
            if slide.get('image_url'):
                html_content.append(f'        <img src="{slide.get("image_url")}" alt="Slide Image">')
            
            if slide.get('notes'):
                html_content.append(f'        <div class="notes">Заметки докладчика: {slide.get("notes")}</div>')
            
            html_content.append('    </div>')
        
        html_content.append('</body>\n</html>')
        
        return '\n'.join(html_content)

