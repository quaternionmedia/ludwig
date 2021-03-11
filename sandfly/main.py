from sandfly.specs import Mixer
from sandfly.boards import Qu24
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
    pm.register(Qu24(hook=pm.hook, port='Launchpad X:Launchpad X MIDI 2', client_name='Qu24'))
    return pm


if __name__ == '__main__':
    main()