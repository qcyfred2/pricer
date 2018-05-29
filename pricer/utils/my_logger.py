# -*- coding: utf-8 -*-

import logging
import logging.handlers
from pricer.constants import LOG_PATH


infile = LOG_PATH
handler = logging.handlers.RotatingFileHandler(
    infile, mode='a', maxBytes=10 * 1024 * 1024, backupCount=3, encoding='utf-8')
fmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'

formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
