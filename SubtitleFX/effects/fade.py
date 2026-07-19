

class Fade:

    def __init__(self, fade_in, fade_out):
        self.fade_in = fade_in
        self.fade_out = fade_out

    def render(self, sub_file):
        events = sub_file.return_events()
        for event in events:
            event.set_fade(self.fade_in, self.fade_out)
        sub_file.set_events(events)
        return sub_file