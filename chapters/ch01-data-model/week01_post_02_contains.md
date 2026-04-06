# 第1周-02｜把“成员判断”写成语言能力：`__contains__`

容器类最常见的调用之一就是成员判断：某个元素在不在集合里。  
如果你不给 `OrderBook` 这项能力，调用方会出现两类坏味道：
- 业务逻辑里充斥 `any(...)`、for 循环扫描
- 每个调用点都自己实现一遍“怎么判断存在”，风格与边界不一致

这一篇专注一个知识点：让 `"A-1" in book` 成为可读、可控、可优化的能力。

## 1. 要解决什么问题

你在服务里经常会写：
- “订单号是否存在？”（幂等、去重、校验）
- “某订单号是否已处理？”（任务队列）

理想代码是：

```python
if order_id in book:
    ...
```

而不是到处复制粘贴：

```python
if any(o.order_id == order_id for o in book.orders()):
    ...
```

## 2. 概念部分：核心思路与关键机制

成员判断语法糖 `x in container` 对应的协议大致是：
1. 如果对象实现了 `__contains__`，优先调用它
2. 否则尝试迭代（`__iter__`），用线性扫描判定

所以 `__contains__` 的价值不只是“少写点代码”，而是：
- 把“成员判断”的语义收敛到一个地方（统一边界）
- 为未来优化留接口（从线性扫描升级到索引/缓存）

另外一个工程细节：`in` 的左侧可以是任意对象，因此 `__contains__` 的入参通常写成 `object`，然后在内部做类型保护，避免隐式错误。

## 3. 实战部分：代码片段 + 运行命令 + 结果说明

本周的 `OrderBook.__contains__` 实现如下：

```python
class OrderBook:
    ...
    def __contains__(self, order_id: object) -> bool:
        if not isinstance(order_id, str):
            return False
        return any(order.order_id == order_id for order in self._orders)
```

这段实现的取舍：
- 返回 `False` 而不是抛异常：让调用方 `123 in book` 这种误用“安全失败”
- 当前是线性扫描：先保证语义正确，再根据规模升级数据结构

运行方式：

```bash
cd /Users/lianggao/MyWorkSpace/001-360/python-learning/fluent-python-tutorial
uv sync
uv run python chapters/ch01-data-model/main.py
```

你会在输出里看到 `是否包含订单 A-1: True`。

## 4. 工程验收：lint/类型检查/测试结果

这一篇的验收重点在“边界一致性”：

```bash
uv run pytest -q
```

你应该能通过如下测试语义：
- `"A-1" in book` 为 True
- `"A-2" in book` 为 False
- `123 in book` 为 False（而不是异常）

如果未来你把内部结构换成 dict 或加缓存，这些测试不变，语义不变，调用方不变。

## 5. 思考题

1. 现在 `__contains__` 是线性扫描：订单量达到多少时你会考虑换成索引？你会用 dict 还是 set？
2. `__contains__` 返回 False vs 抛异常：在你的团队代码规范里，哪种更合适？
3. 如果订单号大小写不敏感（`a-1` 等价 `A-1`），你会把规范化逻辑放在哪里，才能避免全链路重复处理？
