import ezmsg.core as ez

from ezmsg.eeg.openbci import OpenBCISourceSettings

from .ssvepsystem import(
    SSVEPSystem,
    SSVEPSystemSettings
)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description = 'OpenBCI Joystick Recording Script'
    )

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
        default = 50
    )

    parser.add_argument(
        '--poll',
        type = float,
        help = 'Poll Rate (Hz). 0 for auto-config',
        default = 0.0
    )

    args = parser.parse_args()

    settings = OpenBCISourceSettings(
        device = args.device,
        blocksize = args.blocksize,
        poll_rate = None if args.poll <= 0 else args.poll
    )

    settings = SSVEPSystemSettings(
        device = args.device
     )

    system = SSVEPSystem( settings )
    

    ez.run_system( system )
