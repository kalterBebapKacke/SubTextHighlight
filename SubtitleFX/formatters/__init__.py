from . import *
from enum import Enum
from .base import FORMATTER_REGISTER
from .joined import JoinedFormatter
from .one_word import OneWordFormatter
from .sentence import SentenceFormatter

# putting formatter here as a string to have better support
class Formatters(str, Enum):
    one_word = 'onewordformatter'
    sentence = 'sentenceformatter'
    joined   = 'joinedformatter'