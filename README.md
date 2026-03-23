# Interior Design SaaS - DesignAI

AI-powered interior design platform with style detection, design recommendations, and interactive chat.

## Architecture

```
project-in/
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── routes/             # API endpoints (auth, projects, chat, styles)
│   │   ├── config.py           # App configuration
│   │   ├── database.py         # MongoDB connection
│   │   ├── models.py           # Pydantic models
│   │   └── auth.py             # JWT authentication
│   ├── ml/
│   │   ├── model.py            # ResNet50 classifier model
│   │   ├── train.py            # Training script
│   │   ├── evaluate.py         # Evaluation script
│   │   └── predictor.py        # Inference + design knowledge base
│   ├── main.py                 # FastAPI app entry point
│   └── requirements.txt
├── frontend/                   # React TypeScript + MUI Frontend
│   ├── src/
│   │   ├── pages/              # Login, Register, Dashboard, ProjectView, StyleExplorer
│   │   ├── components/         # Layout shell
│   │   ├── App.tsx             # Routes
│   │   ├── store.ts            # Zustand state management
│   │   ├── api.ts              # Axios API client
│   │   ├── types.ts            # TypeScript types
│   │   └── theme.ts            # MUI theme
│   └── package.json
├── dataset_train/              # 14,876 training images (19 styles)
└── dataset_test/               # 3,729 test images
```

## 19 Interior Design Styles

Asian, Coastal, Contemporary, Craftsman, Eclectic, Farmhouse, French Country, Industrial, Mediterranean, Mid-Century Modern, Modern, Rustic, Scandinavian, Shabby Chic, Southwestern, Traditional, Transitional, Tropical, Victorian

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **MongoDB** (running on localhost:27017)
- **GPU** recommended for training (optional, CPU works too)

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

# Copy and configure env
copy .env.example .env         # Windows
# cp .env.example .env         # Mac/Linux
```

### 2. Train the Model

```bash
cd backend
python -m ml.train --data_dir ../dataset_train/dataset_train --epochs 25 --batch_size 32
```

### 3. Evaluate the Model

```bash
python -m ml.evaluate --model_path ./ml/models/interior_style_classifier.pth --test_dir ../dataset_test/dataset_test
```

### 4. Start Backend

```bash
cd backend
source venv/Scripts/activate        # Git Bash (Windows)
# venv\Scripts\activate             # PowerShell (Windows)
# source venv/bin/activate          # Mac/Linux

uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 6. Open App

Visit **http://localhost:5173** in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/projects/` | List projects |
| POST | `/api/projects/` | Create project |
| GET | `/api/projects/:id` | Get project |
| DELETE | `/api/projects/:id` | Delete project |
| POST | `/api/projects/:id/upload-plan` | Upload site plan + analyze |
| GET | `/api/projects/:id/chat/` | Get chat messages |
| POST | `/api/projects/:id/chat/` | Send message, get AI response |
| GET | `/api/styles/` | List all design styles |
| GET | `/api/health` | Health check |

## Features

- **User Authentication** - JWT-based register/login
- **Project Management** - Create, view, delete design projects
- **Image Upload & Style Detection** - Upload site plan → ResNet50 classifies style
- **AI Chat Interface** - Contextual design recommendations
- **Style Explorer** - Browse all 19 styles with details
- **Responsive UI** - MUI + FontAwesome, mobile-friendly
