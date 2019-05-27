from django.apps import AppConfig

import core.plugins.first_game


plugins = {}


def prepare_plugins():
    global plugins
    plugin_list = []
    core.plugins.first_game.setPlugins(plugin_list)

    for plugin in plugin_list:
        plugin.info = plugin.register()
        from core.models import Achievement
        ach, flag = Achievement.objects.get_or_create(name=plugin.name, desc=plugin.desc)

        if flag:
            print("New achievement detected:")
            print(ach.name)
            print(ach.desc)

        plugin.pk = ach.pk
        plugins[plugin.pk] = plugin


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        import sys
        if 'runserver' not in sys.argv:
            return True
        prepare_plugins()
        print("CoreConfig done!")





