# Document Translation App

A powerful web application for translating PowerPoint presentations using Azure AI Translator and OpenRouter LLM enhancement.

## Features

- 📄 **PPTX Document Translation**: Upload and translate PowerPoint presentations
- 🌍 **Multiple Languages**: Support for 20+ languages including English, Spanish, French, German, Japanese, Chinese, and more
- 🤖 **LLM Enhancement**: Optional AI-powered translation refinement using Claude 3.5 Sonnet via OpenRouter
- 🖼️ **Image Text Translation**: OCR-based translation of text embedded in images (optional, requires Azure Computer Vision)
- 🎨 **Formatting Preservation**: Maintains original document formatting, fonts, and styles
- 📊 **Batch Processing**: Translates all slides, text frames, and tables in one go
- ⚡ **Smart Detection**: Automatically skips text already in target language for faster processing
- 🚀 **Modern UI**: Beautiful, responsive interface with drag-and-drop file upload

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Azure Translator**: Enterprise-grade translation service
- **OpenRouter**: Access to Claude 3.5 Sonnet for LLM enhancement
- **python-pptx**: PowerPoint file processing
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Modern UI library
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API calls

## Prerequisites

- Python 3.12 (do not use Python 3.14, as some dependencies are not compatible yet)
- Node.js 18+ and npm
- Azure Translator API credentials (Key, Endpoint, Region)
- OpenRouter API key (for LLM enhancement)

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment with Python 3.12:
```bash
py -3.12 -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the `backend` directory with your credentials:
```env
AZURE_TRANSLATOR_KEY=your_azure_translator_key
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
AZURE_TRANSLATOR_REGION=japaneast

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_API_URL=https://openrouter.ai/api/v1
```

6. Start the backend server:
```bash
python -m uvicorn app.main:app --reload
```

The backend API will be available at `http://127.0.0.1:8000`
API documentation: `http://127.0.0.1:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173/`

## Usage

1. **Start both servers** (backend on port 8000, frontend on port 5173)
2. **Open the app** in your browser at `http://localhost:5173/`
3. **Select target language** from the dropdown menu
4. **Toggle LLM enhancement** if you want AI-powered translation refinement (slower but higher quality)
5. **Upload a PPTX file** by dragging and dropping or clicking to browse
6. **Wait for translation** to complete (progress indicator will show status)
7. **Download the translated document** using the download button

## Supported Languages

English (en), Spanish (es), French (fr), German (de), Italian (it), Portuguese (pt), Russian (ru), Japanese (ja), Korean (ko), Chinese Simplified (zh-Hans), Chinese Traditional (zh-Hant), Arabic (ar), Hindi (hi), Dutch (nl), Swedish (sv), Polish (pl), Turkish (tr), Indonesian (id), Vietnamese (vi), Thai (th)

## API Endpoints

### Translation Endpoints
- `POST /api/translation/translate` - Translate a single text
- `POST /api/translation/batch-translate` - Translate multiple texts
- `POST /api/translation/improve` - Improve translation using LLM

### Document Endpoints
- `POST /api/document/upload` - Upload a PPTX file
- `POST /api/document/translate` - Translate an uploaded document
- `GET /api/document/download/{filename}` - Download a translated document

### Editor Endpoints
- `POST /api/editor/save-edits` - Save manual translation edits
- `POST /api/editor/suggest-improvement` - Get AI suggestions for translation improvement

## File Limits

- **Maximum file size**: 10 MB
- **Supported formats**: .pptx (PowerPoint)

## Project Structure

```
document-translation-app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/          # API endpoints
│   │   ├── models/              # Pydantic models
│   │   ├── services/            # Business logic
│   │   └── utils/               # Helper functions
│   ├── uploads/                 # Temporary upload storage
│   ├── outputs/                 # Translated documents
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API client
│   │   ├── styles/              # CSS styles
│   │   └── types/               # TypeScript types
│   ├── package.json             # Node dependencies
│   └── vite.config.ts           # Vite configuration
└── README.md
```

## Development Notes

- The backend uses Python 3.12 specifically to avoid compatibility issues with FastAPI and Pydantic
- The frontend dev server proxies API requests to the backend (configured in `vite.config.ts`)
- Upload and output directories are created automatically on first run
- CORS is enabled for local development

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError" when starting the server**
- Make sure you're in the `backend` directory
- Ensure the virtual environment is activated
- Run `pip install -r requirements.txt` again

**"uvicorn: command not found"**
- Activate the virtual environment: `venv\Scripts\activate`
- Use: `python -m uvicorn app.main:app --reload`

**"Azure Translator Error"**
- Check your `.env` file has correct Azure credentials
- Verify the region matches your Azure resource location

### Frontend Issues

**"npm command not found"**
- Install Node.js from https://nodejs.org/

**TypeScript errors in IDE**
- Run `npm install` to ensure all type definitions are installed
- Restart your IDE/editor

**"Connection refused" when uploading**
- Ensure the backend server is running on port 8000
- Check the proxy configuration in `vite.config.ts`

## License

This project is for educational and demonstration purposes. It allows users to upload documents, translate them into different languages, and edit the translated content before finalizing.

## Project Structure

The project is organized into two main parts: the backend and the frontend.

### Backend

The backend is built using FastAPI and is responsible for handling API requests, processing documents, and integrating with translation services.

- **app/**: Contains the main application code.
  - **api/**: Defines the API routes for translation and document management.
  - **services/**: Contains the logic for interacting with Azure Translator and OpenRouter.
  - **models/**: Defines the data models used in the application.
  - **utils/**: Utility functions for file handling and logging.
- **tests/**: Contains unit tests for the application.
- **requirements.txt**: Lists the dependencies required for the backend.
- **.env.example**: Example environment configuration for sensitive settings.

### Frontend

The frontend is built using React and provides a user interface for interacting with the translation services.

- **public/**: Contains the main HTML file for the application.
- **src/**: Contains the React components, services, hooks, and styles.
  - **components/**: UI components for document upload, translation editing, and language selection.
  - **services/**: Functions for making API calls to the backend.
  - **hooks/**: Custom hooks for managing state.
  - **styles/**: CSS styles for the application.
- **package.json**: Configuration file for npm, listing dependencies and scripts.
- **tsconfig.json**: TypeScript configuration file.
- **vite.config.ts**: Configuration for Vite, the build tool used for the frontend.

## Features

- Upload documents in various formats (e.g., PPTX).
- Translate documents into multiple languages using Azure AI Services.
- Enhanced translation capabilities with OpenRouter.
- Edit translated content before finalizing.
- Preview the translated document in real-time.

## Getting Started

To get started with the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd document-translation-app
   ```

2. Set up the backend:
   - Navigate to the `backend` directory.
   - Install the required dependencies:
     ```
     pip install -r requirements.txt
     ```
   - Create a `.env` file based on `.env.example` and configure your API keys.

3. Start the backend server:
   ```
   uvicorn app.main:app --reload
   ```

4. Set up the frontend:
   - Navigate to the `frontend` directory.
   - Install the required dependencies:
     ```
     npm install
     ```
   - Start the frontend development server:
     ```
     npm run dev
     ```

5. Open your browser and navigate to `http://localhost:3000` to access the application.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.