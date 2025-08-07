#!/usr/bin/env python3
"""
Test script for enhanced SearchImageTool with Unsplash integration
"""

import json
from typing import List, Optional


class SearchImageToolTest:
    """Isolated test version of SearchImageTool"""
    
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


def test_image_url_validation():
    """Test image URL validation functionality"""
    print("🧪 Testing image URL validation...")
    
    tool = SearchImageToolTest()
    
    # Test valid URLs
    valid_urls = [
        "https://example.com/image.jpg",
        "https://example.com/image.jpeg",
        "https://example.com/image.png",
        "https://example.com/image.webp",
        "https://images.unsplash.com/photo-123456",
        "https://unsplash.com/photos/abc123",
        "https://api.example.com/image?w=800&h=600",
        "https://api.example.com/image?format=jpg",
        "https://api.example.com/image?fm=png"
    ]
    
    for url in valid_urls:
        assert tool._is_valid_image_url(url), f"Should be valid: {url}"
    
    print("✅ Valid URLs correctly identified")
    
    # Test invalid URLs
    invalid_urls = [
        "",
        None,
        "https://example.com/page.html",
        "https://example.com/document.pdf",
        "https://example.com/video.mp4",
        "not-a-url"
    ]
    
    for url in invalid_urls:
        assert not tool._is_valid_image_url(url), f"Should be invalid: {url}"
    
    print("✅ Invalid URLs correctly rejected")
    
    return True


def test_unsplash_determination():
    """Test logic for determining when to use Unsplash"""
    print("🧪 Testing Unsplash source determination...")
    
    tool = SearchImageToolTest()
    
    # Test image_type based decisions
    test_cases = [
        # (slide_title, keywords, image_type, expected_unsplash)
        ("AI Overview", [], "professional", True),
        ("AI Overview", [], "general", True),
        ("AI Overview", [], "technical", False),
        ("Business Meeting", [], "", True),  # Professional title
        ("Corporate Strategy", [], "", True),  # Professional title
        ("Python Programming", ["code", "programming"], "", True),  # Default to Unsplash (no professional keywords but defaults to True)
        ("Team Presentation", ["business", "meeting"], "", True),  # Professional keywords
        ("Data Analysis", [], "", True),  # Default to Unsplash
    ]
    
    for slide_title, keywords, image_type, expected in test_cases:
        result = tool._determine_use_unsplash(slide_title, keywords, image_type)
        assert result == expected, f"Failed for {slide_title}, {keywords}, {image_type}: expected {expected}, got {result}"
    
    print("✅ Unsplash determination logic works correctly")
    
    return True


def test_professional_keyword_detection():
    """Test detection of professional keywords"""
    print("🧪 Testing professional keyword detection...")
    
    tool = SearchImageToolTest()
    
    # Test professional keywords in slide titles
    professional_titles = [
        "Business Strategy Overview",
        "Corporate Meeting Agenda", 
        "Professional Development",
        "Presentation Skills",
        "Team Meeting Notes"
    ]
    
    for title in professional_titles:
        result = tool._determine_use_unsplash(title, [], "")
        assert result == True, f"Should use Unsplash for professional title: {title}"
    
    print("✅ Professional titles correctly detected")
    
    # Test professional keywords in keyword lists
    professional_keyword_sets = [
        ["business", "strategy"],
        ["corporate", "finance"],
        ["professional", "development"],
        ["presentation", "skills"],
        ["meeting", "agenda"]
    ]
    
    for keywords in professional_keyword_sets:
        result = tool._determine_use_unsplash("Generic Title", keywords, "")
        assert result == True, f"Should use Unsplash for professional keywords: {keywords}"
    
    print("✅ Professional keywords correctly detected")
    
    return True


def test_technical_content_detection():
    """Test detection of technical content that should use Tavily"""
    print("🧪 Testing technical content detection...")
    
    tool = SearchImageToolTest()
    
    # Test technical image types
    technical_cases = [
        ("Programming Concepts", [], "technical"),
        ("Database Design", [], "technical"),
        ("Algorithm Analysis", [], "technical"),
    ]
    
    for slide_title, keywords, image_type in technical_cases:
        result = tool._determine_use_unsplash(slide_title, keywords, image_type)
        assert result == False, f"Should use Tavily for technical content: {slide_title}"
    
    print("✅ Technical content correctly routed to Tavily")
    
    return True


def test_parameter_handling():
    """Test parameter handling and edge cases"""
    print("🧪 Testing parameter handling...")
    
    tool = SearchImageToolTest()
    
    # Test empty/None parameters
    result = tool._determine_use_unsplash("", [], "")
    assert result == True, "Should default to Unsplash for empty parameters"
    
    result = tool._determine_use_unsplash("Test", None, "")
    assert result == True, "Should handle None keywords gracefully"
    
    # Test case insensitivity
    result = tool._determine_use_unsplash("BUSINESS MEETING", [], "")
    assert result == True, "Should be case insensitive for titles"
    
    result = tool._determine_use_unsplash("", ["PROFESSIONAL"], "")
    assert result == True, "Should be case insensitive for keywords"
    
    result = tool._determine_use_unsplash("", [], "PROFESSIONAL")
    assert result == True, "Should be case insensitive for image types"
    
    print("✅ Parameter handling works correctly")
    
    return True


def test_url_filtering_edge_cases():
    """Test edge cases for URL filtering"""
    print("🧪 Testing URL filtering edge cases...")
    
    tool = SearchImageToolTest()
    
    # Test URLs with query parameters
    param_urls = [
        "https://example.com/image?w=800&h=600&format=jpg",
        "https://api.service.com/photo?fm=png&q=80",
        "https://cdn.example.com/img?w=1200",
        "https://images.example.com/photo?h=800"
    ]
    
    for url in param_urls:
        assert tool._is_valid_image_url(url), f"Should accept URL with image parameters: {url}"
    
    print("✅ URLs with image parameters correctly accepted")
    
    # Test Unsplash specific URLs
    unsplash_urls = [
        "https://images.unsplash.com/photo-1234567890",
        "https://unsplash.com/photos/abc123def456",
        "https://images.unsplash.com/photo-1234?w=800&q=80"
    ]
    
    for url in unsplash_urls:
        assert tool._is_valid_image_url(url), f"Should accept Unsplash URL: {url}"
    
    print("✅ Unsplash URLs correctly accepted")
    
    return True


def main():
    """Run all tests"""
    print("🚀 Starting enhanced SearchImageTool tests...\n")
    
    tests = [
        ("Image URL Validation", test_image_url_validation),
        ("Unsplash Source Determination", test_unsplash_determination),
        ("Professional Keyword Detection", test_professional_keyword_detection),
        ("Technical Content Detection", test_technical_content_detection),
        ("Parameter Handling", test_parameter_handling),
        ("URL Filtering Edge Cases", test_url_filtering_edge_cases),
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
        print("🎉 All SearchImageTool tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

