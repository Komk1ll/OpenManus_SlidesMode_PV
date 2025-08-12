#!/usr/bin/env python3
"""
PresentationAgent - Comprehensive presentation generation agent
Integrates all enhanced tools for complete presentation workflow
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from app.tool.presentation_tools import (
    GenerateStructureTool,
    GenerateSlideContentTool,
    SearchImageTool,
    ExportPresentationTool
)
from app.tool.base import ToolResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PresentationConfig:
    """Configuration for presentation generation"""
    topic: str
    slide_count: int = 10
    language: str = "auto"  # auto, english, russian
    include_images: bool = True
    export_formats: List[str] = None
    output_directory: str = "./presentations"
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["markdown", "html", "json"]


class PresentationAgent:
    """
    Comprehensive presentation generation agent that orchestrates
    all enhanced tools for complete presentation workflow
    """
    
    def __init__(self):
        """Initialize the PresentationAgent with all enhanced tools"""
        self.structure_tool = GenerateStructureTool()
        self.content_tool = GenerateSlideContentTool()
        self.image_tool = SearchImageTool()
        self.export_tool = ExportPresentationTool()
        
        logger.info("PresentationAgent initialized with enhanced tools")
    
    async def create_presentation(self, config: PresentationConfig) -> Dict[str, Any]:
        """
        Create a complete presentation using the enhanced workflow
        
        Args:
            config: PresentationConfig with all generation parameters
            
        Returns:
            Dict containing the complete presentation data and metadata
        """
        logger.info(f"Starting presentation creation for topic: {config.topic}")
        
        try:
            # Step 1: Generate presentation structure
            logger.info("Step 1: Generating presentation structure...")
            structure_result = await self._generate_structure(config)
            
            if structure_result.error:
                logger.error(f"Structure generation failed: {structure_result.error}")
                return {"error": f"Structure generation failed: {structure_result.error}"}
            
            structure = structure_result.output
            logger.info(f"Generated structure with {len(structure.get('slides', []))} slides")
            
            # Step 2: Generate content for each slide
            logger.info("Step 2: Generating slide content...")
            slides_with_content = await self._generate_slide_contents(structure, config)
            
            # Step 3: Search and add images (if enabled)
            if config.include_images:
                logger.info("Step 3: Searching and adding images...")
                slides_with_images = await self._add_images_to_slides(slides_with_content, config)
            else:
                slides_with_images = slides_with_content
                logger.info("Step 3: Skipped image search (disabled in config)")
            
            # Step 4: Compile final presentation
            logger.info("Step 4: Compiling final presentation...")
            presentation = self._compile_presentation(structure, slides_with_images, config)
            
            # Step 5: Export to requested formats
            logger.info("Step 5: Exporting presentation...")
            export_results = await self._export_presentation(presentation, config)
            
            # Step 6: Prepare final result
            result = {
                "success": True,
                "presentation": presentation,
                "exports": export_results,
                "metadata": {
                    "topic": config.topic,
                    "slide_count": len(slides_with_images),
                    "language": self._detect_language(config.topic),
                    "includes_images": config.include_images,
                    "export_formats": config.export_formats
                }
            }
            
            logger.info("Presentation creation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Presentation creation failed: {str(e)}")
            return {"error": f"Presentation creation failed: {str(e)}"}
    
    async def _generate_structure(self, config: PresentationConfig) -> ToolResult:
        """Generate the presentation structure using GenerateStructureTool"""
        return await self.structure_tool.execute(
            topic=config.topic,
            slide_count=config.slide_count,
            language=config.language
        )
    
    async def _generate_slide_contents(self, structure: Dict, config: PresentationConfig) -> List[Dict]:
        """Generate content for each slide using GenerateSlideContentTool"""
        slides_with_content = []
        slides = structure.get('slides', [])
        presentation_topic = structure.get('title', config.topic)
        presentation_context = structure.get('description', '')
        
        for i, slide_info in enumerate(slides, 1):
            logger.info(f"Generating content for slide {i}/{len(slides)}: {slide_info.get('title', 'Untitled')}")
            
            try:
                content_result = await self.content_tool.execute(
                    slide_info=slide_info,
                    presentation_topic=presentation_topic,
                    presentation_context=presentation_context
                )
                
                if content_result.error:
                    logger.warning(f"Content generation failed for slide {i}: {content_result.error}")
                    # Use fallback content
                    slide_content = self._create_fallback_content(slide_info)
                else:
                    slide_content = content_result.output
                
                # Merge slide info with generated content
                final_slide = {**slide_info, **slide_content}
                slides_with_content.append(final_slide)
                
            except Exception as e:
                logger.error(f"Error generating content for slide {i}: {str(e)}")
                # Use fallback content
                slide_content = self._create_fallback_content(slide_info)
                final_slide = {**slide_info, **slide_content}
                slides_with_content.append(final_slide)
        
        return slides_with_content
    
    async def _add_images_to_slides(self, slides: List[Dict], config: PresentationConfig) -> List[Dict]:
        """Add images to slides using SearchImageTool"""
        slides_with_images = []
        
        for i, slide in enumerate(slides, 1):
            logger.info(f"Searching image for slide {i}/{len(slides)}: {slide.get('title', 'Untitled')}")
            
            try:
                # Prepare image search parameters
                slide_title = slide.get('title', '')
                slide_content = self._extract_text_content(slide.get('content', []))
                keywords = slide.get('keywords', [])
                image_type = slide.get('image_type', 'general')
                
                # Search for image
                image_result = await self.image_tool.execute(
                    slide_title=slide_title,
                    slide_content=slide_content,
                    keywords=keywords,
                    image_type=image_type
                )
                
                if image_result.error:
                    logger.warning(f"Image search failed for slide {i}: {image_result.error}")
                    slide['image_url'] = None
                else:
                    slide['image_url'] = image_result.output
                    if image_result.output:
                        logger.info(f"Found image for slide {i}")
                    else:
                        logger.warning(f"No image found for slide {i}")
                
            except Exception as e:
                logger.error(f"Error searching image for slide {i}: {str(e)}")
                slide['image_url'] = None
            
            slides_with_images.append(slide)
        
        return slides_with_images
    
    async def _export_presentation(self, presentation: Dict, config: PresentationConfig) -> Dict[str, Any]:
        """Export presentation to requested formats using ExportPresentationTool"""
        export_results = {}
        
        for format_type in config.export_formats:
            logger.info(f"Exporting presentation to {format_type.upper()} format...")
            
            try:
                # Determine output path
                output_path = f"{config.output_directory}/presentation.{format_type}"
                if format_type == "pdf":
                    output_path = f"{config.output_directory}/presentation.pdf"
                
                export_result = await self.export_tool.execute(
                    presentation=presentation,
                    format=format_type,
                    output_path=output_path
                )
                
                if export_result.error:
                    logger.error(f"Export to {format_type} failed: {export_result.error}")
                    export_results[format_type] = {"success": False, "error": export_result.error}
                else:
                    logger.info(f"Successfully exported to {format_type}")
                    export_results[format_type] = {
                        "success": True, 
                        "output": export_result.output,
                        "path": output_path if format_type != "pdf" else output_path
                    }
                
            except Exception as e:
                logger.error(f"Error exporting to {format_type}: {str(e)}")
                export_results[format_type] = {"success": False, "error": str(e)}
        
        return export_results
    
    def _compile_presentation(self, structure: Dict, slides: List[Dict], config: PresentationConfig) -> Dict[str, Any]:
        """Compile the final presentation data structure"""
        return {
            "title": structure.get('title', config.topic),
            "description": structure.get('description', ''),
            "slides": slides,
            "metadata": {
                "created_by": "PresentationAgent",
                "topic": config.topic,
                "slide_count": len(slides),
                "language": self._detect_language(config.topic),
                "includes_images": config.include_images
            }
        }
    
    def _create_fallback_content(self, slide_info: Dict) -> Dict[str, Any]:
        """Create fallback content when content generation fails"""
        return {
            "title": slide_info.get('title', 'Slide Title'),
            "subtitle": slide_info.get('subtitle', ''),
            "content": [
                {
                    "type": "paragraph",
                    "text": f"Content for {slide_info.get('title', 'this slide')} will be generated."
                },
                {
                    "type": "bullet_point",
                    "text": "Key point 1"
                },
                {
                    "type": "bullet_point",
                    "text": "Key point 2"
                }
            ],
            "notes": f"Speaker notes for {slide_info.get('title', 'this slide')}"
        }
    
    def _extract_text_content(self, content_items: List[Dict]) -> str:
        """Extract text content from content items for image search"""
        text_parts = []
        for item in content_items:
            if item.get('text'):
                text_parts.append(item['text'])
        return ' '.join(text_parts)
    
    def _detect_language(self, text: str) -> str:
        """Detect language of the text"""
        import re
        cyrillic_pattern = re.compile(r'[а-яё]', re.IGNORECASE)
        if cyrillic_pattern.search(text):
            return "russian"
        return "english"
    
    async def create_quick_presentation(self, topic: str, slide_count: int = 8) -> Dict[str, Any]:
        """
        Quick presentation creation with default settings
        
        Args:
            topic: Presentation topic
            slide_count: Number of slides to generate
            
        Returns:
            Dict containing the complete presentation
        """
        config = PresentationConfig(
            topic=topic,
            slide_count=slide_count,
            include_images=True,
            export_formats=["markdown", "html", "json"]
        )
        
        return await self.create_presentation(config)
    
    async def create_presentation_with_pdf(self, topic: str, slide_count: int = 8) -> Dict[str, Any]:
        """
        Create presentation with PDF export included
        
        Args:
            topic: Presentation topic
            slide_count: Number of slides to generate
            
        Returns:
            Dict containing the complete presentation with PDF export
        """
        config = PresentationConfig(
            topic=topic,
            slide_count=slide_count,
            include_images=True,
            export_formats=["markdown", "html", "json", "pdf"]
        )
        
        return await self.create_presentation(config)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return ["markdown", "html", "json", "pdf"]
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the PresentationAgent capabilities"""
        return {
            "name": "PresentationAgent",
            "version": "2.0.0",
            "capabilities": [
                "Language-aware structure generation",
                "Enhanced content generation with quotes and code",
                "Unsplash and Tavily image integration",
                "PDF export functionality",
                "Multi-format export (markdown, html, json, pdf)",
                "Comprehensive error handling and logging"
            ],
            "supported_languages": ["english", "russian", "auto-detect"],
            "supported_formats": self.get_supported_formats(),
            "tools": [
                "GenerateStructureTool",
                "GenerateSlideContentTool", 
                "SearchImageTool",
                "ExportPresentationTool"
            ]
        }


