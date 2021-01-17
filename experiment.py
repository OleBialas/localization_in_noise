import pandas as pd
from pathlib import Path
from freefield import main
import slab
DIR = Path(__file__).parent.resolve()  # location of the main folder


def run_block(speaker_seq, gain, noise, stimulus_duration, fixation_point):

    # MRT background noise
    response = pd.DataFrame(columns=["ele_target", "azi_target", "ele_response", "azi_response"])
    main.write(tag="noisebuflen", value=len(noise.data[:, 0]), procs="RX8s")
    main.write(tag="noise", value=noise.data[:, 0], procs="RX8s")
    for speaker in speaker_seq:
        stim = slab.Sound.pinknoise(duration=stimulus_duration)
        noise.level = stim.level - 6
        stim.level = stim.level+gain
        main.write("playbuflen", stim.nsamples, "RX8s")
        main.set_signal_and_speaker(signal=stim, speaker=speaker, calibrate=False)
        main.play_and_wait_for_button()
        azi, ele = main.get_headpose(convert=True, average=True, n=5)
        speaker_seq.add_response([azi, ele])
        head_in_position = False  # check if the head is in position for next trial
        while not head_in_position:
            head_in_position = main.check_pose(fixation_point)
        else:
            main.play_warning_sound(duration=.5, speaker=23)
    return speaker_seq
