import numpy as np
import ezmsg as ez
from ezbci.stampedmessage import StampedMessage

# This will bring in all of the info being output by the BCI. See eegmessage.py for more information on each import.
from eegmessage import EEGMessage, EEGInfoMessage, EEGDataMessage

# Typing allows for autocompletion that is relevant. "Type hinting" to tell editor what
# that variable will be and get better code completion. Python idgnores all typing when running files,
# its just for the programmer.
from typing import (#Doc: https://www.pythonsheets.com/notes/python-typing.html
    Optional,
    AsyncGenerator, #Doc: https://www.python.org/dev/peps/pep-0525/#asynchronous-generators
)
class TransformOutput(StampedMessage):
    # Stamped message: Message that gets a time stamp when created.
    output: np.ndarray

class SpectralExtractorSettings(ez.Settings):
    pass
    # Settings are things that do not change throughout the use of the unit
    # TODO Prio 1: If this Unit will calculate the dominant freq for spectral output, the preset frequencies should be here. 
    # Then we see out of those presets which freq bin has the max value. 

#change to spectral extractorState
class SpectralExtractorState(ez.State): # State changes during operation, things to keep track of during co-routine calls.
    # In state we want to include the SAMPLING RATE of the incoming message from eegmessage.
    info: Optional[EEGInfoMessage] = None
    # Calling the type of sampFreq and setting the intial value to None.
    sampFreq: Optional[float] = None #
   

class SpectralExtractor(ez.Unit):
    """
    Performs an FFT using numpy.fft.fft on data collected from EEG channels.
    TODO Prio 2: Have fft only work on relevant channels i.e. occipital channel
    """
    #SETTINGS: fftSettings
    STATE: SpectralExtractorState

    INPUT_SIGNAL = ez.InputStream(EEGMessage)
    OUTPUT_DECODE = ez.OutputStream(TransformOutput)

    @ez.subscriber(INPUT_SIGNAL) # 1:1 relation between co-routines and inputs
    @ez.publisher(OUTPUT_DECODE) # Multiple outputs can be published (i.e. spectral content and frequency output for the graphs module)

    async def transform(self, message: EEGMessage) -> AsyncGenerator:
        # Checks to see the class of EEGMessage that is coming in.
        if isinstance(message, EEGInfoMessage):
            self.STATE.info = message

        # We will always receive an info message before data message, first line is a good check.
        elif isinstance(message, EEGDataMessage):
            if self.STATE.info is None: return
            else:
                # Taking the fft of the channel data over the time data, indicated by selecting axis=0. Expecting a complex output array. 
                # N is the window length which will by in cycles/second. 
                freqTrans = np.fft.fft( message.data, axis=0) 
                N = np.size(message.data, axis = 0) 
                # freqBins is the sample frequencies given by fft.fftfreq. The number of unique sample frequencies, uniqN, should be freqBins/2+1 (1 for the zero freq) per
                # Nyquist Frequency Theorem. fft.fft.freq accounts for the zero frequency, so it is not necessary for us to add 1 to the result. 
                freqBins = np.fft.fftfreq( N, 1/self.STATE.info.fs)
                # We'll create a uniq variable for this in case we need to obtain less than the Nyquist frequencies. 
                uniqBins = freqBins[:int(len(freqBins)/2)]
                uniqFreq: np.ndarray = freqTrans[:int(len(freqTrans)/2)]
                uBshape = uniqBins.shape
                uFshape = uniqFreq.shape
                # maxpow_idx gives us the "unravelled index" of the max power spectrum frequency. We need the frequency bin that the unique power
                #  (found in uniqFreq? consider renaming?) belongs to. 
                maxpow_idx = np.unravel_index(uniqFreq.argmax(),uFshape)
                #TODO Prio 0 I fixed argmax giving me the "ravelled?/linear" index, but do not know if the column information from the maxpow_idx is important. 
                selection = uniqBins[maxpow_idx[0]]
            # syntax for how to output on a particular topic. 
            yield (self.OUTPUT_DECODE, TransformOutput(output=selection))