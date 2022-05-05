from dataclasses import replace

from typing import( AsyncGenerator, Optional)

import ezmsg.core as ez
import numpy as np

from ezmsg.eeg.eegmessage import ( EEGMessage )

class InjectorSettings( ez.Settings ):
    freq: float #Frequency of signal to inject, in Hz

class InjectorState( ez.State ):
    cur_sample: int = 0


class Injector( ez.Unit ):
    """
    Injector injects sinusoidal frequency of your choice into all 
    channels of any EEGMessage stream. 
    """

    SETTINGS: InjectorSettings
    STATE: InjectorState

    INPUT_SIGNAL = ez.InputStream( EEGMessage )
    OUTPUT_SIGNAL = ez.OutputStream( EEGMessage )

    @ez.subscriber( INPUT_SIGNAL )
    @ez.publisher( OUTPUT_SIGNAL )
    async def inject( self, msg: EEGMessage) -> AsyncGenerator:
        
        t = (np.arange( msg.n_time) + self.STATE.cur_sample)/msg.fs
        tone = np.sin( 2 * np.pi * self.SETTINGS.freq * t)
        output = (msg.data.T + tone).T 

        self.STATE.cur_sample = self.STATE.cur_sample + msg.n_time

        # Nice to have: reset counter  of cur sample by checking if the below is close to zero. 
        # if (2*np.pi * self.SETTINGS.freq * t * self.STATE.cur_sample)/msg.fs
        yield ( self.OUTPUT_SIGNAL, replace( msg, data = output) )