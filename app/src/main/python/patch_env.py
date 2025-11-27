import os
import sys
import logging
import shutil
from java.lang import System
from java import jarray, jbyte
from com.chaquo.python import Python

def apply_android_patches():
    """
    应用 Android 环境特定的补丁
    """
    setup_android_logging()
    patch_paths()
    sync_assets_data()

def setup_android_logging():
    """
    重定向标准输出和日志到 Android Logcat
    """
    class LogcatWriter:
        def __init__(self, level):
            self.level = level
            from android.util import Log
            self.Log = Log
            self.tag = "AutoPCR_Py"

        def write(self, message):
            if message.strip():
                for line in message.rstrip().splitlines():
                    if self.level == 'I':
                        self.Log.i(self.tag, line)
                    elif self.level == 'E':
                        self.Log.e(self.tag, line)
        
        def flush(self):
            pass

    sys.stdout = LogcatWriter('I')
    sys.stderr = LogcatWriter('E')
    logging.basicConfig(level=logging.INFO)

def sync_assets_data():
    """
    将打包在 assets 中的数据文件同步到可写目录
    """
    try:
        import autopcr.constants as constants

        context = Python.getPlatform().getApplication()
        asset_manager = context.getAssets()
        
        data_asset_path = "data"
        target_data_dir = constants.DATA_DIR

        # 递归地遍历 assets 中的 data 目录
        for root, dirs, files in _walk_assets(asset_manager, data_asset_path):
            # 获取相对路径
            rel_path = root[len(data_asset_path):].lstrip('/')
            target_root = os.path.join(target_data_dir, rel_path)
            
            if not os.path.exists(target_root):
                os.makedirs(target_root)
            
            for file in files:
                asset_file_path = os.path.join(root, file)
                target_file_path = os.path.join(target_root, file)

                if not os.path.exists(target_file_path):
                    print(f"正在从 assets 复制: {asset_file_path} -> {target_file_path}")
                    in_stream = None
                    try:
                        in_stream = asset_manager.open(asset_file_path)
                        with open(target_file_path, "wb") as fout:
                            # 使用 Java 字节数组作为缓冲区
                            buf = jarray(jbyte)(4096)
                            while True:
                                n = in_stream.read(buf)
                                if n == -1:
                                    break
                                # 将 Java 字节数组转换为 Python bytes 写入
                                fout.write(buf[:n])
                    except Exception as e:
                        print(f"复制文件失败 {asset_file_path}: {e}")
                    finally:
                        if in_stream:
                            try:
                                in_stream.close()
                            except:
                                pass
        print("Assets data 同步完成。")
    except Exception as e:
        print(f"Assets data 同步失败: {e}")

def _walk_assets(asset_manager, path):
    """一个辅助函数，用于递归遍历 Android assets 目录。"""
    try:
        all_files = list(asset_manager.list(path))
    except:
        all_files = []
        
    dirs = [d for d in all_files if "." not in d]  # 简单的文件夹判断
    files = [f for f in all_files if "." in f]
    yield path, dirs, files
    for d in dirs:
        yield from _walk_assets(asset_manager, os.path.join(path, d))

def patch_paths():
    """
    修改 autopcr.constants 中的路径为 Android 可写目录
    """
    try:
        import autopcr.constants as constants
        
        context = Python.getPlatform().getApplication()
        files_dir = str(context.getFilesDir().getAbsolutePath())
        android_root = os.path.join(files_dir, "autopcr_data")
        
        print(f"重定向存储路径到: {android_root}")
        
        constants.ROOT_DIR = android_root
        constants.CACHE_DIR = os.path.join(android_root, 'cache/')
        constants.RESULT_DIR = os.path.join(android_root, 'result/')
        constants.DATA_DIR = os.path.join(android_root, 'data/')
        constants.CONFIG_PATH = os.path.join(constants.CACHE_DIR, 'http_server/')
        constants.OLD_CONFIG_PATH = os.path.join(android_root, 'old_config')
        constants.CLAN_BATTLE_FORBID_PATH = os.path.join(constants.CONFIG_PATH, 'clan_battle_forbidden.txt')
        constants.LOG_PATH = os.path.join(android_root, 'log/')
        
        for path in [constants.ROOT_DIR, constants.CACHE_DIR, constants.RESULT_DIR, 
                     constants.DATA_DIR, constants.CONFIG_PATH, constants.LOG_PATH]:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

        constants.refresh_headers()
        print("路径补丁已应用，并已刷新 headers。")

    except Exception as e:
        print(f"路径补丁应用出错: {e}")
