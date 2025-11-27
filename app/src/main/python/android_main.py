# Android 启动入口脚本
# 此脚本将由 Android Service 调用以启动服务器

import os
import sys
import logging

# 配置 Python 路径
if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AutoPCR_Android")

def start_server():
    """
    启动 AutoPCR 服务器
    """
    logger.info("正在初始化 AutoPCR Android 服务...")
    
    try:
        # 导入并应用环境补丁
        import patch_env
        patch_env.apply_android_patches()
        
        logger.info("环境补丁已应用，正在启动服务器...")
        
        # 导入原有的服务器模块
        import asyncio
        from autopcr.http_server.httpserver import HttpServer
        from autopcr.constants import SERVER_PORT
        from autopcr.db.dbstart import db_start
        from autopcr.module.crons import queue_crons
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 关键修复：计算并传递前端资源的绝对路径
        import autopcr.http_server
        http_server_path = os.path.dirname(os.path.abspath(autopcr.http_server.__file__))
        static_dir = os.path.join(http_server_path, 'ClientApp')
        
        # 初始化服务器
        server = HttpServer(host='127.0.0.1', port=SERVER_PORT, static_dir=static_dir)
        
        # 初始化数据库和定时任务
        queue_crons()
        loop.create_task(db_start())
        
        logger.info(f"服务器正在启动，监听 127.0.0.1:{SERVER_PORT}")
        
        # 启动服务器
        server.run_forever(loop)
        
    except Exception as e:
        logger.error(f"服务器启动失败: {e}", exc_info=True)
        raise e

if __name__ == "__main__":
    start_server()
