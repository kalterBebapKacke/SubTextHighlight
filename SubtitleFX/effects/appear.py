

class Appear:

    def render(self, sub_file):
        events = sub_file.return_events()
        for event in events:
            event.set_appear_style(r'{\alpha&HFF}')
        sub_file.set_events(events)
        return sub_file