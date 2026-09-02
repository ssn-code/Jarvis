from backend.config.settings import settings, Settings


def test_settings_initialization():
    """Verify that the settings singleton initializes with required subsystems."""
    assert settings.app_name == "JARVIS"
    assert settings.env in ["development", "production", "testing"]
    assert settings.db.sqlite_db_path is not None
    assert settings.presentation.api_port == 8000
    assert settings.presentation.theme in ["dark", "light"]
    assert settings.voice.wake_word == "jarvis"
    assert settings.security.default_verification_level in ["SAFE", "CONFIRM", "ADMIN"]
    assert settings.mcp.auto_activation is True


def test_custom_settings_instance(tmp_path):
    """Verify that settings can be instantiated cleanly."""
    custom = Settings(env="testing")
    assert custom.env == "testing"
