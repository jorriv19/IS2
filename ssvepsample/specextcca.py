
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
        cca = CCA(n_components=2)
        #  correlations with the incoming data of the BCI (2 in this case). 
        
        # Time formed from the message 'n_time' data (1, 2, 3...) and dividing by 
        #  sampling frequency (500 Hz).[0.000, 0.002, 0.004,...]
        # Harmonics desired for checking correlations is from settings (3) and can be played
        #  with in the future to adjust ITR or accuracy.  
        time = np.arange(msg.n_time)/msg.fs
        harm_idx = (np.arange(self.SETTINGS.n_harm)+1)
        
        # Main code block. 
        # allcores will contain all the correlation coefficients produced by sklearn CCA funtion 
        #  for the (3) frequencies of interest. 
        # Y contains all of the sine and cosine functions and their harmonics for each FoI. Y_n,
        #  where n is the FoI, should be of size (# of time points, 2*harmonics). # of time points
        #  can be changed by the Window size chosen in our System settings. 
        # Since the fit_transform function does not output correlations, but outputs the the 
        #  covariance matrices maximizing the relationship between msg.data and Y, we use
        #  np.corrcoef to calculate and add the correlation values to allcores. 
        
        allcores = []
        for f in self.SETTINGS.freqoi:
            Y =[]
            for h in harm_idx:
                Y.append(np.sin(2*np.pi*f*h*time))
                Y.append(np.cos(2*np.pi*f*h*time))
            Y = np.array(Y).T
            A, B = cca.fit_transform(msg.data, Y ) 
            corrs = [np.corrcoef(A[:, i], B[:, i])[0, 1] for i in range(cca.n_components)]
            allcores.append(corrs[0])
        
        max_freq = self.SETTINGS.freqoi[np.argmax(allcores)]
        
        # Our frequency of interest should be f_cca
        yield (self.OUTPUT_DECODE, TransformOutput(max_freq))
