from datetime import datetime

class TimeConverter:
    """核心时间转换逻辑，与界面无关，可单元测试"""

    @staticmethod
    def timestamp_to_time(ts_val: str) -> str:
        """时间戳转时间字符串"""
        ts_val = ts_val.strip()
        try:
            ts = float(ts_val)
            if ts > 1e12:  # 毫秒判断
                ts /= 1000
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            raise ValueError("无效的时间戳")

    @staticmethod
    def time_to_timestamp(time_str: str) -> str:
        """时间字符串转时间戳"""
        time_str = time_str.strip()
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            return str(int(dt.timestamp()))
        except Exception:
            raise ValueError("无效的时间格式，应为 YYYY-MM-DD HH:MM:SS")
