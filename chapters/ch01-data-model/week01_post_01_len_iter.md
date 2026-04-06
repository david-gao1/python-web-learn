# 第1周-01｜让业务对象像容器一样工作：`__len__` + `__iter__`

本周我们用一个很小的业务对象 `OrderBook` 来练 Python 数据模型。很多代码“能跑”但“不像 Python”，症状通常是：到处都是 `get_size()`、`items()`、`to_list()` 这类方法，调用者需要记一堆自定义 API。

这一篇只解决两件事：让 `OrderBook` 支持 `len(book)`，以及能被 `for` 循环直接迭代。

## 1. 要解决什么问题

你正在写一个订单集合类：
- 业务上：要统计订单数，遍历订单做计算。
- 工程上：你希望调用层代码自然、少记忆、少样板。

理想的调用方式是：

```python
book = OrderBook(...)
if len(book) == 0:
    ...
for order in book:
    ...
```

而不是：

```python
book = OrderBook(...)
if book.size() == 0:
    ...
for order in book.get_orders():
    ...
```

## 2. 概念部分：核心思路与关键机制

把 `OrderBook` 视作“容器类型”。容器在 Python 里不是靠继承某个基类来识别，而是靠协议（protocol）：只要你实现了约定的特殊方法，语言就会用对应的语法糖和内建函数来驱动你的对象。

你需要知道两条映射关系：
- `len(obj)` 会触发 `obj.__len__()`
- `for x in obj` 会先尝试 `iter(obj)`，它会触发 `obj.__iter__()`

你可以把这理解为：`__len__` 和 `__iter__` 是“把类接入 Python 容器世界的两根线”。

## 3. 实战部分：代码片段 + 运行命令 + 结果说明

本周项目里，`OrderBook` 内部用一个 list 存订单（这不是重点，重点是对外行为）：

```python
class OrderBook:
    def __init__(self, orders: list[Order] | None = None) -> None:
        self._orders: list[Order] = list(orders or [])

    def __len__(self) -> int:
        return len(self._orders)

    def __iter__(self) -> Iterator[Order]:
        return iter(self._orders)
```

运行方式：

```bash
cd /Users/lianggao/MyWorkSpace/001-360/python-learning/fluent-python-tutorial
uv sync
uv run python chapters/ch01-data-model/main.py
```

你会看到输出里包含 `OrderBook(size=..., ...)`，并且可以在 `main.py` 里用 `len(book)`、`for order in book` 直接操作 `OrderBook`。

## 4. 工程验收：lint/类型检查/测试结果

本项目使用 `uv` 管理依赖，并把 ruff/mypy/pytest 作为门禁：

```bash
uv run ruff check .
uv run mypy .
uv run pytest -q
```

验收标准：
- `len(book)` 返回值准确
- `list(book)` 的顺序与内部订单追加顺序一致
- `mypy` 严格模式通过（避免容器元素类型漂移）

## 5. 思考题

1. `__iter__` 直接 `return iter(self._orders)` 的好处是什么？什么时候你会自己写一个生成器来迭代？
2. 你会让 `OrderBook` 变成“迭代器”吗？如果把 `__iter__` 写成 `return self` 会带来什么问题？
3. 如果 `OrderBook` 的内部结构从 list 换成 dict（按 order_id 索引），`__len__` 和 `__iter__` 应该如何调整，才能保持对外语义稳定？
