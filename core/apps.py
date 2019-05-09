from django.apps import AppConfig

import core.plugins.first_game

plugins = {}


def prepare_plugins():
    global plugins
    plugin_list = []
    core.plugins.first_game.setPlugins(plugin_list)

    for plugin in plugin_list:
        plugin.info = plugin.register()
        plugins[plugin.pk] = plugin


class CoreConfig(AppConfig):
    name = 'core'
    prepare_plugins()





