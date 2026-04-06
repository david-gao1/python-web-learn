from decimal import Decimal

from week01_data_model.order_book import Order, OrderBook


def main() -> None:
    book = OrderBook(
        [
            Order("A-1", "AAPL", 2, Decimal("10.5")),
            Order("A-2", "TSLA", 1, Decimal("20")),
        ]
    )
    print(book)
    print("订单总金额:", book.total_amount())
    print("是否包含订单 A-1:", "A-1" in book)


if __name__ == "__main__":
    main()
