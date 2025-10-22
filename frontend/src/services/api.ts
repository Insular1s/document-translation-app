import axios from 'axios';
import type {
  TranslationResponse,
  DocumentUploadResponse,
  DocumentTranslationResponse,
  TranslationRequest,
  DocumentTranslationRequest,
  TranslationEdit,
} from '../types';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Translation APIs
export const translateText = async (request: TranslationRequest): Promise<TranslationResponse> => {
  const response = await api.post('/translation/translate', request);
  return response.data;
};

export const improveTranslation = async (
  originalText: string,
  currentTranslation: string,
  targetLanguage: string,
  feedback?: string
): Promise<TranslationResponse> => {
  const response = await api.post('/translation/improve', {
    original_text: originalText,
    current_translation: currentTranslation,
    target_language: targetLanguage,
    feedback,
  });
  return response.data;
};

// Document APIs
export const uploadDocument = async (file: File): Promise<DocumentUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/document/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const translateDocument = async (
  request: DocumentTranslationRequest
): Promise<DocumentTranslationResponse> => {
  const formData = new FormData();
  formData.append('filename', request.filename);
  formData.append('target_language', request.target_language);
  if (request.source_language) {
    formData.append('source_language', request.source_language);
  }
  formData.append('use_llm', request.use_llm ? 'true' : 'false');
  if (request.llm_model) {
    formData.append('llm_model', request.llm_model);
  }
  formData.append('preserve_formatting', request.preserve_formatting !== false ? 'true' : 'false');

  const response = await api.post('/document/translate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const downloadDocument = (filename: string): void => {
  window.open(`${API_BASE_URL}/document/download/${filename}`, '_blank');
};

export const getAvailableModels = async (): Promise<{ models: Record<string, string>; default: string }> => {
  const response = await api.get('/document/models');
  return response.data;
};

export const getDocumentContent = async (filename: string) => {
  const response = await api.get(`/editor/document-content/${filename}`);
  return response.data;
};

export const updateDocumentContent = async (filename: string, edits: Array<{ id: string; text: string }>) => {
  const response = await api.post('/editor/update-content', {
    filename,
    edits
  });
  return response.data;
};

// Editor APIs
export const saveEdits = async (edits: TranslationEdit[]): Promise<{ success: boolean; edited_count: number }> => {
  const response = await api.post('/editor/save-edits', { edits });
  return response.data;
};

export const getSupportedLanguages = async (): Promise<{ languages: string[] }> => {
  const response = await api.get('/languages');
  return response.data;
};

export default api;