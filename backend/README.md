# Promptly 🪄
A backend service built with FastAPI that integrates Generative AI (Gemini, OpenAI) to solve text-processing problems like summarization, rewriting, grammar correction, and Q&A. It also supports PDF Q&A by indexing documents in a vector database (Qdrant).  

---

## ✨ Features
- 🔥 **Text Processing**: Summarization, rewriting, grammar correction, and Q&A
- 📄 **PDF Processing**: Upload PDFs and ask questions about them
- ⚡ **Caching Layer**: Uses Valkey (Redis alternative) to cache AI responses
- 📦 **Vector Search**: Uses Qdrant for semantic search on PDF chunks
- 🐳 **Docker Dev Containers**: Simplified local development
- ⚙️ **Background Processing**: Handles heavy AI tasks via RQ workers

---

## 🏗️ Tech Stack
| Component         | Purpose                      |
|--------------------|------------------------------|
| FastAPI            | REST API framework           |
| Valkey             | Caching + RQ job queue       |
| Qdrant             | Vector database for PDFs     |
| RQ (Redis Queue)   | Background job processing    |
| Gemini API         | Generative AI integration    |
| Docker + Dev Containers | Containerized development |

---

## 🚀 Quick Start (with Docker Dev Containers)

### 📁 Prerequisites
- Docker
- Visual Studio Code + [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Gemini API Key
- OpenAI API Key

### 1. Clone the Repository
```bash
git clone https://github.com/ridamsinghal25/promptly.git

cd promptly
```

### 2. Environment Variables
Create a .env file in the backend directory and add the following environment variables:

```bash
GEMINI_API_KEY=your_google_gemini_api_key

OPENAI_API_KEY=your_openai_api_key
```

### 3. Build & Run (Dev Container)
- Open Command Palette (Ctrl+Shift+P)
- Dev Containers: Build & Reopen Container

Make sure that the extension is enabled.

- API → `http://localhost:8000 `
- Valkey → `localhost:6379`
- Qdrant → `localhost:6333`


### 4. Create Virtual Environment
Inside the backend directory create a virtual environment

```bash

python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

Ignore if virtual environment already exists

### 5. Install Dependencies

```bash
cd backend

pip install -r requirements.txt
```


### 6. Run the Application
```bash
# Navigate to the backend directory (if not already there)
cd backend

# Run the FastAPI server
python -m src.server
```

The API will be available at `http://localhost:8000/docs`

### 7. Start Background Workers
In another terminal (inside the Dev Container):

```bash
rq worker --with-scheduler --url redis://valkey:6379

```

### 8. Access Services via Port Forwarding (VS Code)
If you're using VS Code, you can access the services through port forwarding:

You can do this by forward ports:

1. Going to the "Ports" tab in VS Code terminal panel
2. Clicking the "+" icon to add a port
3. Entering 8000 for API server or 6333 for Qdrant

- **API Server**: The FastAPI server is running on port 8000. You can access it at `http://localhost:8000`

- **Qdrant Dashboard**: Qdrant is running on port 6333. To access the Qdrant web UI dashboard, you can open it in your browser at `http://localhost:6333`

### 9. 📡 How to Interact with the API

When you make a request to either `/process-text`, `/upload-pdf`, or `/process-pdf`, the API does not process the task immediately. Instead:

1. The task is **queued** to a background worker (via RQ).
2. The API responds with a unique `task_id` and status `queued`.
3. You must **poll the `/result/{task_id}` endpoint** repeatedly until the result becomes available.

---

---

# 🛠️ Docker Services

| Service | Port  | Description                  |
|---------|-------|------------------------------|
| FastAPI | 8000  | Backend API                  |
| Valkey  | 6379  | Cache & job queue backend    |
| Qdrant  | 6333  | Vector database for PDFs     |

---


# ☁️ Deployment

This app can be deployed on:

- 🐳 Docker Compose (self-host)
- Render/Fly.io (for API)
- Managed Redis (for Valkey alternative)
- Managed Qdrant Cloud

---

# 📖 Example Workflow

1. Upload a PDF → `/upload-pdf`
2. Ask question about PDF → `/process-pdf`
3. Check job result → `/result/{task_id}`
4. Repeat? Cache returns instant response

---

# 🧑‍💻 Dev Notes

- Use Valkey as Redis drop-in replacement (lighter, faster)
- PDF chunks stored in Qdrant with embeddings for semantic search
- Background tasks (LLM calls) handled by RQ workers
