import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const translateDocument = async (documentData, targetLanguage) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/translate`, {
            document: documentData,
            target_language: targetLanguage,
        });
        return response.data;
    } catch (error) {
        console.error('Error translating document:', error);
        throw error;
    }
};

export const editTranslation = async (translationId, editedContent) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/editor/${translationId}`, {
            content: editedContent,
        });
        return response.data;
    } catch (error) {
        console.error('Error editing translation:', error);
        throw error;
    }
};

export const fetchTranslationStatus = async (translationId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/editor/${translationId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching translation status:', error);
        throw error;
    }
};