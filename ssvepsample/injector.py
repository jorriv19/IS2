from typing import( 
    AsyncGenerator,
    Optional
)

import ezmsg.core as ez

from ezmsg.eeg.eegmessage import (
    EEGMessage,
    #EEGDataMessage,
    #EEGInfoMessage
)

class InjectorSettings( ez.Settings ):
    freq: float #Frequency of signal to inject, in Hz

class InjectorState( ez.State ):
    info: Optional[ EEGMessage ]  = None


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
        self.STATE.info = msg
        #if isinstance( msg, EEGInfoMessage ):
        #    ...
        #elif isinstance( msg, EEGDataMessage ): 
        #    ...
    
        yield ( self.OUTPUT_SIGNAL, msg )