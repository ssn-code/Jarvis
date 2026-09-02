import os
from pathlib import Path
from typing import Literal
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project
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
        description="OpenRouter API Key. Required to make LLM requests."
    )
    api_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API."
    )
    
    # Model Configurations (Never hardcoded in logic, defined here as defaults and configurable via env)
    planner_model: str = Field(
        default="deepseek/deepseek-chat",
        description="Default model for agent planning and task decomposition (DeepSeek V3)."
    )
    chat_model: str = Field(
        default="qwen/qwen-2.5-32b-instruct",
        description="Default model for user chatting (Qwen 3 32B)."
    )
    coding_model: str = Field(
        default="qwen/qwen-2.5-coder-32b-instruct",
        description="Default model for writing and fixing code (Qwen Coder)."
    )
    vision_model: str = Field(
        default="qwen/qwen-2-vl-72b-instruct",
        description="Default model for screen and screenshot understanding (Qwen VL)."
    )


class DatabaseSettings(BaseSettings):
    """Configuration for database storage systems."""
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    sqlite_db_path: Path = Field(
        default=BASE_DIR / "app" / "brain" / "jarvis.db",
        description="Path to SQLite database file."
    )
    chromadb_dir: Path = Field(
        default=BASE_DIR / "app" / "brain" / "chroma",
        description="Directory path for storing ChromaDB vectors."
    )


class VoiceSettings(BaseSettings):
    """Configuration for voice recognition and generation services."""
    model_config = SettingsConfigDict(
        env_prefix="VOICE_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    wake_word: str = Field(default="jarvis", description="Wake word to listen for.")
    whisper_model: str = Field(default="base", description="Whisper speech recognition model size.")
    piper_voice: str = Field(default="en_US-lessac-medium", description="Piper TTS voice model identifier.")
    continuous_listening: bool = Field(default=True, description="Enable continuous audio listening in background.")
    push_to_talk: bool = Field(default=False, description="Use push-to-talk mode.")


class SecuritySettings(BaseSettings):
    """Configuration for encryption, permissions, and sandbox constraints."""
    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Cryptographic key for local secrets encryption
    encryption_key: SecretStr = Field(
        default=SecretStr(""),
        description="Fernet symmetric key for encrypting local keys/credentials."
    )
    
    # Minimum required permission for direct tool execution
    default_verification_level: Literal["SAFE", "CONFIRM", "ADMIN"] = Field(
        default="CONFIRM",
        description="Default security verification level for new/unknown tools."
    )
    
    # Safe directory path for file sandbox operations
    sandbox_workspace: Path = Field(
        default=BASE_DIR / "app" / "brain" / "sandbox",
        description="Path to local folder where python/code executions are sandboxed."
    )


class PresentationSettings(BaseSettings):
    """Configuration for UI theme, layout, and API parameters."""
    model_config = SettingsConfigDict(
        env_prefix="PRESENTATION_",
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # API Server configuration
    api_host: str = Field(default="127.0.0.1", description="FastAPI host binding.")
    api_port: int = Field(default=8000, description="FastAPI port number.")
    
    # UI configuration
    theme: Literal["dark", "light"] = Field(default="dark", description="Visual UI theme style.")
    window_width: int = Field(default=1200, description="Initial width of desktop application.")
    window_height: int = Field(default=800, description="Initial height of desktop application.")


class Settings(BaseSettings):
    """Main settings wrapper for JARVIS OS."""
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Environment mode
    env: Literal["development", "production", "testing"] = Field(
        default="development",
        description="Execution mode of the application."
    )
    
    # Sub-settings
    openrouter: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    presentation: PresentationSettings = Field(default_factory=PresentationSettings)


# Global settings instance
settings = Settings()
