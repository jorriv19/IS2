
import ezmsg.core as ez
import numpy as np 

from sklearn.cross_decomposition import CCA

from ezmsg.eeg.eegmessage import EEGMessage

from typing import (
    Optional,
    AsyncGenerator,
    List 
)
from dataclasses import(field)


class TransformOutput(ez.Message):
    # Stamped message: Message that gets a time stamp when created.
    output: float

class SpectralExtractorSettings(ez.Settings):
    #Set our frequencies of interest to be selected from, and harmonics we'd like to check. 
    freqoi: List[float] = field( default_factory = list([7, 9, 13]) )
    n_harm: int = 3

class SpectralextractorState(ez.State): 
    sampFreq: Optional[float] = None #
   

class SpectralExtractor(ez.Unit):
    """
    Performs a CCA on data collected from EEG channels.
    
    """
    SETTINGS: SpectralExtractorSettings
    STATE: SpectralextractorState

    INPUT_SIGNAL = ez.InputStream(EEGMessage)
    OUTPUT_DECODE = ez.OutputStream(TransformOutput)

    @ez.subscriber(INPUT_SIGNAL) 
    @ez.publisher(OUTPUT_DECODE) 
    async def extract(self, msg: EEGMessage) -> AsyncGenerator:
        cca = CCA(n_components=1)
        # TODO: make a check for which freq from freqoi is closest to the input data
        # Fit the CCA data on the training data set, which can be from
        # our injector unit if appropriate in the future. 
        Y =[]
        time = np.arange(msg.n_time)/msg.fs
        harm_idx = []
        harm_idx.extend(range(1,(SpectralExtractorSettings.n_harm)))
        
        for f in SpectralExtractorSettings.freqoi:
            for h in harm_idx:
                Y.append(np.sin(2*np.pi*f*h*time))
                Y.append(np.cos(2*np.pi*f*h*time))
        Y = np.array(Y).T
        cca.fit( msg.data, Y )
        A, B = cca.transform(msg.data, Y ) 
        
        print("this is the first output: " + str(A))
        print("this is the second output: "+ str(B))
        # Our frequency of interest should be f_cca
        yield (self.OUTPUT_DECODE, TransformOutput(A))