# boards


<p align="center">
<a href="https://pypi.org/pypi/zillionare-ths-boards">
    <img src="https://img.shields.io/pypi/v/zillionare-ths-boards.svg"
        alt = "Release Status">
</a>

<a href="https://github.com/zillionare/boards/actions">
    <img src="https://github.com/zillionare/boards/actions/workflows/release.yml/badge.svg?branch=release" alt="CI Status">
</a>

<a href="https://zillionare.github.io/boards/">
    <img src="https://img.shields.io/website/https/zillionare.github.io/boards/index.html.svg?label=docs&down_message=unavailable&up_message=available" alt="Documentation Status">
</a>

</p>


同花顺概念板块与行业板块数据本地化项目


* Free software: MIT
* Documentation: <https://zillionare.github.io/boards/>


## Features

### 自动同步
通过boards serve启动服务器之后，每日凌晨5时自动同步板块数据，并将其按当天日期保存。

注意我们使用了akshare来从同花顺获取板块数据。akshare的相应接口并没有时间参数，也即，所有同步的板块数据都只能是最新的板块数据。但如果在当天5时之后，同花顺更新的板块数据，则更新的数据将不会反映在当天日期为索引的数据当中。

### 板块操作
提供了根据板块代码获取板块名字(get_name)、根据名字查代码(get_code)、根据名字进行板块名的模糊查找（fuzzy_match_board_name增）等功能。

此外，我们还提供了filter方法，允许查找同时属于于多个板块的个股。

### 获取新增加的概念板块
新概念板块往往是近期炒作的热点。您可以通过ConceptBoard.find_new_concept_boards来查询哪些板块是新增加的。

此功能对行业板块无效。

### 获取新加入概念板块的个股
对某个概念而言，新加入的个股可能是有资金将要运作的标志。通过ConceptBoard.new_members_in_board可以查询新加入某个概念板块的个股列表。

### 命令行接口
提供了命令行接口，以查询服务状态(status), 启动服务(serve), 停止服务(stop)及以下命令：

#### 查询新增概念板块
```
boards new_boards
```
#### 查询概念板块新增个股
```
boards new_members
```
上述两个命令需要至少有两天以上的同步数据。

#### 查询个股所属概念
```
boards show concepts 000001
```
#### 列出所有的概念板块
```
boards show concepts
```

#### 查询同时处于某几个概念板块中的个股
```
boards filter 医药 医疗器械 --without 跨境支付
```
## 其他
boards使用akshare来下载数据。下载速度较慢，且可能遇到服务器拒绝应答的情况。这种情况下，boards将会以退火算法，自动延迟下载速度重试5次，以保证最终能完全下载数据，且不被封IP。在此过程中，您可能看到诸如下面的信息输出，这是正常现象。
```text
Document is empty, retrying in 30 seconds...
Document is empty, retrying in 30 seconds...
Document is empty, retrying in 30 seconds...
Document is empty, retrying in 60 seconds...
Document is empty, retrying in 120 seconds...
```

## Credits

This package was created with the [ppw](https://zillionare.github.io/python-project-wizard) tool. For more information, please visit the [project page](https://zillionare.github.io/python-project-wizard/).