# Convenience functions for easy usage
async def create_presentation(topic: str, slide_count: int = 8, include_pdf: bool = False) -> Dict[str, Any]:
    """
    Convenience function to create a presentation
    
    Args:
        topic: Presentation topic
        slide_count: Number of slides
        include_pdf: Whether to include PDF export
        
    Returns:
        Complete presentation data
    """
    agent = PresentationAgent()
    
    if include_pdf:
        return await agent.create_presentation_with_pdf(topic, slide_count)
    else:
        return await agent.create_quick_presentation(topic, slide_count)


async def create_custom_presentation(config: PresentationConfig) -> Dict[str, Any]:
    """
    Create a presentation with custom configuration
    
    Args:
        config: PresentationConfig with custom settings
        
    Returns:
        Complete presentation data
    """
    agent = PresentationAgent()
    return await agent.create_presentation(config)


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        # Create a simple presentation
        result = await create_presentation("Artificial Intelligence in Healthcare", 6)
        
        if result.get("success"):
            print("✅ Presentation created successfully!")
            print(f"Title: {result['presentation']['title']}")
            print(f"Slides: {len(result['presentation']['slides'])}")
            print(f"Exports: {list(result['exports'].keys())}")
        else:
            print(f"❌ Presentation creation failed: {result.get('error')}")
    
    asyncio.run(main())

