import contextlib
import datetime
import io
import logging
import os
import re
from typing import Any, Dict, List, Set

import akshare as ak
import arrow
import numpy as np
import pandas as pd
import zarr
from numpy.core import defchararray
from retry import retry

logger = logging.getLogger(__name__)


def to_float_or_none(v: Any):
    try:
        return float(v)
    except Exception:
        return None


@retry(Exception, tries=5, backoff=2, delay=30, logger=logger)
def stock_board_industry_cons_ths(symbol):
    logger.info("fetching industry board members for %s", symbol)
    with contextlib.redirect_stderr(io.StringIO()):
        return ak.stock_board_industry_cons_ths(symbol)


@retry(Exception, tries=5, backoff=2, delay=30, logger=logger)
def stock_board_concept_cons_ths(symbol):
    logger.info("fetching concept board members for %s", symbol)
    with contextlib.redirect_stderr(io.StringIO()):
        return ak.stock_board_concept_cons_ths(symbol)


@retry(Exception, tries=5, backoff=2, delay=30, logger=logger)
def stock_board_industry_name_ths():
    logger.info("fetching industry board list")
    with contextlib.redirect_stderr(io.StringIO()):
        return ak.stock_board_industry_name_ths()


@retry(Exception, tries=5, backoff=2, delay=30, logger=logger)
def stock_board_concept_name_ths():
    logger.info("fetching concept board list")
    with contextlib.redirect_stderr(io.StringIO()):
        return ak.stock_board_concept_name_ths()


