"""
新しい GitHub Copilot CLI (@github/copilot) を使用したコードレビュー自動化

このスクリプトは、2025年版の公式 GitHub Copilot CLI を使用します。
リポジトリ: https://github.com/github/copilot-cli

必要条件:
- Node.js v22以上
- npm v10以上
- npm install (リポジトリのルートで実行)
- アクティブなCopilot サブスクリプション
"""

import subprocess
import sys
import json
import time
if sys.platform != "win32":
    import pexpect
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class CopilotCLIResult:
    """Copilot CLIの実行結果"""

    success: bool
    prompt: str
    response: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class NewCopilotCLI:
    """新しい GitHub Copilot CLI (@github/copilot) のラッパー"""

    def __init__(self):
        # npx を使用して、ローカルにインストールされたcopilot-cli を実行
        self.copilot_command = "npx copilot"

    def check_installation(self) -> Dict[str, any]:
        """
        Copilot CLIのインストール状況を確認

        Returns:
            Dict: インストール状況と詳細情報
        """
        status = {
            "installed": False,
            "version": None,
            "node_version": None,
            "npm_version": None,
        }

        # Node.jsの確認
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                status["node_version"] = result.stdout.strip()
        except Exception:
            pass

        # npmの確認
        try:
            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                status["npm_version"] = result.stdout.strip()
        except Exception:
            pass

        # Copilot CLIの確認
        try:
            command_parts = self.copilot_command.split()
            result = subprocess.run(
                command_parts + ["--version"],
                capture_output=True,
                text=True,
                timeout=10,  # npxの初回実行は時間がかかる場合がある
            )
            if result.returncode == 0:
                status["installed"] = True
                status["version"] = result.stdout.strip()
        except FileNotFoundError:
            pass
        except Exception:
            pass

        return status

    def send_prompt_interactive(
        self, prompt: str, timeout: int = 60
    ) -> CopilotCLIResult:
        """
        対話型でプロンプトを自動送信

        pexpect を使用して対話型 CLI とのやり取りを自動化します。
        この機能は現在、Windowsではサポートされていません。

        Args:
            prompt: 送信するプロンプト
            timeout: タイムアウト時間（秒）

        Returns:
            CopilotCLIResult: 実行結果
        """
        if sys.platform == "win32":
            return CopilotCLIResult(
                success=False,
                prompt=prompt,
                error="Automated interactive prompt is not supported on Windows.",
            )

        start_time = time.time()

        try:
            # npx copilotプロセスを開始
            child = pexpect.spawn(
                self.copilot_command, timeout=timeout, encoding="utf-8"
            )

            # デバッグ用にやり取りをコンソールに出力
            child.logfile_read = sys.stdout

            # Copilot CLIのプロンプト `>` を待つ
            child.expect(r">\s*", timeout=20)  # 初回起動は時間がかかることがある

            # プロンプトを送信
            child.sendline(prompt)

            # 応答の終わりを待つ（次のプロンプト `>` が表示されるまで）
            child.expect(r">\s*", timeout=timeout)

            response = child.before

            # プロセスを正常に終了
            child.sendline("/exit")
            child.expect(pexpect.EOF)
            child.close()

            execution_time = time.time() - start_time

            if child.exitstatus == 0:
                # 応答から送信したプロンプト部分を削除
                clean_response = response.strip().replace(prompt, "").strip()
                return CopilotCLIResult(
                    success=True,
                    prompt=prompt,
                    response=clean_response,
                    execution_time=execution_time,
                )
            else:
                error_message = child.before  # エラーメッセージを取得
                return CopilotCLIResult(
                    success=False,
                    prompt=prompt,
                    error=f"Process exited with status {child.exitstatus}. Output: {error_message}",
                    execution_time=execution_time,
                )

        except pexpect.exceptions.TIMEOUT:
            return CopilotCLIResult(
                success=False,
                prompt=prompt,
                error=f"Timeout after {timeout} seconds",
                execution_time=timeout,
            )
        except pexpect.exceptions.EOF:
            return CopilotCLIResult(
                success=False,
                prompt=prompt,
                error=f"EOF reached. Process terminated unexpectedly. Output: {child.before}",
                execution_time=time.time() - start_time,
            )
        except Exception as e:
            return CopilotCLIResult(
                success=False,
                prompt=prompt,
                error=str(e),
                execution_time=time.time() - start_time,
            )

    def create_prompt_for_code_review(
        self, code: str, instruction: str, language: str = "python"
    ) -> str:
        """
        コードレビュー用のプロンプトを作成

        Args:
            code: レビュー対象のコード
            instruction: レビュー指示
            language: プログラミング言語

        Returns:
            str: フォーマットされたプロンプト
        """
        prompt = f"""{instruction}

以下のコードをレビューしてください:

```{language}
{code}
```

レビューには以下を含めてください:
1. コード品質の評価
2. 改善提案
3. PEP8準拠（Pythonの場合）
4. 型ヒントの追加提案
5. 改善されたコードの例
"""
        return prompt


