#!/bin/bash
# Copilot CLI認証テストスクリプト

echo "=== Copilot CLI認証状態確認 ==="
echo ""
echo "対話モードで起動します。以下の手順を実施してください："
echo ""
echo "1. /login コマンドで認証（未認証の場合）"
echo "2. ブラウザでGitHubにログイン"
echo "3. 簡単な質問（例: 'Pythonでhello worldを書いて'）を入力してテスト"
echo "4. /exit で終了"
echo ""
echo "Press Enter to start Copilot CLI..."
read

copilot
