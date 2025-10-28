"""
Image Translator Service using Azure Computer Vision OCR.

This service handles:
1. Extract text from images using OCR
2. Translate the extracted text
3. Overlay translated text back onto images
"""

import logging
import io
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests

logger = logging.getLogger(__name__)


class ImageTranslator:
    """Handles OCR-based image translation using Azure Computer Vision."""
    
    def __init__(self, vision_endpoint: str, vision_key: str):
        """
        Initialize the ImageTranslator.
        
        Args:
            vision_endpoint: Azure Computer Vision endpoint
            vision_key: Azure Computer Vision API key
        """
        self.vision_endpoint = vision_endpoint.rstrip('/')
        self.vision_key = vision_key
        logger.info("ImageTranslator initialized")
    
    def extract_text_from_image(self, image_bytes: bytes, content_type: str = "image/png") -> List[Dict[str, Any]]:
        """
        Extract text from image using Azure Computer Vision OCR.
        
        Args:
            image_bytes: Image data as bytes
            content_type: MIME type of the image
            
        Returns:
            List of text regions with text, bounding boxes, and confidence
        """
        if not self.vision_key or not self.vision_endpoint:
            logger.warning("Azure Vision credentials not configured, skipping OCR")
            return []
        
        try:
            # Convert unsupported formats (WMF, EMF) to PNG
            if content_type in ['image/x-wmf', 'image/x-emf', 'image/wmf', 'image/emf']:
                logger.info(f"Converting {content_type} to PNG for OCR")
                try:
                    img = Image.open(io.BytesIO(image_bytes))
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')
                    png_buffer = io.BytesIO()
                    img.save(png_buffer, format='PNG')
                    image_bytes = png_buffer.getvalue()
                    content_type = 'image/png'
                except Exception as e:
                    logger.error(f"Failed to convert {content_type} to PNG: {e}")
                    return []
            
            # Use Azure Computer Vision Read API
            ocr_url = f"{self.vision_endpoint}/vision/v3.2/read/analyze"
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.vision_key,
                'Content-Type': 'application/octet-stream'
            }
            
            # Don't specify language - let Azure auto-detect (supports Japanese, English, etc.)
            params = {
                'model-version': 'latest'
            }
            
            # Submit image for OCR
            response = requests.post(
                ocr_url,
                headers=headers,
                params=params,
                data=image_bytes,
                timeout=30
            )
            response.raise_for_status()
            
            # Get operation location
            operation_url = response.headers.get('Operation-Location')
            if not operation_url:
                logger.error("No Operation-Location in response")
                return []
            
            # Poll for results
            import time
            max_attempts = 10
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(1)
                result_response = requests.get(
                    operation_url,
                    headers={'Ocp-Apim-Subscription-Key': self.vision_key},
                    timeout=10
                )
                result_response.raise_for_status()
                result = result_response.json()
                
                status = result.get('status')
                if status == 'succeeded':
                    return self._parse_ocr_result(result)
                elif status == 'failed':
                    logger.error(f"OCR failed: {result}")
                    return []
                
                attempt += 1
            
            logger.warning("OCR polling timed out")
            return []
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return []
    
    def _parse_ocr_result(self, result: Dict) -> List[Dict[str, Any]]:
        """
        Parse Azure OCR result into structured format.
        
        Args:
            result: OCR API response
            
        Returns:
            List of text blocks with positions
        """
        text_blocks = []
        
        try:
            analyze_result = result.get('analyzeResult', {})
            read_results = analyze_result.get('readResults', [])
            
            for page in read_results:
                lines = page.get('lines', [])
                for line in lines:
                    text = line.get('text', '').strip()
                    bbox = line.get('boundingBox', [])
                    
                    # Skip empty or very short text (likely OCR artifacts)
                    if not text or len(text) < 2:
                        continue
                    
                    # Skip single character text unless it's CJK (Chinese/Japanese/Korean)
                    if len(text) == 1:
                        # Check if it's a CJK character
                        is_cjk = any('\u4e00' <= c <= '\u9fff' or  # Chinese
                                     '\u3040' <= c <= '\u309f' or  # Hiragana
                                     '\u30a0' <= c <= '\u30ff' or  # Katakana
                                     '\uac00' <= c <= '\ud7af'     # Korean
                                     for c in text)
                        if not is_cjk:
                            logger.debug(f"Skipping single character: '{text}'")
                            continue
                    
                    if text and len(bbox) >= 8:
                        # Bounding box is [x0, y0, x1, y1, x2, y2, x3, y3]
                        # Convert to simpler format: [left, top, width, height]
                        x_coords = [bbox[i] for i in range(0, 8, 2)]
                        y_coords = [bbox[i] for i in range(1, 8, 2)]
                        
                        left = min(x_coords)
                        top = min(y_coords)
                        right = max(x_coords)
                        bottom = max(y_coords)
                        
                        text_blocks.append({
                            'text': text,
                            'bbox': [left, top, right - left, bottom - top],  # [x, y, width, height]
                            'confidence': line.get('appearance', {}).get('style', {}).get('confidence', 1.0)
                        })
            
            logger.info(f"Extracted {len(text_blocks)} text blocks from image")
            return text_blocks
            
        except Exception as e:
            logger.error(f"Error parsing OCR result: {e}")
            return []
    
    def translate_image(
        self,
        image_bytes: bytes,
        content_type: str,
        translation_processor,
        target_language: str,
        source_language: Optional[str] = None,
        use_llm: bool = False,
        llm_model: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Translate text in an image.
        
        Args:
            image_bytes: Original image as bytes
            content_type: MIME type of the image
            translation_processor: Translation processor instance
            target_language: Target language code
            source_language: Source language code (optional)
            use_llm: Whether to use LLM enhancement
            llm_model: LLM model to use
            
        Returns:
            Translated image as bytes, or None if no text found
        """
        try:
            # Extract text from image
            text_blocks = self.extract_text_from_image(image_bytes, content_type)
            
            if not text_blocks:
                logger.info("No text found in image, returning original")
                return None
            
            # Log what we found
            logger.info(f"Found {len(text_blocks)} text blocks in image")
            for i, block in enumerate(text_blocks):
                logger.debug(f"Block {i+1}: '{block['text']}' at {block['bbox']}")
            
            # Open image (convert WMF/EMF if needed)
            try:
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                logger.warning(f"Failed to open image with PIL, converting format: {e}")
                # Try converting format first
                if content_type in ['image/x-wmf', 'image/x-emf', 'image/wmf', 'image/emf']:
                    img = Image.open(io.BytesIO(image_bytes))
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')
                    png_buffer = io.BytesIO()
                    img.save(png_buffer, format='PNG')
                    image = Image.open(png_buffer)
                else:
                    raise
            
            # Convert to RGB if necessary
            if image.mode not in ('RGB', 'RGBA'):
                logger.info(f"Converting image from {image.mode} to RGB")
                image = image.convert('RGB')
            
            # Create a copy to draw on
            translated_image = image.copy()
            draw = ImageDraw.Draw(translated_image)
            
            # Try to load a better font
            try:
                # Try common font paths
                font_size = 20
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Track which text blocks actually need translation
            blocks_to_translate = []
            
            # Translate each text block with small delays to avoid rate limiting
            for i, block in enumerate(text_blocks):
                original_text = block['text']
                bbox = block['bbox']  # [x, y, width, height]
                
                # Small delay between translations to avoid overwhelming the API
                if i > 0:
                    time.sleep(0.1)  # 100ms delay between translations
                
                # Translate the text
                translation_result = translation_processor.translate_text(
                    text=original_text,
                    target_language=target_language,
                    source_language=source_language,
                    force_llm=use_llm,
                    llm_model=llm_model
                )
                
                if translation_result.get('success'):
                    translated_text = translation_result.get('translation', original_text)
                    
                    # Check if translation was skipped (already in target language)
                    if translation_result.get('skipped'):
                        logger.debug(f"Text already in target language: '{original_text[:50]}'")
                        continue  # Skip this block
                    
                    # Validate translation - skip if it looks like an error message or is too long
                    # (OCR sometimes detects garbage that produces LLM error messages)
                    error_indicators = [
                        "I don't see any",
                        "I don't see",
                        "Please share",
                        "Please provide",
                        "provided to translate",
                        "following your instructions",
                        "following your specified"
                    ]
                    
                    if any(indicator in translated_text for indicator in error_indicators):
                        logger.warning(f"Skipping translation that looks like an error message: '{translated_text[:100]}'")
                        continue
                    
                    # Skip if translation is way longer than original (likely error)
                    if len(translated_text) > len(original_text) * 5:
                        logger.warning(f"Skipping translation that's too long compared to original: {len(original_text)} -> {len(translated_text)}")
                        continue
                    
                    # Add to blocks that need translation
                    blocks_to_translate.append({
                        'original': original_text,
                        'translated': translated_text,
                        'bbox': bbox
                    })
                    
                    logger.info(f"Translated in image: '{original_text}' -> '{translated_text}'")
                elif translation_result.get('error'):
                    # Translation failed, log warning and skip this block
                    logger.warning(f"Translation failed for '{original_text[:50]}': {translation_result.get('error')}")
            
            # If no blocks need translation, return None (skip image processing)
            if not blocks_to_translate:
                logger.info("All text already in target language, no image modification needed")
                return None
            
            # Now draw the translations on the image
            for block_data in blocks_to_translate:
                translated_text = block_data['translated']
                bbox = block_data['bbox']
                
                x, y, w, h = bbox
                padding = 5
                
                # Sample colors from the original text region to preserve them
                text_color, bg_color = self._sample_text_colors(image, bbox)
                
                logger.debug(f"Sampled colors - Text: {text_color}, Background: {bg_color}")
                
                # Draw a rectangle with the detected background color over the original text
                draw.rectangle(
                    [x - padding, y - padding, x + w + padding, y + h + padding],
                    fill=bg_color,
                    outline=bg_color
                )
                
                # Calculate font size to fit the bounding box
                adjusted_font_size = self._calculate_font_size(translated_text, w, h, font)
                if adjusted_font_size != font_size:
                    try:
                        font = ImageFont.truetype("arial.ttf", adjusted_font_size)
                    except:
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", adjusted_font_size)
                        except:
                            font = ImageFont.load_default()
                
                # Draw the translated text with the detected text color
                draw.text(
                    (x, y),
                    translated_text,
                    fill=text_color,
                    font=font
                )
            
            logger.info(f"Drew {len(blocks_to_translate)} translated text blocks on image")
            
            # Convert back to bytes, preserving original format when possible
            output_buffer = io.BytesIO()
            
            # Determine output format based on original content type
            save_format = 'PNG'  # Default to PNG
            if content_type in ['image/jpeg', 'image/jpg']:
                save_format = 'JPEG'
            elif content_type == 'image/png':
                save_format = 'PNG'
            
            # Save with appropriate format
            if save_format == 'JPEG':
                # JPEG doesn't support transparency, ensure RGB mode
                if translated_image.mode == 'RGBA':
                    # Create white background
                    rgb_image = Image.new('RGB', translated_image.size, (255, 255, 255))
                    rgb_image.paste(translated_image, mask=translated_image.split()[3] if len(translated_image.split()) == 4 else None)
                    rgb_image.save(output_buffer, format='JPEG', quality=95)
                else:
                    translated_image.save(output_buffer, format='JPEG', quality=95)
            else:
                # PNG format (supports transparency)
                translated_image.save(output_buffer, format='PNG', optimize=True)
            
            logger.info(f"Saved translated image as {save_format}")
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error translating image: {e}")
            return None
    
    def _sample_text_colors(self, image: Image.Image, bbox: list) -> tuple:
        """
        Sample text and background colors from a bounding box region.
        
        Uses smart heuristics to detect text color (preferring black/white/dark colors)
        and preserve background/highlight colors accurately.
        
        Args:
            image: PIL Image object
            bbox: Bounding box [x, y, width, height]
            
        Returns:
            Tuple of (text_color, bg_color) as RGB tuples
        """
        try:
            from collections import Counter
            
            x, y, w, h = bbox
            
            # Ensure coordinates are within image bounds
            img_width, img_height = image.size
            x = max(0, min(x, img_width - 1))
            y = max(0, min(y, img_height - 1))
            x2 = max(x + 1, min(x + w, img_width))
            y2 = max(y + 1, min(y + h, img_height))
            
            # Crop the region
            region = image.crop((x, y, x2, y2))
            
            # Convert to RGB if needed
            if region.mode != 'RGB':
                region = region.convert('RGB')
            
            # Get all pixels
            pixels = list(region.getdata())
            
            if not pixels:
                return ((0, 0, 0), (255, 255, 255))  # Black on white fallback
            
            # Count color frequencies
            color_counter = Counter(pixels)
            
            # Find background (most common color)
            bg_color = color_counter.most_common(1)[0][0]
            bg_brightness = sum(bg_color) / 3
            
            # NEW APPROACH: Look for pure black or white pixels DIRECTLY
            # These are the actual text colors, not anti-aliased edges
            
            # Count black-ish pixels (very dark)
            black_threshold = 30  # RGB sum < 30 is basically black
            black_count = sum(count for color, count in color_counter.items() 
                            if sum(color) <= black_threshold)
            
            # Count white-ish pixels (very light)
            white_threshold = 735  # RGB sum > 735 is basically white (max is 765)
            white_count = sum(count for color, count in color_counter.items() 
                            if sum(color) >= white_threshold)
            
            # Count very dark pixels (dark gray, almost black)
            dark_threshold = 100
            dark_count = sum(count for color, count in color_counter.items() 
                           if black_threshold < sum(color) <= dark_threshold)
            
            logger.debug(f"Color analysis - BG: {bg_color} (brightness: {bg_brightness:.1f}), "
                        f"Black pixels: {black_count}, White pixels: {white_count}, Dark pixels: {dark_count}")
            
            # Decision logic based on actual pixel counts
            if bg_brightness > 128:
                # LIGHT background (white, yellow, cream, light gray, etc.)
                # Text should be DARK or BLACK
                
                # If we found black pixels, use pure black
                if black_count > 0:
                    text_color = (0, 0, 0)
                    logger.debug("Using BLACK text (found black pixels on light background)")
                # If we found dark pixels, use dark gray or black
                elif dark_count > 0:
                    text_color = (0, 0, 0)  # Force to black even if slightly gray
                    logger.debug("Using BLACK text (found dark pixels on light background)")
                else:
                    # No dark pixels found at all, force black anyway
                    text_color = (0, 0, 0)
                    logger.debug("Using BLACK text (default for light background)")
            else:
                # DARK background (black, navy, dark blue, etc.)
                # Text should be LIGHT or WHITE
                
                # If we found white pixels, use pure white
                if white_count > 0:
                    text_color = (255, 255, 255)
                    logger.debug("Using WHITE text (found white pixels on dark background)")
                else:
                    # No white pixels, force white anyway
                    text_color = (255, 255, 255)
                    logger.debug("Using WHITE text (default for dark background)")
            
            # Final safety check: ensure contrast
            contrast = self._calculate_contrast(text_color, bg_color)
            if contrast < 1.5:
                # Very poor contrast, force opposite
                logger.warning(f"Poor contrast ({contrast:.2f}), forcing opposite color")
                if bg_brightness > 128:
                    text_color = (0, 0, 0)
                else:
                    text_color = (255, 255, 255)
            
            logger.info(f"Final colors - Text: {text_color}, Background: {bg_color}, Contrast: {contrast:.2f}")
            return (text_color, bg_color)
            
        except Exception as e:
            logger.warning(f"Error sampling text colors: {e}, using defaults")
            return ((0, 0, 0), (255, 255, 255))  # Black on white fallback
    
    def _color_distance(self, color1: tuple, color2: tuple) -> float:
        """
        Calculate Euclidean distance between two RGB colors.
        
        Args:
            color1: First RGB tuple
            color2: Second RGB tuple
            
        Returns:
            Distance value
        """
        return ((color1[0] - color2[0])**2 + 
                (color1[1] - color2[1])**2 + 
                (color1[2] - color2[2])**2) ** 0.5
    
    def _get_contrasting_color(self, color: tuple) -> tuple:
        """
        Get a contrasting color for the given color.
        
        Args:
            color: RGB tuple
            
        Returns:
            Contrasting RGB tuple
        """
        # Calculate brightness
        brightness = sum(color) / 3
        
        # Return black or white based on brightness
        if brightness > 128:
            return (0, 0, 0)  # Black for light backgrounds
        else:
            return (255, 255, 255)  # White for dark backgrounds
    
    def _calculate_contrast(self, color1: tuple, color2: tuple) -> float:
        """
        Calculate contrast ratio between two colors.
        
        Args:
            color1: First RGB tuple
            color2: Second RGB tuple
            
        Returns:
            Contrast ratio (higher is better, minimum 1.0)
        """
        # Calculate relative luminance
        def luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = luminance(color1)
        l2 = luminance(color2)
        
        # Calculate contrast ratio
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def _calculate_font_size(self, text: str, max_width: int, max_height: int, font) -> int:
        """
        Calculate appropriate font size to fit text in bounding box.
        
        Args:
            text: Text to fit
            max_width: Maximum width
            max_height: Maximum height
            font: Current font
            
        Returns:
            Appropriate font size
        """
        # Start with a reasonable font size
        font_size = 20
        
        try:
            # Simple heuristic: adjust based on text length and box size
            char_width = max_width / len(text) if len(text) > 0 else max_width
            font_size = int(min(char_width * 1.5, max_height * 0.8))
            font_size = max(10, min(font_size, 50))  # Clamp between 10 and 50
        except:
            font_size = 20
        
        return font_size
