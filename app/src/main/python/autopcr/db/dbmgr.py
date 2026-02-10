import os, json, time
from typing import List
from ..constants import CACHE_DIR, DATA_DIR
from .assetmgr import assetmgr
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from ..util.logger import instance as logger

class dbmgr:
    def __init__(self):
        self.ver = None
        self._dbpath = None
        self._engine = None

    async def update_db(self, mgr: assetmgr):
        ver = mgr.ver
        logger.info(f"dbmgr.update_db called, target version: {ver}")
        start_time = time.time()

        self._dbpath = os.path.join(CACHE_DIR, 'db', f'{ver}.db')
        logger.info(f"数据库路径: {self._dbpath}")

        if not os.path.exists(self._dbpath):
            logger.info("数据库文件不存在，从 assetmgr 获取...")
            data = await mgr.db()
            logger.info(f"获取到数据，大小: {len(data)} bytes")
            with open(self._dbpath, 'wb') as f:
                f.write(data)
            logger.info(f'数据库文件已保存: {self._dbpath}')
        else:
            logger.info(f"数据库文件已存在: {self._dbpath}")

        logger.info("创建 SQLAlchemy 引擎...")
        self._engine = create_engine(f'sqlite:///{self._dbpath}')
        self.ver = ver
        logger.info(f"引擎创建完成，版本设置为: {ver}")

        logger.info("开始执行 unhash...")
        unhash_start = time.time()
        self.unhash()
        unhash_time = time.time() - unhash_start
        logger.info(f"unhash 完成，耗时: {unhash_time:.2f}秒")

        # 检查关键表是否存在
        logger.info("检查数据库表完整性...")
        self._check_tables()

        total_time = time.time() - start_time
        logger.info(f'dbmgr.update_db 完成，总耗时: {total_time:.2f}秒')

    def _check_tables(self):
        """检查关键数据库表是否存在"""
        critical_tables = [
            'quest_data',
            'unit_data',
            'item_data',
            'clan_battle_period',
            'talent',
            'unlock_unit_condition'
        ]

        with self.session() as session:
            missing_tables = []
            for table in critical_tables:
                result = session.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                ).fetchone()
                if not result:
                    missing_tables.append(table)
                    logger.warning(f"关键表缺失: {table}")
                else:
                    # 统计表中的行数
                    count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
                    logger.info(f"表 {table}: {count} 行")

            if missing_tables:
                logger.error(f"数据库缺少 {len(missing_tables)} 个关键表: {', '.join(missing_tables)}")
            else:
                logger.info("所有关键表检查通过")

    def session(self) -> Session:
        return Session(self._engine)

    @staticmethod
    def get_create_table(session: Session, table_name: str):
        result = session.execute(text(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")).fetchone()
        return result[0] if result else None

    @staticmethod
    def get_table_columns(session: Session, table_name: str):
        result = session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
        return [row[1] for row in result]

    @staticmethod
    def exec_transaction(session: Session, commands: List[str]) -> bool:
        try:
            for cmd in commands:
                session.execute(text(cmd))
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            session.rollback()
            return False

    def unhash(self):
        rainbow_json = os.path.join(DATA_DIR, 'rainbow.json')
        if not os.path.exists(rainbow_json):
            logger.error("Rainbow table not found, unhashing skipped.")
        else:
            json_object = json.load(open(rainbow_json, 'r'))
            logger.info("Start Unhashing DB.")

            with self.session() as session:
                for hashed_table_name, cols_dict in json_object.items():
                    intact_table_name = cols_dict.get("--table_name")
                    create_table_statement = self.get_create_table(session, hashed_table_name)
                    create_dec_table_statement = self.get_create_table(session, intact_table_name)

                    if create_table_statement is None:
                        if not create_dec_table_statement:
                            logger.warning(f"CreateTableStatement for '{intact_table_name}' not found.")
                        continue

                    hashed_cols = []
                    intact_cols = []

                    for hashed_col_name, intact_col_name in cols_dict.items():
                        if hashed_col_name != "--table_name":
                            hashed_cols.append(hashed_col_name)
                            intact_cols.append(intact_col_name)

                        create_table_statement = create_table_statement.replace(
                            hashed_table_name if hashed_col_name == "--table_name" else hashed_col_name,
                            intact_table_name if hashed_col_name == "--table_name" else intact_col_name
                        )

                    for hashed_col_name in self.get_table_columns(session, hashed_table_name):
                        if hashed_col_name not in hashed_cols:
                            hashed_cols.append(hashed_col_name)
                            intact_cols.append(hashed_col_name)

                    insert_statement = f"INSERT INTO {intact_table_name} (`{'`, `'.join(intact_cols)}`) SELECT `{'`, `'.join(hashed_cols)}` FROM {hashed_table_name}"
                    drop_table_statement = f"DROP TABLE {hashed_table_name}"

                    transaction_cmd = [create_table_statement, insert_statement, drop_table_statement]

                    if not self.exec_transaction(session, transaction_cmd):
                        logger.error(f"Failed when executing a transaction for '{intact_table_name}' ({hashed_table_name}). Transaction: {transaction_cmd}")
                        continue

            logger.info("Unhashing complete.")


instance = dbmgr()
