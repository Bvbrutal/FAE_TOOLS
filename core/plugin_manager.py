import importlib

class PluginBase:
    """所有插件的基础类（约定接口）"""
    name = "BasePlugin"       # 插件名称
    description = "Base plugin interface"

    def run(self, input_value: str) -> str:
        raise NotImplementedError


class PluginManager:
    """插件注册与加载中心"""
    _plugins = {}

    @classmethod
    def register(cls, plugin_class):
        """注册插件类"""
        cls._plugins[plugin_class.name] = plugin_class
        return plugin_class  # 支持装饰器用法

    @classmethod
    def list_plugins(cls):
        """列出所有已注册插件"""
        return list(cls._plugins.keys())

    @classmethod
    def get_plugin(cls, name):
        """获取插件实例"""
        plugin_class = cls._plugins.get(name)
        if not plugin_class:
            raise ValueError(f"插件 '{name}' 未注册")
        return plugin_class()
