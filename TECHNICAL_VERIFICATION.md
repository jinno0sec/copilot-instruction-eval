# Copilot Instruction Eval - 技術検証レポート

## 📋 プロジェクト概要

GitHub Copilotを使用したPythonコードレビューの自動化を目指すプロジェクト。
当初はPlaywrightを使ったGUI自動化を試みたが、技術検証の結果、より実現可能な代替アプローチを発見。

## 🔍 技術検証結果

### 検証日: 2025年10月17日

### 環境情報
- OS: WSL2 Ubuntu 24.04
- Python: 3.12.3
- VS Code: 1.105.0
- Copilot拡張機能: インストール済み (github.copilot, github.copilot-chat)
- Node.js: v24.2.0

### 検証項目と結果

| # | アプローチ | 実現可能性 | 自動化度 | 安定性 | 難易度 | 推奨度 |
|---|-----------|----------|---------|--------|--------|--------|
| 1 | **Playwright + VS Code** | ❌ | - | - | - | ❌ 非推奨 |
| 2 | **GitHub Copilot CLI** | ⚠️ 未インストール | ✅ 完全 | ⭐⭐⭐⭐⭐ | ⭐ 低 | 🥇 **最推奨** |
| 3 | **VS Code Extension** | ✅ | ✅ 完全 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ 中 | 🥈 推奨 |
| 4 | **VS Code CLI + Script** | ✅ | ❌ 部分的 | ⭐⭐⭐ | ⭐ 低 | 🥉 可 |
| 5 | **pyautogui** | ⚠️ 未インストール | ✅ 完全 | ⭐ | ⭐⭐⭐⭐⭐ 高 | ❌ 非推奨 |

## 🚨 現在のコードの問題点

### `copilot_gui_poc.py` の根本的な問題

```python
# ❌ このコードは動作しません
browser = await playwright.chromium.launch(
    executable_path=vs_code_executable_path,  # VS Codeはブラウザではない
    headless=False,
)
```

**問題点:**
1. **技術的誤解**: PlaywrightはChromium/Firefox/WebKitの自動化ツール
2. **VS CodeはElectronアプリ**: ブラウザではないため、Playwrightで制御不可能
3. **動作確認の欠如**: 実際には実行できないコード
4. **検証ロジックなし**: Copilotの応答が正しいか判定する仕組みがない

## ✅ 推奨される解決策

### 🥇 第1位: GitHub Copilot CLI（最推奨）

**理由:**
- ✅ コマンドラインから直接Copilotを利用可能
- ✅ GUI操作が不要
- ✅ 完全自動化が可能
- ✅ 実装が最も簡単
- ✅ 安定性が高い

**インストール方法:**
```bash
# GitHub CLIのインストール（未インストールの場合）
# Ubuntu/Debian
sudo apt install gh

# Copilot拡張機能のインストール
gh extension install github/gh-copilot

# 認証
gh auth login
```

**実装例:**
```python
import subprocess

def review_code_with_copilot(code: str, instruction: str) -> str:
    """GitHub Copilot CLIでコードレビュー"""
    result = subprocess.run(
        ["gh", "copilot", "explain"],
        input=code,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout

# 使用例
code = "def calc(w, h): return w * h"
instruction = "PEP8準拠と型ヒントを追加"
review = review_code_with_copilot(code, instruction)
print(review)
```

### 🥈 第2位: VS Code Extension開発

**理由:**
- ✅ VS Code APIによる安定した動作
- ✅ Copilot APIへ直接アクセス
- ✅ 完全自動化が可能
- ✅ テストフレームワークが充実
- ⚠️ TypeScript/JavaScript知識が必要

**セットアップ:**
```bash
# Yeomanとジェネレータのインストール
npm install -g yo generator-code

# 拡張機能プロジェクトの生成
yo code

# 開発とテスト
npm install
npm run compile
# F5キーでデバッグ実行
```

**実装の骨格:**
```typescript
// extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand(
        'copilot-eval.reviewCode',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;
            
            const code = editor.document.getText();
            
            // Copilot Chatを開く
            await vscode.commands.executeCommand('workbench.action.chat.open');
            
            // レビュー指示を送信
            // Chat APIを使用して自動化
        }
    );
    
    context.subscriptions.push(disposable);
}
```

