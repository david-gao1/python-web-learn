# 第 1 周学习：Python 数据模型

## 这周要解决什么问题
我们经常写出“能跑”的类，但这个类不能自然地接入 Python 生态。  
例如：不能 `len()`、不能迭代、调试输出难看、成员判断写很多样板代码。

## 核心思路
把业务对象接入 Python 的数据模型（特殊方法），让对象“像内置类型一样工作”。
- `__len__`：让 `len(obj)` 可用
- `__iter__`：让 `for x in obj` 可用
- `__contains__`：让 `in` 可用
- `__repr__`：让调试输出可读

## 目录结构
```text
week01-data-model/
├── src/week01_data_model/order_book.py
├── tests/test_order_book.py
├── main.py
└── pyproject.toml
```

## 用 uv 管理环境
```bash
cd /Users/lianggao/MyWorkSpace/001-360/python-learning/week01-data-model
uv venv
uv sync
```

## 运行本周示例
```bash
uv run python main.py
```

## 运行质量门禁
```bash
uv run ruff check .
uv run mypy .
uv run pytest -q
```

## 本周 DoD（完成定义）
- 能解释 `OrderBook` 为什么实现这 4 个特殊方法
- 所有质量检查通过
- 能新增一个字段或规则并补上对应测试

## 思考题
1. `__repr__` 与 `__str__` 在工程里如何分工？
2. `__contains__` 现在是线性扫描，何时该改成索引结构？
3. 如果订单量很大，`__iter__` 之外你会加什么能力来优化查询？
