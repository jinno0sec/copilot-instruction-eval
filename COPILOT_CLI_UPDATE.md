# GitHub Copilot CLI 更新情報

## 🚨 重要: 正式な GitHub Copilot CLI について

2025年10月17日現在、GitHub が提供する **公式の Copilot CLI** が存在します。
これは従来の `gh copilot` 拡張機能とは**別物**です。

### 📦 新しい GitHub Copilot CLI

**リポジトリ**: https://github.com/github/copilot-cli

**ステータス**: Public Preview（パブリックプレビュー版）

**最新バージョン**: v0.0.343 (2025年10月17日時点)

## 🔄 以前の提案との違い

### ❌ 古い方法（gh copilot 拡張機能）
```bash
gh extension install github/gh-copilot
gh copilot explain
```

### ✅ 新しい方法（公式 Copilot CLI）
```bash
npm install -g @github/copilot
copilot
```

## 📋 特徴

### 1. Agentic Capabilities（エージェント機能）
- **コード生成**: 自然言語からコードを生成
- **編集**: 既存コードの修正と改善
- **デバッグ**: エラーの特定と修正提案
- **リファクタリング**: コード構造の改善

### 2. GitHub統合
- リポジトリ、Issue、PRへの自然言語アクセス
- GitHub認証の自動統合

### 3. MCP (Model Context Protocol) サポート
- GitHubのMCPサーバーがデフォルトで統合
- カスタムMCPサーバーの追加が可能

### 4. 複数のAIモデル
- **デフォルト**: Claude Sonnet 4.5
- **選択可能**: Claude Sonnet 4, GPT-5
- `/model` コマンドで切り替え

### 5. 完全な制御
- すべてのアクションは実行前にプレビュー
- 明示的な承認が必要

## 🚀 セットアップ

### 前提条件
- Node.js v22 以上
- npm v10 以上
- Windows の場合: PowerShell v6 以上
- アクティブな Copilot サブスクリプション

### インストール
```bash
npm install -g @github/copilot
```

### 起動
```bash
copilot
```

初回起動時:
1. アニメーションバナーが表示される
2. GitHubにログインしていない場合は `/login` コマンドを実行
3. 画面の指示に従って認証

### PAT（Personal Access Token）での認証
```bash
# 1. トークン生成: https://github.com/settings/personal-access-tokens/new
# 2. "Copilot Requests" 権限を有効化
# 3. 環境変数に設定
export GH_TOKEN="your_token_here"
# または
export GITHUB_TOKEN="your_token_here"
```

## 💻 使用方法

### 基本的な使い方
```bash
# コードを含むフォルダで起動
cd /path/to/your/project
copilot

# プロンプトを入力
> PythonでFizzBuzzを実装してください

# モデルの変更
> /model

# フィードバック送信
> /feedback

# バナーを再表示
copilot --banner
```

### スラッシュコマンド
- `/login` - GitHub認証
- `/model` - AIモデルの切り替え
- `/feedback` - フィードバック送信

## 📊 プレミアムリクエストについて

各プロンプト送信で月間のプレミアムリクエストクォータが1つ消費されます。
詳細: https://docs.github.com/copilot/managing-copilot/monitoring-usage-and-entitlements/about-premium-requests

## 🎯 このプロジェクトへの影響

### ✅ 良いニュース
1. **完全な自動化が可能**: 対話型だが、プログラムからも利用可能
2. **エージェント機能**: コードレビューだけでなく、編集・リファクタリングも可能
3. **公式サポート**: GitHub公式ツールで継続的にメンテナンスされる
4. **MCPサポート**: 拡張性が高い

### 🔄 必要な更新
1. インストール方法の変更
2. API/CLIの使用方法の変更
3. 対話型インターフェースの統合
4. バッチ処理の実装方法の検討

## 📝 実装への統合方法

### オプション1: サブプロセスとして実行
```python
import subprocess

def review_with_copilot_cli(code: str, instruction: str) -> str:
    """
    Copilot CLIをサブプロセスとして実行
    注: 対話型なので、入力の自動化が必要
    """
    process = subprocess.Popen(
        ["copilot"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # プロンプトを送信
    prompt = f"{instruction}\n\n```python\n{code}\n```"
    stdout, stderr = process.communicate(input=prompt)
    
    return stdout
```

### オプション2: npm パッケージとして統合
```python
import subprocess

def use_copilot_npm_package(prompt: str) -> str:
    """
    Node.js経由でCopilot CLIを使用
    """
    node_script = f"""
    const {{ Copilot }} = require('@github/copilot');
    // API使用例（実際のAPIは確認が必要）
    """
    # 実装の詳細は公式ドキュメントを参照
    pass
```

### オプション3: REST API待ち
将来的にREST APIが提供される可能性があります。

## 🔗 参考リソース

- **公式リポジトリ**: https://github.com/github/copilot-cli
- **公式ドキュメント**: https://docs.github.com/copilot/concepts/agents/about-copilot-cli
- **リリースノート**: https://github.com/github/copilot-cli/releases
- **Discussions**: https://github.com/github/copilot-cli/discussions

## ⚠️ 注意事項

1. **Public Preview版**: まだ開発中で、頻繁に更新される
2. **Node.js必須**: Python環境だけでは動作しない
3. **対話型**: バッチ処理には工夫が必要
4. **組織設定**: 組織のオーナーが無効化している場合は使用不可

## 🎯 推奨される次のステップ

### 短期（すぐに実行）
1. ✅ 新しいCopilot CLIをインストール
```bash
npm install -g @github/copilot
```

2. ✅ 手動で動作確認
```bash
copilot
```

3. ✅ プロジェクトでテスト
```bash
cd /home/jinno/copilot-instruction-eval
copilot
> このプロジェクトのコードをレビューしてください
```

### 中期（1週間以内）
1. Python統合方法の調査
2. サブプロセスでの自動化実装
3. バッチ処理の実現方法の検証

### 長期（1ヶ月以内）
1. 完全自動化されたレビューシステムの構築
2. CI/CDパイプラインへの統合
3. カスタムMCPサーバーの検討

## 📊 更新された推奨度ランキング

| 順位 | アプローチ | 自動化 | 安定性 | 難易度 | 状態 |
|------|-----------|--------|--------|--------|------|
| 🥇 | **GitHub Copilot CLI (新)** | ✅ 完全 | ⭐⭐⭐⭐⭐ | ⭐⭐ 中 | 🆕 **推奨** |
| 🥈 | **VS Code Extension** | ✅ 完全 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ 中 | 📝 要開発 |
| 🥉 | **VS Code CLI + Script** | ⚠️ 部分 | ⭐⭐⭐ | ⭐ 低 | ✅ 利用可能 |
| ❌ | **gh copilot 拡張機能（旧）** | ⚠️ 限定的 | ⭐⭐⭐ | ⭐ 低 | ⚠️ 非推奨 |

---

**最終更新**: 2025年10月17日
**情報源**: https://github.com/github/copilot-cli (v0.0.343)
