import React, { useState, useEffect } from 'react';
import DocumentUpload from './components/DocumentUpload';
import LanguageSelector from './components/LanguageSelector';
import ProgressIndicator from './components/ProgressIndicator';
import PreviewPanel from './components/PreviewPanel';
import TranslationEditor from './components/TranslationEditor';
import type { DocumentTranslationResponse } from './types';
import { getAvailableModels } from './services/api';
import './styles/main.css';

const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'ru', name: 'Russian' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'zh-Hans', name: 'Chinese (Simplified)' },
  { code: 'zh-Hant', name: 'Chinese (Traditional)' },
  { code: 'ar', name: 'Arabic' },
  { code: 'hi', name: 'Hindi' },
  { code: 'nl', name: 'Dutch' },
  { code: 'sv', name: 'Swedish' },
  { code: 'pl', name: 'Polish' },
  { code: 'tr', name: 'Turkish' },
  { code: 'id', name: 'Indonesian' },
  { code: 'vi', name: 'Vietnamese' },
  { code: 'th', name: 'Thai' }
];

function App() {
  const [targetLanguage, setTargetLanguage] = useState<string>('en');
  const [translationResult, setTranslationResult] = useState<DocumentTranslationResponse | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [translatingMessage, setTranslatingMessage] = useState('');
  const [useLLM, setUseLLM] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [availableModels, setAvailableModels] = useState<Record<string, string>>({});
  const [showEditor, setShowEditor] = useState(false);
  const [showFinalPreview, setShowFinalPreview] = useState(false);

  useEffect(() => {
    // Fetch available models on mount
    getAvailableModels().then((data) => {
      setAvailableModels(data.models);
      setSelectedModel(data.default);
    }).catch((error) => {
      console.error('Failed to fetch models:', error);
    });
  }, []);

  const handleTranslationComplete = (result: DocumentTranslationResponse) => {
    setTranslationResult(result);
    setIsTranslating(false);
    setShowEditor(true); // Go directly to editor after translation
  };

  const handleTranslationStart = (message: string) => {
    setIsTranslating(true);
    setTranslatingMessage(message);
  };

  const handleNewTranslation = () => {
    setTranslationResult(null);
    setIsTranslating(false);
    setShowEditor(false);
    setShowFinalPreview(false);
  };

  const handleReviewEdit = () => {
    setShowEditor(true);
    setShowFinalPreview(false);
  };

  const handleEditorSave = () => {
    setShowEditor(false);
    setShowFinalPreview(true); // Show preview after saving edits
  };

  const handleEditorCancel = () => {
    setShowEditor(false);
    setShowFinalPreview(true); // Go to preview even if cancelled
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📄 Document Translation App</h1>
        <p>Translate PowerPoint presentations using Azure AI and LLM enhancement</p>
      </header>

      <main className="app-main">
        <div className="controls-section">
          <LanguageSelector
            languages={SUPPORTED_LANGUAGES}
            selectedLanguage={targetLanguage}
            onLanguageChange={setTargetLanguage}
          />
          
          <div className="llm-toggle">
            <label>
              <input
                type="checkbox"
                checked={useLLM}
                onChange={(e) => setUseLLM(e.target.checked)}
              />
              <span>Use LLM Enhancement</span>
            </label>
          </div>

          {useLLM && Object.keys(availableModels).length > 0 && (
            <div className="model-selector">
              <label htmlFor="model-select">AI Model:</label>
              <select
                id="model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {Object.entries(availableModels).map(([id, name]) => (
                  <option key={id} value={id}>
                    {name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {isTranslating && <ProgressIndicator message={translatingMessage} />}

        {!isTranslating && !translationResult && (
          <DocumentUpload
            targetLanguage={targetLanguage}
            useLLM={useLLM}
            llmModel={selectedModel}
            onTranslationStart={handleTranslationStart}
            onTranslationComplete={handleTranslationComplete}
          />
        )}

        {translationResult && showEditor && (
          <TranslationEditor
            filename={translationResult.output_filename}
            onSaveComplete={handleEditorSave}
            onCancel={handleEditorCancel}
          />
        )}

        {translationResult && showFinalPreview && (
          <PreviewPanel
            result={translationResult}
            onNewTranslation={handleNewTranslation}
            onReviewEdit={handleReviewEdit}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by Azure Translator & OpenRouter</p>
      </footer>
    </div>
  );
}

export default App;