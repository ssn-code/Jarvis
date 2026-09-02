# JARVIS — Modular Personal AI Assistant

> **Google Gemini-style Android UI + powerful desktop AI assistant + voice + vision + memory + MCP tools + automation.**

JARVIS is built as a real, extensible personal AI operating system. The interface remains clean and simple on the surface, while the backend provides a modular, production-ready AI architecture.

---

## Current Status: Phase J0 Complete

Phase J0 (Architecture & Setup) establishes the complete runnable foundation:
- **FastAPI Core Backend** with SQLite async database foundation, structured logging, and system telemetry.
- **Google Gemini-Inspired Frontend** built with React, TypeScript, Vite, and modern CSS dark-mode tokens.
- **Pydantic v2 Configuration** with environment protection and secret masking.
- **Model Context Protocol (MCP) Foundation** ready for tool discovery and server registration.
- **Comprehensive Automated Test Suite** verifying configuration, database persistence, system metrics, and API routes.

---

## Project Structure

```text
JARVIS/
├── backend/
│   ├── api/             # FastAPI app and REST routes (/health, /api/*)
│   ├── core/            # Domain models and entity definitions
│   ├── config/          # Pydantic Settings & environment loader
│   ├── database/        # Async-safe SQLite database manager
│   ├── llm/             # Multi-provider LLM abstraction (Phase J2)
│   ├── memory/          # Short and long-term memory (Phase J3)
│   ├── voice/           # Voice pipeline (Phase J4)
│   ├── vision/          # Vision and screenshot analysis (Phase J10)
│   ├── mcp/             # Model Context Protocol subsystem (Phase J5+)
│   ├── tools/           # Internal tools and helpers
│   ├── automation/      # Task automation engine (Phase J11)
│   ├── security/        # Security sandboxing and permission gating
│   ├── system/          # Host monitoring (CPU, RAM, Disk, Uptime)
│   └── utils/           # Loguru structured logging
├── frontend/            # React + TypeScript + Vite Gemini-style UI
│   ├── src/
│   │   ├── components/  # Header, Sidebar, ChatArea, Composer, MCP/Memory views
│   │   ├── services/    # Typed API client
│   │   ├── styles/      # Design tokens and responsive styles
│   │   └── types/       # TypeScript interface models
│   ├── package.json
│   └── vite.config.ts
├── mcp-servers/         # MCP configuration templates & custom servers
├── config/              # Shared configurations
├── docs/                # Architecture documentation
├── tests/               # Backend unit and integration test suite
├── .env.example         # Environment template
└── pyproject.toml       # Python project configuration
```

---

## Getting Started

### 1. Prerequisites

- **Python**: `>= 3.13`
- **Node.js**: `>= 20` (Node v24 tested)
- **uv** (or standard virtual environment)

### 2. Setup Environment

```bash
# Copy template configuration
cp .env.example .env

# Activate virtual environment
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate # macOS/Linux
```

### 3. Run Backend Server

```bash
.venv\Scripts\python.exe -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8000 --reload
```

- Health check: `http://127.0.0.1:8000/health`
- Swagger API Docs: `http://127.0.0.1:8000/docs`

### 4. Run Frontend Development Server

```bash
cd frontend
npm.cmd run dev
```

- Application runs at: `http://localhost:5173`

---

## Running Tests

Run the automated test suite:

```bash
.venv\Scripts\python.exe -m pytest tests/ -v
```

Build the frontend bundle:

```bash
cd frontend
npm.cmd run build
```

---

## Roadmap

- **[x] Phase J0** — Architecture & Setup
- **[ ] Phase J1** — Gemini-Style Chat UI
- **[ ] Phase J2** — LLM Integration (OpenRouter / NVIDIA / Local models)
- **[ ] Phase J3** — Short & Long-Term Memory
- **[ ] Phase J4** — Real-Time Voice Pipeline
- **[ ] Phase J5** — MCP Client & Server Registry
- **[ ] Phase J6** — Dynamic MCP Tool Routing
- **[ ] Phase J7** — MCP Security & Permission Gating
- **[ ] Phase J8** — Computer & OS Control
- **[ ] Phase J9** — Web Browsing & Research
- **[ ] Phase J10** — Vision & Screenshot Understanding
- **[ ] Phase J11** — Task Automation Engine
- **[ ] Phase J12** — IoT & Device Integration
- **[ ] Phase J13** — Advanced MCP Platform
- **[ ] Phase J14** — Optimization & Production Polish

---

## License

MIT License — see [LICENSE](LICENSE).
