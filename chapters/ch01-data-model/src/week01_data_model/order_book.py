"""
第 1 章学习载体：用一个业务对象演示 Python 数据模型（特殊方法 / 协议）。

这份代码刻意选择一个很小的领域对象：OrderBook（订单集合），目的是把“语言能力”
映射到“你实现的特殊方法”，并且用测试把行为固定下来。

核心映射（记住这些就够用）：
- len(book)        -> book.__len__()
- for x in book    -> iter(book) -> book.__iter__()
- x in book        -> book.__contains__(x)（优先；没有则退化为迭代扫描）
- book[i] / book[a:b] -> book.__getitem__(index_or_slice)
- repr(book)       -> book.__repr__()

工程观点：
- 你通常不直接调用这些 dunder 方法；写它们是为了让解释器/标准库调用。
- 协议是“行为约定”而不是继承关系：实现了方法，就获得了语言级语法糖。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import overload
from typing import Iterator


@dataclass(frozen=True)
class Order:
    """
    一个不可变订单对象（frozen=True）。

    为什么用 Decimal：
    - 金额计算避免 float 的二进制舍入误差
    """

    order_id: str
    symbol: str
    quantity: int
    price: Decimal

    @property
    def amount(self) -> Decimal:
        """订单金额：price * quantity。作为 property 体现“派生属性”的语义。"""
        return self.price * self.quantity


class OrderBook:
    """
    订单集合（容器/序列的最小实现示例）。

    目标不是“实现完整的订单系统”，而是演示：
    - 如何用数据模型把业务对象做成“像内置类型一样好用”
    - 如何用类型提示与测试把行为固定为可演进的接口
    """

    def __init__(self, orders: list[Order] | None = None) -> None:
        """
        orders 是可选的初始订单列表。

        list(orders or []) 的好处：
        - None 时得到空列表
        - 传入已有 list 时做一次浅拷贝，避免外部 list 被修改影响内部状态
        """
        self._orders: list[Order] = list(orders or [])

    def add(self, order: Order) -> None:
        """追加一条订单。这里的 API 是业务方法，和 dunder 协议方法区分开。"""
        self._orders.append(order)

    def __len__(self) -> int:
        """支持 len(book)。"""
        return len(self._orders)

    def __iter__(self) -> Iterator[Order]:
        """
        支持 for order in book。

        工程建议：可迭代对象不要同时扮演迭代器（不要 return self），否则：
        - 迭代状态会污染对象自身
        - 并发/嵌套迭代更容易产生诡异 bug
        """
        return iter(self._orders)

    @overload
    def __getitem__(self, index: int) -> Order: ...

    @overload
    def __getitem__(self, index: slice) -> list[Order]: ...

    def __getitem__(self, index: int | slice) -> Order | list[Order]:
        """
        支持 book[i] 与 book[a:b]。

        为什么用 overload：
        - book[0]   -> Order
        - book[:10] -> list[Order]
        这样 mypy --strict 才能在调用点推导出正确类型。
        """
        return self._orders[index]

    def __contains__(self, order_id: object) -> bool:
        """
        支持 "A-1" in book。

        参数写成 object 是刻意的：
        - `in` 左侧允许任何对象，类型保护由容器实现负责
        - 这里选择“安全失败”：非 str 直接返回 False，而不是抛异常
        """
        if not isinstance(order_id, str):
            return False
        return any(order.order_id == order_id for order in self._orders)

    def __repr__(self) -> str:
        """
        支持 repr(book) 与交互式调试输出。

        工程约束：
        - 信息密度优先：给出 size 与关键指标（total_amount）
        - 输出稳定：字段顺序固定，便于日志检索与对比
        - 注意敏感信息：不要在 repr 里输出隐私字段或密钥
        """
        return f"OrderBook(size={len(self)}, total_amount={self.total_amount()})"

    def total_amount(self) -> Decimal:
        """
        订单总金额：sum(order.amount)。

        start=Decimal("0") 的原因：
        - 避免 sum 在空序列时返回 int 0，导致类型漂移（Decimal vs int）
        """
        return sum((order.amount for order in self._orders), start=Decimal("0"))
