from .base import BaseFormatter

class JoinedFormatter(BaseFormatter):

    def _format(self, subs: list) -> list:
        new_subs = []
        cur_sentence = str()
        cur_subs = list()
        self.time_resolver.set_cur_subs()

        for i, sub in enumerate(subs):
            last = i == len(subs) - 1
            cur_sentence, cur_subs = self.add(cur_sentence, cur_subs, sub)
            next_sentence = self.next_word(cur_sentence, subs, i, last)

            if last or self.if_word_split(next_sentence):
                start = self.time_resolver.start(cur_subs, i)
                end   = self.time_resolver.end(subs, i, last)
                new_subs.extend(self.event_factory.build(cur_sentence, start, end, cur_subs))

                cur_sentence, cur_subs = self.reset_sentence()
        return new_subs

    def reset_sentence(self):
        cur_sentence = str()
        cur_subs = list()
        return cur_sentence, cur_subs

    def add(self, cur_sentence, cur_subs, sub):
        cur_sentence = cur_sentence + ' ' + sub.text if cur_sentence else sub.text
        cur_subs.append(sub)
        return cur_sentence, cur_subs

    def next_word(self, cur_sentence:str, subs:list, index:int, last:bool):
        if last:
            return cur_sentence

        new_sentence = cur_sentence + ' ' + subs[index + 1].text
        return new_sentence

    def if_word_split(self, next_sentence:str):
        if len(next_sentence) > self.word_max:
            return True
        return False