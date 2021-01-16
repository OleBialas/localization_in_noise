import time
import sys
import pandas as pd
from pathlib import Path
from freefield import setup, camera
import slab
import numpy as np


EXPDIR = Path('D:\\Projects\\MRT_noise_elevation')
RCO_FOLDER = EXPDIR / Path('rcx')
_stim_dur = 1.0
# 4 speakers from elevation -37.5° to +37.5° with 25° steps between
setup.set_speaker_config("dome")
setup._dB_level = 75
# camera.init(type="freefield")
warning = slab.Sound.clicktrain(duration=0.4).data.flatten()
speakers = [20, 22, 24, 26]  # 29, 31, 33, 35, 37, 39, 41, 42, 44, 46]
speaker_list = setup.speakers_from_list(speakers)
speaker_repitition = 1

def run_block(speaker_seq, gain, noise):

    # MRT background noise
    response = pd.DataFrame(columns=["ele_target", "azi_target", "ele_response", "azi_response"])
    setup.set_variable(variable="noisebuflen", value=len(noise.data[:, 0]), proc="RX8s")
    setup.set_variable(variable="noise", value=noise.data[:, 0], proc="RX8s")
    while speaker_seq.n_remaining > 0:  # loop through sequence
        speaker_nr = speaker_seq.__next__()
        speaker, ch, proc, azi_t, ele_t, _, _ = setup.speaker_from_number(speaker_nr)
        stim = slab.Sound.pinknoise(duration=_stim_dur)
        noise.level = stim.level - 6
        stim.level = stim.level+gain
        setup.set_variable("playbuflen", stim.nsamples, "RX8s")
        setup.set_signal_and_speaker(signal=stim, speaker=speaker,
                                     apply_calibration=False)
        setup.trigger()
        setup.wait_to_finish_playing()
        while not setup.get_variable(variable="response", proc="RP2"):
            time.sleep(0.01)
        ele_r, azi_r = camera.get_headpose(convert=True, average=True, n_images=5)
        trial = {"azi_target": azi_t, "ele_target": ele_t,
                 "azi_response": azi_r, "ele_response": ele_r}
        response = response.append(trial, ignore_index=True)
        head_in_position = 0  # check if the head is in position for next trial
        while head_in_position == 0:
            while not setup.get_variable(variable="response", proc="RP2"):
                time.sleep(0.01)
            ele, azi = camera.get_headpose(
                n_images=1, convert=True, average=True)
            if ele is np.nan:
                ele = 0
            if azi is np.nan:
                azi = 0
            if np.abs(ele - 0 < 10) and np.abs(azi - 0 < 10):
                head_in_position = 1
            else:
                print(np.abs(ele-0), np.abs(azi-0))
                setup.set_variable("data", warning, "RX8s")
                setup.set_variable("chan", 23, "RX8s")
                setup.set_variable("playbuflen", len(warning), "RX8s")
                setup.trigger()
                setup.wait_to_finish_playing()
    return response


if __name__ == '__main__':
    # Show specific test stimulus to participant
    test = warning  # set any tone to present
    rx81_path = "D:/Projects/freefield_toolbox/rcx/play_buf.rcx"
    setup.initialize_devices(ZBus=True, cam=False, RX8_file=rx81_path)
    setup.set_variable("data", test, "RX8s")
    setup.set_variable("chan", 23, "RX8s")
    setup.set_variable("playbuflen", len(test), "RX8s")
    setup.trigger()
    setup.wait_to_finish_playing()
