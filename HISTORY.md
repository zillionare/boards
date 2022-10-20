# History

## 0.2 (2022-10-14)
* 增加latest_boards命令，用以查找最近`n`天新增的概念板块。
* 重构filter命令，允许按行业和概念同时查找。
## 0.1.4 (2022-10-09)
* Board.search变更为filter
* 增加filter, show命令。
## 0.1.3 (2022-10-09)
* [#1](https://github.com/zillionare/boards/issues/1) fixed: tqdm caused sync failure
* better cli output messages
* use environment variable boards_run_at to customize scheduled sync time.
## 0.1.1 （2022-10-01）
* fixed: daily sync not started
* Features:
  * add `info` API to get last sync date and which days are synced to the store
  * add `get_stock_alias` API to translate stock code to its alias
## 0.1.0 (2022-09-23)

* First release on PyPI.
