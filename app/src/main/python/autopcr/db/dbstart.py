import glob, os
import time

from ..sdk.sdkclients import bsdkclient
from ..core.sdkclient import account, platform
from ..core.apiclient import apiclient
from ..model.sdkrequests import SourceIniGetMaintenanceStatusRequest
from ..constants import CACHE_DIR
from ..core.datamgr import datamgr
from ..util import aiorequests
from ..util.logger import instance as logger
import brotli

async def db_start():
    os.makedirs(os.path.join(CACHE_DIR, 'db'), exist_ok=True)
    dbs = glob.glob(os.path.join(CACHE_DIR, "db", "*.db"))
    if dbs:
        db = max(dbs)
        version = int(os.path.basename(db).split('.')[0])
    else:
        version = int(
                (await apiclient(bsdkclient(account("autopcr", "autopcr", platform.Android)))
                .request(SourceIniGetMaintenanceStatusRequest()))
                .manifest_ver
        )
    await datamgr.try_update_database(version)

async def do_update_database() -> int:
    logger.info("开始更新数据库...")
    start_time = time.time()

    # 1. 获取版本信息
    info = f'https://redive.estertion.win/last_version_cn.json'
    logger.info(f"正在获取版本信息: {info}")

    rsp = await aiorequests.get(info, stream=True, timeout=20)
    version = (await rsp.json())['TruthVersion']
    logger.info(f"远程数据库版本: {version}")

    # 2. 下载数据库
    url = f'https://redive.estertion.win/db/redive_cn.db.br'
    save_path = os.path.join(CACHE_DIR, "db", f"{version}.db")

    logger.info(f"数据库下载地址: {url}")
    logger.info(f"本地保存路径: {save_path}")

    try:
        logger.info("开始下载数据库文件...")
        download_start = time.time()
        rsp = await aiorequests.get(url, headers={'Accept-Encoding': 'br'}, stream=True, timeout=20)
        download_time = time.time() - download_start
        logger.info(f"下载完成，耗时: {download_time:.2f}秒，状态码: {rsp.status_code}")

        if 200 == rsp.status_code:
            logger.info("开始解压数据库...")
            decompress_start = time.time()
            content = await rsp.content
            decompressed = brotli.decompress(content)
            decompress_time = time.time() - decompress_start
            logger.info(f"解压完成，耗时: {decompress_time:.2f}秒，大小: {len(decompressed)} bytes")

            logger.info("开始保存数据库到本地...")
            with open(save_path, "wb") as f:
                f.write(decompressed)
            logger.info(f"数据库已保存到: {save_path}")
        else:
            raise ValueError(f"下载失败，状态码: {rsp.status_code}")
    except Exception as e:
        logger.error(f"数据库下载/解压失败: {e}")
        raise e

    total_time = time.time() - start_time
    logger.info(f"数据库更新完成，总耗时: {total_time:.2f}秒，版本: {version}")
    return int(version)
