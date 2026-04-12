from . import one_word, sentence, joined

FormatterRegister = {
    "one_word" : one_word.OneWordFormatter,
    "sentence" : sentence.SentenceFormatter,
    "joined"   : joined.JoinedFormatter
}