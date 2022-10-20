在项目中使用boards,您需要从boards中导入IndustryBoard或者ConceptBoard:

```
    from boards import IndustryBoard, ConceptBoard
    ib = IndustryBoard()
    ib.init()

    # do the same to ConceptBoard if it's needed
```

## 命令行
安装完成后，您的系统将自动增加`boards`命令（仅对MacOs和Linux有效）。提供了以下命令：

### 服务管理
```
# 启动服务
boards serve

# 停止服务
boards stop

# 查看服务状态，以及数据同步情况
boards status
```

#### 查询新增概念板块
```
boards new_boards
```
#### 查询概念板块新增个股
```
boards new_members
```

#### 查询最新新增的n个概念
```
boards latest_boards 3
```

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
boards filter --industry 计算机应用 --with-concpets 医药 医疗器械 --without 跨境支付
```

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
ib.init()

ib.get_code("种植业与林业")
```

请参考API文档。

!!! Notice
    同花顺返回的股票代码均为6位数字。当您在其它语境下使用（比如通过zillionare-omicron)来使用时，一般需要进行转换，以加上交易所识别码。
