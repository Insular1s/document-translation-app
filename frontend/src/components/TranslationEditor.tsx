import React, { useState, useEffect } from 'react';
import { getDocumentContent, updateDocumentContent } from '../services/api';
import type { DocumentContentResponse, SlideContent, TextFrame } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface TranslationEditorProps {
  filename: string;
  onSaveComplete: () => void;
  onCancel: () => void;
}

interface EditedContent {
  [key: string]: string;
}

const TranslationEditor: React.FC<TranslationEditorProps> = ({ filename, onSaveComplete, onCancel }) => {
  const [content, setContent] = useState<DocumentContentResponse | null>(null);
  const [editedContent, setEditedContent] = useState<EditedContent>({});
  const [currentSlide, setCurrentSlide] = useState<number>(0);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imageKey, setImageKey] = useState(0);

  useEffect(() => {
    loadDocumentContent();
  }, [filename]);

  const loadDocumentContent = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getDocumentContent(filename);
      setContent(data);
      
      // Initialize edited content with original content
      const initial: EditedContent = {};
      data.slides.forEach((slide: SlideContent) => {
        slide.text_frames.forEach((frame: TextFrame) => {
          initial[frame.id] = frame.text;
        });
      });
      setEditedContent(initial);
    } catch (err: any) {
      setError(err.message || 'Failed to load document content');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextChange = (frameId: string, newText: string) => {
    setEditedContent(prev => ({
      ...prev,
      [frameId]: newText
    }));
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setError(null);
      
      // Prepare edits array
      const edits = Object.entries(editedContent).map(([id, text]) => ({
        id,
        text
      }));
      
      await updateDocumentContent(filename, edits);
      // Reload the slide image after saving
      setImageKey(prev => prev + 1);
      onSaveComplete();
    } catch (err: any) {
      setError(err.message || 'Failed to save changes');
    } finally {
      setIsSaving(false);
    }
  };

  const getCurrentSlideData = () => {
    if (!content || !content.slides[currentSlide]) return null;
    return content.slides[currentSlide];
  };

  const hasChanges = () => {
    if (!content) return false;
    return content.slides.some((slide: SlideContent) =>
      slide.text_frames.some((frame: TextFrame) =>
        editedContent[frame.id] !== frame.text
      )
    );
  };

  if (isLoading) {
    return (
      <div className="translation-editor loading">
        <div className="spinner"></div>
        <p>Loading document content...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="translation-editor error">
        <p>❌ {error}</p>
        <button onClick={onCancel} className="btn btn-secondary">
          Go Back
        </button>
      </div>
    );
  }

  if (!content) {
    return null;
  }

  const currentSlideData = getCurrentSlideData();

  return (
    <div className="translation-editor">
      <div className="editor-header">
        <h2>📝 Review & Edit Translation</h2>
        <p>Edit translations as needed. Click "Save & Preview" when done to see the final result.</p>
      </div>

      <div className="editor-navigation">
        <button
          onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))}
          disabled={currentSlide === 0}
          className="btn btn-secondary"
        >
          ← Previous
        </button>
        <span className="slide-counter">
          Slide {currentSlide + 1} of {content.slides.length}
        </span>
        <button
          onClick={() => setCurrentSlide(Math.min(content.slides.length - 1, currentSlide + 1))}
          disabled={currentSlide === content.slides.length - 1}
          className="btn btn-secondary"
        >
          Next →
        </button>
      </div>

      <div className="editor-layout">
        {/* Slide Preview Panel - Actual PPTX Slide Image */}
        <div className="slide-context">
          <div className="slide-preview">
            <div className="slide-image-container">
              <h3>Slide {currentSlideData?.slide_number}</h3>
              <div className="actual-slide-preview">
                <img
                  key={`slide-${currentSlide}-${imageKey}`}
                  src={`${API_BASE_URL}/api/editor/slide-preview/${filename}/${currentSlide}?t=${Date.now()}`}
                  alt={`Slide ${currentSlideData?.slide_number} preview`}
                  onError={(e) => {
                    console.error('Failed to load slide image');
                    e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="800" height="600" fill="%23f0f0f0"/><text x="400" y="300" text-anchor="middle" font-size="24" fill="%23999">Slide Preview Unavailable</text></svg>';
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Editor Panel */}
        <div className="editor-content">
          <h4>📝 Edit Text Blocks</h4>
          {currentSlideData && currentSlideData.text_frames.map((frame: TextFrame, idx: number) => (
            <div key={frame.id} className="text-frame-editor">
              <div className="editor-label">
                <span className="block-badge">{idx + 1}</span>
                <label>Text Block {idx + 1}</label>
                {editedContent[frame.id] !== frame.text && (
                  <span className="edited-badge">✏️ Edited</span>
                )}
              </div>
              
              {/* Show original text if available */}
              {frame.original_text && (
                <div className="original-text-box">
                  <label className="original-label">📄 Original Text:</label>
                  <div className="original-text-content">
                    {frame.original_text}
                  </div>
                </div>
              )}
              
              {/* Translation editor */}
              <div className="translation-editor-box">
                <label className="translation-label">
                  {frame.original_text ? '🌐 Translated Text:' : 'Edit Text:'}
                </label>
                <textarea
                  value={editedContent[frame.id] || frame.text}
                  onChange={(e) => handleTextChange(frame.id, e.target.value)}
                  rows={Math.max(3, frame.text.split('\n').length + 1)}
                  className="edit-textarea"
                  placeholder="Enter translation..."
                />
              </div>
              
              {editedContent[frame.id] !== frame.text && (
                <div className="change-indicator">
                  <small>⚠️ Modified from original translation</small>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="editor-actions">
        <button onClick={onCancel} className="btn btn-secondary" disabled={isSaving}>
          Skip to Preview
        </button>
        <button
          onClick={handleSave}
          className="btn btn-primary"
          disabled={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save & Preview'}
        </button>
      </div>

      {hasChanges() && (
        <div className="changes-indicator">
          ⚠️ You have unsaved changes on {
            content.slides.filter((slide: SlideContent) =>
              slide.text_frames.some((frame: TextFrame) =>
                editedContent[frame.id] !== frame.text
              )
            ).length
          } slide(s)
        </div>
      )}
    </div>
  );
};

export default TranslationEditor;
