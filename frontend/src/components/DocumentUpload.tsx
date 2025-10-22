import React, { useState, useRef } from 'react';
import { uploadDocument, translateDocument } from '../services/api';
import type { DocumentTranslationResponse } from '../types';

interface DocumentUploadProps {
  targetLanguage: string;
  useLLM: boolean;
  llmModel?: string;
  onTranslationStart: (message: string) => void;
  onTranslationComplete: (result: DocumentTranslationResponse) => void;
}

function DocumentUpload({
  targetLanguage,
  useLLM,
  llmModel,
  onTranslationStart,
  onTranslationComplete,
}: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await handleFile(files[0]);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await handleFile(files[0]);
    }
  };

  const handleFile = async (file: File) => {
    setError(null);
    setUploadProgress('');

    // Validate file type
    if (!file.name.endsWith('.pptx')) {
      setError('Only PowerPoint (.pptx) files are supported');
      return;
    }

    // Validate file size (100MB)
    if (file.size > 100 * 1024 * 1024) {
      setError('File size must be less than 100MB');
      return;
    }

    try {
      // Upload file
      setUploadProgress('Uploading document...');
      const uploadResponse = await uploadDocument(file);
      
      if (!uploadResponse.success) {
        throw new Error(uploadResponse.error || 'Upload failed');
      }

      // Start translation
      setUploadProgress('Translating document...');
      onTranslationStart('Translating document...');

      const translationResponse = await translateDocument({
        filename: uploadResponse.filename,
        target_language: targetLanguage,
        use_llm: useLLM,
        llm_model: llmModel,
        preserve_formatting: true,
      });

      setUploadProgress('Translation complete!');
      onTranslationComplete(translationResponse);
      
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      setUploadProgress('');
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="document-upload">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pptx"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        
        <div className="upload-icon">📁</div>
        <h3>Drop your PowerPoint file here</h3>
        <p>or click to browse</p>
        <span className="file-info">Supports .pptx files up to 100MB</span>
      </div>

      {uploadProgress && (
        <div className="upload-progress">
          <p>{uploadProgress}</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}
    </div>
  );
}

export default DocumentUpload;