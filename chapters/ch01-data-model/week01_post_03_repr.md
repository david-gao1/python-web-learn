# 第1周-03｜让调试变快：`__repr__` 不是“好看”，是“信息密度”

写业务代码时，打印对象是最常见的调试方式之一。  
但很多自定义类默认打印出来是 `<Foo object at 0x...>`，几乎没有信息。

这一篇只讲一个知识点：用 `__repr__` 把对象的“关键状态”以稳定、可读、可定位的方式暴露出来。

## 1. 要解决什么问题

你遇到过这种排查：
- 线上报警：金额不对
- 你把 `OrderBook` 打印出来：只看到内存地址
- 你不得不再写多行打印：打印长度、打印金额、打印前几条订单

理想情况是：`print(book)` 或在 REPL 里输入 `book`，就能看到摘要信息。

## 2. 概念部分：核心思路与关键机制

Python 有两类常见字符串表示：
- `__repr__`：给开发者看的，偏“可调试”，应尽量包含关键信息
- `__str__`：给用户看的，偏“可展示”，可以更友好

工程里最常用的是 `__repr__`，原因很现实：日志、异常、调试器、REPL 更依赖它。

写 `__repr__` 的核心原则不是“优雅”，而是：
- 信息密度足够：能帮助你快速定位问题
- 不泄露敏感信息：不要把 token、隐私数据直接打印进日志
- 输出稳定：字段顺序、格式尽量稳定，便于 grep 与对比

## 3. 实战部分：代码片段 + 运行命令 + 结果说明

本周我们给 `OrderBook` 做了一个摘要式 `repr`：

```python
class OrderBook:
    ...
    def __repr__(self) -> str:
        return f"OrderBook(size={len(self)}, total_amount={self.total_amount()})"
```

为什么这个设计有效：
- `size` 可以立刻判断容器是否为空、是否少数据
- `total_amount` 能快速暴露金额异常（本项目的核心业务指标）

运行方式：

```bash
cd /Users/lianggao/MyWorkSpace/001-360/python-learning/fluent-python-tutorial
uv sync
uv run python chapters/ch01-data-model/main.py
```

你会看到类似输出：
- `OrderBook(size=2, total_amount=41.0)`

## 4. 工程验收：lint/类型检查/测试结果

本篇的验收并不追求“字符串长得一模一样”，而是确保关键信息存在：

```bash
uv run pytest -q
```

测试会检查：
- `repr(book)` 包含 `OrderBook`
- 包含 `size=...`
- 包含总金额的字符串表示

## 5. 思考题

1. `__repr__` 应该展示多少订单明细？只展示摘要是否足够？你的判断标准是什么？
2. 如果 `Order` 里出现敏感字段（比如用户邮箱），你会如何避免它通过 `repr` 泄露到日志？
3. 你会在什么情况下同时实现 `__repr__` 和 `__str__`？两者内容如何区分，才能避免维护成本翻倍？
