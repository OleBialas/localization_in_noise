# STEP 1: import
import sys
from pathlib import Path
import os
from localization_in_noise import *
import slab
from freefield import setup, camera
import numpy as np

# STEP 2: Define variables
EXPDIR = Path("D:\Projects\MRT_noise_elevation")
speakers = [20, 22, 24, 26, 29, 31, 33, 35, 37, 39, 41, 42, 44, 46]
speaker_repetition = 4  # explain what this varibale is for
noise_dur = 0.5
n_images = 5
resolution = 0.7
n_reps_calbration = 3
n_reps_training = 3
n_reps_test = 3
n_reps_experiment = 2
rx81_path = str(EXPDIR / Path("rcx/play_buffer_from_channel.rcx"))
rp2_path = str(EXPDIR / Path("rcx/button_response.rcx"))
noise_path = EXPDIR / Path("MRT_noise/MRT_noise_experiment.wav")
conditions = [-10, 0, 5]

# STEP 3: enter subject name
subject = "Laura"
SUBDIR = EXPDIR / subject

# STEP 4: make subject folder(s) and generate stimulus sequences:
if Path(SUBDIR).is_dir():
    print("#### WARNING! Directory already exists ####")
else:
    os.makedirs(SUBDIR)
    block_seq = slab.Trialsequence(conditions=conditions, n_reps=n_reps_experiment, kind='non_repeating')
    block_seq.save_json(SUBDIR / Path("block_sequence.json"))

# STEP 5: calibrate camera
camera.init()
camera.set(n_images=n_images, resolution=resolution)
coords = camera.calibrate_camera(n_reps=n_reps_calbration)

# Look at data, then decide what to remove:
coords_clean = coords.copy()
coords_clean = coords_clean[np.logical_not(np.logical_and(coords.cam == 0, coords.ele_world > 0))]
coords_clean = coords_clean[np.logical_not(np.logical_and(coords.cam == 1, coords.ele_world < 0))]
camera.camera_to_world(coords_clean)

# STEP 6: audiovisual training
response = setup.localization_test_freefield(speakers=speakers, n_reps=n_reps_training, visual=True)
response.to_csv(SUBDIR/Path("%s_training.csv" % (subject)))


# STEP 7: localization test
response = setup.localization_test_freefield(speakers=speakers, n_reps=n_reps_test, visual=False)
response.to_csv(SUBDIR/Path("%s_test.csv" % (subject)))

# STEP 8: run Experiment
noise = slab.Sound.read(noise_path)
setup.initialize_devices(ZBus=True, cam=True, RX8_file=rx81_path, RP2_file=rp2_path)

block_seq = slab.Trialsequence()
block_seq.load_json(SUBDIR / Path("block_sequence.json"))
for gain in block_seq:
    input("### Press enter to start block %s ###" % block_seq.this_n)
    speaker_seq = slab.Trialsequence(conditions=speakers, n_reps=speaker_repetition, kind='non_repeating')
    response = run_block(speaker_seq, gain, noise)
    response.to_csv(SUBDIR/Path("%s_experiment_%s_block_seq.csv" % (subject, block_seq.this_n)))

"""
def run_experiment(subject, speaker_list, speaker_repitition):  # should not be needed as soon as run_block is working

    while block_seq.n_remaining > 0:
        gain = block_seq.__next__()
        speaker_seq = slab.Trialsequence(
            conditions=speaker_list, n_reps=speaker_repitition, kind='non_repeating')
        input("### Press enter to start block %s ###" % block_seq.this_n)

        setup.halt()
"""
