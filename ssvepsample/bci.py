import ezmsg.core as ez

from ezmsg.eeg.openbci import (
    OpenBCISourceSettings, 
    GainState,
    PowerStatus,
    BiasSetting,
    OpenBCIChannelConfigSettings,
    OpenBCIChannelSetting,
)

from .ssvepsystem import(
    SSVEPSystem,
    SSVEPSystemSettings
)

from typing import (
    Dict,
    Optional
)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description = 'OpenBCI Joystick Recording Script'
    )

    ## OpenBCI Arguments
    parser.add_argument(
        '--device',
        type = str,
        help = 'Serial port to pull data from',
        default = 'simulator'
    )

    parser.add_argument(
        '--blocksize',
        type = int,
        help = 'Sample block size @ 500 Hz',
        default = 100
    )

    parser.add_argument(
        '--gain',
        type = int,
        help = 'Gain setting for all channels.  Valid settings {1, 2, 4, 6, 8, 12, 24}',
        default = 24
    )

    parser.add_argument(
        '--bias',
        type = str,
        help = 'Include channels in bias calculation. Default: 11111111',
        default = '11111111'
    )

    parser.add_argument(
        '--powerdown',
        type = str,
        help = 'Channels to disconnect/powerdown. Default: 00111111',
        default = '00111111'
    )

    parser.add_argument(
        '--impedance',
        action = 'store_true',
        help = "Enable continuous impedance monitoring",
        default = False
    )

    parser.add_argument(
        '--poll',
        type = float,
        help = 'Poll Rate (Hz). 0 for auto-config',
        default = 0.0
    )

    args = parser.parse_args()

    device: str = args.device
    blocksize: int = args.blocksize
    gain: int = args.gain
    bias: str = args.bias
    powerdown: str = args.powerdown
    impedance: bool = args.impedance

    gain_map: Dict[ int, GainState ] = {
        1:  GainState.GAIN_1,
        2:  GainState.GAIN_2,
        4:  GainState.GAIN_4,
        6:  GainState.GAIN_6,
        8:  GainState.GAIN_8,
        12: GainState.GAIN_12,
        24: GainState.GAIN_24
    }

    ch_setting = lambda ch_idx: (
        OpenBCIChannelSetting(
            gain = gain_map[ gain ],
            power = ( PowerStatus.POWER_OFF
                if powerdown[ch_idx] == '1'
                else PowerStatus.POWER_ON ),
            bias = ( BiasSetting.INCLUDE
                if bias[ch_idx] == '1'
                else BiasSetting.REMOVE
            )
        )
    )

    openbci_settings = OpenBCISourceSettings(
        device = args.device,
        blocksize = args.blocksize,
        impedance = args.impedance,
        ch_config = OpenBCIChannelConfigSettings(
            ch_setting = tuple( [
                ch_setting( i ) for i in range( 8 )
            ] )
        ),
        poll_rate = None if args.poll <= 0 else args.poll
    )

    settings = SSVEPSystemSettings(
        openbci_settings = openbci_settings
     )

    system = SSVEPSystem( settings )
    

    ez.run_system( system )
