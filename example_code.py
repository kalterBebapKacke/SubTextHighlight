import SubTextHighlight
import os
import pysubs2
import traceback

def debug():
    os.environ['debug'] = 'True'

def main1():
    input = './media/plain_video.webm'
    output = './media/edited_video.mp4'
    sub_args = SubTextHighlight.sub_args(input=input, output=output, input_video=input, subtitle_type='separate_on_period', fill_sub_times=False, alignment=2)
    highlight_args =  SubTextHighlight.highlight_args(primarycolor='00AAFF')
    effect_args = SubTextHighlight.effects_args((50, 50))
    sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
    sub_edit()

def main2():
    input = './media/plain_video.webm'
    output = './media/subtitles.ass'
    sub_args = SubTextHighlight.sub_args(input=input, output=output, subtitle_type='separate_on_period', fill_sub_times=False, alignment=2)
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

        self.input_video = './media/plain_video.webm'

        self.test_functions = [self.one_word_only_and_fade,
            self.separate_on_period_and_highlighting,
            self.join_and_word_max,
            self.appear
        ]

    def __call__(self):
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
        sub_args = SubTextHighlight.sub_args(input=self.input_video, output=None, subtitle_type='one_word_only', fill_sub_times=False)
        sub_file:pysubs2.SSAFile = SubTextHighlight.Subtitle_Edit(sub_args)()
        sub_file.save(self.blank_srt_path)

    def return_output_name(self, func):
        return f'./test_output/{func.__name__}.mp4', f'./test_output/{func.__name__}.ass'

    def exec_test(self, output_mp4:str, output_ass:str, sub_args:SubTextHighlight.sub_args, highlight_args:SubTextHighlight.highlight_args = None, effect_args:SubTextHighlight.effects_args = None):
        # executes the test on the given parameters
        sub_args.input = self.blank_srt_path
        sub_args.output = output_ass
        sub_edit = SubTextHighlight.Subtitle_Edit(sub_args, highlight_args, effect_args)
        sub_edit()
        SubTextHighlight.utils.add_subtitles_with_ffmpeg_with_given_ass(self.input_video, output_mp4, output_ass)

    def one_word_only_and_fade(self):
        output_mp4, output_ass = self.return_output_name(self.one_word_only_and_fade)
        sub_args = SubTextHighlight.sub_args(input='', output='', subtitle_type='one_word_only', fill_sub_times=False)
        effect_args = SubTextHighlight.effects_args(fade=(50, 50))
        self.exec_test(output_mp4, output_ass, sub_args, effect_args=effect_args)

    def separate_on_period_and_highlighting(self):
        output_mp4, output_ass = self.return_output_name(self.separate_on_period_and_highlighting)
        sub_args = SubTextHighlight.sub_args(input='', output='', subtitle_type='separate_on_period', fill_sub_times=False)
        highlighter_args = SubTextHighlight.highlight_args(highlight_word_max=0, primarycolor='00AAFF')
        self.exec_test(output_mp4, output_ass, sub_args, highlight_args=highlighter_args)

    def join_and_word_max(self):
        output_mp4, output_ass = self.return_output_name(self.join_and_word_max)
        sub_args = SubTextHighlight.sub_args(input='', output='', subtitle_type='join', fill_sub_times=False, word_max=20)
        self.exec_test(output_mp4, output_ass, sub_args)

    def appear(self):
        output_mp4, output_ass = self.return_output_name(self.appear)
        sub_args = SubTextHighlight.sub_args(input='', output='', subtitle_type='appear', fill_sub_times=False)
        self.exec_test(output_mp4, output_ass, sub_args)



if __name__ == '__main__':
    debug()
    t = Test_Class()
    t()
