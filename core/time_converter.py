from datetime import datetime
from core.plugin_manager import PluginManager, PluginBase
import pytz

@PluginManager.register
class TimeConverter(PluginBase):
    name = "时间戳转换"
    description = "时间戳 ↔ 时间字符串 互转，支持时区"

    def run(self, input_value: str, tz: str = "Asia/Shanghai") -> str:
        """
        input_value: str, 时间戳或时间字符串
        tz: str, 时区名称，默认 Asia/Shanghai
        """
        val = input_value.strip()
        if not val:
            return "输入为空"

        try:
            timezone = pytz.timezone(tz)
        except Exception:
            return f"未知时区: {tz}"

        # 尝试解析为时间戳
        try:
            ts = float(val)
            # 处理毫秒时间戳
            if ts > 1e12:
                ts /= 1000
            dt = datetime.fromtimestamp(ts, tz=timezone)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            # 尝试解析为时间字符串
            try:
                dt = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
                dt = timezone.localize(dt)
                return str(int(dt.timestamp()))
            except ValueError:
                return "格式错误：请输入时间戳或 YYYY-MM-DD HH:MM:SS"