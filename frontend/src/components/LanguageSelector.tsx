import React from 'react';

interface Language {
    code: string;
    name: string;
}

interface LanguageSelectorProps {
    languages: Language[];
    selectedLanguage: string;
    onLanguageChange: (language: string) => void;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({ languages, selectedLanguage, onLanguageChange }) => {
    return (
        <div className="language-selector">
            <label htmlFor="language-select">Select Language:</label>
            <select
                id="language-select"
                value={selectedLanguage}
                onChange={(e) => onLanguageChange(e.target.value)}
            >
                {languages.map((language) => (
                    <option key={language.code} value={language.code}>
                        {language.name}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default LanguageSelector;