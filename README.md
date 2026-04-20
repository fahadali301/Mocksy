# Mocksy: AI Video Interview Platform

Mocksy is a stateful, dynamic AI-powered mock interview platform that simulates real-world job interviews. It allows candidates to upload their resumes and undergo hands-free, face-to-face video interviews or text chat sessions tailored precisely to their CV and target role.

---

## Tech Stack
- **Backend**: FastAPI (Python), WebSockets (real-time streaming), Postgres (SQLAlchemy),
- **Frontend**: React (Vite), CSS Layouts, Web Speech API (Native Speech-to-Text & Text-to-Speech)
- **AI Brain**: Groq Cloud API (Low Tier Latency LLM responses)

---

## Getting Started

Follow these steps to run the full application locally.

### 1. Backend Setup

Open a terminal and navigate to the project root directory.

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Setup:**
   Ensure you have a `.env` file in the root directory containing your Groq API key:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key_here
   GROQ_ENABLED=true
   ```
4. **Run the Database Migrations (if applicable) & Server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *The backend handles both REST endpoints (Port `8000`) and WebSocket streaming routes.*

### 2. Frontend Setup

Open a **second** terminal and navigate to the `frontend/` directory.

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```
2. **Start the development server:**
   ```bash
   npm run dev -- --host 0.0.0.0
   ```
   *(Using `--host 0.0.0.0` makes the interface accessible on your phone via your computer's local IP address, e.g., `http://192.168.1.X:5174`)*

---

## The User Flow

Once both servers are running, access the frontend (typically `http://localhost:5174`) to experience the platform.

### Phase 1: Authentication & Dashboard
1. **Register/Login**: Users create an account. Auth is handled securely via JWT tokens across both REST and WebSocket layers.
2. **CV Upload**: Users upload a PDF resume using the dashboard grid. The backend parses the PDF and stores a preview in the DB.

### Phase 2: Starting the Interview
1. **Click "Start Mock Interview"**: This triggers a modal asking for the **Target Role** (e.g., *Senior Frontend Dev*) and the **Interview Mode**.
2. **Mode Selection**:
   - **Text Chat**: Standard chat interface.
   - **Video Call**: Immersive split-screen experience.

### Phase 3: The Video Interview Experience 🎥
If the Video Call is selected:
1. **Camera Feed**: Mocksy captures the user's camera to render a sleek, mirrored video feed.
2. **AI Avatar**: An animated agent appears on the screen, reacting with audio-visual lip-sync behaviors whenever the AI speaks.
3. **Conversational Turn**:
   - The user taps the microphone button to speak *("Tap to Talk")*. Mocksy converts speech to text using the browser's native `SpeechRecognition` API.
   - The raw text is streamed straight to the FastAPI **WebSocket** backend.
   - The Groq API generates an intelligent, empathetic follow-up question.
   - The AI's response is spoken out loud to you via the `SpeechSynthesis` Web API, while generating cinematic pop-up subtitles on the screen.

### Phase 4: Final Evaluation
1. **Click "End Interview"**: The camera explicitly shuts down. Note: The user can explicitly send `exit` in the text command too.
2. **Scorecard**: The backend reviews the entire conversation history, evaluates accuracy and tone, and returns a comprehensive scorecard (Overall Score, Summary, Strengths, and Improvements) which the user can read to improve their interview skills.

## Frontend REPO Link: https://github.com/itxmuhammadwaqarali/mocksy_frontend

---

*Mocksy effectively mirrors the stress and dynamics of real AI filtering gates and technical interviews!*
