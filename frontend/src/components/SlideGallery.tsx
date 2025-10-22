import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface SlideGalleryProps {
  filename: string;
  totalSlides: number;
}

const SlideGallery: React.FC<SlideGalleryProps> = ({ filename, totalSlides }) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  return (
    <div className="slide-gallery">
      <h3>📑 Preview Edited Slides</h3>
      
      <div className="gallery-navigation">
        <button
          onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))}
          disabled={currentSlide === 0}
          className="btn btn-secondary"
        >
          ← Previous
        </button>
        <span className="slide-counter">
          Slide {currentSlide + 1} of {totalSlides}
        </span>
        <button
          onClick={() => setCurrentSlide(Math.min(totalSlides - 1, currentSlide + 1))}
          disabled={currentSlide === totalSlides - 1}
          className="btn btn-secondary"
        >
          Next →
        </button>
      </div>

      <div className="gallery-preview">
        <img
          key={`gallery-slide-${currentSlide}`}
          src={`${API_BASE_URL}/api/editor/slide-preview/${filename}/${currentSlide}?t=${Date.now()}`}
          alt={`Slide ${currentSlide + 1} preview`}
          onError={(e) => {
            console.error('Failed to load slide image');
            e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="800" height="600" fill="%23f0f0f0"/><text x="400" y="300" text-anchor="middle" font-size="24" fill="%23999">Slide Preview Unavailable</text></svg>';
          }}
        />
      </div>

      <div className="thumbnail-strip">
        {Array.from({ length: totalSlides }, (_, i) => (
          <div
            key={i}
            className={`thumbnail ${currentSlide === i ? 'active' : ''}`}
            onClick={() => setCurrentSlide(i)}
          >
            <img
              src={`${API_BASE_URL}/api/editor/slide-preview/${filename}/${i}?t=${Date.now()}`}
              alt={`Slide ${i + 1} thumbnail`}
              onError={(e) => {
                e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150"><rect width="200" height="150" fill="%23f0f0f0"/><text x="100" y="75" text-anchor="middle" font-size="14" fill="%23999">Slide ' + (i + 1) + '</text></svg>';
              }}
            />
            <span className="thumbnail-label">{i + 1}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SlideGallery;
