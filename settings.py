"""
settings.py
──────────────────────────────────────────────────
Central configuration for NIVESH.
Every file imports from here — never reads .env directly.

Industry standard:
- Single source of truth for all settings
- Logger configured once, imported everywhere
- Cache initialized once, reused everywhere
"""


import os
import logging
from functools import lru_cache
from logging import Logger

from dotenv import load_dotenv

load_dotenv()

def setup_logger(name: str = "nivesh")-> logging.Logger:
    """
    Create and configure the application logger.

    Log levels (low to high):
        DEBUG    → detailed info for debugging
        INFO     → normal app events
        WARNING  → something unexpected but not breaking
        ERROR    → something broke
        CRITICAL → app cannot continue
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Console handler ───────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    # ── File handler ──────────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(BASE_DIR, "nivesh.log")

    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger("nivesh")

logger = setup_logger("nivesh")

# ------- API KEYS-------------------------------------

def get_groq_api_key()-> str:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        logger.critical("GROQ_API_KEY not found in .env")
        raise EnvironmentError("GROQ_API_KEY is missing. Add it to your .env file.")
    return key

def get_news_api_key()-> str:
    key = os.getenv("NEWS_API_KEY")
    if not key:
        logger.warning("NEWS_API_KEY not found — news features will be limited.")
    return key or ""

# ------- LLM SETTING --------------------------------

LLM_MODEL       = "llama-3.1-8b-instant"
LLM_TEMPERATURE = 0
LLM_MAX_TOKENS  = 1024

# -------- CACHE -------------------------------------

CACHE_TTL_SECONDS= 600

import time

_cache: dict = {}

def cache_get(key: str):
    """Get value from cache if not expired."""
    if key in _cache:
        timestamp, data = _cache[key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            logger.debug(f"Cache HIT for key: {key}")
            return data
        else:
            logger.debug(f"Cache EXPIRED for key: {key}")
            del _cache[key]
    logger.debug(f"Cache MISS for key: {key}")
    return None

def cache_set(key: str, data) -> None:
    """Store value in cache with current timestamp."""
    _cache[key] = (time.time(), data)
    logger.debug(f"Cache SET for key: {key}")

def cache_clear() -> None:
    """Clear entire cache."""
    _cache.clear()
    logger.info("Cache cleared")

# ---------- APP SETTINGS --------------------------------

APP_NAME = "NIVESH"
APP_VERSION = "1.0.0"
APP_TAGLINE = "AI-Powered Indian Stock Research Analyst"

# -------- Startup log ------------------------------------
logger.info(f"{APP_NAME} v{APP_VERSION} — config loaded")
logger.info("Settings loaded successfully")