class Board:
    """行业板块及概念板块基类

    数据组织：
        /
        ├── concept
        │   ├── boards [date, name, code, members] #members is count of all members
        │   ├── members
        │   │   ├── 20220925 [('board', '<U6'), ('code', '<U6')]
        │   │   └── 20221001 [('board', '<U6'), ('code', '<U6')]
        │   └── valuation
        │       ├── 20220925 [code, turnover, vr, amount, circulation_stock, circulation_market_value]

    /{category}/members.attrs.get("latest")表明当前数据更新到哪一天。
    """

    _store = None
    _store_path = None
    category = "NA"
    syncing = False

    @classmethod
    def init(cls, store_path: str = None):
        """初始化存储。如果本地数据为空，还将启动数据同步。

        Args:
            store_path: 存储路径。如果未指定，则将读取`boards_store_path`环境变量。如果未指定环境变量，则使用安装目录下的boards.zarr目录。
        """
        if cls._store is not None:
            return

        cur_dir = os.path.dirname(__file__)
        cls._store_path = (
            store_path
            or os.environ.get("boards_store_path")
            or os.path.join(cur_dir, "boards.zarr")
        )

        logger.info("the store is %s", cls._store_path)
        try:
            cls._store = zarr.open(cls._store_path, mode="a")
            if f"/{cls.category}/boards" in cls._store:  # already contains data
                return
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.exception(e)
            os.rename(cls._store_path, f"{store_path}.corrupt")

        if cls.syncing:
            return

        try:
            cls.syncing = True
            # we need fetch boards list and its members for at least last day
            cls.fetch_board_list()
            cls.fetch_board_members()
        finally:
            cls.syncing = False

    @classmethod
    def close(cls):
        """关闭存储"""
        cls._store = None
        logger.info("store closed")

    @classmethod
    def fetch_board_list(cls):
        if cls.category == "industry":
            df = stock_board_industry_name_ths()
            df["members"] = 0
            dtype = [("name", "<U16"), ("code", "<U6"), ("members", "i4")]
            boards = (
                df[["name", "code", "members"]].to_records(index=False).astype(dtype)
            )
        else:
            df = stock_board_concept_name_ths()
            df = df.rename(
                columns={
                    "日期": "date",
                    "概念名称": "name",
                    "成分股数量": "members",
                    "网址": "url",
                    "代码": "code",
                }
            )

            df.members.fillna(0, inplace=True)
            dtype = [
                ("date", "datetime64[D]"),
                ("name", "<U16"),
                ("code", "<U6"),
                ("members", "i4"),
            ]
            boards = (
                df[["date", "name", "code", "members"]]
                .to_records(index=False)
                .astype(dtype)
            )

        key = f"{cls.category}/boards"
        cls._store[key] = boards

    @classmethod
    def fetch_board_members(cls):
        members = []
        counts = []
        valuation = []
        seen_valuation = set()
        boards = cls._store[f"{cls.category}/boards"]
        total_boars = len(boards)
        for i, name in enumerate(boards["name"]):
            code = cls.get_code(name)

            if i in range(1, total_boars // 10):
                logger.info(f"progress for fetching {cls.category} board: {i/10:.0%}")

            if cls.category == "industry":
                df = stock_board_industry_cons_ths(symbol=name)
                df["board"] = code
                counts.append(len(df))
                members.append(df)

                # 记录市值
                for (
                    _,
                    _,
                    code,
                    *_,
                    turnover,
                    vr,
                    amount,
                    circulation_stock,
                    circulation_market_value,
                    pe,
                    _,
                ) in df.itertuples():
                    if code in seen_valuation:
                        continue
                    else:
                        if "亿" in amount:
                            amount = float(amount.replace("亿", "")) * 1_0000_0000
                        if "亿" in circulation_stock:
                            circulation_stock = (
                                float(circulation_stock.replace("亿", "")) * 1_0000_0000
                            )
                        if "亿" in circulation_market_value:
                            circulation_market_value = (
                                float(circulation_market_value.replace("亿", ""))
                                * 1_0000_0000
                            )

                        turnover = to_float_or_none(turnover)
                        vr = to_float_or_none(vr)
                        amount = to_float_or_none(amount)
                        circulation_stock = to_float_or_none(circulation_stock)
                        circulation_market_value = to_float_or_none(
                            circulation_market_value
                        )
                        pe = to_float_or_none(pe)

                        valuation.append(
                            (
                                code,
                                turnover,
                                vr,
                                amount,
                                circulation_stock,
                                circulation_market_value,
                                pe,
                            )
                        )
            else:
                df = stock_board_concept_cons_ths(symbol=name)
                df["board"] = code
                members.append(df)
        # for industry board, ak won't return count of the board, had to do by ourself
        if cls.category == "industry":
            cls._store[f"{cls.category}/boards"]["members"] = counts

        # Notice: without calendar, we'll duplicate valuation/members in case of today is holiday
        today = arrow.now().format("YYYYMMDD")

        members_path = f"{cls.category}/members/{today}"
        members = (pd.concat(members))[["board", "代码", "名称"]].to_records(index=False)
        members_dtype = [("board", "<U6"), ("code", "<U6"), ("name", "<U8")]
        cls._store[members_path] = np.array(members, dtype=members_dtype)
        cls._store[f"{cls.category}/members"].attrs["latest"] = today

        valuation_path = f"{cls.category}/valuation/{today}"
        valuation_dtype = [
            ("code", "<U6"),
            ("turnover", "f4"),
            ("vr", "f4"),
            ("amount", "f8"),
            ("circulation_stock", "f8"),
            ("circulation_market_value", "f8"),
            ("pe", "f4"),
        ]
        cls._store[valuation_path] = np.array(valuation, dtype=valuation_dtype)

    @property
    def members_group(self):
        return self.__class__._store[f"{self.category}/members"]

    @property
    def valuation_group(self):
        return self.__class__._store[f"{self.category}/valuation"]

    @property
    def boards(self):
        return self.__class__._store[f"{self.category}/boards"]

    @boards.setter
    def boards(self, value):
        self.__class__._store[f"{self.category}/boards"] = value

    @property
    def store(self):
        return self.__class__._store

    def info(self) -> Dict[str, Any]:
        last_sync_date = self.store[f"{self.category}/members"].attrs.get("latest")
        history = list(self.members_group.keys())

        return {
            "last_sync_date": last_sync_date,
            "history": history,
        }

    def get_boards(self, code: str, date: datetime.date = None) -> List[str]:
        """给定股票，返回其所属的板块

        Args:
            code: 股票代码

        Returns:
            股票所属板块列表
        """
        latest = self.store[f"{self.category}/members"].attrs.get("latest")
        if latest is None:
            raise ValueError("data not ready, please call `sync` first!")
        date = arrow.get(date or latest).format("YYYYMMDD")

        members = self.members_group[date]
        idx = np.argwhere(members["code"] == code).flatten()
        if len(idx):
            return members[idx]["board"].tolist()
        else:
            return None

    def get_members(self, code: str, date: datetime.date = None) -> List[str]:
        """给定板块代码，返回该板块内所有的股票代码

        Args:
            code: 板块代码
            date: 指定日期。如果为None，则使用最后下载的数据

        Returns:
            属于该板块的所有股票代码的列表
        """
        latest = self.store[f"{self.category}/members"].attrs.get("latest")
        if latest is None:
            raise ValueError("data not ready, please call `sync` first!")
        date = arrow.get(date or latest).format("YYYYMMDD")

        members = self.members_group[date]
        idx = np.argwhere(members["board"] == code).flatten()
        if len(idx):
            return members[idx]["code"].tolist()
        else:
            return None

    def get_name(self, code: str) -> str:
        """translate code to board name"""
        idx = np.argwhere(self.boards["code"] == code).flatten()
        if len(idx):
            return self.boards[idx]["name"][0]
        else:
            return None

    def get_stock_alias(self, code: str) -> str:
        """给定股票代码，返回其名字"""
        latest = self.store[f"{self.category}/members"].attrs.get("latest")
        members = self.members_group[latest]
        idx = np.argwhere(members["code"] == code).flatten()
        if len(idx) > 0:
            return members[idx[0]]["name"].item()
        return code

    def fuzzy_match_board_name(self, name: str) -> List[str]:
        """给定板块名称，查找名字近似的板块，返回其代码

        Args:
            name: 用以搜索的板块名字

        Returns:
            板块代码列表
        """
        idx = np.flatnonzero(defchararray.find(self.boards["name"], name) != -1)
        if len(idx):
            return self.boards[idx]["code"].tolist()
        else:
            return None

    @classmethod
    def get_code(cls, name: str) -> str:
        """给定板块名字，转换成代码

        Args:
            name: 板块名字

        Returns:
            对应板块代码
        """
        boards = cls._store[f"{cls.category}/boards"]
        idx = np.argwhere(boards["name"] == name).flatten()
        if len(idx):
            return boards[idx][0]["code"]

        return None

    def get_bars(
        self, code_or_name: str, start: datetime.date, end: datetime.date = None
    ):
        """获取板块的日线指数数据

        Args:
            code_or_name: 板块代码或者名字。

        Returns:

        """
        if code_or_name.startswith("8"):
            name = self.get_name(code_or_name)

            if name is None:
                raise ValueError(f"invalid {code_or_name}")

        else:
            name = code_or_name

        start = f"{start.year}{start.month:02}{start.day:02}"
        if end is None:
            end = arrow.now().format("YYYYMMDD")
        else:
            end = f"{end.year}{end.month:02}{end.day:02}"

        return ak.stock_board_industry_index_ths(name, start, end)

    def search(self, in_boards: List[str], without: List[str] = []) -> List[str]:
        """查找同时存在于`in_boards`板块，但不在`without`板块的股票

        in_boards中的元素，既可以是代码、也可以是板块名称，还可以是模糊查询条件

        Args:
            in_boards: 查询条件，股票必须在这些板块中同时存在
            without: 板块列表，股票必须不出现在这些板块中。

        Returns:
            满足条件的股票代码列表
        """
        #
        normalized = []
        for board in in_boards:
            if not re.match(r"\d+", board):
                found = self.fuzzy_match_board_name(board) or []
                normalized.extend(found)
            else:
                normalized.append(board)

        results = None
        for board in normalized:
            if board not in self.boards["code"]:
                logger.warning("wrong board code %, skipped", board)
                continue

            if results is None:
                results = set(self.get_members(board))
            else:
                results = results.intersection(set(self.get_members(board)))

        final_result = []
        for stock in results:
            if set(self.get_boards(stock)).intersection(set(without)):
                continue

            final_result.append(stock)
        return final_result


class IndustryBoard(Board):
    category = "industry"


class ConceptBoard(Board):
    category = "concept"

    def find_new_concept_boards(self, days=10) -> pd.DataFrame:
        """查找`days`以内新出的概念板块

        Args:
            days:
        Returns:
            在`days`天以内出现的新概念板块代码列表,包含date, name, code, members诸列
        """
        today = arrow.now()
        start = today.shift(days=-days).date()

        # exclude date is None from self.boards
        idx = np.argwhere(~np.isnat(self.boards["date"])).flatten()
        if len(idx) == 0:
            return None

        boards = self.boards[idx]
        idx = np.argwhere(boards["date"] > start).flatten()
        if len(idx):
            return pd.DataFrame(
                boards[idx], columns=["date", "name", "code", "members"]
            )
        else:
            return None

    def new_members_in_board(self, days: int = 10) -> Dict[str, Set]:
        """查找在`days`天内新增加到某个概念板块的个股列表

        如果某个板块都是新加入，则所有成员都会被返回

        Args:
            days: 查找范围

        Raises:
            ValueError: 如果板块数据没有更新到最新，则抛出此异常。

        Returns:
            以板块为key，个股集合为键值的字典。
        """
        start = arrow.now().shift(days=-days)
        start_key = int(start.format("YYYYMMDD"))

        for x in self.members_group.keys():
            if int(x) >= start_key:
                start = x
                break
        else:
            logger.info("board data is old than %s, call sync before this op", start)
            raise ValueError("data is out of dayte")

        old = self.members_group[start]
        latest_day = self.members_group.attrs.get("latest")

        if (arrow.get(latest_day, "YYYYMMDD") - arrow.now()).days > 1:
            logger.info("concept board is out of date, latest is %s", latest_day)
            raise ValueError("concept board is out-of-date. Please do sync first")

        latest = self.members_group[latest_day]

        results = {}
        for board in set(latest["board"]):
            idx = np.argwhere([latest["board"] == board]).flatten()
            latest_stocks = set(latest[idx]["code"])

            idx_old = np.argwhere([old["board"] == board]).flatten()
            if len(idx_old) == 0:
                results[board] = latest_stocks
            else:
                old_stocks = set(old[idx_old]["code"])
                diff = latest_stocks - old_stocks
                if len(diff):
                    results[board] = diff

        return results


def sync_board():
    try:
        logger.info("start sync...")
        IndustryBoard.syncing = True
        IndustryBoard.init()
        IndustryBoard.fetch_board_list()
        IndustryBoard.fetch_board_members()

        ConceptBoard.syncing = True
        ConceptBoard.init()
        ConceptBoard.fetch_board_list()
        ConceptBoard.fetch_board_members()
    except Exception as e:
        logger.exception(e)
    finally:
        IndustryBoard.syncing = False
        ConceptBoard.syncing = False
