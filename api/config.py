"""
Cigar Lounge — Configuration
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cigar-lounge-secret-key-change-in-production')

    # Database
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'cigar_lounge')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # Upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    UPLOAD_FOLDER = BASE_DIR / 'app' / 'static' / 'images' / 'products'
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    # OSS (Alibaba Cloud)
    OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID', '')
    OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET', '')
    OSS_BUCKET = os.environ.get('OSS_BUCKET', '')
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', '')
    OSS_CDN_DOMAIN = os.environ.get('OSS_CDN_DOMAIN', '')

    # Pagination
    ITEMS_PER_PAGE = 20

    # i18n
    SUPPORTED_LANGUAGES = ['zh', 'en', 'ru']
    DEFAULT_LANGUAGE = 'zh'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cigar_lounge_dev.db'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://xuejia:xuejia_pass_2026@localhost/cigar_lounge?charset=utf8mb4'
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
