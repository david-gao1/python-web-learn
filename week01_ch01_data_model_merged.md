# 第1章合并版｜Python 数据模型：让业务对象“像内置类型一样工作”

很多 Python 项目里都有一类隐形成本：自定义类“能跑”，但“不像 Python”。  
表现就是一堆需要记忆的自定义方法：`size()`、`items()`、`to_list()`、`has(id)`……调用方写起来不自然，调试也不友好。

《流畅的 Python》第 1 章要你建立的观念是：Python 的很多“语法糖”和内建能力，并不是魔法，而是通过 **数据模型（data model）+ 协议（protocol）** 驱动的。你只要把类接入这些协议，就能免费获得大量一致、可组合、可测试的语言能力。

这篇把第 1 周的 4 篇文章合并，统一讲清楚一件事：怎样从“自定义 API 的类”，升级成“遵守 Python 协议的对象”。

---

## 1. 要解决什么问题

我们用一个简单但真实的业务对象 `OrderBook`（订单集合）作为练习载体，希望它做到：
- 统计订单数量：`len(book)`
- 遍历订单：`for order in book: ...`
- 判断订单号是否存在：`"A-1" in book`
- 调试输出可读：`repr(book)` / `print(book)`
- 具备序列体验：`book[0]`、`book[:10]`

这些能力的共同点是：它们不是“你写一个方法就行”，而是“你对外呈现的行为要符合语言直觉”。符合直觉的对象，调用方就不用背 API，代码风格也会更统一。

---

## 2. 概念部分：核心思路与关键机制

### 2.1 数据模型是什么：不是 OOP 概念，是“语言协议表”

你可以把 Python 数据模型理解为：  
**一张“语法/内建函数 -> 特殊方法（dunder）”的映射表**。

例如：
- `len(obj)` -> `obj.__len__()`
- `iter(obj)` / `for x in obj` -> `obj.__iter__()`
- `x in obj` -> `obj.__contains__(x)`（优先），否则退化为迭代扫描
- `obj[i]` / `obj[a:b]` -> `obj.__getitem__(i_or_slice)`
- `repr(obj)` -> `obj.__repr__()`

关键点：这些特殊方法多数不是给你直接调用的，而是给 **解释器** 或 **标准库** 调用的。  
这就是“Pythonic”的来源：你写的是协议，获得的是语言级能力。

### 2.2 协议是什么：鸭子类型的工程化版本

“协议”在这里不是指 `Protocol` 类型提示，而是更基础的语言层面概念：  
只要对象实现了某些特殊方法，就被视作支持某种能力。

容器协议的一个典型好处：你不需要继承某个基类，也不需要注册到某个框架里。  
你只要实现 `__len__` / `__iter__`，它就能被 `len()` / `for` 使用。

### 2.3 为什么 `len(obj)` 不是 `obj.len()`：为了让协议可替换

第 1 章里一个重要观点是：`len` 之类的功能做成内建函数而不是方法，是为了：
- 让语言对“长度”这个能力有统一入口（适用于不同类型）
- 让解释器有优化空间（内置类型可走更快路径）
- 让协议在类型之间可替换（你实现了 `__len__`，就自然接入）

从工程角度看，统一入口意味着一致性：团队更容易写出统一风格的代码，也更容易复用通用工具函数。

---

## 3. 实战部分：把 `OrderBook` 接入容器与序列协议

项目路径：

```bash
cd /Users/lianggao/MyWorkSpace/001-360/python-learning/week01-data-model
uv sync
```

