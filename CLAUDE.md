# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## セットアップ

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Mac / Linux
pip install -r requirements.txt
```

## よく使うコマンド

```bash
# 依存ライブラリの追加後に記録
pip freeze > requirements.txt

# スクリプト実行
python src/main.py

# テスト実行（pytest 導入後）
pytest
pytest tests/test_xxx.py    # 単一テストファイル実行
pytest -k "test_function"   # 特定のテスト関数を実行
```

## 環境変数

機密情報は `.env` ファイルで管理する（Git管理外）。スクリプト内では `python-dotenv` などを使って読み込む。

```python
from dotenv import load_dotenv
import os
load_dotenv()
value = os.getenv("KEY_NAME")
```
