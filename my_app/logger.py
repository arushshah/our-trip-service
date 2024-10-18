import logging

def setup_logger(name="flask.app"):
    """Sets up the logger with a StreamHandler."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()  # Stream logs to console
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:  # Avoid duplicate handlers
        logger.addHandler(handler)

    return logger
