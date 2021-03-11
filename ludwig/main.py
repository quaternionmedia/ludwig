from ludwig.specs import Mixer
from ludwig.boards import Qu24
from pluggy import PluginManager

def main():
    pm = get_plugin_manager()
    try:
        while True:
            exec(input('> '))
    except Exception as e:
        print(e)
    # finally:
    #     pm.hook.close()

def get_plugin_manager():
    pm = PluginManager('mixer')
    pm.add_hookspecs(Mixer)
    # pm.register(Qu24(hook=pm.hook, port='QU-24 MIDI 1', client_name='Qu24'))
    pm.register(Qu24(hook=pm.hook, port='Launchpad X:Launchpad X MIDI 2', client_name='Qu24'))
    # pm.register(Qu24(hook=pm.hook, port='FreeWheeling:FreeWheeling IN 1', input_name='FreeWheeling:FreeWheeling OUT 1', client_name='Qu24'))
    return pm


if __name__ == '__main__':
    main()