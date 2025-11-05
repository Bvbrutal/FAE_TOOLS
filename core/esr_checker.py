from core.plugin_manager import PluginManager, PluginBase

@PluginManager.register
class ESRChecker(PluginBase):
    name = "ESR查看"
    description = "解析 ESR 值（十六进制）"

    def run(self, input_value: str) -> str:
        val = input_value.strip()
        if not val:
            return "输入为空"
        try:
            esr = int(val, 16)
            return f"ESR=0x{esr:X}\n二进制: {esr:032b}"
        except ValueError:
            return "请输入有效的十六进制 ESR 值（例如 0x96000010）"
