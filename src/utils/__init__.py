# __init__.py

# 导入包中的模块
from .hot_key_press_util import HotKeyPressListener
from . import map_util
from . import config_util

# 定义包级别的变量
# ocr = "This is a package variable"

# 设置 __all__ 变量
__all__ = ['map_util', HotKeyPressListener, 'config_util']
