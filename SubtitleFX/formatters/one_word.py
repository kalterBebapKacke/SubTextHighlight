from .base import BaseFormatter, register

@register
class OneWordFormatter(BaseFormatter):
    
    def _format(self, subs: list) -> list:
        new_subs = []
        for i, sub in enumerate(subs):
            last = i == len(subs) - 1
            start = self.time_resolver.start(subs, i)
            end   = self.time_resolver.end(subs, i, last)
            new_subs.extend(self.event_factory.build(sub.text, start, end, [sub]))
        return new_subs