import axios from 'axios';
import { DocumentTranslationResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with base URL that includes /api
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});



export const getAvailableModels = async () => {
  const response = await api.get('/document/models');
  return response.data;
};

export const translateDocument = async (
  file: File,
  targetLanguage: string,
  useLLM: boolean = false,
  llmModel?: string
): Promise<DocumentTranslationResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('target_language', targetLanguage);
  formData.append('use_llm', String(useLLM));
  
  if (llmModel) {
    formData.append('llm_model', llmModel);
  }

  const response = await api.post('/document/translate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getDocumentContent = async (filename: string) => {
  const response = await api.get(`/editor/document-content/${filename}`);
  return response.data;
};

export const updateDocumentContent = async (filename: string, edits: Array<{ id: string; text: string }>) => {
  const response = await api.post('/editor/update-content', {
    filename,
    edits,
  });
  return response.data;
};

export const downloadDocument = (filename: string) => {
  window.open(`${API_BASE_URL}/api/document/download/${filename}`, '_blank');
};