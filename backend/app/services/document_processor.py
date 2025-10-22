"""
Document Processor Service for PPTX Translation.

This service handles:
1. PPTX text extraction from slides, shapes, and tables.
2. Formatting preservation during translation.
3. Integration with Translation Processor for Azure and OpenRouter translation.

Algorithm:
- Extracts text from PPTX slides and shapes
- Translates text while preserving formatting
- Creates new translated PPTX file
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional
from pptx import Presentation
from pptx.util import Pt

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processes PPTX documents for translation with formatting preservation."""

    def __init__(self, translation_processor):
        """
        Initialize the DocumentProcessor.

        Args:
            translation_processor: An instance of the translation processor to handle translation logic.
        """
        self.translation_processor = translation_processor
        logger.info("DocumentProcessor initialized")

    def process_pptx(
        self,
        input_path: Path,
        output_path: Path,
        target_language: str,
        source_language: Optional[str] = None,
        use_llm: bool = False,
        llm_model: Optional[str] = None,
        preserve_formatting: bool = True
    ) -> Dict[str, Any]:
        """
        Process PPTX file and create translated version.

        Args:
            input_path: Path to input PPTX file
            output_path: Path to save translated PPTX
            target_language: Target language code
            source_language: Source language code (optional)
            use_llm: Whether to use LLM enhancement
            llm_model: LLM model to use (optional)
            preserve_formatting: Whether to preserve original formatting

        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Processing PPTX: {input_path.name}")
        
        stats = {
            'filename': input_path.name,
            'slides_processed': 0,
            'text_frames_translated': 0,
            'tables_translated': 0,
            'source_language': source_language,
            'target_language': target_language,
            'method': 'llm' if use_llm else 'azure'
        }

        try:
            # Load presentation
            prs = Presentation(input_path)
            
            # Process each slide
            for slide_idx, slide in enumerate(prs.slides):
                logger.info(f"Processing slide {slide_idx + 1}/{len(prs.slides)}")
                
                for shape in slide.shapes:
                    # Process text frames
                    if shape.has_text_frame:
                        self._process_text_frame(
                            shape.text_frame,
                            target_language,
                            source_language,
                            use_llm,
                            llm_model,
                            preserve_formatting
                        )
                        stats['text_frames_translated'] += 1
                    
                    # Process tables
                    elif shape.has_table:
                        self._process_table(
                            shape.table,
                            target_language,
                            source_language,
                            use_llm,
                            llm_model
                        )
                        stats['tables_translated'] += 1
                
                stats['slides_processed'] += 1
            
            # Save translated presentation
            prs.save(output_path)
            logger.info(f"Translated PPTX saved to: {output_path}")
            
            return {
                'success': True,
                **stats
            }

        except Exception as e:
            logger.error(f"Error processing PPTX: {e}")
            return {
                'success': False,
                'error': str(e),
                **stats
            }

    def _process_text_frame(
        self,
        text_frame,
        target_language: str,
        source_language: Optional[str],
        use_llm: bool,
        llm_model: Optional[str],
        preserve_formatting: bool
    ):
        """Process a text frame and translate its content."""
        try:
            original_text = text_frame.text.strip()
            if not original_text:
                return
            
            # Translate text
            result = self.translation_processor.translate_text(
                text=original_text,
                target_language=target_language,
                source_language=source_language,
                force_llm=use_llm,
                llm_model=llm_model
            )
            
            if result.get('success') and result.get('translation'):
                translated_text = result['translation']
                
                if preserve_formatting:
                    self._replace_text_preserve_format(text_frame, translated_text)
                else:
                    text_frame.text = translated_text
                    
        except Exception as e:
            logger.error(f"Error processing text frame: {e}")

    def _process_table(
        self,
        table,
        target_language: str,
        source_language: Optional[str],
        use_llm: bool,
        llm_model: Optional[str]
    ):
        """Process a table and translate its cells."""
        try:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        result = self.translation_processor.translate_text(
                            text=cell.text.strip(),
                            target_language=target_language,
                            source_language=source_language,
                            force_llm=use_llm,
                            llm_model=llm_model
                        )
                        
                        if result.get('success') and result.get('translation'):
                            cell.text = result['translation']
                            
        except Exception as e:
            logger.error(f"Error processing table: {e}")

    def _replace_text_preserve_format(self, text_frame, new_text: str):
        """
        Replace text in a text frame while preserving formatting.

        Args:
            text_frame: The text frame object from the document.
            new_text: The new text to insert.
        """
        try:
            # Preserve first paragraph's formatting
            if text_frame.paragraphs:
                first_para = text_frame.paragraphs[0]
                if first_para.runs:
                    first_run = first_para.runs[0]
                    font_size = first_run.font.size
                    font_name = first_run.font.name
                    font_bold = first_run.font.bold
                    font_italic = first_run.font.italic
                    
                    # Clear and replace
                    text_frame.clear()
                    p = text_frame.paragraphs[0]
                    run = p.add_run()
                    run.text = new_text
                    
                    # Apply preserved formatting
                    if font_size:
                        run.font.size = font_size
                    if font_name:
                        run.font.name = font_name
                    if font_bold is not None:
                        run.font.bold = font_bold
                    if font_italic is not None:
                        run.font.italic = font_italic
                else:
                    text_frame.text = new_text
            else:
                text_frame.text = new_text
                
        except Exception as e:
            logger.error(f"Error preserving format: {e}")
            text_frame.text = new_text