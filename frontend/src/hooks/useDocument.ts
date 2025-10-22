import { useState, useEffect } from 'react';

const useDocument = (initialDocument = null) => {
    const [document, setDocument] = useState(initialDocument);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const uploadDocument = async (file) => {
        setLoading(true);
        setError(null);
        try {
            // Logic to upload the document to the backend
            const formData = new FormData();
            formData.append('file', file);
            const response = await fetch('/api/document/upload', {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) {
                throw new Error('Failed to upload document');
            }
            const data = await response.json();
            setDocument(data.document);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const clearDocument = () => {
        setDocument(null);
    };

    return {
        document,
        loading,
        error,
        uploadDocument,
        clearDocument,
    };
};

export default useDocument;