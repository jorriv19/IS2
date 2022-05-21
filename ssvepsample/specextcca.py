import numpy as np
import ezmsg.core as ez

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
    # In state we want to include the SAMPLING RATE of the incoming message from eegmessage.
    info: Optional[EEGInfoMessage] = None
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
    async def extract(self, message: EEGMessage) -> AsyncGenerator:


            yield (self.OUTPUT_DECODE, TransformOutput(output=))