# ConnLab Testing Skill

每个 Task 完成后，必须自动生成 pytest 测试。

---

## 必须生成测试：

1. 模块是否能导入
2. 函数是否能运行
3. 基本输入输出是否正确
4. 不崩溃（最重要）

---

## 测试要求：

* 使用 pytest
* 放在 tests/ 目录
* 文件名：test_<module>.py
* 每个核心函数至少一个测试

---

## 示例：

```python
def test_create_project():
    result = create_project("DL-001")
    assert result is not None
```

---

## 禁止：

* 不写测试
* 写无法运行的测试
* 写依赖复杂环境的测试

---

## 输出必须包含：

1. 测试文件代码
2. 如何运行 pytest
3. 预期结果
