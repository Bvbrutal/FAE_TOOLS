from datetime import datetime
from core.plugin_manager import PluginManager, PluginBase

@PluginManager.register
class TimeConverter(PluginBase):
    name = "时间戳转换"
    description = "时间戳 ↔ 时间字符串 互转"

    def run(self, input_value: str) -> str:
        val = input_value.strip()
        if not val:
            return "输入为空"

        # 判断类型
        try:
            ts = float(val)
            if ts > 1e12:
                ts /= 1000
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                dt = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
                return str(int(dt.timestamp()))
            except ValueError:
                return "格式错误：请输入时间戳或 YYYY-MM-DD HH:MM:SS"
