import { useState, useEffect } from 'react';
import { translateText } from '../services/translationService';

const useTranslation = (initialText: string, targetLanguage: string) => {
    const [translatedText, setTranslatedText] = useState<string>(initialText);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const translate = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await translateText(initialText, targetLanguage);
                setTranslatedText(response.translatedText);
            } catch (err) {
                setError('Translation failed. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        if (initialText) {
            translate();
        }
    }, [initialText, targetLanguage]);

    return { translatedText, loading, error };
};

export default useTranslation;