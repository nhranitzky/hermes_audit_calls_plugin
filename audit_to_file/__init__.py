import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any

def get_hermes_profile() -> tuple[str, Path, Path]:
    """Return the active Hermes profile name, profile home, and data directory."""
    hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).resolve()

    if hermes_home.parent.name == "profiles":
        return hermes_home.name, hermes_home, hermes_home.parent.parent

    return "default", hermes_home, hermes_home



def _initialize_logger(log_file: Path) -> logging.Logger:
    """Create the tool audit logger and attach a rotating file handler."""
    logger = logging.getLogger("audit_calls")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=30)
    except OSError:
        handler = logging.NullHandler()

    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger

_, PROFILE_HOME, _ = get_hermes_profile()
LOG_FILE = PROFILE_HOME / "logs" / "audit.log"
logger = _initialize_logger(LOG_FILE)


def on_post_llm_call(*, task_id: str = "", session_id: str = "", provider: str = "", base_url: str = "",
                     api_mode: str = "", model: str = "", api_call_count: int = 0,
                     assistant_message: Any = None, response: Any = None,
                     api_duration: float = 0.0, finish_reason: str = "",
                     usage: Any = None, assistant_content_chars: int = 0,
                     assistant_tool_call_count: int = 0, assistant_response: Any = None,
                     **kwargs: Any) -> None:
    """Record metadata for completed LLM API calls."""
    logger.info("LLM_CALL  => session=%s, model=%s/%s, api_calls=%s, api_duration=%s (s), tool_calls=%s, usage=%s, chars=%s, rest=%s",
                session_id, provider, model, api_call_count, api_duration,
                assistant_tool_call_count, usage, 
                assistant_content_chars,kwargs)


def on_post_tool_call(*, tool_name: str = "", args: Any = None, result: Any = None,
                      task_id: str = "", session_id: str = "", tool_call_id: str = "",
                      duration_ms: int = 0, **_: Any) -> None:
    """Record metadata for completed tool calls."""
    try:
        parsed = json.loads(result) if isinstance(result, str | bytes | bytearray) else result
        is_error = isinstance(parsed, dict) and parsed.get("error") is not None
    except Exception:
        is_error = True

    logger.info("TOOL_CALL => session=%s, tool=%s, error=%s, duration=%s (ms): args=%s",
                session_id, tool_name, is_error, duration_ms, json.dumps(args, default=str)[:200])


def register(ctx):
    """Register the plugin hooks with the Hermes runtime."""
    ctx.register_hook("post_tool_call", on_post_tool_call)
    ctx.register_hook("post_api_request", on_post_llm_call) 
