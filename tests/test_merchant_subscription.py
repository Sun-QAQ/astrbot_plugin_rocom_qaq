import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def _install_astrbot_stubs():
    class _Logger:
        def info(self, *args, **kwargs):
            pass

        def warning(self, *args, **kwargs):
            pass

        def error(self, *args, **kwargs):
            pass

        def debug(self, *args, **kwargs):
            pass

    class _Filter:
        def command(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    class _MessageChain:
        def at_all(self):
            return self

        def message(self, *args, **kwargs):
            return self

        def file_image(self, *args, **kwargs):
            return self

    class _Star:
        def __init__(self, context=None):
            self.context = context

    class _StarTools:
        @staticmethod
        def get_data_dir():
            return Path(".")

    class _AstrBotConfig(dict):
        pass

    def _register(*args, **kwargs):
        def decorator(cls):
            return cls

        return decorator

    astrbot_module = types.ModuleType("astrbot")
    api_module = types.ModuleType("astrbot.api")
    event_module = types.ModuleType("astrbot.api.event")
    star_module = types.ModuleType("astrbot.api.star")
    core_module = types.ModuleType("astrbot.core")
    message_module = types.ModuleType("astrbot.core.message")
    components_module = types.ModuleType("astrbot.core.message.components")

    api_module.logger = _Logger()
    event_module.filter = _Filter()
    event_module.AstrMessageEvent = object
    event_module.MessageChain = _MessageChain
    star_module.Context = object
    star_module.Star = _Star
    star_module.register = _register
    star_module.StarTools = _StarTools
    core_module.AstrBotConfig = _AstrBotConfig
    components_module.Plain = object
    components_module.Image = object

    sys.modules.setdefault("astrbot", astrbot_module)
    sys.modules.setdefault("astrbot.api", api_module)
    sys.modules.setdefault("astrbot.api.event", event_module)
    sys.modules.setdefault("astrbot.api.star", star_module)
    sys.modules.setdefault("astrbot.core", core_module)
    sys.modules.setdefault("astrbot.core.message", message_module)
    sys.modules.setdefault("astrbot.core.message.components", components_module)


_install_astrbot_stubs()
PACKAGE_PARENT = Path(__file__).resolve().parents[2]
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from astrbot_plugin_rocom_qaq.main import RocomPlugin


class MerchantSubscriptionJitterTest(unittest.TestCase):
    def _plugin(self, jitter_seconds=30):
        plugin = object.__new__(RocomPlugin)
        plugin._merchant_jitter_seconds = jitter_seconds
        return plugin

    def test_merchant_check_jitter_uses_non_negative_range(self):
        plugin = self._plugin(30)

        with patch("astrbot_plugin_rocom_qaq.main.random.uniform", return_value=12.5) as uniform:
            jitter = plugin._merchant_check_jitter_seconds()

        self.assertEqual(jitter, 12.5)
        self.assertGreaterEqual(jitter, 0)
        uniform.assert_called_once_with(0, 30)

    def test_merchant_check_jitter_allows_zero_when_disabled(self):
        plugin = self._plugin(0)

        with patch("astrbot_plugin_rocom_qaq.main.random.uniform", return_value=0) as uniform:
            jitter = plugin._merchant_check_jitter_seconds()

        self.assertEqual(jitter, 0)
        self.assertGreaterEqual(jitter, 0)
        uniform.assert_called_once_with(0, 0)


if __name__ == "__main__":
    unittest.main()
