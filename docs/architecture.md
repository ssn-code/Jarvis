# JARVIS Architecture Documentation

## 1. Core Vision & Philosophy

**JARVIS** is a modular personal AI assistant designed with a clean, mobile-first Google Gemini-style user experience on top of an extensible, security-first backend:

> **"Simple on the surface. Powerful underneath."**

JARVIS avoids over-complicated sci-fi HUDs and cyber dashboards, offering a calm, distraction-free conversational surface while leveraging advanced capabilities under the hood:
- Long-term selective memory (SQLite + vector embeddings)
- Model Context Protocol (MCP) tool integration
- Dynamic MCP server activation & permission gating
- Host computer control with safety tiers (`READ_ONLY`, `AUTOMATIC`, `USER_APPROVAL`, `RESTRICTED`, `BLOCKED`)
- Real-time voice and vision pipelines

---

## 2. High-Level Architecture Diagram

```text
                                JARVIS
                                  │
       ┌──────────────────────────┼──────────────────────────┐
       │                          │                          │
       ↓                          ↓                          ↓
    Frontend                   AI Brain                   Security
  (React + TS)              (FastAPI Core)            (Permission & Logs)
       │                          │                          │
       │                 ┌────────┴────────┐                 │
       │                 ↓        ↓        ↓                 │
       │                LLM     Memory  Planner              │
       │                 │        │        │                 │
       │                 └────────┬────────┘                 │
       │                          ↓                          │
       │                     MCP Manager                     │
       │                          │                          │
       │                 ┌────────┴────────┐                 │
       │                 ↓        ↓        ↓                 │
       │             Filesystem Browser   Git                │
       │             MCP Server MCP Server MCP Server        │
       │                                                     │
       └─────────────────────────────────────────────────────┘
```

---

## 3. Directory Layout

```text
JARVIS/
│
├── backend/
│   ├── api/                     # FastAPI application & REST routers
│   │   └── routers/             # chat, memory, mcp, system, settings
│   ├── core/                    # Domain models & core entity definitions
│   ├── llm/                     # Multi-provider LLM abstraction (Phase J2)
│   ├── memory/                  # Short & long-term memory system (Phase J3)
│   ├── voice/                   # Audio pipeline: STT, TTS, VAD (Phase J4)
│   ├── vision/                  # Vision & screenshot analysis (Phase J10)
│   ├── mcp/                     # Model Context Protocol subsystem (Phase J5+)
│   │   ├── manager/             # Lifecycle and connection manager
│   │   ├── registry/            # Server & tool registry
│   │   ├── clients/             # Transport clients (stdio, SSE)
│   │   ├── configs/             # Server configurations
│   │   └── permissions/         # Security & approval gates
│   ├── tools/                   # Built-in helper tools
│   ├── automation/              # Scheduled & triggered tasks (Phase J11)
│   ├── security/                # Sandboxing, encryption, access control
│   ├── system/                  # Host monitoring (CPU, RAM, Disk, Uptime)
│   └── database/                # SQLite async-safe connection manager
│
├── frontend/                    # React 19 + TypeScript + Vite app
│   ├── src/
│   │   ├── components/          # Header, Sidebar, ChatArea, Composer, Views
│   │   ├── services/            # Typed backend API client
│   │   ├── styles/              # Gemini dark mode tokens & layout
│   │   └── types/               # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
│
├── mcp-servers/                 # Dedicated MCP configurations & custom servers
│   ├── configs/
│   └── custom/
│
├── config/                      # Global configurations
├── tests/                       # Automated unit & integration tests
├── scripts/                     # Developer & deployment utilities
├── docs/                        # Architecture & reference documentation
├── .env.example                 # Configuration template
├── pyproject.toml               # Python project configuration
└── README.md                    # Project overview & running instructions
```

---

## 4. Backend Subsystems

### 4.1 FastAPI Core API
- **Entry point**: `backend/api/app.py`
- **CORS enabled** for local frontend and mobile clients.
- **Async Lifespan**: Automates database migrations and logging setup on startup.

### 4.2 Database Layer (`backend/database/manager.py`)
- SQLite storage configured with **WAL mode** and **PRAGMA foreign_keys = ON**.
- Dedicated thread execution wrapped in async locks to prevent concurrency bottlenecks.
- Canonical tables:
  1. `conversations`: Sessions, titles, timestamps, and metadata.
  2. `messages`: Role, content, tool calls, and payload timestamps.
  3. `memories`: Key-value knowledge items with categories and importance ratings.
  4. `mcp_servers`: Registered external MCP endpoints and activation modes.
  5. `mcp_tools`: Discovered tools with input/output schemas and risk ratings.
  6. `tool_executions`: Execution audit history and latency metrics.
  7. `automations`: Scheduled and event-driven triggers.
  8. `settings`: Key-value user overrides.
  9. `audit_logs`: Immutable security log tracking all privileged tool calls.

### 4.3 Host Telemetry (`backend/system/monitor.py`)
- Non-blocking host resource probes using `psutil`.
- Tracks CPU load, memory utilization, disk storage, and host runtime.

---

## 5. Frontend Subsystems

### 5.1 Design Tokens (`frontend/src/styles/theme.css`)
- Colors: Deep surface dark mode (`#131314` base, `#1e1f20` surface, `#282a2c` elevated).
- Accents: Google Gemini tri-color gradient (`#4285F4` -> `#9B72CF` -> `#D96570`).
- Responsive: Floating pill composer, collapsible drawer navigation, card grids.

### 5.2 Gemini-Style UI Components
- **Header**: Minimalist toolbar with live system connectivity badge.
- **Sidebar**: History drawer with session management and quick navigation.
- **ChatArea**: Responsive bubble layout with quick-start suggestion chips.
- **Composer**: Expanding multiline text area with attachment, voice toggle, and send buttons.
- **Dedicated Panels**: MCP Server management, Long-Term Memory browser, Host Telemetry, and System Settings.

---

## 6. Safety & Security Model

1. **Secret Masking**: Sensitive keys (such as `NVIDIA_API_KEY`) are protected using `pydantic.SecretStr` and never returned in API responses.
2. **Permission Levels**: Tools are governed by five explicit tiers:
   - `READ_ONLY`
   - `AUTOMATIC`
   - `USER_APPROVAL`
   - `RESTRICTED`
   - `BLOCKED`
3. **Execution Auditing**: Privileged tool executions log actor, parameters, approval status, and execution duration in `audit_logs`.