核心实现位于：[order_book.py](file:///Users/lianggao/MyWorkSpace/001-360/python-learning/week01-data-model/src/week01_data_model/order_book.py)

### 3.1 `__len__`：把“数量”变成语言能力

```python
def __len__(self) -> int:
    return len(self._orders)
```

意义不在于少写两行，而在于：
- 调用方不需要知道你内部是 list 还是别的数据结构
- 所有需要“大小”的地方都能统一写法：`len(book)`

### 3.2 `__iter__`：把“遍历”变成语言能力

```python
def __iter__(self) -> Iterator[Order]:
    return iter(self._orders)
```

工程上的最佳实践是：**可迭代对象不要同时扮演迭代器**。  
这也是为什么这里直接返回 `iter(self._orders)`，而不是让 `OrderBook` 自己维护遍历状态。

### 3.3 `__contains__`：把“成员判断”收敛到一个边界

`x in book` 的价值是：让调用层代码自然、短、少分支。  
更重要的是，它让你未来优化查询时“有一个统一入口”。

```python
def __contains__(self, order_id: object) -> bool:
    if not isinstance(order_id, str):
        return False
    return any(order.order_id == order_id for order in self._orders)
```

这里故意把入参写成 `object`：因为 `in` 左边可以是任意类型。  
内部做类型保护，能让误用更可控（返回 False，而不是在业务代码里炸异常）。

### 3.4 `__repr__`：为调试提供“高信息密度摘要”

`__repr__` 的目标不是“好看”，而是“能定位问题”。  
建议遵循三条：
- 展示关键状态（例如 size、关键指标）
- 输出稳定（字段顺序、格式稳定）
- 避免泄露敏感信息（不要输出 token、隐私数据）

```python
def __repr__(self) -> str:
    return f"OrderBook(size={len(self)}, total_amount={self.total_amount()})"
```

### 3.5 `__getitem__`：让对象具有“序列体验”

工程里经常会有这类代码：
- 排查：只看前 10 条
- 分页：取第 N 条

`__getitem__` 能让这些场景变得自然：`book[0]`、`book[:10]`。  
另外，切片与索引返回类型不同（`Order` vs `list[Order]`），为了让 `mypy --strict` 通过，我们使用 `@overload`：

```python
from typing import overload

@overload
def __getitem__(self, index: int) -> Order: ...

@overload
def __getitem__(self, index: slice) -> list[Order]: ...

def __getitem__(self, index: int | slice) -> Order | list[Order]:
    return self._orders[index]
```

这一步的核心不是“为了类型检查而写复杂”，而是用类型系统把 API 的真实行为固定下来，减少误用。

---

## 4. 工程验收：用 uv + ruff/mypy/pytest 让行为可复现

运行示例：

```bash
uv run python main.py
```

质量门禁：

```bash
uv run ruff check .
uv run mypy .
uv run pytest -q
```

你应该能看到：
- `len(book)` 与测试一致
- `list(book)` 顺序稳定
- `"A-1" in book` 行为稳定（含错误类型输入）
- `book[0]` / `book[:2]` 通过测试

---

## 5. 思考题（更贴近第 1 章的“设计意识”）

1. 如果你把 `OrderBook.__iter__` 写成 `return self`，让它自己做迭代器，会带来哪些可维护性问题？在并发场景里会发生什么？
2. `__contains__` 当前是线性扫描：你会用什么数据结构优化？优化后如何保持 API 不变、测试不变？
3. `__repr__` 应该输出多少内容才“信息密度足够”？如果未来 `Order` 增加敏感字段，如何防止泄露？
4. `__getitem__` 的切片返回 list 可能导致大内存：如果订单数量很大，你会如何提供“惰性切片”的能力？

---

## 附录：本章对应的代码与文章来源

本合并文由以下分篇整理而来（你仍可保留它们作为更短的拆分版本）：
- [week01_post_01_len_iter.md](file:///Users/lianggao/MyWorkSpace/001-360/python-learning/week01-data-model/week01_post_01_len_iter.md)
- [week01_post_02_contains.md](file:///Users/lianggao/MyWorkSpace/001-360/python-learning/week01-data-model/week01_post_02_contains.md)
- [week01_post_03_repr.md](file:///Users/lianggao/MyWorkSpace/001-360/python-learning/week01-data-model/week01_post_03_repr.md)
- [week01_post_04_getitem.md](file:///Users/lianggao/MyWorkSpace/001-360/python-learning/week01-data-model/week01_post_04_getitem.md)
