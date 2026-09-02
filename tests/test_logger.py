import logging
from app.utils import setup_logging, logger
from app.config import settings


def test_logger_setup(tmp_path):
    """Verify that logger initialization completes without error and sets up log directories."""
    # Override settings path to a temp dir for testing
    settings.db.sqlite_db_path = tmp_path / "test.db"
    
    # Run setup
    setup_logging()
    
    # Assert logs directory was created
    logs_dir = tmp_path / "logs"
    assert logs_dir.exists()
    assert logs_dir.is_dir()
    
    # Verify we can log a test message
    logger.info("Test log statement to verify setup.")
