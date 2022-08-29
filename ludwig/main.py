from .mixer import Mixer
from .boards import Qu24
from pluggy import PluginManager
from argparse import ArgumentTypeError


def channel(n: int):
    n = int(n)
    if n > 109:
        raise ArgumentTypeError('invalid QU channel number')
    else:
        return n


def main():
    pm = get_plugin_manager()
    try:
        from argparse import ArgumentParser

        parser = ArgumentParser(description='remote sound board operation')
        parser.add_argument(
            'channels',
            metavar='N',
            type=channel,
            nargs='+',
            help='an integer for the accumulator',
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '-m', '--mute', dest='mute', action='store_true', help='mute the channel(s)'
        )
        group.add_argument(
            '-u',
            '--unmute',
            dest='unmute',
            action='store_true',
            help='unmute the channel(s)',
        )
        args = parser.parse_args()

        args = parser.parse_args()
        # print(args)
        for c in args.channels:
            if args.mute:
                print('muting', c)
                pm.hook.mute(channel=c)
            elif args.unmute:
                print('unmuting', c)
                pm.hook.unmute(channel=c)
    except Exception as e:
        print(e)
    finally:
        pm.hook.close()


def get_plugin_manager():
    pm = PluginManager('mixer')
    pm.add_hookspecs(Mixer)
    pm.register(Qu24(hook=pm.hook, port='QU-24 MIDI 1', client_name='Qu24'))
    # pm.register(Qu24(hook=pm.hook, port='Launchpad X:Launchpad X MIDI 2', client_name='Qu24'))
    # pm.register(Qu24(hook=pm.hook, port='FreeWheeling:FreeWheeling IN 1', input_name='FreeWheeling:FreeWheeling OUT 1', client_name='Qu24'))
    return pm


if __name__ == '__main__':
    main()
