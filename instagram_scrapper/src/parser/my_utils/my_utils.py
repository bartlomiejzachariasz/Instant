import h5py
import numpy as np
from tensorflow.keras.callbacks import Callback

INPUT_PATH = "../preprocessed/mydataset.hdf5"
NUMBER_OF_CHUNKS = 30
PHOTOS_IN_CHUNK = 1000
NUMBER_OF_PHOTOS = NUMBER_OF_CHUNKS*PHOTOS_IN_CHUNK

class LossHistory(Callback):
    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))

def create_generator(start=0,stop=0.7,batch_size=300,verbose = False,output = "labels"):
    
    assert start<=stop and start >= 0 and stop <= 1 and batch_size<PHOTOS_IN_CHUNK
    
    batches_in_chunk = int(PHOTOS_IN_CHUNK/batch_size)
    start = int(start*(NUMBER_OF_PHOTOS))
    end = int(stop*(NUMBER_OF_PHOTOS))
    counter = start
    while True:
        container = int(counter/PHOTOS_IN_CHUNK)
        _from = counter%PHOTOS_IN_CHUNK
        _to = _from + batch_size
        excess = max(0,_from+batch_size-PHOTOS_IN_CHUNK)
        with h5py.File(INPUT_PATH,"r") as f:
            X = f["data"][str(container)][_from:_to]/255
            Y = f[output][str(container)][_from:_to]
        if _to < end:
            with h5py.File(INPUT_PATH,"r") as f:
                X = np.concatenate([X,f["data"][str((container+1)%NUMBER_OF_CHUNKS)][0:excess]/255],axis=0)
                Y = np.concatenate([Y,f[output][str((container+1)%NUMBER_OF_CHUNKS)][0:excess]],axis=0)
        counter += batch_size
        if counter >= end:
            counter = start
        if verbose == True:
            print("Generated X of shape {} and Y of shape: {} from container [\"{}\"][{}:{}] and container [\"{}\"][0:{}]"
                  .format(X.shape,Y.shape,container,_from,min(PHOTOS_IN_CHUNK,_to),container+1,excess))    
        yield X,Y
        
        del X,Y