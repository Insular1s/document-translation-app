import React from 'react';
import { DocumentTranslationResponse } from '../types';
import { downloadDocument } from '../services/api';
import SlideGallery from './SlideGallery';

interface PreviewPanelProps {
  result: DocumentTranslationResponse;
  onNewTranslation: () => void;
  onReviewEdit: () => void;
}

const PreviewPanel: React.FC<PreviewPanelProps> = ({ result, onNewTranslation, onReviewEdit }) => {
  const handleDownload = async () => {
    try {
      await downloadDocument(result.output_filename);
    } catch (error) {
      console.error('Error downloading file:', error);
      alert('Failed to download file. Please try again.');
    }
  };

  return (
    <div className="preview-panel">
      <div className="result-card">
        <h3>✅ Translation Completed & Edited!</h3>
        <p style={{ textAlign: 'center', color: '#666', marginTop: '10px' }}>
          Preview your edited slides below. You can go back to edit or download the final document.
        </p>
        
        <div className="result-stats">
          <div className="stat-item">
            <strong>Output File</strong>
            <span>{result.output_filename}</span>
          </div>
          <div className="stat-item">
            <strong>Target Language</strong>
            <span>{result.target_language}</span>
          </div>
          <div className="stat-item">
            <strong>Slides Translated</strong>
            <span>{result.slides_translated}</span>
          </div>
          <div className="stat-item">
            <strong>Text Frames Translated</strong>
            <span>{result.text_frames_translated}</span>
          </div>
        </div>

        <div className="action-buttons">
          <button onClick={handleDownload} className="btn btn-primary">
            📥 Download Final Document
          </button>
          <button onClick={onReviewEdit} className="btn btn-secondary">
            ✏️ Edit Again
          </button>
          <button onClick={onNewTranslation} className="btn btn-secondary">
            🔄 Translate Another Document
          </button>
        </div>
      </div>

      <SlideGallery 
        filename={result.output_filename}
        totalSlides={result.slides_translated}
      />
    </div>
  );
};

export default PreviewPanel;