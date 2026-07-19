from dataclasses import dataclass

import pysubs2

@dataclass()
class TimeResolver:

    fill_sub_times: bool
    duration: int | None = None
    cur_subs: bool = False

    def set_cur_subs(self):
        self.cur_subs = True

    def start(self, subs: list[pysubs2.SSAEvent], index: int) -> int:
        if index == 0 and self.fill_sub_times:
            return pysubs2.make_time(s=0)

        if self.cur_subs:
            return subs[0].start

        return subs[index].start

    def end(self, subs: list, index: int, last: bool) -> int:
        if last and self.fill_sub_times:
            if self.duration is not None:
                return pysubs2.make_time(s=self.duration)
            else:
                raise ValueError('For the argument "fill_sub_times" an video has to be inputted via input_video or the subtitles have to be generated from a audio/video.')

        if self.fill_sub_times:
            return subs[index + 1].start

        return subs[index].end
