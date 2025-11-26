import SubTextHighlight
import os
import pysubs2
import traceback
import whisper

def debug():
    os.environ['debug'] = 'True'

def main1():
    input = './media/plain_video.mp4'
    output = './media/edited_video.mp4'
    sub_args = SubTextHighlight.sub_args(input=input, output=output, input_video=input, subtitle_type='separate_on_period', fill_sub_times=False, alignment=2, fontname='Arial Rounded MT Bold', whisper_refine=True)
    highlight_args =  SubTextHighlight.highlight_args(primarycolor='00AAFF')
    effect_args = SubTextHighlight.effects_args((50, 50))
    sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
    sub_edit()

def main2():
    input = './media/plain_video.mp4'
    output = './media/subtitles.ass'
    sub_args = SubTextHighlight.sub_args(input=input, output=output, subtitle_type='separate_on_period', fill_sub_times=False, alignment=2, fontname='Arial Rounded MT Bold', whisper_refine=True)
    highlight_args =  SubTextHighlight.highlight_args(primarycolor='00AAFF')
    effect_args = SubTextHighlight.effects_args((50, 50))
    sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
    sub_edit()

class Test_Class():

    def __init__(self):
        debug()
        if not os.path.exists('./test_output'):
            os.mkdir('./test_output')

        # making a blank srt file with the wanted input format can decrease run time considerably, since whisper wont have to generate the subtitles
        # for every test case
        self.blank_srt_path = './test_output/blank.srt'

        self.input_video = './media/plain_video.mp4'

        self.test_functions = [
            self.one_word_only_and_fade,
            self.separate_on_period_and_highlighting,
            self.join_and_word_max,
            self.appear,
            self.rounded_borders
        ]

    def __call__(self, force_generate: bool = False):
        if not os.path.exists(self.blank_srt_path) or force_generate is True:
            self.blank_srt()

        for test_func in self.test_functions:
            try:
                print('////////////////////////////')
                print(f'Now testing {test_func.__name__}')
                test_func()
            except Exception as e:
                print(e)
                print(traceback.format_exc())

    def blank_srt(self):
        sub_args = SubTextHighlight.sub_args(
            input=self.input_video,
            output=None,
            subtitle_type='one_word_only',
            fill_sub_times=False,
            whisper_refine=True
        )
        sub_file: pysubs2.SSAFile = SubTextHighlight.Subtitle_Edit(sub_args)()
        sub_file.save(self.blank_srt_path)

    def _run_test(self, func_name, subtitle_type, fill_sub_times, word_max=None,
                  highlight_args=None, effect_args=None, alignment=2):
        """Helper method to run a test with given parameters"""
        output_mp4 = f'./test_output/{func_name}.mp4'
        output_ass = f'./test_output/{func_name}.ass'

        sub_args = SubTextHighlight.sub_args(
            input=self.blank_srt_path,
            output=output_ass,
            subtitle_type=subtitle_type,
            fill_sub_times=fill_sub_times,
            alignment=alignment,
            input_video=self.input_video
        )

        if word_max is not None:
            sub_args.word_max = word_max

        sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
        sub_edit()
        SubTextHighlight.utils.add_subtitles_with_ffmpeg_with_given_ass(
            self.input_video, output_mp4, output_ass
        )

    def one_word_only_and_fade(self):
        self._run_test(
            func_name='one_word_only_and_fade',
            subtitle_type='one_word_only',
            fill_sub_times=True,
            effect_args=SubTextHighlight.effects_args(fade=(50, 50))
        )

    def separate_on_period_and_highlighting(self):
        self._run_test(
            func_name='separate_on_period_and_highlighting',
            subtitle_type='separate_on_period',
            fill_sub_times=False,
            highlight_args=SubTextHighlight.highlight_args(
                highlight_word_max=0,
                primarycolor='00AAFF'
            )
        )

    def join_and_word_max(self):
        self._run_test(
            func_name='join_and_word_max',
            subtitle_type='join',
            fill_sub_times=False,
            word_max=20
        )

    def appear(self):
        self._run_test(
            func_name='appear',
            subtitle_type='join',
            fill_sub_times=False,
            word_max=20,
            effect_args=SubTextHighlight.effects_args(fade=(50, 50), appear=True)
        )

    def rounded_borders(self):
        self._run_test(
            func_name='rounded_borders',
            subtitle_type='join',
            fill_sub_times=False,
            word_max=20,
            effect_args=SubTextHighlight.effects_args(
                fade=(50, 50),
                args_border=SubTextHighlight.args_border()
            )
        )

    def rounded_background_highlight(self):
        self._run_test(
            func_name='rounded_background_highlight',
            subtitle_type='separate_on_period',
            fill_sub_times=False,
            highlight_args=SubTextHighlight.highlight_args(
                highlight_word_max=0,
            ),
            effect_args=SubTextHighlight.effects_args(
                fade=(50, 50),
                args_border=SubTextHighlight.args_border(use_borders_as_highlight=True)
            )
        )




if __name__ == '__main__':
    debug()
    t = Test_Class()
    #t(force_generate=False)
    #t.separate_on_period_and_highlighting()
    #t.blank_srt()
    #main1()
    #main2()
    #t.separate_on_period_and_highlighting()
    t.rounded_borders()
    #t.rounded_background_highlight()