### 🥉 第3位: VS Code CLI + スクリプト

**理由:**
- ✅ 実装が簡単
- ✅ VS Code CLIが既に利用可能
- ❌ GUI操作は手動
- ⚠️ 部分的な自動化のみ

**実装例:**
```python
import subprocess
import tempfile

def open_in_vscode(code: str):
    """コードをVS Codeで開く"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    subprocess.run(["code", temp_path])
    print(f"VS Codeで {temp_path} を開きました")
    print("次のステップ:")
    print("1. Ctrl+Alt+I でCopilot Chatを開く")
    print("2. レビュー指示を入力")
    return temp_path
```

## 📝 次のアクションプラン

### 短期（すぐに実装可能）

1. **GitHub Copilot CLIのインストールと検証**
   ```bash
   gh extension install github/gh-copilot
   ```

2. **簡単な自動化スクリプトの作成**
   - `gh copilot explain` を使用
   - `gh copilot suggest` を使用
   - 結果の検証ロジックを追加

3. **テストケースの作成**
   - PEP8準拠の確認
   - 型ヒントの存在確認
   - ドキュメント文字列の確認

### 中期（1-2週間）

1. **VS Code Extension プロジェクトの作成**
   - Yeomanでスキャフォールディング
   - 基本的なコマンド実装
   - Copilot Chat APIとの統合

2. **自動テストの実装**
   - VS Code Extension Test Runner
   - CI/CDパイプラインの構築

### 長期（1ヶ月以上）

1. **VS Code Extension の完成とリリース**
   - Marketplace への公開
   - ドキュメント整備
   - ユーザーフィードバックの収集

2. **機能拡張**
   - 複数ファイルの一括レビュー
   - カスタムレビュールールの設定
   - レポート生成機能

## 📚 参考リソース

### GitHub Copilot CLI
- [GitHub CLI](https://cli.github.com/)
- [GitHub Copilot in the CLI](https://docs.github.com/en/copilot/github-copilot-in-the-cli)

### VS Code Extension開発
- [VS Code Extension API](https://code.visualstudio.com/api)
- [Extension Samples](https://github.com/microsoft/vscode-extension-samples)
- [Chat API](https://code.visualstudio.com/api/extension-guides/chat)

### 学習リソース
- [Your First Extension](https://code.visualstudio.com/api/get-started/your-first-extension)
- [Extension Capabilities](https://code.visualstudio.com/api/extension-capabilities/overview)

## 🔧 既存コードの修正方針

### `copilot_gui_poc.py` の扱い

**オプション1: 削除または参考実装として保存**
- 現在のコードは動作しないため、`archive/` フォルダに移動
- 新しいアプローチで再実装

**オプション2: GitHub Copilot CLIを使用した再実装**
```python
# copilot_cli_automation.py として新規作成
import subprocess
from typing import Optional, Dict

class CopilotCodeReviewer:
    def __init__(self):
        self.gh_command = "gh"
    
    def review_code(self, code: str, instruction: str) -> Dict:
        """コードレビューを実行して結果を返す"""
        result = subprocess.run(
            [self.gh_command, "copilot", "explain"],
            input=code,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "review": result.stdout,
                "automated": True
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "automated": True
            }
```

## 📊 成功の測定基準

実装が成功したと判断する基準:

1. ✅ **自動化達成**: 人間の介入なしでレビューが完了
2. ✅ **検証可能**: レビュー結果が期待通りか自動判定
3. ✅ **再現性**: 同じコードで同様の結果が得られる
4. ✅ **安定性**: エラーハンドリングが適切
5. ✅ **テスト可能**: 自動テストが実装されている

## 🎯 まとめ

現在の `copilot_gui_poc.py` は**技術的に実行不可能**な実装です。
しかし、以下の代替アプローチにより**目的は十分達成可能**です:

1. 🥇 **GitHub Copilot CLI** - 最も簡単で効果的
2. 🥈 **VS Code Extension** - 最も安定で拡張性が高い
3. 🥉 **VS Code CLI** - 部分的な自動化が可能

**推奨される次のステップ:**
```bash
# 1. GitHub Copilot CLIをインストール
gh extension install github/gh-copilot

# 2. 動作確認
gh copilot explain --help

# 3. 新しい実装ファイルで自動化を実現
python copilot_cli_automation.py
```
