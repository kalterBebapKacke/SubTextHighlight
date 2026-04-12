from .base import BaseFormatter
from .joined import JoinedFormatter

class SentenceFormatter(JoinedFormatter):

    def _format(self, subs: list) -> list:
        new_subs = []
        cur_sentence = str()
        cur_subs = list()
        self.time_resolver.set_cur_subs()

        for i, sub in enumerate(subs):
            last = i == len(subs) - 1
            cur_sentence, cur_subs = self.add(cur_sentence, cur_subs, sub)

            if last or self.if_split(cur_sentence):
                start = self.time_resolver.start(cur_subs, i)
                end   = self.time_resolver.end(subs, i, last)
                new_subs.extend(self.event_factory.build(sub.text, start, end, cur_subs))

                cur_sentence, cur_subs = self.reset_sentence()
        return new_subs

    def if_split(self, cur_sentence):
        if cur_sentence.__contains__('.') or cur_sentence.__contains__('?') or cur_sentence.__contains__('!') or cur_sentence.__contains__(','):
            return True
        return False