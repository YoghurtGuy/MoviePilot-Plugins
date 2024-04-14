import time

from app.plugins import _PluginBase
from app.core.event import eventmanager
from app.schemas.types import EventType
from typing import Any, List, Dict, Tuple
from app.log import logger
from app.chain.subscribe import SubscribeChain


class SubscribeSearch(_PluginBase):
    # 插件名称
    plugin_name = "SubscribeSearch"
    # 插件描述
    plugin_desc = "添加订阅后自动搜索。"
    # 插件图标
    plugin_icon = "webhook.png"
    # 插件版本
    plugin_version = "1.1"
    # 插件作者
    plugin_author = "YoghurtGuy"
    # 作者主页
    author_url = "https://github.com/YoghurtGuy"
    # 插件配置项ID前缀
    plugin_config_prefix = "subscribe_search_"
    # 加载顺序
    plugin_order = 41
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _delay = None
    _enabled = False

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self._delay = config.get("delay")

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        request_options = ["POST", "GET"]
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 8
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'delay',
                                            'label': '延迟时间',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                ]
            }
        ], {
            "enabled": False,
            "delay": 90
        }

    def get_page(self) -> List[dict]:
        pass

    @eventmanager.register(EventType.SubscribeAdded)
    def subscribesearch(self, event):
        if not self._enabled:
            return

        event_info: dict = event.event_data
        # 入库数据
        subscribe_id = event_info.get("subscribe_id")
        logger.info(f"有新的订阅，订阅ID：{subscribe_id}")
        time.sleep(self._delay)
        logger.info(f"延迟{self._delay}秒结束，开始搜索")
        SubscribeChain().search(subscribe_id)

    def stop_service(self):
        """
        退出插件
        """
        pass
