"""
実装アプローチの具体例

このファイルには、VS Code & Copilot自動化の実現可能な実装例を記載します。
各アプローチは独立して実行できるように設計されています。
"""

import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional


# ============================================================================
# アプローチ1: VS Code CLI + ファイル操作
# ============================================================================


class VSCodeCLIApproach:
    """VS Code CLIを使用したアプローチ"""

    def __init__(self, vscode_command: str = "code"):
        self.vscode_command = vscode_command

    def create_temp_file(self, code: str) -> Path:
        """一時ファイルにコードを保存"""
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        )
        temp_file.write(code)
        temp_file.close()
        return Path(temp_file.name)

    def open_in_vscode(self, file_path: Path) -> bool:
        """VS Codeでファイルを開く"""
        try:
            result = subprocess.run(
                [self.vscode_command, str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception as e:
            print(f"VS Code起動エラー: {e}")
            return False

    def run_workflow(self, code: str, instruction: str) -> dict:
        """
        ワークフロー実行
        
        注意: このアプローチはGUI操作を自動化できません。
        ユーザーが手動でCopilotを操作する必要があります。
        """
        print("=" * 70)
        print("アプローチ1: VS Code CLI + ファイル操作")
        print("=" * 70)

        # ファイル作成
        temp_file = self.create_temp_file(code)
        print(f"✅ 一時ファイル作成: {temp_file}")

        # VS Codeで開く
        success = self.open_in_vscode(temp_file)
        if success:
            print(f"✅ VS Codeでファイルを開きました")
            print(f"\n📝 次のステップ（手動）:")
            print(f"   1. Copilot Chatを開く (Ctrl+Alt+I)")
            print(f"   2. 次の指示を入力: {instruction}")
            print(f"   3. 応答を確認")
            print(f"\n⚠️  このアプローチは完全自動化できません")
        else:
            print(f"❌ VS Code起動に失敗しました")

        return {
            "success": success,
            "temp_file": str(temp_file),
            "automated": False,
            "message": "手動操作が必要",
        }


# ============================================================================
# アプローチ2: GitHub Copilot CLI
# ============================================================================


class GitHubCopilotCLIApproach:
    """GitHub Copilot CLIを使用したアプローチ（最も推奨）"""

    def __init__(self):
        self.gh_command = "gh"

    def check_availability(self) -> bool:
        """GitHub Copilot CLIの利用可能性確認"""
        try:
            result = subprocess.run(
                [self.gh_command, "copilot", "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def explain_code(self, code: str) -> Optional[str]:
        """コードの説明を取得"""
        try:
            # gh copilot explain を使用
            result = subprocess.run(
                [self.gh_command, "copilot", "explain"],
                input=code,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout
            else:
                return None
        except Exception as e:
            print(f"エラー: {e}")
            return None

    def suggest_command(self, instruction: str) -> Optional[str]:
        """コマンド提案を取得"""
        try:
            # gh copilot suggest を使用
            result = subprocess.run(
                [self.gh_command, "copilot", "suggest", instruction],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout
            else:
                return None
        except Exception as e:
            print(f"エラー: {e}")
            return None

    def run_workflow(self, code: str, instruction: str) -> dict:
        """ワークフロー実行"""
        print("=" * 70)
        print("アプローチ2: GitHub Copilot CLI")
        print("=" * 70)

        if not self.check_availability():
            print("❌ GitHub Copilot CLIが利用できません")
            print("   インストール方法: gh extension install github/gh-copilot")
            return {
                "success": False,
                "automated": True,
                "message": "GitHub Copilot CLI未インストール",
            }

        print("✅ GitHub Copilot CLI利用可能")

        # コードの説明を取得
        print(f"\n📝 コードの説明を取得中...")
        explanation = self.explain_code(code)

        if explanation:
            print(f"✅ 説明取得成功:")
            print(f"\n{explanation}\n")
        else:
            print(f"❌ 説明取得失敗")

        # コマンド提案を取得
        print(f"\n📝 指示: {instruction}")
        suggestion = self.suggest_command(instruction)

        if suggestion:
            print(f"✅ 提案取得成功:")
            print(f"\n{suggestion}\n")
        else:
            print(f"❌ 提案取得失敗")

        return {
            "success": explanation is not None or suggestion is not None,
            "explanation": explanation,
            "suggestion": suggestion,
            "automated": True,
            "message": "完全自動化可能",
        }


# ============================================================================
# アプローチ3: pyautogui GUI自動化
# ============================================================================


class PyAutoGUIApproach:
    """pyautoguiを使用したGUI自動化アプローチ"""

    def __init__(self):
        try:
            import pyautogui

            self.pyautogui = pyautogui
            self.available = True
        except ImportError:
            self.pyautogui = None
            self.available = False

    def find_vscode_window(self) -> bool:
        """VS Codeウィンドウを探す（実装例）"""
        # 実際の実装では、ウィンドウタイトルや画像認識を使用
        print("  VS Codeウィンドウを検索中...")
        return False  # プレースホルダー

    def click_copilot_icon(self):
        """Copilotアイコンをクリック"""
        if not self.available:
            return False

        # 実装例（座標は環境依存）
        # self.pyautogui.click(x=100, y=200)
        print("  Copilotアイコンをクリック（シミュレーション）")
        return True

    def type_instruction(self, instruction: str):
        """指示を入力"""
        if not self.available:
            return False

        # self.pyautogui.write(instruction, interval=0.05)
        print(f"  指示を入力: {instruction}（シミュレーション）")
        return True

    def run_workflow(self, code: str, instruction: str) -> dict:
        """ワークフロー実行"""
        print("=" * 70)
        print("アプローチ3: pyautogui GUI自動化")
        print("=" * 70)

        if not self.available:
            print("❌ pyautoguiが利用できません")
            print("   インストール方法: pip install pyautogui")
            return {
                "success": False,
                "automated": True,
                "message": "pyautogui未インストール",
            }

        print("✅ pyautogui利用可能")
        print("\n⚠️  注意: このアプローチは以下の問題があります:")
        print("   - 画面座標が環境依存")
        print("   - 画面解像度やウィンドウサイズで動作が変わる")
        print("   - テーマやUI変更で壊れる可能性")
        print("   - 実装の難易度が高い")

        print("\n📝 実装ステップ（概念実証）:")
        print("  1. VS Codeウィンドウをアクティブ化")
        print("  2. Copilotアイコンの画像認識")
        print("  3. クリック座標の計算")
        print("  4. テキスト入力")
        print("  5. 応答の画面キャプチャ")

        return {
            "success": False,
            "automated": True,
            "message": "実装が複雑で環境依存性が高い",
        }


# ============================================================================
# アプローチ4: VS Code Extension開発（推奨度最高）
# ============================================================================


class VSCodeExtensionApproach:
    """VS Code Extension APIを使用したアプローチ"""

    def generate_extension_template(self) -> str:
        """拡張機能のテンプレートコードを生成"""
        return """
// VS Code Extension の実装例（TypeScript）

import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('Copilot Automation Extension が起動しました');

    // コマンド登録
    let disposable = vscode.commands.registerCommand(
        'copilot-automation.reviewCode',
        async () => {
            // アクティブなエディタを取得
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('アクティブなエディタがありません');
                return;
            }

            // コード取得
            const code = editor.document.getText();

            // Copilot APIを呼び出し（実装例）
            // 注: 実際のCopilot API利用には適切な認証とAPI設定が必要
            const instruction = 'PEP8に準拠し、型ヒントを追加してください';
            
            // チャットビューを開く
            await vscode.commands.executeCommand('workbench.action.chat.open');
            
            // 指示を送信（API経由）
            // await sendToCopilot(code, instruction);
            
            vscode.window.showInformationMessage('コードレビューを実行中...');
        }
    );

    context.subscriptions.push(disposable);
}

export function deactivate() {}
"""

    def generate_package_json(self) -> str:
        """package.jsonの生成"""
        return """{
  "name": "copilot-automation",
  "displayName": "Copilot Automation",
  "description": "GitHub Copilotを使用したコードレビュー自動化",
  "version": "0.0.1",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": [
    "Other"
  ],
  "activationEvents": [],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "copilot-automation.reviewCode",
        "title": "Copilot: コードレビュー実行"
      }
    ]
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.80.0",
    "@types/node": "^18.x",
    "typescript": "^5.1.0"
  }
}
"""

    def run_workflow(self, code: str, instruction: str) -> dict:
        """ワークフロー説明"""
        print("=" * 70)
        print("アプローチ4: VS Code Extension 開発（最推奨）")
        print("=" * 70)

        print("\n✅ 最も安定した実装方法")
        print("\n📝 実装ステップ:")
        print("  1. Yeomanで拡張機能プロジェクトを作成")
        print("     npm install -g yo generator-code")
        print("     yo code")
        print("\n  2. Extension APIを使用してCopilotと連携")
        print("     - vscode.commands.executeCommand()")
        print("     - Chat API (vscode.chat)")
        print("\n  3. 自動テストの実装")
        print("     - VS Code Extension Test Runner")
        print("     - Mochaフレームワーク")
        print("\n  4. デバッグとデプロイ")
        print("     - F5キーでデバッグ実行")
        print("     - vsce publish でマーケットプレイスに公開")

        print("\n📦 必要なファイル:")
        print("  - package.json (拡張機能マニフェスト)")
        print("  - extension.ts (メインロジック)")
        print("  - tsconfig.json (TypeScript設定)")

        print("\n💡 利点:")
        print("  ✅ VS Code APIによる安定した動作")
        print("  ✅ Copilot APIへの直接アクセス")
        print("  ✅ 自動テストが容易")
        print("  ✅ エラーハンドリングが充実")

        return {
            "success": True,
            "automated": True,
            "message": "最も推奨される実装方法",
            "extension_template": self.generate_extension_template(),
            "package_json": self.generate_package_json(),
        }


# ============================================================================
# メイン実行
# ============================================================================


def main():
    """全てのアプローチをデモンストレーション"""
    print("\n" + "=" * 70)
    print("  実装アプローチ比較デモ")
    print("=" * 70)

    # テストコードと指示
    test_code = """
def calculate_area(width, height):
    return width * height
"""

    test_instruction = "PEP8に準拠し、型ヒントとドキュメント文字列を追加してください"

    results = {}

    # アプローチ1: VS Code CLI
    print("\n")
    approach1 = VSCodeCLIApproach()
    results["cli"] = approach1.run_workflow(test_code, test_instruction)
    time.sleep(1)

    # アプローチ2: GitHub Copilot CLI
    print("\n")
    approach2 = GitHubCopilotCLIApproach()
    results["gh_copilot"] = approach2.run_workflow(test_code, test_instruction)
    time.sleep(1)

    # アプローチ3: pyautogui
    print("\n")
    approach3 = PyAutoGUIApproach()
    results["pyautogui"] = approach3.run_workflow(test_code, test_instruction)
    time.sleep(1)

    # アプローチ4: VS Code Extension
    print("\n")
    approach4 = VSCodeExtensionApproach()
    results["extension"] = approach4.run_workflow(test_code, test_instruction)

    # 結果サマリー
    print("\n" + "=" * 70)
    print("  結果サマリー")
    print("=" * 70)

    print("\n📊 各アプローチの評価:")
    print(
        f"\n  1. VS Code CLI:        自動化度: ❌ | 安定性: ⭐⭐⭐   | 実装難易度: ⭐"
    )
    print(
        f"  2. GitHub Copilot CLI: 自動化度: ✅ | 安定性: ⭐⭐⭐⭐⭐ | 実装難易度: ⭐"
    )
    print(
        f"  3. pyautogui:          自動化度: ✅ | 安定性: ⭐      | 実装難易度: ⭐⭐⭐⭐⭐"
    )
    print(
        f"  4. VS Code Extension:  自動化度: ✅ | 安定性: ⭐⭐⭐⭐⭐ | 実装難易度: ⭐⭐⭐"
    )

    print("\n🏆 推奨順位:")
    print("  1位: GitHub Copilot CLI (gh copilot)")
    print("       → 完全自動化可能、実装が簡単")
    print("  2位: VS Code Extension")
    print("       → 最も安定、TypeScript知識が必要")
    print("  3位: VS Code CLI + スクリプト")
    print("       → 部分的な自動化のみ")
    print("  4位: pyautogui")
    print("       → 環境依存性が高すぎる")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
