"""
Configuration settings for the paperwork generation API.
"""

import os
from pathlib import Path


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
        
        # Ensure directories exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.signatures_dir.mkdir(parents=True, exist_ok=True)
        self.sig1_dir.mkdir(parents=True, exist_ok=True)
        self.sig2_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # API settings
        self.api_title = "Paperwork Generation API"
        self.api_version = "1.0.0"
        self.api_description = "HTTP API for generating loadsheets and timesheets from JSON data"
        
        # Server settings
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # LibreOffice settings for PDF conversion
        self.libreoffice_timeout = 60
        
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
        return os.getenv("PAPERWORK_DISABLE_PDF", "false").lower() != "true"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings instance."""
    return settings
