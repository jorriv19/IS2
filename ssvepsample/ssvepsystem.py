import ezmsg.core as ez


from ezmsg.eeg.openbci import (
    OpenBCISource, 
    OpenBCISourceSettings
)

from ezmsg.sigproc.window import(
    Window,
    WindowSettings
)

from dataclasses import(field)

from .injector import Injector, InjectorSettings 
from .specextcca import SpectralExtractor, SpectralExtractorSettings

class DebugPrint( ez.Unit):
    INPUT = ez.InputStream( ez.Message)
    @ez.subscriber( INPUT )
    async def print(self, msg: ez.Message) -> None: 
        print( msg )


class SSVEPSystemSettings(ez.Settings):
    device: str


class SSVEPSystem( ez.System ):
    #Settings, state, and streams need to be type hinted
    SETTINGS: SSVEPSystemSettings

    SOURCE = OpenBCISource()
    INJECTOR = Injector()
    DEBUG = DebugPrint()
    EXTRACTOR = SpectralExtractor()
    WINDOW = Window()


    def configure( self ) -> None:
        self.SOURCE.apply_settings( 
            OpenBCISourceSettings(
                device = self.SETTINGS.device,
                blocksize = 50
                ) 
        )
        self.INJECTOR.apply_settings(
            InjectorSettings(
                freq = 13
            )
        )
        self.EXTRACTOR.apply_settings(
            SpectralExtractorSettings(
                freqoi = [7, 9, 13], 
                n_harm = 3 
            )
        )
        self.WINDOW.apply_settings(
            WindowSettings(
                window_dur=2, 
                window_shift=1
            )
        )

    
    def network( self ) -> ez.NetworkDefinition:
        return (
            #( self.SOURCE.OUTPUT_SIGNAL, self.DEBUG.INPUT ),
            ( self.SOURCE.OUTPUT_SIGNAL, self.WINDOW.INPUT_SIGNAL),
            ( self.WINDOW.OUTPUT_SIGNAL, self.INJECTOR.INPUT_SIGNAL ), 
            ( self.INJECTOR.OUTPUT_DECODE, self.EXTRACTOR.INPUT_SIGNAL), 
            ( self.EXTRACTOR.OUTPUT_DECODE,  self.DEBUG.INPUT )
        )

