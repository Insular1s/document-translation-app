// API Response Types
export interface TranslationResponse {
  success: boolean;
  translation: string;
  source_language?: string;
  target_language: string;
  method: string;
  error?: string;
}

export interface DocumentUploadResponse {
  success: boolean;
  filename: string;
  file_path: string;
  file_size: number;
  error?: string;
}

export interface DocumentTranslationResponse {
  success: boolean;
  filename: string;
  output_filename: string;
  target_language: string;
  slides_translated: number;
  text_frames_translated: number;
  use_llm: boolean;
  llm_model?: string;
  message?: string;
  error?: string;
}

// UI State Types
export interface Language {
  code: string;
  name: string;
}

export interface TranslationEdit {
  original_text: string;
  current_translation: string;
  edited_translation: string;
  target_language: string;
}

export interface UploadedDocument {
  filename: string;
  file_path: string;
  file_size: number;
  upload_time: Date;
}

// Request Types
export interface TranslationRequest {
  text: string;
  target_language: string;
  source_language?: string;
  context?: string;
  use_llm?: boolean;
}

export interface DocumentTranslationRequest {
  filename: string;
  target_language: string;
  source_language?: string;
  use_llm?: boolean;
  llm_model?: string;
  preserve_formatting?: boolean;
}

export interface LLMModel {
  id: string;
  name: string;
}

export interface TextFrame {
  id: string;
  text: string;
  shape_index: number;
}

export interface SlideContent {
  slide_number: number;
  text_frames: TextFrame[];
}

export interface DocumentContentResponse {
  success: boolean;
  filename: string;
  total_slides: number;
  slides: SlideContent[];
  error?: string;
}

export interface DocumentContent {
  filename: string;
  slides: SlideContent[];
  total_slides: number;
}