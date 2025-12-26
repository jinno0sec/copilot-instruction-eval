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

import argparse
import subprocess
import sys
import json
import time
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
        対話型でプロンプトを送信（実験的）

        注意: Copilot CLIは対話型のため、自動化は制限されます。
        この実装は概念実証であり、実際の使用では調整が必要です。

        Args:
            prompt: 送信するプロンプト
            timeout: タイムアウト時間（秒）

        Returns:
            CopilotCLIResult: 実行結果
        """
        start_time = time.time()

        try:
            # 注: これは簡易実装です。実際のCopilot CLIは対話型のため、
            # pexpectなどのライブラリを使用した方が安定します。
            command_parts = self.copilot_command.split()
            process = subprocess.Popen(
                command_parts,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # プロンプトを送信
            stdout, stderr = process.communicate(
                input=prompt + "\n", timeout=timeout
            )

            execution_time = time.time() - start_time

            if process.returncode == 0 or stdout:
                return CopilotCLIResult(
                    success=True,
                    prompt=prompt,
                    response=stdout,
                    execution_time=execution_time,
                )
            else:
                return CopilotCLIResult(
                    success=False,
                    prompt=prompt,
                    error=stderr,
                    execution_time=execution_time,
                )

        except subprocess.TimeoutExpired:
            return CopilotCLIResult(
                success=False,
                prompt=prompt,
                error=f"Timeout after {timeout} seconds",
                execution_time=timeout,
            )
        except Exception as e:
            return CopilotCLIResult(
                success=False, prompt=prompt, error=str(e), execution_time=0
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

    def review_code_batch(
        self, code: str, instruction: str, output_file: Path
    ) -> Dict:
        """
        バッチモードでのコードレビュー（実験的）

        注意: これは実験的な実装です。Copilot CLIの仕様により、
        完全な自動化は保証されません。

        Args:
            code: レビュー対象のコード
            instruction: レビュー指示
            output_file: 結果の保存先

        Returns:
            Dict: 実行結果
        """
        print("=" * 70)
        print("バッチモード コードレビュー（実験的）")
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
    parser = argparse.ArgumentParser(
        description="新しい GitHub Copilot CLI を使用したコードレビュー自動化ツール",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input-file",
        type=Path,
        default=Path("code/sample_code_to_review.py"),
        help="レビュー対象のコードファイル (デフォルト: code/sample_code_to_review.py)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="対話的なプロンプトを表示せず、実験的なバッチモードでレビューを実行する",
    )
    parser.add_argument(
        "--show-guide",
        action="store_true",
        help="Copilot CLIの使用ガイドを表示する",
    )
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  新しい GitHub Copilot CLI を使用したコードレビュー")
    print("=" * 70 + "\n")

    reviewer = NewCopilotCodeReviewer()

    # 前提条件の確認
    if not reviewer.check_prerequisites():
        print("\n❌ 前提条件を満たしていません。")
        print("   セットアップを完了してから再実行してください。")
        if not args.show_guide:
            reviewer.show_usage_guide()
        sys.exit(1)

    if args.show_guide:
        reviewer.show_usage_guide()
        sys.exit(0)

    # 入力ファイルの存在確認
    if not args.input_file.exists():
        print(f"❌ 入力ファイルが見つかりません: {args.input_file}")
        sys.exit(1)

    # コードと指示の読み込み
    try:
        test_code = args.input_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)

    instruction = (
        "このPythonコードをPEP8に準拠するようにレビューし、"
        "型ヒントとドキュメント文字列を追加してください。"
    )

    if args.batch:
        # 結果ディレクトリの準備
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)

        # 出力ファイルパスの生成
        output_filename = f"{args.input_file.stem}_review_result.json"
        output_file = results_dir / output_filename

        # バッチモードでレビューを実行
        result = reviewer.review_code_batch(test_code, instruction, output_file)

        print("\n📊 結果の概要:")
        print(f"  - 成功: {result.get('success')}")
        print(f"  - 実行時間: {result.get('execution_time', 0):.2f}秒")
        if result.get('error'):
            print(f"  - エラー: {result.get('error')}")

    else:
        # 手動レビューのための準備と指示表示
        print("\n" + "=" * 70)
        print("手動レビューモード")
        print("=" * 70)
        reviewer.review_code_manual(test_code, instruction)

    print("\n" + "=" * 70)
    print("  完了")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
