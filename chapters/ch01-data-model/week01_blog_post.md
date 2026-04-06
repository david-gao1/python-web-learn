# 第1周｜把业务对象写得像 Python 内置类型：从 `OrderBook` 学数据模型

很多人写 Python 类时，会遇到一个尴尬问题：类能跑，但“不像 Python”。  
你会发现自己经常在业务代码里写这样的东西：
- `book.size()` 而不是 `len(book)`
- `book.has("A-1")` 而不是 `"A-1" in book`
- 打印对象时只看到内存地址，调试效率很低

这周的目标就是解决这个问题：把一个业务对象接入 Python 数据模型，让它像列表、字典一样自然可用。

## 1. 要解决什么问题

场景很真实：你有一个订单集合 `OrderBook`，需要支持以下操作：
- 统计订单数量
- 遍历所有订单
- 判断某个订单号是否存在
- 快速查看对象摘要用于调试

如果不使用数据模型，你会写出一堆自定义方法。  
这种代码短期可用，长期会让团队成员在“风格不统一”和“接口记不住”上浪费时间。

## 2. 核心思路是什么

把 `OrderBook` 当成“容器类型”来设计。  
容器在 Python 里有约定俗成的协议，协议对应的就是特殊方法：
- `__len__` 对应 `len(obj)`
- `__iter__` 对应 `for x in obj`
- `__contains__` 对应 `x in obj`
- `__repr__` 对应调试输出

可以把它理解成“给你的类接上语言插座”。  
一旦插好，Python 的内建函数和语法糖就能直接使用你的对象。

## 3. 关键机制怎么工作

我们在本周项目里实现了一个最小 `OrderBook`：

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator


@dataclass(frozen=True)
class Order:
    order_id: str
    symbol: str
    quantity: int
    price: Decimal

    @property
    def amount(self) -> Decimal:
        return self.price * self.quantity


class OrderBook:
    def __init__(self, orders: list[Order] | None = None) -> None:
        self._orders = list(orders or [])

    def __len__(self) -> int:
        return len(self._orders)

    def __iter__(self) -> Iterator[Order]:
        return iter(self._orders)

    def __contains__(self, order_id: object) -> bool:
        if not isinstance(order_id, str):
            return False
        return any(order.order_id == order_id for order in self._orders)

    def __repr__(self) -> str:
        return f"OrderBook(size={len(self)}, total_amount={self.total_amount()})"
```

这里有两个工程细节值得注意：
- `__contains__` 参数写成 `object`，是为了兼容任意 `in` 输入，再在内部做类型判断。
- `__repr__` 不是“漂亮输出”，而是“调试输出”。重点是信息密度和可定位性。

## 4. 怎么实际使用

先用 `uv` 管理虚拟环境和依赖，再跑示例和测试：

```bash
cd /Users/lianggao/MyWorkSpace/001-360/python-learning/fluent-python-tutorial
uv sync
uv run python chapters/ch01-data-model/main.py
uv run ruff check .
uv run mypy .
uv run pytest -q
```

运行后你会得到三个直接收益：
- 调用层代码更自然：`len(book)`、`"A-1" in book`
- 调试更快：`print(book)` 就能看到关键摘要
- 质量更稳：lint、类型检查、测试形成最小门禁

这比“只把功能写出来”更接近工程实践，因为它同时考虑了可读性、可维护性和协作成本。

## 5. 还有哪些思考题

1. `OrderBook.__contains__` 现在是线性扫描，订单规模上来后该如何优化？
2. `__repr__` 应该展示多少信息？什么时候会泄露敏感数据？
3. 如果要让 `OrderBook` 支持切片访问（如 `book[:10]`），你会实现什么方法？

---

本周结论很简单：  
数据模型不是语法技巧，而是“让业务对象进入 Python 生态”的最低成本方式。  
当对象行为符合语言直觉时，代码会更短，团队理解成本会更低，后续扩展也更稳。
