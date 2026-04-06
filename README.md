# Fluent Python Tutorial（学习仓库）

这个仓库按《流畅的 Python（第2版）》目录推进，每个章节以“理解 + 应用”的方式交付：
- 可运行代码
- 自动化测试
- 教学文章（可拆分/可合并）

## 环境与工具

本仓库使用 `uv` 管理虚拟环境与依赖，质量门禁为 `ruff + mypy + pytest`。

```bash
cd /Users/lianggao/MyWorkSpace/001-360/python-learning/fluent-python-tutorial
uv sync
```

## 运行第 1 章（数据模型）

```bash
uv run python chapters/ch01-data-model/main.py
uv run ruff check .
uv run mypy .
uv run pytest -q
```

## 目录
- `chapters/`：按章组织的学习内容
- `docs/`：教程写作模板与规范
- `flasky/`：第三方学习项目（不参与本仓库的 lint/typecheck/test 门禁）
