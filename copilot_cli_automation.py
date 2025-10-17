"""
GitHub Copilot CLIを使用したコードレビュー自動化

このスクリプトは、GitHub Copilot CLIを使用して、
Pythonコードのレビューと改善提案を自動化します。

必要条件:
- GitHub CLIがインストールされていること
- gh copilot拡張機能がインストールされていること
  インストール: gh extension install github/gh-copilot
- GitHub認証が完了していること
  認証: gh auth login
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ReviewResult:
    """レビュー結果を格納するデータクラス"""

    success: bool
    code: str
    instruction: str
    review: Optional[str] = None
    error: Optional[str] = None
    automated: bool = True
    validation: Optional[Dict] = None


class GitHubCopilotCLI:
    """GitHub Copilot CLIのラッパークラス"""

    def __init__(self, gh_command: str = "gh"):
        self.gh_command = gh_command

    def check_installation(self) -> Dict[str, bool]:
        """
        GitHub CLIとCopilot拡張機能のインストール状況を確認

        Returns:
            Dict[str, bool]: 各コンポーネントのインストール状況
        """
        status = {"gh_cli": False, "copilot_extension": False}

        # GitHub CLIの確認
        try:
            result = subprocess.run(
                [self.gh_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            status["gh_cli"] = result.returncode == 0
        except FileNotFoundError:
            pass

        # Copilot拡張機能の確認
        if status["gh_cli"]:
            try:
                result = subprocess.run(
                    [self.gh_command, "copilot", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                status["copilot_extension"] = result.returncode == 0
            except Exception:
                pass

        return status

    def explain_code(self, code: str, timeout: int = 30) -> Optional[str]:
        """
        コードの説明を取得

        Args:
            code: 説明を取得したいコード
            timeout: タイムアウト時間（秒）

        Returns:
            Optional[str]: コードの説明、失敗時はNone
        """
        try:
            result = subprocess.run(
                [self.gh_command, "copilot", "explain"],
                input=code,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"エラー: {result.stderr}", file=sys.stderr)
                return None
        except subprocess.TimeoutExpired:
            print(f"タイムアウト: {timeout}秒以内に応答がありませんでした", file=sys.stderr)
            return None
        except Exception as e:
            print(f"エラー: {e}", file=sys.stderr)
            return None

    def suggest_improvement(self, instruction: str, timeout: int = 30) -> Optional[str]:
        """
        改善提案を取得

        Args:
            instruction: 改善指示
            timeout: タイムアウト時間（秒）

        Returns:
            Optional[str]: 改善提案、失敗時はNone
        """
        try:
            result = subprocess.run(
                [self.gh_command, "copilot", "suggest", "-t", "shell", instruction],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"エラー: {result.stderr}", file=sys.stderr)
                return None
        except subprocess.TimeoutExpired:
            print(f"タイムアウト: {timeout}秒以内に応答がありませんでした", file=sys.stderr)
            return None
        except Exception as e:
            print(f"エラー: {e}", file=sys.stderr)
            return None


class CodeValidator:
    """コードレビュー結果を検証するクラス"""

    @staticmethod
    def check_type_hints(code: str) -> bool:
        """型ヒントの存在を確認"""
        # 簡易チェック: "->" または ":" が関数定義に含まれているか
        import re

        pattern = r"def\s+\w+\s*\([^)]*:\s*\w+|def\s+\w+\s*\([^)]*\)\s*->"
        return bool(re.search(pattern, code))

    @staticmethod
    def check_docstrings(code: str) -> bool:
        """ドキュメント文字列の存在を確認"""
        return '"""' in code or "'''" in code

    @staticmethod
    def check_pep8_basics(code: str) -> Dict[str, bool]:
        """
        基本的なPEP8準拠をチェック

        Returns:
            Dict[str, bool]: 各チェック項目の結果
        """
        checks = {
            "has_docstrings": CodeValidator.check_docstrings(code),
            "has_type_hints": CodeValidator.check_type_hints(code),
            "no_trailing_whitespace": not any(
                line.endswith(" ") for line in code.split("\n")
            ),
            "proper_indentation": "    " in code,  # 4スペースインデント
        }
        return checks

    @staticmethod
    def validate_review(original_code: str, reviewed_code: str) -> Dict:
        """
        レビュー結果を検証

        Args:
            original_code: 元のコード
            reviewed_code: レビュー後のコード

        Returns:
            Dict: 検証結果
        """
        original_checks = CodeValidator.check_pep8_basics(original_code)
        reviewed_checks = CodeValidator.check_pep8_basics(reviewed_code)

        improvements = {}
        for key in original_checks:
            if not original_checks[key] and reviewed_checks[key]:
                improvements[key] = "改善されました"
            elif original_checks[key] and reviewed_checks[key]:
                improvements[key] = "維持されています"
            elif original_checks[key] and not reviewed_checks[key]:
                improvements[key] = "悪化しました"
            else:
                improvements[key] = "未改善"

        return {
            "original": original_checks,
            "reviewed": reviewed_checks,
            "improvements": improvements,
            "score": sum(reviewed_checks.values()) / len(reviewed_checks) * 100,
        }


