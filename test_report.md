# 🧪 Python 自动化测试报告

- **执行时间**: GitHub Actions 自动触发
- **整体状态**: ❌ 失败 (Failed - 需修复)
- **测试框架**: Pytest (GitHub Actions)
- **退出状态码**: 1
- **测试统计**: 通过 5 / 失败 1 / 跳过 0

---

### 测试用例

- **tests/test_main.py::test_default_excel_file**: passed
- **tests/test_main.py::test_parse_line**: passed
- **tests/test_main.py::test_bad_input**: passed
- **tests/test_main.py::test_datetime_and_duration**: failed
- **tests/test_main.py::test_process_data_and_duplicate_prevention**: passed
- **tests/test_main.py::test_module_cli_exits_from_stdin**: passed

### 失败详情

#### tests/test_main.py::test_datetime_and_duration

```text
def test_datetime_and_duration():
        assert split_datetime("2026年7月9日 7:05") == ("2026-07-09", "07:05")
        assert convert_duration("2:00:00") == 2
        assert convert_duration("1:30:00") == 1.5
>       assert convert_duration("invalid") == 0
E       AssertionError: assert None == 0
E        +  where None = convert_duration('invalid')

tests\test_main.py:46: AssertionError
```

### 🤖 给 Codex 的反馈指引

如测试失败，请结合本报告及 GitHub Actions 控制台日志分析并修复。
