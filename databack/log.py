import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def init_logging():
    uvicorn = logging.getLogger("uvicorn.access")
    for h in uvicorn.handlers:
        uvicorn.removeHandler(h)
    handler = InterceptHandler()
    uvicorn.addHandler(handler)
