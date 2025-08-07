#!/usr/bin/env python3
"""
Test script for enhanced ExportPresentationTool with PDF export
"""

import json
import os
import tempfile
from typing import Dict


class ExportPresentationToolTest:
    """Isolated test version of ExportPresentationTool"""
    
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
        title = presentation.get('title', 'Presentation')
        description = presentation.get('description', '')
        
        html_content = f"""<!DOCTYPE html>
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
    <h1>{title}</h1>"""
        
        if description:
            html_content += f"    <p>{description}</p>\n"
        
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
                
                if item_type == 'bullet_point':
                    html_content += f'        <ul><li>{text}</li></ul>\n'
                elif item_type == 'paragraph':
                    html_content += f'        <p>{text}</p>\n'
                elif item_type == 'code':
                    language = item.get('language', '')
                    html_content += f'        <pre><code class="{language}">{text}</code></pre>\n'
                elif item_type == 'quote':
                    html_content += f'        <blockquote>{text}</blockquote>\n'
            
            if slide.get('image_url'):
                html_content += f'        <img src="{slide.get("image_url")}" alt="Slide Image">\n'
            
            if slide.get('notes'):
                html_content += f'        <div class="notes"><em>Заметки докладчика: {slide.get("notes")}</em></div>\n'
            
            html_content += '    </div>\n'
        
        html_content += '</body>\n</html>'
        return html_content

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


def create_test_presentation() -> Dict:
    """Create a test presentation with various content types"""
    return {
        "title": "Test Presentation",
        "description": "A comprehensive test presentation with various content types",
        "slides": [
            {
                "title": "Introduction",
                "subtitle": "Getting Started",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "This is a test presentation to verify export functionality."
                    },
                    {
                        "type": "bullet_point",
                        "text": "First bullet point with important information"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Second bullet point with additional details"
                    }
                ],
                "image_url": "https://example.com/image1.jpg",
                "notes": "Introduction slide notes for the presenter"
            },
            {
                "title": "Technical Content",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "This slide demonstrates technical content with code examples."
                    },
                    {
                        "type": "code",
                        "language": "python",
                        "text": "def hello_world():\n    print('Hello, World!')\n    return True"
                    },
                    {
                        "type": "quote",
                        "text": "Code is poetry written for machines to understand.",
                        "author": "Anonymous Developer"
                    }
                ],
                "notes": "Technical slide with code examples and quotes"
            }
        ]
    }


def test_format_support():
    """Test that all formats are supported"""
    print("🧪 Testing format support...")
    
    tool = ExportPresentationToolTest()
    presentation = create_test_presentation()
    
    # Test supported formats
    supported_formats = ["markdown", "html", "json"]
    
    for format_type in supported_formats:
        if format_type == "markdown":
            result = tool._export_to_markdown(presentation)
        elif format_type == "html":
            result = tool._export_to_html(presentation)
        elif format_type == "json":
            result = json.dumps(presentation, indent=2, ensure_ascii=False)
        
        assert result, f"Failed to export to {format_type}"
        assert len(result) > 0, f"Empty export for {format_type}"
        
        print(f"✅ {format_type.upper()} export works")
    
    return True


def test_markdown_export():
    """Test markdown export functionality"""
    print("🧪 Testing markdown export...")
    
    tool = ExportPresentationToolTest()
    presentation = create_test_presentation()
    
    markdown = tool._export_to_markdown(presentation)
    
    # Check for required elements
    assert "# Test Presentation" in markdown, "Title should be in markdown"
    assert "## Слайд 1: Introduction" in markdown, "Slide titles should be in markdown"
    assert "### Getting Started" in markdown, "Subtitles should be in markdown"
    assert "- First bullet point" in markdown, "Bullet points should be in markdown"
    assert "```python" in markdown, "Code blocks should be in markdown"
    assert "> Code is poetry" in markdown, "Quotes should be in markdown"
    assert "![Slide Image]" in markdown, "Images should be in markdown"
    assert "*Заметки докладчика:" in markdown, "Notes should be in markdown"
    
    print("✅ Markdown export contains all required elements")
    
    return True


def test_html_export():
    """Test HTML export functionality"""
    print("🧪 Testing HTML export...")
    
    tool = ExportPresentationToolTest()
    presentation = create_test_presentation()
    
    html = tool._export_to_html(presentation)
    
    # Check for required elements
    assert "<!DOCTYPE html>" in html, "HTML should have DOCTYPE"
    assert "<title>Test Presentation</title>" in html, "HTML should have title"
    assert "<h1>Test Presentation</h1>" in html, "HTML should have main heading"
    assert "<h2>Слайд 1: Introduction</h2>" in html, "HTML should have slide headings"
    assert "<h3>Getting Started</h3>" in html, "HTML should have subtitles"
    assert "<ul><li>First bullet point" in html, "HTML should have bullet points"
    assert "<pre><code" in html, "HTML should have code blocks"
    assert "<blockquote>" in html, "HTML should have quotes"
    assert '<img src="https://example.com/image1.jpg"' in html, "HTML should have images"
    assert "Заметки докладчика:" in html, "HTML should have notes"
    
    print("✅ HTML export contains all required elements")
    
    return True


