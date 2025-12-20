import logging


class LineCountRotatingFileHandler(logging.FileHandler):
    """
    This Custom Handler will emit each log message.
    it prevent exceed the no.of max lines
    """

    def __init__(self, filename, mode="a", encoding=None, delay=False, max_lines=1000):
        super().__init__(filename, mode, encoding, delay)
        self.max_lines = max_lines

    def emit(self, record):
        super().emit(record)
        self._trim_file()

    def _trim_file(self):
        try:
            with open(self.baseFilename, "r+", encoding=self.encoding or "utf-8") as f:
                lines = f.readlines()

                if len(lines) <= self.max_lines:
                    return

                # Keep only the last `max_lines` lines
                f.seek(0)
                f.writelines(lines[-self.max_lines :])
                f.truncate()
        except Exception:
            self.handleError(None)

class IgnoreReloadFilter(logging.Filter):
    """
    This will ignore all default django builtin reloader
    """
    def filter(self, record):
        return not record.name.startswith("django.utils.autoreload") and not record.name.startswith("django.request")

LOGGER_METHODS = {
    "DEBUG": logging.Logger.debug,
    "INFO": logging.Logger.info,
    "WARNING": logging.Logger.warning,
    "ERROR": logging.Logger.error,
    "CRITICAL": logging.Logger.critical,
}


def log_message(
    module_name: str, message: str, level: str = "INFO", **kwargs
) -> logging.Logger:
    """
    Log a message at the given level and given module name.
    module_name: e.g. 'users', 'videos'
    level: Any one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    message: message to show on log file
    kwargs: for extra args (e.g. exc_info=True)
    """
    if level not in LOGGER_METHODS:
        raise ValueError(f"Invalid level for logger.")
    # create a fresh logger

    logger = logging.getLogger(f"{module_name}")
    LOGGER_METHODS[level](logger, message, **kwargs)

    return logger
