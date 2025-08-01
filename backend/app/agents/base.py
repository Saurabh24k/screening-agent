import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the AI Screening System.
    Provides standard logging, config injection, and interface for process().
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = self._initialize_logger()

    def _initialize_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"agent.{self.name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def log_info(self, message: str, candidate_id: Optional[str] = None):
        prefix = f"[{candidate_id}] " if candidate_id else ""
        self.logger.info(f"{prefix}{message}")

    def log_warning(self, message: str, candidate_id: Optional[str] = None):
        prefix = f"[{candidate_id}] " if candidate_id else ""
        self.logger.warning(f"{prefix}{message}")

    def log_error(self, message: str, candidate_id: Optional[str] = None, exc: Optional[Exception] = None):
        prefix = f"[{candidate_id}] " if candidate_id else ""
        if exc:
            self.logger.error(f"{prefix}{message} | Exception: {str(exc)}")
        else:
            self.logger.error(f"{prefix}{message}")

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """
        Each agent must implement this method.
        Processes the input data and returns output.
        """
        raise NotImplementedError("Agent must implement the process() method.")
