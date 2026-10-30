# Worklog

Worklog is a Python package that writes parsed work entries into `Worklog.xlsx` and skips duplicates. Its Git repository root is the package directory.

From the **parent directory** of a clone:

```sh
git clone https://github.com/rarnhe/Worklog.git
python -m pip install -r Worklog/requirements.txt
python -m Worklog
```

Enter one JSON entry per line, then an empty line to commit the batch. Type `exit` to quit.

Example:

```json
{"开发":"2026年7月29日 17:45,2:30:00"}
```

From the clone directory, run `python -m pytest -v tests` for local tests. GitHub Actions runs the same tests on Windows and writes both `test_report.md` and the Actions Step Summary.
