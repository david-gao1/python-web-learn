from decimal import Decimal

from week01_data_model.order_book import Order, OrderBook


def test_len_and_iter_behavior() -> None:
    book = OrderBook()
    book.add(Order("A-1", "AAPL", 2, Decimal("10.5")))
    book.add(Order("A-2", "TSLA", 1, Decimal("20")))

    assert len(book) == 2
    assert [o.order_id for o in book] == ["A-1", "A-2"]


def test_contains_order_id() -> None:
    book = OrderBook([Order("A-1", "AAPL", 1, Decimal("1.0"))])
    assert "A-1" in book
    assert "A-2" not in book
    assert 123 not in book


def test_repr_has_debug_info() -> None:
    book = OrderBook([Order("A-1", "AAPL", 2, Decimal("3.5"))])
    text = repr(book)
    assert "OrderBook" in text
    assert "size=1" in text
    assert "7.0" in text


def test_total_amount() -> None:
    book = OrderBook(
        [
            Order("A-1", "AAPL", 2, Decimal("10.5")),
            Order("A-2", "TSLA", 3, Decimal("2.0")),
        ]
    )
    assert book.total_amount() == Decimal("27.0")