def test_enhanced_html_for_pdf():
    """Test enhanced HTML for PDF export"""
    print("🧪 Testing enhanced HTML for PDF...")
    
    tool = ExportPresentationToolTest()
    presentation = create_test_presentation()
    
    html = tool._get_enhanced_html_for_pdf(presentation)
    
    # Check for PDF-specific styling
    assert "@page" in html, "PDF HTML should have @page styles"
    assert "page-break-after: always" in html, "PDF HTML should have page breaks"
    assert "title-page" in html, "PDF HTML should have title page"
    assert "quote-author" in html, "PDF HTML should have quote author styling"
    assert "content-item" in html, "PDF HTML should have content item styling"
    assert "margin: 2cm" in html, "PDF HTML should have page margins"
    
    print("✅ Enhanced HTML for PDF contains all required styling")
    
    return True


def test_content_types_handling():
    """Test handling of different content types"""
    print("🧪 Testing content types handling...")
    
    tool = ExportPresentationToolTest()
    
    # Create presentation with all content types
    presentation = {
        "title": "Content Types Test",
        "description": "Testing all content types",
        "slides": [
            {
                "title": "All Content Types",
                "content": [
                    {"type": "paragraph", "text": "This is a paragraph"},
                    {"type": "bullet_point", "text": "This is a bullet point"},
                    {"type": "code", "language": "javascript", "text": "console.log('Hello');"},
                    {"type": "quote", "text": "This is a quote", "author": "Test Author"}
                ]
            }
        ]
    }
    
    # Test markdown
    markdown = tool._export_to_markdown(presentation)
    assert "This is a paragraph" in markdown
    assert "- This is a bullet point" in markdown
    assert "```javascript" in markdown
    assert "> This is a quote" in markdown
    
    # Test HTML
    html = tool._export_to_html(presentation)
    assert "<p>This is a paragraph</p>" in html
    assert "<ul><li>This is a bullet point</li></ul>" in html
    assert '<pre><code class="javascript">' in html
    assert "<blockquote>This is a quote</blockquote>" in html
    
    # Test enhanced HTML
    enhanced_html = tool._get_enhanced_html_for_pdf(presentation)
    assert "<p>This is a paragraph</p>" in enhanced_html
    assert "<ul><li>This is a bullet point</li></ul>" in enhanced_html
    assert '<pre><code class="javascript">' in enhanced_html
    assert "<blockquote>This is a quote" in enhanced_html
    assert "— Test Author" in enhanced_html
    
    print("✅ All content types handled correctly")
    
    return True


def test_file_operations():
    """Test file save operations"""
    print("🧪 Testing file operations...")
    
    tool = ExportPresentationToolTest()
    presentation = create_test_presentation()
    
    # Test saving to temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test markdown save
        md_path = os.path.join(temp_dir, "test.md")
        markdown = tool._export_to_markdown(presentation)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        assert os.path.exists(md_path), "Markdown file should be created"
        assert os.path.getsize(md_path) > 0, "Markdown file should not be empty"
        
        # Test HTML save
        html_path = os.path.join(temp_dir, "test.html")
        html = tool._export_to_html(presentation)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        assert os.path.exists(html_path), "HTML file should be created"
        assert os.path.getsize(html_path) > 0, "HTML file should not be empty"
        
        # Test JSON save
        json_path = os.path.join(temp_dir, "test.json")
        json_content = json.dumps(presentation, indent=2, ensure_ascii=False)
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(json_content)
        
        assert os.path.exists(json_path), "JSON file should be created"
        assert os.path.getsize(json_path) > 0, "JSON file should not be empty"
    
    print("✅ File operations work correctly")
    
    return True


def main():
    """Run all tests"""
    print("🚀 Starting enhanced ExportPresentationTool tests...\n")
    
    tests = [
        ("Format Support", test_format_support),
        ("Markdown Export", test_markdown_export),
        ("HTML Export", test_html_export),
        ("Enhanced HTML for PDF", test_enhanced_html_for_pdf),
        ("Content Types Handling", test_content_types_handling),
        ("File Operations", test_file_operations),
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
        print("🎉 All ExportPresentationTool tests passed!")
        print("\n📝 Note: PDF export functionality requires pdfkit and wkhtmltopdf")
        print("   Install with: pip install pdfkit && sudo apt-get install wkhtmltopdf")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

