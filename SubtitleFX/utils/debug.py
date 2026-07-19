import logging
from typing import Optional
import sys

def debug(file:Optional[str]=None):
    if file:
        logging.basicConfig(filename=file, filemode='w', encoding='utf-8', level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
