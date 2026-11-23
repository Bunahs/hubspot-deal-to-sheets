
import os
from pathlib import Path
from dotenv import load_dotenv

# Xác định thư mục gốc của project
BASE_DIR = Path(__file__).resolve().parent

# Đọc file .env
load_dotenv(BASE_DIR / ".env")

# HubSpot configuration
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")

HUBSPOT_BASE_URL = "https://api.hubapi.com"

# Google Sheets configuration
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Chuyển đường dẫn credentials thành đường dẫn tuyệt đối
if GOOGLE_CREDENTIALS:
    GOOGLE_CREDENTIALS = str(
        (BASE_DIR / GOOGLE_CREDENTIALS).resolve()
    )


def validate_config():
    """Kiểm tra các thông tin cấu hình bắt buộc."""

    missing = []

    if not HUBSPOT_ACCESS_TOKEN:
        missing.append("HUBSPOT_ACCESS_TOKEN")

    if not GOOGLE_CREDENTIALS:
        missing.append("GOOGLE_CREDENTIALS")

    if not GOOGLE_SHEET_ID:
        missing.append("GOOGLE_SHEET_ID")

    if missing:
        raise ValueError(
            "Missing configuration: " + ", ".join(missing)
        )

    if not os.path.exists(GOOGLE_CREDENTIALS):
        raise FileNotFoundError(
            f"Google credentials file not found: {GOOGLE_CREDENTIALS}"
        )

    return True
