import os

def debug():
    os.environ['debug'] = 'True'

def new_example_code():
    from SubTextHighlight import SubtitleConfig, StyleConfig, preset_youtube
    video = './tests/input/plain_video.mp4'  # set the input to a video, which will generate the subtitles for me
    ass = './tests/input/blank.srt'
    output = './media/output_video.mp4'  # set the output to a .mp4, so that the subtitles will be burned in

    conf = SubtitleConfig(
        ass, output, video,
        subtitle_type='separate_on_period',
        fill_sub_times=False,
        subtitle_style=StyleConfig(alignment=2),
        highlight_word_max=0,
        highlight_as_borders=True,
        fade=(50, 50),
    )
    conf.render()
    conf.save()

    # Or use the youtube preset, that gives a similar result
    preset_youtube(ass, output, video)


if __name__ == '__main__':
    #debug()
    #t = Test_Class()
    #t(force_generate=False)
    #t.separate_on_period_and_highlighting()
    #t.blank_srt()
    #main1()
    #main2()
    #t.separate_on_period_and_highlighting()
    #t.rounded_borders()
    #t.rounded_background_highlight()
    #t.rounded_background_appear()
    #t.appear()
    new_example_code()