"""
Configuration settings for the paperwork generation API.
"""

import logging
import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        # Base directories
        self.base_dir = Path(__file__).parent.parent
        self.templates_dir = Path(
            os.getenv("PAPERWORK_TEMPLATES_DIR", self.base_dir / "templates")
        ).expanduser()
        self.signatures_dir = Path(
            os.getenv("PAPERWORK_SIGNATURES_DIR", self.base_dir / "signatures")
        ).expanduser()
        self.output_dir = Path(
            os.getenv("PAPERWORK_OUTPUT_DIR", self.base_dir / "output")
        ).expanduser()
        
        # API settings
        self.api_title = "Paperwork Generation API"
        self.api_version = "1.0.0"
        self.api_description = "HTTP API for generating loadsheets and timesheets from JSON data"
        
        # Server settings
        self.host = os.getenv("HOST", "::")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # LibreOffice settings for PDF conversion
        self.libreoffice_timeout = 60
        self._pdf_enabled_override: Optional[bool] = None
        
    @property
    def sig1_dir(self) -> Path:
        """Directory containing signature 1 images."""
        return self.signatures_dir / "sig1"
    
    @property
    def sig2_dir(self) -> Path:
        """Directory containing signature 2 images."""
        return self.signatures_dir / "sig2"
    
    @property
    def loadsheet_template(self) -> Path:
        """Path to loadsheet Excel template."""
        return self.templates_dir / "loadsheet.xlsx"
    
    @property
    def timesheet_template(self) -> Path:
        """Path to timesheet Excel template."""
        return self.templates_dir / "timesheet.xlsx"

    @property
    def pdf_enabled(self) -> bool:
        """Whether LibreOffice PDF conversion should run."""
        if self._pdf_enabled_override is not None:
            return self._pdf_enabled_override
        return os.getenv("PAPERWORK_DISABLE_PDF", "false").lower() != "true"

    def set_pdf_enabled(self, enabled: bool) -> None:
        """Override PDF conversion toggle at runtime."""
        self._pdf_enabled_override = bool(enabled)

    def clear_pdf_override(self) -> None:
        """Clear any PDF override, falling back to environment variable."""
        self._pdf_enabled_override = None


def create_app_directories(settings: "Settings"):
    """Create the necessary directories for the application."""
    logger = logging.getLogger("paperworkgen")
    try:
        settings.templates_dir.mkdir(parents=True, exist_ok=True)
        settings.signatures_dir.mkdir(parents=True, exist_ok=True)
        settings.sig1_dir.mkdir(parents=True, exist_ok=True)
        settings.sig2_dir.mkdir(parents=True, exist_ok=True)
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Application directories created successfully.")
    except PermissionError:
        logger.warning(
            "Could not create application directories due to a permission error. "
            "Please ensure the user running the application has write access to the volume."
        )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings instance."""
    return settings
