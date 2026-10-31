"""Generate both test_report.md and the GitHub Actions step summary."""
import os
from pathlib import Path

import pytest

_RESULTS = []


def pytest_configure(config):
    _RESULTS.clear()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when in ("setup", "teardown") and report.failed):
        _RESULTS.append((report.nodeid, report.outcome,
                         str(report.longrepr) if report.failed else ""))


def pytest_sessionfinish(session, exitstatus):
    passed = exitstatus == 0
    status = "✅ 通过 (Passed)" if passed else "❌ 失败 (Failed - 需修复)"
    counts = {
        label: sum(result == label for _, result, _ in _RESULTS)
        for label in ("passed", "failed", "skipped")
    }
    details = "\n".join(
        f"- **{name}**: {result}" for name, result, _ in _RESULTS
    ) or "- 未执行测试（请查看收集或导入错误）"
    failures = "\n\n".join(
        f"#### {name}\n\n```text\n{error}\n```"
        for name, result, error in _RESULTS if result == "failed"
    ) or "无测试失败；如整体失败请查看 Actions 日志。"
    content = f"""# 🧪 Python 自动化测试报告

- **执行时间**: GitHub Actions 自动触发
- **整体状态**: {status}
- **测试框架**: Pytest (GitHub Actions)
- **退出状态码**: {int(exitstatus)}
- **测试统计**: 通过 {counts['passed']} / 失败 {counts['failed']} / 跳过 {counts['skipped']}

---

### 测试用例

{details}

### 失败详情

{failures}

### 🤖 给 Codex 的反馈指引

如测试失败，请结合本报告及 GitHub Actions 控制台日志分析并修复。
"""
    Path("test_report.md").write_text(content, encoding="utf-8")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(content)
