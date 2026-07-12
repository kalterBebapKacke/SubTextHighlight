from abc import ABC, abstractmethod

class BaseFormatter(ABC):
    def __init__(self, event_factory, time_resolver, word_max):
        self.event_factory = event_factory
        self.time_resolver = time_resolver
        self.word_max = word_max

    def format(self, subs_file):
        events = subs_file.return_events()

        self.time_resolver.duration = subs_file.duration
        events = self._format(events)

        subs_file.set_events(events)
        return subs_file

    @abstractmethod
    def _format(self, subs: list) -> list:
        ...