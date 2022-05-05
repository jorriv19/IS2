import ezmsg.core as ez


from ezmsg.eeg.openbci import (
    OpenBCISource, 
    OpenBCISourceSettings
)

from .injector import Injector #.injector will only work in a python module

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


    def configure( self ) -> None:
        self.SOURCE.apply_settings( 
            OpenBCISourceSettings(
                device = self.SETTINGS.device,
                blocksize = 50
                ) 
        )

    def network( self ) -> ez.NetworkDefinition:
        return (
            #( self.SOURCE.OUTPUT_SIGNAL, self.DEBUG.INPUT ),
            ( self.SOURCE.OUTPUT_SIGNAL, self.INJECTOR.INPUT_SIGNAL ), 
            ( self.INJECTOR.OUTPUT_SIGNAL, self.DEBUG.INPUT )
        )

