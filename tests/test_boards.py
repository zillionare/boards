import datetime
import os
import shutil
import unittest
from unittest import mock

import arrow
import pandas as pd
from numpy.testing import assert_array_equal

from boards.board import ConceptBoard, IndustryBoard

concept_cons_ths = None

# fmt: off
industry_names = pd.DataFrame(
    [["种植业与林业", "881101"], ["种子生产", "884001"], ["其他种植业", "884003"]],
    columns=["name", "code"],
)

concept_names = pd.DataFrame([[datetime.date(2021, 5, 10), '农业种植', 43,
        'http://q.10jqka.com.cn/gn/detail/code/308016/', '308016'],
       [datetime.date(2022, 5, 25), '粮食概念', 28,
        'http://q.10jqka.com.cn/gn/detail/code/301279/', '308956'],
       [datetime.date(2021, 1, 22), '转基因', 11,
        'http://q.10jqka.com.cn/gn/detail/code/300435/', '300435']],
        columns=['日期', '概念名称', '成分股数量', '网址', '代码'])

industry_members = [
    pd.DataFrame(
        [[1, '002041', '登海种业', 20.25, 0.25, 0.05, 0.05, 1.02, 1.41, 1.83,
            '1.82亿', '8.80亿', '178.20亿', '79.45'],
        [2, '600265', 'ST景谷', 15.27, 0.07, 0.01, -0.13, 0.13, 0.81, 3.15,
            '0.03亿', '1.30亿', '19.82亿', '--'],
        [3, '000998', '隆平高科', 14.74, -0.61, -0.09, 0.34, 0.72, 0.93, 1.62,
            '1.38亿', '12.96亿', '191.03亿', '--'],
        [4, '601118', '海南橡胶', 4.36, -0.91, -0.04, 0.23, 0.19, 0.69, 1.82,
            '0.35亿', '42.79亿', '186.58亿', '--'],
        [5, '600598', '北大荒', 13.87, -2.12, -0.3, 0.0, 1.0, 1.32, 2.82,
            '2.48亿', '17.78亿', '246.56亿', '13.24']],
        columns=['序号', '代码', '名称', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额', '流通股', '流通市值', '市盈率']
    ),
    pd.DataFrame([
       [1, '002041', '登海种业', 20.25, 0.25, 0.05, 0.05, 1.02, 1.41, 1.83,
        '1.82亿', '8.80亿', '178.20亿', '79.45'],
       [2, '000998', '隆平高科', 14.74, -0.61, -0.09, 0.34, 0.72, 0.93, 1.62,
        '1.38亿', '12.96亿', '191.03亿', '--'],
       [3, '600354', '敦煌种业', 6.08, -2.72, -0.17, 0.0, 2.44, 1.1, 2.88,
        '0.79亿', '5.28亿', '32.09亿', '--'],
       [4, '600371', '万向德农', 12.6, -2.93, -0.38, 0.0, 1.7, 0.99, 2.7,
        '0.63亿', '2.93亿', '36.86亿', '37.99'],
       [5, '000713', '丰乐种业', 8.7, -3.12, -0.28, -0.12, 2.33, 1.12, 3.23,
        '1.26亿', '6.14亿', '53.42亿', '172.37']],
        columns=['序号', '代码', '名称', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额', '流通股', '流通市值', '市盈率']
    ),
    pd.DataFrame(
       [[1, '601118', '海南橡胶', 4.36, -0.91, -0.04, 0.23, 0.19, 0.69, 1.82,
        '0.35亿', '42.79亿', '186.58亿', '--'],
       [2, '002772', '众兴菌业', 7.37, -2.12, -0.16, 0.0, 1.41, 0.92, 3.45,
        '0.42亿', '4.03亿', '29.69亿', '--'],
       [4, '600108', '亚盛集团', 3.16, -2.47, -0.08, 0.32, 1.52, 1.12, 2.78,
        '0.94亿', '19.47亿', '61.52亿', '89.51'],
       [5, '600540', '新赛股份', 4.7, -2.49, -0.12, 0.0, 1.25, 0.82, 3.94,
        '0.34亿', '5.81亿', '27.32亿', '--'],
       [6, '600359', '新农开发', 8.95, -3.66, -0.34, -0.11, 5.73, 0.9, 4.63,
        '1.99亿', '3.82亿', '34.15亿', '30.19']],
        columns=['序号', '代码', '名称', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额', '流通股', '流通市值', '市盈率']
    ),
]

concept_members = [
    pd.DataFrame([
       [2, '002041', '登海种业', 20.25, 0.25, 0.05, 0.05, 1.02, 1.41, 1.83,
        '1.82亿', '8.80亿', '178.20亿', '79.45'],
       [7, '601118', '海南橡胶', 4.36, -0.91, -0.04, 0.23, 0.19, 0.69, 1.82,
        '0.35亿', '42.79亿', '186.58亿', '--'],
       [8, '002582', '好想你', 6.91, -0.58, -0.04, -0.29, 0.53, 0.72, 1.73,
        '0.13亿', '3.54亿', '24.44亿', '669.57'],
       [9, '600108', '亚盛集团', 3.16, -2.47, -0.08, 0.32, 1.52, 1.12, 2.78,
        '0.94亿', '19.47亿', '61.52亿', '89.51'],
       [10, '000998', '隆平高科', 14.74, -0.61, -0.09, 0.34, 0.72, 0.93,
        1.62, '1.38亿', '12.96亿', '191.03亿', '--']],
        columns=['序号', '代码', '名称', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额','流通股', '流通市值', '市盈率']),
    pd.DataFrame([
       [2, '002041', '登海种业', 20.25, 0.25, 0.05, 0.05, 1.02, 1.41, 1.83,
        '1.82亿', '8.80亿', '178.20亿', '79.45'],
       [5, '002505', '鹏都农牧', 2.83, -2.41, -0.07, 0.0, 0.58, 0.89, 2.76,
        '1.05亿', '63.74亿', '180.39亿', '231.70'],
       [6, '600108', '亚盛集团', 3.16, -2.47, -0.08, 0.32, 1.52, 1.12, 2.78,
        '0.94亿', '19.47亿', '61.52亿', '89.51'],
       [7, '600300', '维维股份', 3.31, -2.65, -0.09, -0.3, 1.32, 1.04, 2.94,
        '0.71亿', '16.17亿', '53.53亿', '53.87'],
       [8, '000998', '隆平高科', 14.74, -0.61, -0.09, 0.34, 0.72, 0.93, 1.62,
        '1.38亿', '12.96亿', '191.03亿', '--']],
       columns=['序号', '代码', '名称', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额','流通股', '流通市值', '市盈率']),
    pd.DataFrame([[1, '002041', '登海种业', 20.25, 0.25, 0.05, 0.05, 1.02, 1.41, 1.83,
        '1.82亿', '8.80亿', '178.20亿', '79.45'],
       [2, '000998', '隆平高科', 14.74, -0.61, -0.09, 0.34, 0.72, 0.93, 1.62,
        '1.38亿', '12.96亿', '191.03亿', '--'],
       [3, '300189', '神农科技', 4.29, -3.38, -0.15, -0.23, 1.96, 1.19, 3.15,
        '0.82亿', '9.63亿', '41.31亿', '--'],
       [4, '600354', '敦煌种业', 6.08, -2.72, -0.17, 0.0, 2.44, 1.1, 2.88,
        '0.79亿', '5.28亿', '32.09亿', '--'],
       [5, '002170', '芭田股份', 6.11, -3.17, -0.2, 0.0, 1.89, 0.9, 4.91,
        '0.82亿', '7.08亿', '43.27亿', '36.31']],
       columns=['序号', '代码', '名称', '现价', '涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅', '成交额', '流通股', '流通市值', '市盈率'])
]
# fmt: on


class BoardTest(unittest.TestCase):
    @mock.patch(
        "boards.board.stock_board_industry_name_ths", return_value=industry_names
    )
    @mock.patch(
        "boards.board.stock_board_industry_cons_ths", side_effect=industry_members
    )
    @mock.patch("boards.board.stock_board_concept_name_ths", return_value=concept_names)
    @mock.patch(
        "boards.board.stock_board_concept_cons_ths", side_effect=concept_members
    )
    def setUp(self, mock_0, mock_1, mock_2, mock_3) -> None:
        shutil.rmtree("/tmp/boards.zarr", ignore_errors=True)
        os.environ["boards_store_path"] = "/tmp/boards.zarr"

        with mock.patch("arrow.now", return_value=arrow.get("2022-05-26")):
            IndustryBoard.close()
            ConceptBoard.close()

            IndustryBoard.init()
            ConceptBoard.init()

            ib = IndustryBoard()
            cb = ConceptBoard()
            assert_array_equal(ib.boards["name"], ["种植业与林业", "种子生产", "其他种植业"])
            assert_array_equal(cb.boards["name"], ["农业种植", "粮食概念", "转基因"])

    def test_get_members(self):
        ib = IndustryBoard()
        actual = ib.get_members("881101")
        exp = ["002041", "600265", "000998", "601118", "600598"]
        self.assertListEqual(exp, actual)

        cb = ConceptBoard()
        actual = cb.get_members("308956")
        exp = ["002041", "002505", "600108", "600300", "000998"]
        self.assertListEqual(actual, exp)

    def test_get_boards(self):
        ib = IndustryBoard()
        actual = ib.get_boards("002041")
        exp = ["881101", "884001"]
        self.assertListEqual(actual, exp)

        cb = ConceptBoard()
        actual = cb.get_boards("002041")
        exp = ["308016", "308956", "300435"]
        self.assertListEqual(actual, exp)

    def test_fuzzy_match_board_name(self):
        ib = IndustryBoard()
        actual = ib.fuzzy_match_board_name("农")
        self.assertIsNone(actual)

        actual = ib.fuzzy_match_board_name("种")
        exp = ["881101", "884001", "884003"]
        self.assertListEqual(exp, actual)

        cb = ConceptBoard()
        actual = cb.fuzzy_match_board_name("基因")
        self.assertListEqual(["300435"], actual)

    def test_get_name(self):
        ib = IndustryBoard()
        cb = ConceptBoard()

        actual = ib.get_name("881101")
        self.assertEqual("种植业与林业", actual)

        actual = cb.get_name("308016")
        self.assertEqual("农业种植", actual)

    def test_get_code(self):
        ib = IndustryBoard()
        cb = ConceptBoard()

        actual = ib.get_code("种植业与林业")
        self.assertEqual("881101", actual)

        actual = cb.get_code("农业种植")
        self.assertEqual("308016", actual)

    def test_search(self):
        ib = IndustryBoard()
        cb = ConceptBoard()

        in_boards = ["881101", "其他"]
        stocks = ib.search(in_boards)
        self.assertSetEqual(set({"601118"}), set(stocks))

        in_boards = ["881101", "其他"]
        stocks = ib.search(in_boards, without=["881101"])
        self.assertSetEqual(set(), set(stocks))

        in_boards = ["308016", "基因"]
        stocks = cb.search(in_boards)
        self.assertSetEqual(set(["002041", "000998"]), set(stocks))

        stocks = cb.search(in_boards, without=["308956"])
        self.assertSetEqual(set(), set(stocks))

    def test_find_new_concept_boards(self):
        cb = ConceptBoard()

        with mock.patch("arrow.now", return_value=arrow.get("2022-05-27")):
            boards = cb.find_new_concept_boards()
            self.assertEqual(boards.loc[0, "code"], "308956")

    @mock.patch("boards.board.stock_board_concept_name_ths", return_value=concept_names)
    @mock.patch(
        "boards.board.stock_board_concept_cons_ths", side_effect=concept_members
    )
    def test_new_members_in_board(self, mock_0, mock_1):
        with mock.patch("arrow.now", return_value=arrow.get("2022-05-27")):
            ConceptBoard.fetch_board_list()
            ConceptBoard.fetch_board_members()

            cb = ConceptBoard()
            members = cb.members_group["20220526"]
            exp = set(members[-3:]["code"])
            cb.members_group["20220526"] = members[:-3]

            stocks = cb.new_members_in_board(1)
            self.assertDictEqual(stocks, {"300435": exp})
