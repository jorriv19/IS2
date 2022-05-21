
import ezmsg.core as ez
import numpy as np 

from sklearn.cross_decomposition import CCA

from ezmsg.eeg.eegmessage import EEGMessage

from typing import (
    Optional,
    AsyncGenerator, 
)

class TransformOutput(EEGMessage):
    # Stamped message: Message that gets a time stamp when created.
    output: np.ndarray

class SpectralExtractorSettings(ez.Settings):
    pass

class SpectralextractorState(ez.State): 
    # TODO: check this, cant see big picture with settings and state of this unit. 
    # Calling the type of sampFreq and setting the intial value to None.
    sampFreq: Optional[float] = None #
   

class SpectralExtractor(ez.Unit):
    """
    Performs a CCA on data collected from EEG channels.
    
    """
    #SETTINGS: SpectralExtractorSettings
    STATE: SpectralextractorState

    INPUT_SIGNAL = ez.InputStream(EEGMessage)
    OUTPUT_DECODE = ez.OutputStream(TransformOutput)

    @ez.subscriber(INPUT_SIGNAL) 
    @ez.publisher(OUTPUT_DECODE) 
    async def extract(self, msg: EEGMessage) -> AsyncGenerator:
        cca = CCA(n_components=1)
        # Fit the CCA data on the training data set, which can be from
        # our injector unit if appropriate in the future. 
        cca.fit(msg.n_time, msg.data)
        t_cca, f_cca = cca.transform(msg.n_time, msg.data)
        print(f_cca)
        # Our frequency of interest should be f_cca
        yield (self.OUTPUT_DECODE, TransformOutput(f_cca))