class NewCopilotCodeReviewer:
    """新しい Copilot CLI を使用したコードレビューシステム"""

    def __init__(self):
        self.copilot = NewCopilotCLI()

    def check_prerequisites(self) -> bool:
        """前提条件を確認"""
        print("=" * 70)
        print("前提条件の確認")
        print("=" * 70)

        status = self.copilot.check_installation()

        # Node.js確認
        if not status["node_version"]:
            print("❌ Node.js がインストールされていません")
            print("\nインストール方法:")
            print("  https://nodejs.org/ からダウンロード")
            print("  または: sudo apt install nodejs (Ubuntu)")
            return False
        else:
            print(f"✅ Node.js: {status['node_version']}")

            # バージョンチェック（v22以上が必要）
            version_num = status["node_version"].replace("v", "").split(".")[0]
            if int(version_num) < 22:
                print(
                    "⚠️  警告: Node.js v22以上が推奨されています"
                    f"（現在: {status['node_version']}）"
                )

        # npm確認
        if not status["npm_version"]:
            print("❌ npm がインストールされていません")
            return False
        else:
            print(f"✅ npm: {status['npm_version']}")

        # Copilot CLI確認
        if not status["installed"]:
            print("❌ GitHub Copilot CLI がインストールされていません")
            print("\nインストール方法:")
            print("  npm install -g @github/copilot")
            print("\n初回起動:")
            print("  copilot")
            print("  /login コマンドでGitHub認証")
            return False
        else:
            print(f"✅ GitHub Copilot CLI: {status['version']}")

        print()
        return True

    def review_code_automated(
        self, code: str, instruction: str, output_file: Path
    ) -> Dict:
        """
        自動化されたコードレビューを実行

        pexpect を利用して、Copilot CLIとの対話を自動化します。
        結果は指定されたファイルにJSON形式で保存されます。

        Args:
            code: レビュー対象のコード
            instruction: レビュー指示
            output_file: 結果の保存先

        Returns:
            Dict: 実行結果
        """
        print("=" * 70)
        print("自動コードレビューを実行中...")
        print("=" * 70)

        # プロンプトの作成
        prompt = self.copilot.create_prompt_for_code_review(code, instruction)

        # 実行
        result = self.copilot.send_prompt_interactive(prompt, timeout=120)

        # 結果の保存
        result_dict = asdict(result)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)

        if result.success:
            print("\n✅ レビュー完了")
            print(f"📄 結果を保存: {output_file}")
            print(f"⏱️  実行時間: {result.execution_time:.2f}秒")
        else:
            print("\n❌ レビュー失敗")
            print(f"エラー: {result.error}")

        return result_dict

    def show_usage_guide(self):
        """使用ガイドを表示"""
        print("\n" + "=" * 70)
        print("GitHub Copilot CLI 使用ガイド")
        print("=" * 70)

        print("\n📦 インストール:")
        print("  npm install (このリポジトリのルートで)")

        print("\n🚀 起動:")
        print("  npx copilot")

        print("\n🔐 認証（初回のみ）:")
        print("  > /login")
        print("  ブラウザで認証を完了")

        print("\n💬 基本的な使い方:")
        print("  > PythonでFizzBuzzを実装してください")
        print("  > このコードをPEP8準拠にリファクタリングしてください")

        print("\n🔧 便利なコマンド:")
        print("  > /model      # AIモデルの切り替え")
        print("  > /feedback   # フィードバック送信")
        print("  > /help       # ヘルプ表示")

        print("\n🎯 コードレビューの例:")
        print("  > 以下のPythonコードをレビューしてください:")
        print("  > - PEP8準拠を確認")
        print("  > - 型ヒントを追加")
        print("  > - ドキュメント文字列を追加")
        print("  > ")
        print("  > ```python")
        print("  > def calc(w, h):")
        print("  >     return w * h")
        print("  > ```")

        print("\n📚 参考リソース:")
        print("  公式ドキュメント:")
        print(
            "  https://docs.github.com/copilot/concepts/agents/"
            "about-copilot-cli"
        )
        print("\n  GitHubリポジトリ:")
        print("  https://github.com/github/copilot-cli")

        print("\n" + "=" * 70 + "\n")


def main():
    """メイン実行関数"""
    print("\n" + "=" * 70)
    print("  新しい GitHub Copilot CLI を使用したコードレビュー")
    print("=" * 70 + "\n")

    reviewer = NewCopilotCodeReviewer()

    # 前提条件の確認
    if not reviewer.check_prerequisites():
        print("\n❌ 前提条件を満たしていません。")
        print("   セットアップを完了してから再実行してください。")
        reviewer.show_usage_guide()
        sys.exit(1)

    # 使用ガイドの表示
    reviewer.show_usage_guide()

    # テストコード
    test_code = """
def calculate_area(width, height):
    # This function calculates the area of a rectangle
    return width * height

def get_user_input():
    # Get user input for width and height
    w = input("Enter width: ")
    h = input("Enter height: ")
    return w, h

if __name__ == "__main__":
    w, h = get_user_input()
    area = calculate_area(int(w), int(h))
    print("Area:", area)
"""

    instruction = (
        "このPythonコードをPEP8に準拠するようにレビューし、"
        "型ヒントとドキュメント文字列を追加してください。"
    )

    # 自動レビューの実行
    print("\n" + "=" * 70)
    print("デモ: 自動コードレビューの実行")
    print("=" * 70)

    if sys.platform == "win32":
        print("⚠️  警告: 自動レビューは現在 Windows ではサポートされていません。")
        print("   この機能は pexpect ライブラリを使用しており、Unix系のOSでのみ動作します。")
    else:
        output_file = Path("copilot_review_result_new.json")
        result = reviewer.review_code_automated(
            test_code, instruction, output_file
        )
        print("\n📊 結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n" + "=" * 70)
    print("  完了")
    print("=" * 70 + "\n")

    print("💡 今後の改善案:")
    print("   1. Windows環境での自動化対応（例: wexpect ライブラリの利用）")
    print("   2. Copilot CLIのNode.js APIを直接利用した、より安定した連携")
    print("   3. VS Code Extension API を利用した、さらに高度な連携")
    print()


if __name__ == "__main__":
    main()
