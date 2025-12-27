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
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict

# pexpect をインポート (Unix系OSのみ)
if sys.platform != "win32":
    try:
        import pexpect
    except ImportError:
        # このエラーは、check_prerequisitesで処理されるべきだが、念のため
        print("エラー: pexpect ライブラリがインストールされていません。'pip install pexpect' を実行してください。")
        sys.exit(1)


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

    def send_prompt_automated(
        self, prompt: str, timeout: int = 120
    ) -> CopilotCLIResult:
        """
        pexpectを使用して対話型CLIにプロンプトを自動送信 (Unix系OSのみ)

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
                error="Automated interaction with pexpect is not supported on Windows.",
            )

        start_time = time.time()
        try:
            child = pexpect.spawn(self.copilot_command, timeout=timeout, encoding='utf-8')
            # デバッグ用にコンソールに出力する場合
            # child.logfile_read = sys.stdout

            # 初期のプロンプト "> " を待つ
            child.expect(r'>\s*', timeout=20)

            # プロンプトを送信
            child.sendline(prompt)

            # 応答が完了し、次のプロンプトが表示されるのを待つ
            child.expect(r'>\s*', timeout=timeout)

            execution_time = time.time() - start_time
            response = child.before
            child.close()

            # 応答から送信したプロンプトのエコーを削除
            cleaned_response = response.replace(prompt, "", 1).strip()

            return CopilotCLIResult(
                success=True,
                prompt=prompt,
                response=cleaned_response,
                execution_time=execution_time,
            )

        except pexpect.exceptions.TIMEOUT:
            execution_time = time.time() - start_time
            error_output = f"Timeout after {timeout} seconds."
            if 'child' in locals() and hasattr(child, 'before') and child.before:
                error_output += f"\nOutput before timeout:\n{child.before}"
            return CopilotCLIResult(
                success=False,
                prompt=prompt,
                error=error_output,
                execution_time=execution_time,
            )
        except pexpect.exceptions.EOF:
            execution_time = time.time() - start_time
            error_output = "Process exited unexpectedly (EOF)."
            if 'child' in locals() and hasattr(child, 'before') and child.before:
                error_output += f"\nOutput before exit:\n{child.before}"
            return CopilotCLIResult(
                success=False,
                prompt=prompt,
                error=error_output,
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return CopilotCLIResult(
                success=False,
                prompt=prompt,
                error=str(e),
                execution_time=execution_time,
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

    def review_code_manual(self, code: str, instruction: str):
        """
        手動でのコードレビュー（対話型）

        Copilot CLIは対話型のため、この関数は指示を表示するだけです。
        ユーザーは手動でCopilot CLIを起動して使用する必要があります。

        Args:
            code: レビュー対象のコード
            instruction: レビュー指示
        """
        print("=" * 70)
        print("コードレビュー準備完了")
        print("=" * 70)

        # プロンプトの生成
        prompt = self.copilot.create_prompt_for_code_review(code, instruction)

        # 一時ファイルに保存
        temp_file = Path("/tmp/copilot_review_prompt.txt")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        print("\n✅ レビュープロンプトを作成しました")
        print(f"📄 保存先: {temp_file}")

        print("\n" + "=" * 70)
        print("次のステップ（手動実行）")
        print("=" * 70)
        print("\n1. ターミナルで Copilot CLI を起動:")
        print("   $ npx copilot")
        print("\n2. 以下のプロンプトをコピー＆ペースト:")
        print("\n" + "-" * 70)
        print(prompt)
        print("-" * 70)

        print("\n3. または、ファイルから読み込み:")
        print(f"   $ cat {temp_file} | npx copilot")

        print("\n⚠️  注意: 新しい Copilot CLI は対話型のため、")
        print("   完全な自動化にはさらなる実装が必要です。")

    def review_code_automated(
        self, code: str, instruction: str, output_file: Path
    ) -> Dict:
        """
        自動モードでのコードレビュー (pexpectを使用, Unix系OSのみ)

        Args:
            code: レビュー対象のコード
            instruction: レビュー指示
            output_file: 結果の保存先

        Returns:
            Dict: 実行結果
        """
        print("=" * 70)
        print("自動モード コードレビュー")
        print("=" * 70)

        # プロンプトの作成
        prompt = self.copilot.create_prompt_for_code_review(code, instruction)

        # 実行
        result = self.copilot.send_prompt_automated(prompt, timeout=120)

        # 結果の保存
        result_dict = asdict(result)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)

        if result.success:
            print(f"\n✅ レビュー完了 (実行時間: {result.execution_time:.2f}秒)")
            print(f"📄 結果を保存: {output_file}")
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
    print("  新しい GitHub Copilot CLI を使用したコードレビュー自動化")
    print("=" * 70 + "\n")

    reviewer = NewCopilotCodeReviewer()

    # 1. 前提条件の確認
    if not reviewer.check_prerequisites():
        print("\n❌ 前提条件を満たしていません。セットアップを完了してから再実行してください。")
        reviewer.show_usage_guide()
        sys.exit(1)

    # Windowsの場合は、手動モードのガイドを表示して終了
    if sys.platform == "win32":
        print("⚠️  Windowsでは自動実行はサポートされていません。")
        print("   手動での実行方法を以下に示します。")
        reviewer.show_usage_guide()
        sys.exit(0)

    # 2. レビュー対象のコードを読み込む
    #    ここでは`/code/sample.py` を対象とする
    code_dir = Path(__file__).parent / "code"
    target_file = code_dir / "sample.py"
    output_file = Path("results") / "review_result.json"

    # results ディレクトリがなければ作成
    output_file.parent.mkdir(exist_ok=True)

    if not target_file.exists():
        print(f"❌エラー: レビュー対象ファイルが見つかりません: {target_file}")
        # サンプルファイルを作成
        target_file.parent.mkdir(exist_ok=True)
        sample_code = """
def calculate_area(width, height):
    # This function calculates the area of a rectangle
    return width * height
"""
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(sample_code)
        print(f"✅サンプルファイルを作成しました: {target_file}")
        code_to_review = sample_code
    else:
        with open(target_file, "r", encoding="utf-8") as f:
            code_to_review = f.read()
        print(f"✅レビュー対象ファイルを読み込みました: {target_file}")

    # 3. レビュー指示
    instruction = (
        "あなたはシニアPython開発者です。以下の観点でコードをレビューしてください。\n"
        "1. コードの品質と可読性\n"
        "2. PEP8への準拠\n"
        "3. 型ヒントとドキュメント文字列の提案\n"
        "4. 考えられるバグやエッジケース\n"
        "5. 全体的な改善案と、修正後のコード例"
    )

    # 4. 自動レビューの実行
    print(f"\n🚀 自動コードレビューを開始します... (対象: {target_file})")
    result = reviewer.review_code_automated(
        code_to_review, instruction, output_file
    )

    # 5. 結果の表示
    if result.get("success"):
        print("\n" + "=" * 70)
        print("  レビュー結果の概要")
        print("=" * 70)

        response_text = result.get("response", "応答がありません。")
        # 応答が長い場合、最初の500文字だけ表示
        if len(response_text) > 500:
            print(response_text[:500] + "...")
        else:
            print(response_text)

        print("\n" + "=" * 70)
        print(f"✅ 全てのレビュー結果は {output_file} に保存されました。")
    else:
        print("\n" + "=" * 70)
        print("  レビューが失敗しました。")
        print("=" * 70)
        print(f"エラー詳細は {output_file} を確認してください。")

    print("\n" + "=" * 70)
    print("  スクリプト完了")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
