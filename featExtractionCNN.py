import glob
import os
import numpy as np
import librosa
import cfg


n_mfcc = 14
window_size = 44100
hop_length=512
# Unique index for every class
classes = {"string": 0, "keyboard": 1, "vocal": 2, "guitar": 3, "brass": 4}
train_dir = "nsynth-train"
valid_dir = "nsynth-valid"
save_dir = "."
datafile = "dataCNN.npz"

def windows(data):
    start = 0
    while start + window_size < len(data):
        yield data[start:start + window_size]
        start += (window_size // 2)

def process_raw_data(direc):
    target_shape = (n_mfcc, window_size // hop_length + 1, 1)
    features = np.empty((0, n_mfcc, window_size // hop_length + 1, 1))
    labels = []
    for fn in glob.glob(os.path.join(direc, "*.wav")):
        sound, _ = librosa.load(fn)
        for subsound in windows(sound):
            mfccs = librosa.feature.mfcc(
                        y=subsound, n_mfcc=n_mfcc, hop_length=hop_length)
            mfccs = mfccs.reshape(target_shape)
            features = np.concatenate((features, mfccs[None]), axis=0)
            labels.append(classes[fn.split('/')[-1].split('_')[0]])
    return features, one_hot_encode(np.array(labels, dtype=np.int))

def one_hot_encode(labels):
    n_labels = len(labels)
    n_unique_labels = len(np.unique(labels))
    one_hot_encode = np.zeros((n_labels, n_unique_labels))
    one_hot_encode[np.arange(n_labels), labels] = 1
    return one_hot_encode

def compile_all_data():
    tr_features, tr_labels = process_raw_data(train_dir)
    ts_features, ts_labels = process_raw_data(valid_dir)

    np.savez(os.path.join(save_dir, datafile), 
             tr_features=tr_features, tr_labels=tr_labels,
             ts_features=ts_features, ts_labels=ts_labels)

if __name__ == "__main__":
    compile_all_data()