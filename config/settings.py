from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
STYLE_FILE = ASSETS_DIR / "styles.css"

load_dotenv(BASE_DIR / ".env")

APP_NAME = "HEYIYUN 中国电力工程企业项目经营管理平台"
APP_EN_NAME = "Power Engineering ERP & Project Management Platform"
APP_VERSION = "0.1.0"
DEFAULT_ROLE = "总经理"
DEFAULT_USER = "演示用户"
DATE_FORMAT = "%Y-%m-%d"
