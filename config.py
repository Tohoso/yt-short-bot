import os
from dotenv import load_dotenv
import logging
import pathlib

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger('youtube-shorts-bot')

# 環境変数読み込み
load_dotenv()

# プロジェクトルートディレクトリ
ROOT_DIR = pathlib.Path(__file__).parent.absolute()

# Discord設定
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# AI API設定
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # 後方互換性のために残す
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# YouTube API設定
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
YOUTUBE_REDIRECT_URI = os.getenv('YOUTUBE_REDIRECT_URI', 'http://localhost:8080')

# ディレクトリ設定
OUTPUT_DIR = os.path.join(ROOT_DIR, os.getenv('OUTPUT_DIR', 'outputs'))
TEMP_DIR = os.path.join(ROOT_DIR, os.getenv('TEMP_DIR', 'temp'))
BACKGROUNDS_DIR = os.path.join(ROOT_DIR, os.getenv('BACKGROUNDS_DIR', 'assets/backgrounds'))
CREDENTIALS_DIR = os.path.join(ROOT_DIR, 'credentials')

# ファイルパス
DISCORD_TOKEN_FILE = os.path.join(CREDENTIALS_DIR, 'discord_token.txt')
OPENAI_API_KEY_FILE = os.path.join(CREDENTIALS_DIR, 'openai_api_key.txt')
ANTHROPIC_API_KEY_FILE = os.path.join(CREDENTIALS_DIR, 'anthropic_api_key.txt')
YOUTUBE_CLIENT_SECRETS_FILE = os.path.join(CREDENTIALS_DIR, 'client_secrets.json')

# 動画設定
VIDEO_DURATION = 6  # 秒
VIDEO_WIDTH = 1080  # 幅（ショート動画の推奨サイズ）
VIDEO_HEIGHT = 1920  # 高さ（ショート動画の推奨サイズ）

# テキスト設定
TEXT_FONT = 'Arial'  # フォント
TEXT_SIZE = 70  # フォントサイズ
TEXT_COLOR = 'white'  # テキスト色
TEXT_STROKE_COLOR = 'black'  # テキスト縁取り色
TEXT_STROKE_WIDTH = 2  # テキスト縁取り幅

# ファイルから認証情報を読み込む関数
def read_token_from_file(file_path):
    """ファイルからトークンを読み込む"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read().strip()
    return None

# 環境変数がない場合はファイルから読み込み
if not DISCORD_TOKEN:
    DISCORD_TOKEN = read_token_from_file(DISCORD_TOKEN_FILE)

if not OPENAI_API_KEY:
    OPENAI_API_KEY = read_token_from_file(OPENAI_API_KEY_FILE)

if not ANTHROPIC_API_KEY:
    ANTHROPIC_API_KEY = read_token_from_file(ANTHROPIC_API_KEY_FILE)

# 設定の検証
def validate_config():
    """設定値の検証"""
    config_valid = True
    
    if not DISCORD_TOKEN:
        logger.error("Discord Tokenが設定されていません")
        config_valid = False
        
    if not ANTHROPIC_API_KEY:
        logger.error("Anthropic API Keyが設定されていません")
        config_valid = False
        
    if not os.path.exists(YOUTUBE_CLIENT_SECRETS_FILE):
        logger.error(f"YouTube Client Secrets File ({YOUTUBE_CLIENT_SECRETS_FILE}) が見つかりません")
        config_valid = False
        
    return config_valid

# ディレクトリの存在確認と作成
def ensure_directories():
    """必要なディレクトリの存在を確認し、なければ作成"""
    for directory in [OUTPUT_DIR, TEMP_DIR, BACKGROUNDS_DIR, CREDENTIALS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"ディレクトリを作成しました: {directory}")
