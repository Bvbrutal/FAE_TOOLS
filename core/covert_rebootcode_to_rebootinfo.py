import json
import re
from core.plugin_manager import PluginManager, PluginBase

@PluginManager.register
class ResetCodeConverter(PluginBase):
    """
    将 reset_info 文本转换为时间+重启原因
    """
    def __init__(self, json_path=None):
        # JSON 映射文件路径，可自定义
        self.json_path = json_path or r'resource/json/reset-info.json'
        self.rebootcode_maps = self.load_json()

    def load_json(self):
        rebootcode_maps = {}
        with open(self.json_path, 'r', encoding='utf-8') as file:
            rebootcode_map = json.load(file)
            for component in rebootcode_map:
                # key 转小写
                rebootcode_map_lower = {key.lower(): value for key, value in rebootcode_map[component].items()}
                rebootcode_maps.update(rebootcode_map_lower)
        return rebootcode_maps

    def run(self, ts_text: str, pri=False):
        """
        ts_text: str, 输入的 reset_info 文本
        pri: bool, 是否打印到控制台
        返回: list[[time_str, message], ...]
        """
        pattern_reset = re.compile(r"0x[0-9a-fA-F]+")
        pattern_time = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
        reset_info_list = pattern_reset.findall(ts_text)
        time_info = pattern_time.findall(ts_text)
        ret = []
        for index, reset_info in enumerate(reset_info_list):
            message = self.rebootcode_maps.get(reset_info.lower(), "未知重启代码")
            t_str = time_info[index] if index < len(time_info) else ""
            ret.append([t_str, message])
            if pri:
                print(t_str, message)
        return ret
