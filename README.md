# Copilot Instruction Eval

GitHub Copilotを使用したPythonコードレビューの自動化プロジェクト

## 📚 プロジェクトファイル一覧

### 📄 コアファイル


### 📖 ドキュメント


## 🚀 クイックスタート

### 🆕 最新情報（2025年10月17日）

**GitHub Copilot CLI の公式版がリリースされました！**

詳細は [`COPILOT_CLI_UPDATE.md`](COPILOT_CLI_UPDATE.md) を参照してください。

### 前提条件

#### オプション1: 新しい Copilot CLI（推奨）

1. Node.js v22以上のインストール
```bash
# Ubuntu/Debian
sudo apt install nodejs npm

# macOS
brew install node

# Windows
winget install OpenJS.NodeJS
```

2. GitHub Copilot CLIのインストール
```bash
npm install -g @github/copilot
```

3. 起動と認証
```bash
copilot
# 初回起動時に /login コマンドで認証
```

#### オプション2: GitHub CLI拡張機能（旧方式）

1. GitHub CLIのインストール
```bash
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh

# Windows
winget install GitHub.cli
```

2. GitHub Copilot拡張機能のインストール
```bash
gh extension install github/gh-copilot
gh auth login
```

### 実行方法

#### 新しい Copilot CLI を使用（推奨）
```bash
# 手動でのインタラクティブなレビュー
copilot

# Pythonスクリプトでの準備
python copilot_cli_new_automation.py
```

#### 技術検証の実行
```bash
python tech_verification.py
```

#### 旧方式のコードレビュー
```bash
python copilot_cli_automation.py
```

#### 各アプローチのデモ
```bash
python approach_examples.py
```

## 📊 技術検証結果

| アプローチ | 実現可能性 | 自動化 | 安定性 | 難易度 | 推奨度 |
|-----------|----------|--------|--------|--------|--------|
| **GitHub Copilot CLI (新)** | ✅ | 完全* | ⭐⭐⭐⭐⭐ | ⭐⭐ | 🥇 **最推奨** |
| VS Code Extension | ✅ | 完全 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 🥈 推奨 |
| VS Code CLI | ✅ | 部分的 | ⭐⭐⭐ | ⭐ | 🥉 可 |
| gh copilot 拡張機能（旧） | ⚠️ | 限定的 | ⭐⭐⭐ | ⭐ | ⚠️ 非推奨 |
| Playwright + VS Code | ❌ | - | - | - | ❌ 非推奨 |

*対話型のため、完全自動化にはpexpectなどの追加実装が必要

詳細は [`TECHNICAL_VERIFICATION.md`](TECHNICAL_VERIFICATION.md) と [`COPILOT_CLI_UPDATE.md`](COPILOT_CLI_UPDATE.md) を参照してください。

## 🎯 推奨される実装

### 新しい GitHub Copilot CLI を使用（最推奨）

**インストール:**
```bash
npm install -g @github/copilot
```

**使用方法:**
```bash
# 対話型で起動
copilot

# プロンプト例
> 以下のPythonコードをレビューしてください:
> - PEP8準拠を確認
> - 型ヒントを追加
> - ドキュメント文字列を追加
> 
> ```python
> def calculate_area(width, height):
>     return width * height
> ```
```

**Python統合（準備用）:**
```python
from copilot_cli_new_automation import NewCopilotCodeReviewer

reviewer = NewCopilotCodeReviewer()

# コードレビュー用のプロンプトを準備
code = """
def calculate_area(width, height):
    return width * height
"""

instruction = "PEP8に準拠し、型ヒントを追加してください"
reviewer.review_code_manual(code, instruction)
```

### 旧方式: gh copilot 拡張機能（非推奨）

<details>
<summary>クリックして展開</summary>

```bash
# インストール
gh extension install github/gh-copilot

# 使用
gh copilot explain "コードの説明"
```

注意: この方式は機能が限定的です。新しいCopilot CLIの使用を推奨します。

</details>

## 📁 ファイル詳細

### `copilot_cli_automation.py`

GitHub Copilot CLIを使用したコードレビュー自動化の実装。

**主要クラス:**

**機能:**

### `tech_verification.py`

各実装アプローチの実現可能性を検証するスクリプト。

**検証項目:**
1. Playwrightのインストール状況
2. VS Code実行パス
3. VS Code CLI
4. GitHub Copilot CLI
5. pyautogui
6. VS Code Extension API
7. Playwrightブラウザ起動

### `approach_examples.py`

4つの実装アプローチの具体例とデモ。

**アプローチ:**
1. VS Code CLI + ファイル操作
2. GitHub Copilot CLI（推奨）
3. pyautogui GUI自動化
4. VS Code Extension開発

## 🔧 開発環境


## 📖 学習リソース

### GitHub Copilot CLI

### VS Code Extension開発

## 🤔 よくある質問

### Q: `copilot_gui_poc.py` が動作しないのはなぜ？

A: PlaywrightはChromium/Firefox/WebKitなどのブラウザを自動化するツールです。VS CodeはElectronアプリケーションであり、ブラウザではないため、Playwrightで直接制御することはできません。

### Q: どの実装方法を選ぶべき？

A: **GitHub Copilot CLIが最推奨**です。理由：

### Q: GitHub Copilot CLIが使えない場合は？

A: 以下の順で検討してください：
1. VS Code Extension開発（最も安定）
2. VS Code CLI + スクリプト（部分的な自動化）

### Q: pyautoguiは使えないの？

A: 技術的には可能ですが、以下の理由で非推奨：

## 🛠️ トラブルシューティング

### GitHub Copilot CLIがインストールできない

```bash
# GitHub CLIのバージョン確認
gh --version

# 拡張機能の再インストール
gh extension remove github/gh-copilot
gh extension install github/gh-copilot

# 認証の確認
gh auth status
gh auth login
```

### VS Codeが見つからない

```bash
# VS Codeのパス確認
which code

# パスが見つからない場合
# Ubuntu: sudo apt install code
# または、VS CodeのSettings > Shell Command: Install 'code' command in PATH
```

## 📝 次のステップ

### 短期
1. GitHub Copilot CLIのインストール
2. `copilot_cli_automation.py` の実行とテスト
3. 自分のコードでレビューを試す

### 中期
1. VS Code Extension プロジェクトの作成
2. カスタムレビュールールの追加
3. 自動テストの実装

### 長期
1. VS Code Extensionのリリース
2. CI/CDパイプラインの構築
3. 複数ファイルの一括レビュー機能

## 📄 ライセンス

このプロジェクトのライセンスについては、[LICENSE](LICENSE) ファイルを参照してください。

## 🙏 貢献

プルリクエストや issue の作成を歓迎します！

## 📧 連絡先

質問や提案がある場合は、GitHub の issue を作成してください。


**最終更新**: 2025年10月17日
