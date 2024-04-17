import json
import os

from app.plugins import _PluginBase
from app.core.event import eventmanager
from app.schemas.types import EventType
from app.utils.http import RequestUtils
from typing import Any, List, Dict, Tuple
from app.log import logger
from app.schemas import TransferInfo, RefreshMediaItem
from app.core.context import MediaInfo


class AlistCopy(_PluginBase):
    # 插件名称
    plugin_name = "AListCopy"
    # 插件描述
    plugin_desc = "转移成功后向AList发送复制请求。"
    # 插件图标
    plugin_icon = "webhook.png"
    # 插件版本
    plugin_version = "1.1"
    # 插件作者
    plugin_author = "YoghurtGuy"
    # 作者主页
    author_url = "https://github.com/YoghurtGuy"
    # 插件配置项ID前缀
    plugin_config_prefix = "aList_copy_"
    # 加载顺序
    plugin_order = 88
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _alist_url = None
    _username = None
    _password = None
    _mp_dir = None
    _from_dir = None
    _to_dir = None
    _enabled = False

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self._alist_url = config.get("alist_url")
            self._mp_dir = config.get('mp_dir')
            self._from_dir = config.get('from_dir')
            self._to_dir = config.get('to_dir')
            self._username = config.get('username')
            self._password = config.get('password')

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
                                            'model': 'alist_url',
                                            'label': 'AList地址'
                                        }
                                    }
                                ]
                            },
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
                                            'model': 'username',
                                            'label': '用户名'
                                        }
                                    }
                                ]
                            },
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
                                            'model': 'password',
                                            'label': '密码'
                                        }
                                    }
                                ]
                            },
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
                                            'model': 'mp_dir',
                                            'label': 'Rclone挂载目录'
                                        }
                                    }
                                ]
                            },
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
                                            'model': 'from_dir',
                                            'label': 'AList原目录'
                                        }
                                    }
                                ]
                            },
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
                                            'model': 'to_dir',
                                            'label': 'AList目的目录'
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
            "alist_url": "",
            "username": "",
            "password": "",
            "mp_dir": "",
            "from_dir": "",
            "to_dir": ""
        }

    def get_page(self) -> List[dict]:
        pass

    # @eventmanager.register(EventType)
    @eventmanager.register(EventType.TransferComplete)
    def send(self, event):
        """
        向Alist发送请求
        """
        if not self._enabled or not self._webhook_url:
            return

        event_info: dict = event.event_data
        # 入库数据
        transferinfo: TransferInfo = event_info.get("transferinfo")
        mediainfo: MediaInfo = event_info.get("mediainfo")
        logger.info(f"转移成功：{mediainfo.title}，目的地址：{transferinfo.target_path}")
        user_info = json.dumps({
            "username": self._username,
            "password": self._password
        })

        ret = RequestUtils(content_type="application/json").post_res(self._alist_url+"/api/auth/login", json=user_info)
        token = None
        if ret:
            token = ret.json()['data']['token']
            logger.info("获取token成功：%s" % token)
        elif ret is not None:
            logger.error(f"发送失败，状态码：{ret.status_code}，返回信息：{ret.text} {ret.reason}")
            return
        dirname, name = os.path.split(transferinfo.target_path)
        send_data = json.dumps({
            "src_dir": dirname.replace(self._mp_dir, self._from_dir),
            "dst_dir": dirname.replace(self._mp_dir, self._to_dir),
            "names": [
                name
            ]
        })
        logger.info(f"发送数据：{send_data}")
        ret = RequestUtils(content_type="application/json").post_res(self._alist_url+"/api/fs/copy", json=send_data)

        if ret:
            logger.info("复制任务提交成功")
        elif ret is not None:
            logger.error(f"发送失败，状态码：{ret.status_code}，返回信息：{ret.text} {ret.reason}")
        else:
            logger.error("发送失败，未获取到返回信息")

    def stop_service(self):
        """
        退出插件
        """
        pass
