from pathlib import Path

from helperFunctions.plugin import find_plugin_classes, import_plugins

TEST_PLUGINS_BASE_PATH = Path(__file__).parent.parent.parent / 'data/plugin_system'


def test_load_plugins():
    imported_modules = import_plugins(TEST_PLUGINS_BASE_PATH)
    assert len(imported_modules) == 2, 'wrong number of plugins imported'
    modules = {m.__name__.split('.')[-1]: m for m in imported_modules}
    assert 'plugin_one' in modules
    assert 'plugin_two' in modules
    assert len(list(find_plugin_classes(modules['plugin_one']))) == 0
    assert len(list(find_plugin_classes(modules['plugin_two']))) == 1
