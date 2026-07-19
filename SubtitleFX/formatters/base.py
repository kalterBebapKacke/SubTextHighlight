from abc import ABC, abstractmethod

FORMATTER_REGISTER = {}

def register(cls):
    FORMATTER_REGISTER[cls.__name__.lower()] = cls
    return cls

class BaseFormatter(ABC):
    def __init__(self, event_factory, time_resolver, char_max):
        self.event_factory = event_factory
        self.time_resolver = time_resolver
        self.char_max = char_max

    def format(self, subs_file):
        events = subs_file.return_events()

        self.time_resolver.duration = subs_file.duration
        events = self._format(events)

        subs_file.set_events(events)
        return subs_file

    @abstractmethod
    def _format(self, subs: list) -> list:
        ...