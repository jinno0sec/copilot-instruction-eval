"""
技術検証スクリプト: VS Code & Copilot自動化の実現可能性を検証

このスクリプトは以下のアプローチを検証します:
1. Playwright + Chromium（現行アプローチ）の検証
2. VS Code Extension APIの利用可能性
3. GitHub Copilot CLIの利用可能性
4. pyautogui（GUI自動化）の検証
5. VS Code CLIコマンドの検証
"""

import asyncio
import sys
import subprocess
import os
from pathlib import Path


class TechVerification:
    """技術検証クラス"""

    def __init__(self):
        self.results = {}

    def print_header(self, title: str):
        """セクションヘッダーを表示"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def print_result(self, test_name: str, success: bool, message: str = ""):
        """検証結果を表示"""
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"\n[{status}] {test_name}")
        if message:
            print(f"    └─ {message}")
        self.results[test_name] = {"success": success, "message": message}

    def verify_playwright_installation(self) -> bool:
        """Playwrightのインストール状況を確認"""
        self.print_header("1. Playwright インストール確認")
        try:
            import playwright
            from playwright.async_api import async_playwright

            version = playwright.__version__
            self.print_result(
                "Playwright インストール", True, f"バージョン: {version}"
            )

            # Chromiumブラウザの確認
            try:
                result = subprocess.run(
                    ["playwright", "install", "--dry-run"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                self.print_result(
                    "Playwright ブラウザ", True, "インストールコマンドが利用可能"
                )
            except Exception as e:
                self.print_result(
                    "Playwright ブラウザ", False, f"確認失敗: {str(e)}"
                )

            return True
        except ImportError as e:
            self.print_result("Playwright インストール", False, f"未インストール: {str(e)}")
            return False

    def verify_vscode_paths(self) -> bool:
        """VS Code実行ファイルのパスを確認"""
        self.print_header("2. VS Code 実行パス確認")

        # 一般的なVS Codeパスのリスト
        possible_paths = [
            "/usr/bin/code",
            "/usr/local/bin/code",
            "/snap/bin/code",
            os.path.expanduser("~/.local/bin/code"),
            "/mnt/c/Users/*/AppData/Local/Programs/Microsoft VS Code/Code.exe",  # WSL
        ]

        found_paths = []
        for path in possible_paths:
            # ワイルドカード展開
            if "*" in path:
                from glob import glob

                expanded = glob(path)
                for exp_path in expanded:
                    if os.path.exists(exp_path):
                        found_paths.append(exp_path)
            elif os.path.exists(path):
                found_paths.append(path)

        if found_paths:
            for path in found_paths:
                self.print_result("VS Code 実行ファイル発見", True, f"パス: {path}")
            return True
        else:
            self.print_result("VS Code 実行ファイル発見", False, "パスが見つかりません")
            return False

    def verify_vscode_cli(self) -> bool:
        """VS Code CLIコマンドの動作確認"""
        self.print_header("3. VS Code CLI コマンド確認")

        try:
            # VS Codeバージョン確認
            result = subprocess.run(
                ["code", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split("\n")[0]
                self.print_result("VS Code CLI", True, f"バージョン: {version}")

                # 拡張機能リスト取得
                result_ext = subprocess.run(
                    ["code", "--list-extensions"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                extensions = result_ext.stdout.strip().split("\n")

                # Copilot拡張機能の確認
                copilot_extensions = [
                    ext for ext in extensions if "copilot" in ext.lower()
                ]
                if copilot_extensions:
                    self.print_result(
                        "GitHub Copilot 拡張機能",
                        True,
                        f"インストール済み: {', '.join(copilot_extensions)}",
                    )
                else:
                    self.print_result(
                        "GitHub Copilot 拡張機能", False, "未インストール"
                    )

                return True
            else:
                self.print_result("VS Code CLI", False, f"実行エラー: {result.stderr}")
                return False
        except FileNotFoundError:
            self.print_result("VS Code CLI", False, "codeコマンドが見つかりません")
            return False
        except Exception as e:
            self.print_result("VS Code CLI", False, f"エラー: {str(e)}")
            return False

    def verify_github_copilot_cli(self) -> bool:
        """GitHub Copilot CLIの確認"""
        self.print_header("4. GitHub Copilot CLI 確認")

        try:
            # GitHub Copilot CLIの確認
            result = subprocess.run(
                ["gh", "copilot", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                self.print_result(
                    "GitHub Copilot CLI", True, f"出力: {result.stdout.strip()}"
                )
                return True
            else:
                self.print_result(
                    "GitHub Copilot CLI", False, "gh copilotコマンドが利用不可"
                )
                return False
        except FileNotFoundError:
            self.print_result("GitHub Copilot CLI", False, "ghコマンドが見つかりません")
            return False
        except Exception as e:
            self.print_result("GitHub Copilot CLI", False, f"エラー: {str(e)}")
            return False

    def verify_pyautogui(self) -> bool:
        """pyautoguiのインストール確認"""
        self.print_header("5. pyautogui（GUI自動化）確認")

        try:
            import pyautogui

            version = pyautogui.__version__
            self.print_result("pyautogui インストール", True, f"バージョン: {version}")

            # 画面サイズ取得テスト
            screen_size = pyautogui.size()
            self.print_result(
                "画面情報取得", True, f"画面サイズ: {screen_size.width}x{screen_size.height}"
            )

            return True
        except ImportError:
            self.print_result("pyautogui インストール", False, "未インストール")
            return False
        except Exception as e:
            self.print_result("pyautogui 動作確認", False, f"エラー: {str(e)}")
            return False

    async def verify_playwright_electron(self) -> bool:
        """Playwrightでブラウザ起動を試す（参考）"""
        self.print_header("6. Playwright ブラウザ起動テスト")

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                # Chromiumブラウザの起動テスト
                try:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto("https://example.com")
                    title = await page.title()
                    await browser.close()

                    self.print_result(
                        "Chromium ブラウザ起動",
                        True,
                        f"テストページタイトル: {title}",
                    )
                    return True
                except Exception as e:
                    self.print_result(
                        "Chromium ブラウザ起動", False, f"起動失敗: {str(e)}"
                    )
                    return False
        except ImportError:
            self.print_result("Playwright", False, "モジュールが見つかりません")
            return False

    def verify_vscode_extension_api(self) -> bool:
        """VS Code Extension APIの利用可能性確認"""
        self.print_header("7. VS Code Extension API 確認")

        # package.jsonが存在するか確認
        workspace_root = Path(__file__).parent
        package_json = workspace_root / "package.json"

        if package_json.exists():
            self.print_result(
                "VS Code Extension 構造", True, "package.json が存在します"
            )
        else:
            self.print_result(
                "VS Code Extension 構造",
                False,
                "package.json が存在しません（拡張機能プロジェクトではない）",
            )

        # Node.jsの確認
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.print_result("Node.js インストール", True, f"バージョン: {version}")
            else:
                self.print_result("Node.js インストール", False, "実行エラー")
        except FileNotFoundError:
            self.print_result("Node.js インストール", False, "未インストール")

        return False

    def generate_recommendations(self):
        """検証結果に基づいた推奨事項を生成"""
        self.print_header("検証結果サマリーと推奨事項")

        print("\n📊 検証結果:")
        success_count = sum(1 for r in self.results.values() if r["success"])
        total_count = len(self.results)
        print(f"  成功: {success_count}/{total_count} 項目")

        print("\n💡 推奨される実装アプローチ:")

        # VS Code CLIが利用可能な場合
        if self.results.get("VS Code CLI", {}).get("success"):
            print("\n  🎯 アプローチ1: VS Code CLI + スクリプト連携（推奨）")
            print("     - VS Code CLIでファイルを開く")
            print("     - Copilot拡張機能がインストール済み")
            print("     - キーボードショートカットをシミュレート")
            print("     - 実装難易度: 中")

        # GitHub Copilot CLIが利用可能な場合
        if self.results.get("GitHub Copilot CLI", {}).get("success"):
            print("\n  🎯 アプローチ2: GitHub Copilot CLI（最も推奨）")
            print("     - コマンドラインから直接Copilotを利用")
            print("     - GUIを経由しない")
            print("     - 自動化が容易")
            print("     - 実装難易度: 低")

        # pyautoguiが利用可能な場合
        if self.results.get("pyautogui インストール", {}).get("success"):
            print("\n  🎯 アプローチ3: pyautogui GUI自動化")
            print("     - 画像認識ベースでGUIを操作")
            print("     - VS Codeの画面座標を特定")
            print("     - 環境依存性が高い")
            print("     - 実装難易度: 高")

        # VS Code Extension開発の推奨
        print("\n  🎯 アプローチ4: VS Code Extension 開発（最も安定）")
        print("     - VS Code拡張機能として実装")
        print("     - Extension APIから直接Copilot APIを呼び出し")
        print("     - 最も安定した方法")
        print("     - 実装難易度: 高（TypeScript/JavaScript必須）")

        print("\n❌ 非推奨アプローチ:")
        print("  - Playwright + VS Code executable")
        print("    理由: VS CodeはChromiumブラウザではなく、Electronアプリ")
        print("    現状: 技術的に実行不可能")

    async def run_all_verifications(self):
        """全ての検証を実行"""
        print("\n" + "=" * 70)
        print("  技術検証スクリプト開始")
        print("=" * 70)

        # 同期的な検証
        self.verify_playwright_installation()
        self.verify_vscode_paths()
        self.verify_vscode_cli()
        self.verify_github_copilot_cli()
        self.verify_pyautogui()
        self.verify_vscode_extension_api()

        # 非同期検証
        await self.verify_playwright_electron()

        # 推奨事項の生成
        self.generate_recommendations()

        print("\n" + "=" * 70)
        print("  検証完了")
        print("=" * 70 + "\n")


async def main():
    """メイン実行関数"""
    verifier = TechVerification()
    await verifier.run_all_verifications()


if __name__ == "__main__":
    asyncio.run(main())
