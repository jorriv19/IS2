import ezmsg.core as ez

from ezmsg.testing.debuglog import DebugLog
from ezmsg.eeg.openbci import (
    OpenBCISource, 
    OpenBCISourceSettings
)

from ezmsg.sigproc.window import(
    Window,
    WindowSettings
)

from ezmsg.sigproc.butterworthfilter import (
    ButterworthFilter,
    ButterworthFilterSettings
)

from dataclasses import(field)

from .injector import Injector, InjectorSettings 
from .specextcca import SpectralExtractor, SpectralExtractorSettings


class SSVEPSystemSettings(ez.Settings):
    openbci_settings: OpenBCISourceSettings


class SSVEPSystem( ez.System ):
    #Settings, state, and streams need to be type hinted
    SETTINGS: SSVEPSystemSettings

    SOURCE = OpenBCISource()
    FILTER = ButterworthFilter()
    INJECTOR = Injector()
    DEBUG = DebugLog()
    EXTRACTOR = SpectralExtractor()
    WINDOW = Window()


    def configure( self ) -> None:
        self.SOURCE.apply_settings( self.SETTINGS.openbci_settings )
        self.FILTER.apply_settings(
            ButterworthFilterSettings(
                order = 5,
                cuton = 5.0,
                cutoff = 40.0
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
            # ( self.SOURCE.OUTPUT_SIGNAL, self.DEBUG.INPUT ),
            ( self.SOURCE.OUTPUT_SIGNAL, self.WINDOW.INPUT_SIGNAL ),
            ( self.WINDOW.OUTPUT_SIGNAL, self.FILTER.INPUT_SIGNAL ),
            # ( self.WINDOW.OUTPUT_SIGNAL, self.INJECTOR.INPUT_SIGNAL ), 
            # ( self.INJECTOR.OUTPUT_DECODE, self.EXTRACTOR.INPUT_SIGNAL), 
            ( self.FILTER.OUTPUT_SIGNAL, self.EXTRACTOR.INPUT_SIGNAL ),
            ( self.EXTRACTOR.OUTPUT_DECODE,  self.DEBUG.INPUT )
        )

