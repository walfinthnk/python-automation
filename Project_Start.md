# プロジェクト開始手順

## 前提条件
- Git がインストール済みであること
- GitHub CLI (`gh`) がインストール・認証済みであること
- Claude Code がインストール済みであること
- Python がインストール済みであること

---

## 手順

### 1. プロジェクトフォルダ作成

```bash
mkdir my-project
cd my-project
```

---

### 2. Git 初期化

```bash
git init
```

---

### 3. .gitignore 作成

不要なファイルをGit管理外にする。

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.pyo
.venv/
venv/

# 環境変数
.env

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
EOF
```

---

### 4. 仮想環境の作成と有効化

```bash
python -m venv .venv

# Windows の場合
.venv\Scripts\activate

# Mac / Linux の場合
source .venv/bin/activate
```

---

### 5. requirements.txt 作成

使用するライブラリをインストールしながら記録する。

```bash
# ライブラリをインストール後に生成
pip install <使用するライブラリ>
pip freeze > requirements.txt
```

再現時は以下でインストール可能：

```bash
pip install -r requirements.txt
```

---

### 6. .env ファイル作成

APIキーなどの機密情報を環境変数で管理する。

```bash
cat > .env << 'EOF'
# APIキーや設定値をここに記述
# 例: ANTHROPIC_API_KEY=your_api_key_here
EOF
```

> `.env` は `.gitignore` に含まれているためGitにはコミットされない。

---

### 7. README.md 作成

プロジェクトの概要・使い方を記録する。

```bash
cat > README.md << 'EOF'
# プロジェクト名

## 概要
このプロジェクトの説明をここに記述する。

## セットアップ

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 使い方
使い方の説明をここに記述する。
EOF
```

---

### 8. CLAUDE.md 自動生成

Claude Code の `/init` スキルを使って `CLAUDE.md` を自動生成する。

```
/init
```

Claude がプロジェクトの構成を解析し、`CLAUDE.md` を生成する。

---

### 9. GitHub リポジトリ作成 & リモート連携

```bash
gh repo create my-project --public --source=. --remote=origin
```

---

### 10. 初回コミット & プッシュ

```bash
git add .
git commit -m "Initial commit"
git push -u origin main
```

---

## 設定まとめ

| 項目 | 設定値 |
|------|--------|
| リポジトリ公開設定 | public |
| デフォルトブランチ | main |
| CLAUDE.md 生成方法 | `/init` スキルで自動生成 |
| 仮想環境 | `.venv` |
| 機密情報管理 | `.env`（Git管理外） |

---

## 完了後の確認

- `git remote -v` でリモートが正しく設定されているか確認
- GitHub のリポジトリページで初回コミットが反映されているか確認
- `.env` が GitHub にアップされていないか確認
- `CLAUDE.md` と `README.md` がリポジトリに含まれているか確認
