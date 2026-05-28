import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import find_dotenv, load_dotenv


_ENV_LOADED = False
_LOADED_ENV_PATH: str | None = None


def load_env_file() -> str | None:
    """
    Аккуратно подгружает .env один раз.

    Приоритет:
    1. LOG_ENV_FILE=/path/to/.env
    2. ближайший .env от текущей рабочей директории вверх
    3. ничего не грузим, если .env не найден

    override=False — реальные переменные окружения важнее .env.
    """
    global _ENV_LOADED, _LOADED_ENV_PATH

    if _ENV_LOADED:
        return _LOADED_ENV_PATH

    explicit_env_file = os.getenv("LOG_ENV_FILE")

    if explicit_env_file:
        env_path = Path(explicit_env_file).expanduser().resolve()

        if env_path.exists():
            load_dotenv(env_path, override=False)
            _LOADED_ENV_PATH = str(env_path)

        _ENV_LOADED = True
        return _LOADED_ENV_PATH

    found_env = find_dotenv(
        filename=".env",
        usecwd=True,
    )

    if found_env:
        load_dotenv(found_env, override=False)
        _LOADED_ENV_PATH = found_env

    _ENV_LOADED = True
    return _LOADED_ENV_PATH


def _parse_bool(val: str | None, default: bool = False) -> bool:
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "y", "on")


def _get_env(name: str, default: str) -> str:
    v = os.getenv(name)
    return default if v is None or v == "" else v


@dataclass(frozen=True)
class LogConfig:
    level: str
    logger_name: str

    console_enabled: bool
    console_format: Literal["text", "json"]

    text_file_enabled: bool
    text_file_path: str

    json_file_enabled: bool
    json_file_path: str

    rotation_when: str
    rotation_interval: int
    rotation_backup_count: int
    rotation_utc: bool

    sanitize_extra: bool
    stream_safe: bool
    stream_debug: bool

    datefmt: str
    text_fmt: str

    json_ts_key: str

    env_file_path: str | None = None


def load_config() -> LogConfig:
    env_file_path = load_env_file()

    level = _get_env("LOG_LEVEL", "INFO").upper()
    if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        level = "INFO"

    console_enabled = _parse_bool(os.getenv("LOG_CONSOLE"), True)
    console_format = _get_env("LOG_CONSOLE_FORMAT", "text").lower()
    if console_format not in {"text", "json"}:
        console_format = "text"

    text_file_enabled = _parse_bool(os.getenv("LOG_FILE_TEXT"), True)
    text_file_path = _get_env("LOG_FILE_TEXT_PATH", "logs/app.log")

    json_file_enabled = _parse_bool(os.getenv("LOG_FILE_JSON"), True)
    json_file_path = _get_env("LOG_FILE_JSON_PATH", "logs/app.json.log")

    rotation_when = _get_env("LOG_ROTATION_WHEN", "midnight")
    rotation_interval = int(_get_env("LOG_ROTATION_INTERVAL", "1"))
    rotation_backup = int(_get_env("LOG_ROTATION_BACKUP", "7"))
    rotation_utc = _parse_bool(os.getenv("LOG_ROTATION_UTC"), False)

    sanitize_extra = _parse_bool(os.getenv("LOG_SANITIZE_EXTRA"), True)

    stream_safe = _parse_bool(os.getenv("STREAM_SAFE"), True)
    stream_debug = _parse_bool(os.getenv("STREAM_DEBUG"), False)

    logger_name = _get_env("LOG_NAME", "app")
    datefmt = _get_env("LOG_DATEFMT", "%Y-%m-%d %H:%M:%S")

    text_fmt = _get_env(
        "LOG_TEXT_FMT",
        "[%(asctime)s] [%(levelname)s] %(message)s",
    )

    json_ts_key = _get_env("LOG_JSON_TS_KEY", "ts")

    return LogConfig(
        level=level,
        logger_name=logger_name,
        console_enabled=console_enabled,
        console_format=console_format,  # type: ignore[arg-type]
        text_file_enabled=text_file_enabled,
        text_file_path=text_file_path,
        json_file_enabled=json_file_enabled,
        json_file_path=json_file_path,
        rotation_when=rotation_when,
        rotation_interval=rotation_interval,
        rotation_backup_count=rotation_backup,
        rotation_utc=rotation_utc,
        sanitize_extra=sanitize_extra,
        stream_safe=stream_safe,
        stream_debug=stream_debug,
        datefmt=datefmt,
        text_fmt=text_fmt,
        json_ts_key=json_ts_key,
        env_file_path=env_file_path,
    )