class CopilotCodeReviewer:
    """コードレビューの自動化を行うメインクラス"""

    def __init__(self):
        self.copilot_cli = GitHubCopilotCLI()
        self.validator = CodeValidator()

    def check_prerequisites(self) -> bool:
        """前提条件を確認"""
        print("=" * 70)
        print("前提条件の確認")
        print("=" * 70)

        status = self.copilot_cli.check_installation()

        if not status["gh_cli"]:
            print("❌ GitHub CLIがインストールされていません")
            print("\nインストール方法:")
            print("  Ubuntu/Debian: sudo apt install gh")
            print("  macOS: brew install gh")
            print("  Windows: winget install GitHub.cli")
            return False

        print("✅ GitHub CLI: インストール済み")

        if not status["copilot_extension"]:
            print("❌ GitHub Copilot拡張機能がインストールされていません")
            print("\nインストール方法:")
            print("  gh extension install github/gh-copilot")
            print("  gh auth login  # 認証が必要な場合")
            return False

        print("✅ GitHub Copilot拡張機能: インストール済み")
        print()
        return True

    def review_code(
        self, code: str, instruction: str, validate: bool = True
    ) -> ReviewResult:
        """
        コードレビューを実行

        Args:
            code: レビュー対象のコード
            instruction: レビュー指示
            validate: レビュー結果を検証するか

        Returns:
            ReviewResult: レビュー結果
        """
        print("=" * 70)
        print("コードレビュー実行中")
        print("=" * 70)
        print(f"\n📝 指示: {instruction}\n")

        # コードの説明を取得
        review = self.copilot_cli.explain_code(code)

        if review is None:
            return ReviewResult(
                success=False,
                code=code,
                instruction=instruction,
                error="レビューの取得に失敗しました",
            )

        print("✅ レビュー取得成功\n")
        print("=" * 70)
        print("レビュー結果")
        print("=" * 70)
        print(review)
        print("=" * 70 + "\n")

        # 検証
        validation_result = None
        if validate:
            # 注: 実際の改善されたコードを取得するには別のアプローチが必要
            # ここでは元のコードに対する検証のみ実施
            validation_result = self.validator.check_pep8_basics(code)
            print("📊 コード品質チェック:")
            for check, result in validation_result.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check}: {result}")
            print()

        return ReviewResult(
            success=True,
            code=code,
            instruction=instruction,
            review=review,
            validation=validation_result,
        )

    def review_file(
        self, file_path: Path, instruction: str, validate: bool = True
    ) -> ReviewResult:
        """
        ファイルのコードレビューを実行

        Args:
            file_path: レビュー対象のファイルパス
            instruction: レビュー指示
            validate: レビュー結果を検証するか

        Returns:
            ReviewResult: レビュー結果
        """
        if not file_path.exists():
            return ReviewResult(
                success=False,
                code="",
                instruction=instruction,
                error=f"ファイルが見つかりません: {file_path}",
            )

        print(f"📄 ファイル: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        return self.review_code(code, instruction, validate)

    def save_result(self, result: ReviewResult, output_path: Path):
        """レビュー結果をファイルに保存"""
        result_dict = asdict(result)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        print(f"💾 結果を保存しました: {output_path}")


def main():
    """メイン実行関数"""
    print("\n" + "=" * 70)
    print("  GitHub Copilot CLI を使用したコードレビュー自動化")
    print("=" * 70 + "\n")

    # レビューアの初期化
    reviewer = CopilotCodeReviewer()

    # 前提条件の確認
    if not reviewer.check_prerequisites():
        print("\n❌ 前提条件を満たしていません。セットアップを完了してください。")
        sys.exit(1)

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

    # レビュー指示
    instruction = "このPythonコードをPEP8に準拠するようにレビューし、型ヒントを追加してください。また、より良いコメントを追加してください。"

    # レビュー実行
    result = reviewer.review_code(test_code, instruction, validate=True)

    # 結果の保存
    if result.success:
        output_path = Path("review_result.json")
        reviewer.save_result(result, output_path)
        print("\n✅ コードレビューが完了しました")
    else:
        print(f"\n❌ コードレビューに失敗しました: {result.error}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("  完了")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
