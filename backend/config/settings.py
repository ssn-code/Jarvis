from pathlib import Path
from typing import Literal, Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class OpenRouterSettings(BaseSettings):
    """Configuration for OpenRouter LLM APIs."""
    model_config = SettingsConfigDict(
        env_prefix="OPENROUTER_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    api_key: SecretStr = Field(
        default=SecretStr(""),
        description="OpenRouter API Key."
    )
    api_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API."
    )
    planner_model: str = Field(
        default="deepseek/deepseek-chat",
        description="Default model for agent planning and task decomposition."
    )
    chat_model: str = Field(
        default="qwen/qwen-2.5-32b-instruct",
        description="Default model for conversation."
    )
    coding_model: str = Field(
        default="qwen/qwen-2.5-coder-32b-instruct",
        description="Default model for writing and reviewing code."
    )
    vision_model: str = Field(
        default="qwen/qwen-2-vl-72b-instruct",
        description="Default model for vision and screenshot analysis."
    )


class LocalLLMSettings(BaseSettings):
    """Configuration for local LLM inference (e.g. Ollama, vLLM)."""
    model_config = SettingsConfigDict(
        env_prefix="LOCAL_LLM_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    url: str = Field(default="http://localhost:11434/v1", description="Local LLM API base URL.")
    model: str = Field(default="llama3.2:3b", description="Local model name or path.")


class DatabaseSettings(BaseSettings):
    """Configuration for database storage systems."""
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    sqlite_db_path: Path = Field(
        default=BASE_DIR / "backend" / "brain" / "jarvis.db",
        description="Path to SQLite database file."
    )
    chromadb_dir: Path = Field(
        default=BASE_DIR / "backend" / "brain" / "chroma",
        description="Directory path for storing ChromaDB vector embeddings."
    )


class VoiceSettings(BaseSettings):
    """Configuration for voice recognition and synthesis."""
    model_config = SettingsConfigDict(
        env_prefix="VOICE_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    wake_word: str = Field(default="jarvis", description="Wake word to listen for.")
    whisper_model: str = Field(default="base", description="Whisper speech recognition model size.")
    piper_voice: str = Field(default="en_US-lessac-medium", description="Piper TTS voice model identifier.")
    continuous_listening: bool = Field(default=False, description="Enable continuous audio listening.")
    push_to_talk: bool = Field(default=True, description="Enable push-to-talk mode.")


class SecuritySettings(BaseSettings):
    """Configuration for security levels, encryption, and sandboxing."""
    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    encryption_key: SecretStr = Field(
        default=SecretStr(""),
        description="Symmetric encryption key for secure credentials storage."
    )
    default_verification_level: Literal["SAFE", "CONFIRM", "ADMIN"] = Field(
        default="CONFIRM",
        description="Default security verification level for tools."
    )
    sandbox_workspace: Path = Field(
        default=BASE_DIR / "backend" / "brain" / "sandbox",
        description="Safe directory for isolated code or file executions."
    )


class PresentationSettings(BaseSettings):
    """Configuration for API server and presentation layers."""
    model_config = SettingsConfigDict(
        env_prefix="PRESENTATION_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    api_host: str = Field(default="127.0.0.1", description="FastAPI host binding.")
    api_port: int = Field(default=8000, description="FastAPI port.")
    theme: Literal["dark", "light"] = Field(default="dark", description="Visual theme style.")
    window_width: int = Field(default=1200, description="Initial application window width.")
    window_height: int = Field(default=800, description="Initial application window height.")


class MCPSettings(BaseSettings):
    """Configuration for Model Context Protocol (MCP) integration."""
    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    auto_activation: bool = Field(default=True, description="Automatically activate required MCP servers per task.")
    connect_timeout_seconds: int = Field(default=10, description="Timeout in seconds when connecting to MCP servers.")


class Settings(BaseSettings):
    """Root configuration for JARVIS."""
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    env: Literal["development", "production", "testing"] = Field(
        default="development",
        description="Current application execution mode."
    )
    app_name: str = Field(default="JARVIS", description="System identifier name.")
    app_version: str = Field(default="0.1.0", description="System version.")

    openrouter: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    local_llm: LocalLLMSettings = Field(default_factory=LocalLLMSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    presentation: PresentationSettings = Field(default_factory=PresentationSettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)


# Global settings singleton
settings = Settings()
