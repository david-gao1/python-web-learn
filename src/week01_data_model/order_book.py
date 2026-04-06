from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import overload
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
        self._orders: list[Order] = list(orders or [])

    def add(self, order: Order) -> None:
        self._orders.append(order)

    def __len__(self) -> int:
        return len(self._orders)

    def __iter__(self) -> Iterator[Order]:
        return iter(self._orders)

    @overload
    def __getitem__(self, index: int) -> Order: ...

    @overload
    def __getitem__(self, index: slice) -> list[Order]: ...

    def __getitem__(self, index: int | slice) -> Order | list[Order]:
        return self._orders[index]

    def __contains__(self, order_id: object) -> bool:
        if not isinstance(order_id, str):
            return False
        return any(order.order_id == order_id for order in self._orders)

    def __repr__(self) -> str:
        return f"OrderBook(size={len(self)}, total_amount={self.total_amount()})"

    def total_amount(self) -> Decimal:
        return sum((order.amount for order in self._orders), start=Decimal("0"))
