from . import subtitle_render
import pysubs2
import dataclasses

@dataclasses.dataclass
class SubtitleFile:

    sub_file: pysubs2.SSAFile

    duration: int | None = dataclasses.field(default=None)
    resolution: tuple[float, float] | None = dataclasses.field(default=None)
    events: list = dataclasses.field(init=False)

    def __post_init__(self):
        self.events = self.sub_file.events

    def is_subfile_resolution_set(self):
        info = self.sub_file.info
        keys = info.keys()
        if 'PlayResX' in keys and 'PlayResY' in keys:
            return True
        else:
            return False

    def set_duration(self, duration):
        self.duration = duration

    def set_resolution(self, resolution:tuple[float, float]):
        self.resolution = resolution

    def return_events(self):
        return self.events

    def set_events(self, events):
        self.events = events

    def return_ssa_file(self):
        self.sub_file.events = self.events
        return self.sub_file

    def return_render_object(self):
        return subtitle_render.SubtitlePipeline(self.events)

def convert(sub_file:pysubs2.SSAFile):
    return SubtitleFile(sub_file=sub_file)

def render(sub_file:SubtitleFile):
    _render_object = sub_file.return_render_object()
    events = _render_object.render()
    sub_file.set_events(events)
    return sub_file.return_ssa_file()


