
To use boards in a project

```
    import boards
```

## 命令行
安装完成后，您的系统将自动增加`boards`命令（仅对MacOs和Linux有效）。提供了以下命令：

### serve
boards通akshare从同花顺网站抓取数据，每次只能抓取当天的数据。为了自动保持与网站一致更新，我们提供了服务模式，需要您运行`boards serve`来开启。这将启动一个服务器，并自动于每日凌晨5时开始更新当天的板块数据。

这个命令接受一个可选参数，即服务器监听的端口。一般保持默认即可。

注意，如果系统重启，您需要重新运行一次上述命令。

在上述命令运行后，boards将自动执行一次数据同步任务。

### status
用以查看当前系统上是否运行了boards服务。

### new_members
查看近期哪些概念板块新增了个股。接受一个可选参数，即查看最近几天内新增的个股数据。默认为10天。

### new_boards
查看近期新增了哪些概念板块。接受一个可选参数，即查看最近几天内新增的概念板块。

## 编程接口
boards提供了[IndustryBoard][boards.board.IndustryBoard]和[ConceptBoard][boards.board.ConceptBoard]两个主要的类。
### 初始化
在使用行业板块数据或者概念板块数据之前，您需要初始化它：

```python
IndustryBoard.init()
ConceptBoard.init()
```
数据将存储在安装目录下的boards.zarr目录下。您也可以通过设置环境变量`boards_store_path`，使之指向数据存储路径。建议这个路径以boards.zarr结束。

如果您定制了这个路径，请确保在使用boards之前，已经创建了其父目录。

### 其它
一般而言，在调用其它api之前，您需要先生成对象实例：
```python
ib = IndustryBoard()
ib.get_code("种植业与林业")
```

请参考API文档。

!!! Notice
    同花顺返回的股票代码均为6位数字。当您在其它语境下使用（比如通过zillionare-omicron)来使用时，一般需要进行转换，以加上交易所识别码。
