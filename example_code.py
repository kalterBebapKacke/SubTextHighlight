import SubTextHighlight
import os

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

if __name__ == '__main__':
    debug()
    main2()
    #main1()