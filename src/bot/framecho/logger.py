import logging
from logging.handlers import TimedRotatingFileHandler
from os import path, getcwd, makedirs
from threading import Lock
from traceback import format_exception
from typing import Union


class Logger:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_logger()
            return cls._instance

    def _init_logger(self):
        self._config_path = path.join(getcwd(), "runtime", "logs")
        makedirs(self._config_path, exist_ok=True)

        self._logger = logging.getLogger("edfy")
        self._logger.setLevel(logging.DEBUG)

        self._info_stream_handler = logging.StreamHandler()
        self._info_stream_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d]\n[%(levelname)s] %(message)s"
            )
        )
        self._info_stream_handler.setLevel(logging.INFO)
        self._logger.addHandler(self._info_stream_handler)

        self._file_handler = TimedRotatingFileHandler(
            path.join(self._config_path, "log.txt"), when="midnight", delay=False
        )
        self._file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d]\n[%(levelname)s] %(message)s"
            )
        )
        self._file_handler.setLevel(logging.INFO)
        self._logger.addHandler(self._file_handler)

    def set_debug_level(self):
        self._logger.info("The logging level is set to debug mode.")
        self._info_stream_handler.setLevel(logging.DEBUG)

    def set_info_level(self):
        self._logger.info("The logging level is set to info mode.")
        self._info_stream_handler.setLevel(logging.INFO)

    def disable_file_logging(self):
        self._logger.info("File logging is disabled.")
        self._file_handler.setLevel(logging.NOTSET)

    def enable_file_logging(self):
        self._logger.info("File logging is enabled.")
        self._file_handler.setLevel(logging.INFO)

    @staticmethod
    def _parse_exception(exc: Exception) -> str:
        return "".join(format_exception(exc))

    def _log(
        self,
        level: str,
        message: Union[str, Exception, None] = None,
        exc: Exception = None,
    ):
        if isinstance(message, Exception):
            exc = message
            message = None

        if exc:
            exception_text = self._parse_exception(exc)
            message = (
                f"{message}\nException:\n{exception_text}"
                if message
                else f"Exception:\n{exception_text}"
            )

        if message:
            getattr(self._logger, level)(message)
        else:
            getattr(self._logger, level)(
                "No message provided, but an exception was logged."
            )

    def debug(self, message: Union[str, Exception, None] = None, exc: Exception = None):
        self._log("debug", message, exc)

    def info(self, message: Union[str, Exception, None] = None, exc: Exception = None):
        self._log("info", message, exc)

    def warning(
        self, message: Union[str, Exception, None] = None, exc: Exception = None
    ):
        self._log("warning", message, exc)

    def error(self, message: Union[str, Exception, None] = None, exc: Exception = None):
        self._log("error", message, exc)

    def critical(
        self, message: Union[str, Exception, None] = None, exc: Exception = None
    ):
        self._log("critical", message, exc)
