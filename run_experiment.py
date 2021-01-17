import os
from experiment import run_block, DIR
import slab
from freefield import main

# devices and circuits for the experiment:
proc_list = [["RX81", "RX8", DIR/"rcx"/"play_buffer_from_channel.rcx"],
             ["RX82", "RX8", DIR/"rcx"/"play_buffer_from_channel.rcx"],
             ["RP2", "RP2",  DIR/"rcx"/"button_response.rcx"]]

subject = "subject0"  # make folder for the subject if it does not exist yet
if not (DIR/"data"/subject).is_dir():
    os.makedirs(DIR/"data"/subject)

# calibrate the camera
main.initialize_setup(setup="arc", default_mode="cam_calibration", zbus=True, connection="GB", camera_type="webcam")
calibration_targets = main.get_speaker_list([9, 16, 23])
main.calibrate_camera_no_visual(calibration_targets, n_reps=1, n_images=5)

# experiment configuration:
target_speakers = main.get_speaker_list([20, 22, 24, 26, 29, 31, 33, 35, 37, 39, 41, 42, 44, 46])
noise_gain = [-10, 0, 5]  # loudness of the MRI noise relative to the stimulus
n_repeat_speakers = 4  # repetitions of each speaker per block
n_repeat_conditions = 2  # repetitions of each noise level


# generate a sequences to determine the order of conditions and targets in the experiment:
block_seq = slab.Trialsequence(conditions=noise_gain, n_reps=n_repeat_conditions, kind='non_repeating')
block_seq.save_json(DIR/"data"/subject/"block_sequence.json")
for i in range(block_seq.n_trials):
    speaker_seq = slab.Trialsequence(conditions=[target_speakers.loc[i] for i in target_speakers.index],
                                     n_reps=n_repeat_speakers, kind='non_repeating')
    speaker_seq.save_pickle(DIR/"data"/subject/f"speaker_sequence{i}.json")

# run a basic localization test
loctest_seq = main.localization_test_freefield(targets=target_speakers, n_reps=n_repeat_speakers, visual=False)
loctest_seq.save_pickle(DIR/"data"/subject/"loctest_seq.json")

# run all the blocks:
main.PROCESSORS.initialize(proc_list=proc_list, zbus=True, connection="GB")
noise = slab.Sound(DIR/"stimuli"/"mri_noise.wav")
block_seq = slab.Trialsequence(DIR/"data"/subject/"block_sequence.json")
for noise_gain in block_seq:
    input("### Press enter to start block %s ###" % block_seq.this_n)
    speaker_seq = slab.Trialsequence(DIR/"data"/subject/f"speaker_sequence{block_seq.this_n}.json")
    speaker_seq = run_block(speaker_seq, noise_gain, noise)
    speaker_seq.save_pickle(DIR/"data"/subject/f"speaker_sequence{block_seq.this_n}.json")
