# 第1周-04｜不用写 `to_list()`：用 `__getitem__` 接入“序列协议”

如果你只实现了 `__len__` 和 `__iter__`，`OrderBook` 已经挺像一个容器了。  
但在工程里，我们还经常需要“像列表一样”做两件事：
- 按下标取一条数据：`book[0]`
- 按切片取一段数据：`book[:10]`

这一篇专注一个知识点：实现 `__getitem__`，让 `OrderBook` 自然拥有“序列”的使用体验。

## 1. 要解决什么问题

典型场景：
- 排查问题时只想看前几条订单（切片）
- 做分页时想拿第 N 条（索引）

如果没有 `__getitem__`，调用方通常会写：

```python
orders = list(book)
first = orders[0]
head = orders[:10]
```

这会带来两个问题：
- 强制把迭代结果物化成 list（对大数据不友好）
- 调用方不得不“知道”你的容器怎么转换

理想调用方式是：

```python
first = book[0]
head = book[:10]
```

## 2. 概念部分：核心思路与关键机制

`obj[index]` 这种下标语法，会触发 `obj.__getitem__(index)`。  
当你实现了 `__getitem__`：
- 索引访问变成语言级能力
- 很多序列相关用法自然可用（例如切片）

在这周的实现里，`OrderBook` 内部本来就用 list 保存订单，因此最简单的做法是把索引/切片代理给内部 list。

类型提示上有个小坑：
- `book[0]` 返回 `Order`
- `book[:2]` 返回 `list[Order]`

为了让 `mypy --strict` 通过，我们用 `@overload` 精确描述这两种签名。

## 3. 实战部分：代码片段 + 运行命令 + 结果说明

实现如下：

```python
from typing import overload

class OrderBook:
    ...
    @overload
    def __getitem__(self, index: int) -> Order: ...

    @overload
    def __getitem__(self, index: slice) -> list[Order]: ...

    def __getitem__(self, index: int | slice) -> Order | list[Order]:
        return self._orders[index]
```

运行方式：

```bash
cd /Users/lianggao/MyWorkSpace/001-360/python-learning/fluent-python-tutorial
uv sync
uv run pytest -q
```

新增测试会验证：
- `book[0].order_id == "A-1"`
- `book[:2]` 得到前两条订单

## 4. 工程验收：lint/类型检查/测试结果

```bash
uv run ruff check .
uv run mypy .
uv run pytest -q
```

验收标准：
- `ruff` 全通过（风格与静态检查）
- `mypy` 严格模式通过（切片/索引类型准确）
- 测试通过（序列行为符合预期）

## 5. 思考题

1. `__getitem__` 返回 list 切片会不会导致大内存占用？你会如何设计一个“惰性切片”版本？
2. 如果内部结构从 list 换成 dict（按 order_id 索引），你还能提供 `book[0]` 吗？如果可以，语义是否还一致？
3. 除了 `__getitem__`，你还会为“序列体验”补哪些方法（例如 `__reversed__`、`index`、`count`）？哪些该做成方法，哪些该留给外部工具函数？
