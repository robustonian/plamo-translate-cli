# PLaMo Translate CLI 使用方法

PLaMo Translate CLIは、plamo-2-translateモデルを使用してローカルで実行される翻訳コマンドラインツールです。16以上の言語間での翻訳をサポートし、ネットワーク経由での使用も可能です。

## インストール

### macOS用

#### Python>=3.13の場合

```bash
brew install cmake
pip install git+https://github.com/google/sentencepiece.git@2734490#subdirectory=python
pip install plamo-translate
```

#### Python<3.13の場合

```bash
pip install plamo-translate
```

#### uv toolを使用する場合

```bash
uv tool install -p 3.12 plamo-translate
```

## 基本的な使用方法

### 1. シンプルな翻訳

```bash
# 日本語から英語へ
plamo-translate --input 'こんにちは、お元気ですか？'
# 出力: Hello, how are you?

# 英語から日本語へ
plamo-translate --input 'Hello, how are you?'
# 出力: こんにちは、お元気ですか？
```

### 2. パイプを使用した翻訳

```bash
# ファイルの内容を翻訳
cat document.txt | plamo-translate

# コマンドのヘルプを翻訳
gcc --help | plamo-translate

# 複数行のテキストを翻訳
echo "家計は火の車だ
今月は厳しい" | plamo-translate
```

### 3. インタラクティブモード

```bash
plamo-translate --interactive
# または
plamo-translate -i
```

インタラクティブモードでは、連続して翻訳を行うことができます：

```
> こんにちは、お元気ですか？
Hello, how are you?
> 「お腹減った〜何食べたい？」「私はうなぎ！」
"I'm hungry! What do you want to eat?" "I want eel!"
> Ctrl+Dで終了
```

## 言語指定

### サポートされている言語

- Japanese（日本語）
- Japanese(easy)（やさしい日本語）
- English（英語）
- Chinese（中国語）
- Taiwanese（台湾語）
- Korean（韓国語）
- Arabic（アラビア語）
- Italian（イタリア語）
- Indonesian（インドネシア語）
- Dutch（オランダ語）
- Spanish（スペイン語）
- Thai（タイ語）
- German（ドイツ語）
- French（フランス語）
- Vietnamese（ベトナム語）
- Russian（ロシア語）

### 言語指定の例

```bash
# 日本語から英語へ
plamo-translate --from Japanese --to English --input '家計は火の車だ'

# 英語からスペイン語へ
plamo-translate --from English --to Spanish --input 'Hello world'

# 中国語から日本語へ
plamo-translate --from Chinese --to Japanese --input '你好世界'
```

## サーバーモード

### ローカルMCPサーバー

翻訳を頻繁に行う場合、サーバーモードを使用することでモデルの読み込み時間を短縮できます：

```bash
# サーバーを起動
plamo-translate server

# 別のターミナルで翻訳実行
plamo-translate --input '家計は火の車だ'
```

### HTTPサーバー（ネットワーク対応）

他のマシンからアクセス可能なHTTPサーバーを起動できます：

```bash
# HTTPサーバーを起動（デフォルト: 0.0.0.0:8080）
plamo-translate http-server

# カスタムホスト・ポートで起動
plamo-translate http-server --host 0.0.0.0 --port 9000
```

## ネットワーク経由での使用

### HTTPサーバーを使用した翻訳

Mac等でHTTPサーバーを起動後、他のマシンから以下のように使用できます：

```bash
# 基本的な使用方法
plamo-translate --http-server 192.168.1.100:8080 --input '家計は火の車だ'

# パイプも使用可能
gcc --help | plamo-translate --http-server 192.168.1.100:8080

# インタラクティブモード
plamo-translate --http-server 192.168.1.100:8080 --interactive

# 言語指定
plamo-translate --http-server 192.168.1.100:8080 --from Japanese --to English --input '家計は火の車だ'
```

### 環境変数の設定

毎回`--http-server`を指定するのを避けるため、環境変数を設定できます：

```bash
# ~/.bashrcや~/.zshrcに追加
export PLAMO_HTTP_SERVER=192.168.1.100:8080

# 以降は通常のコマンドとして使用可能
plamo-translate --input '家計は火の車だ'
gcc --help | plamo-translate
plamo-translate --interactive
```

## オプション一覧

### 共通オプション

| オプション | 短縮形 | 説明 |
|------------|--------|------|
| `--help` | `-h` | ヘルプメッセージを表示 |
| `--version` | `-v` | バージョン情報を表示 |
| `--input TEXT` | | 翻訳するテキストを指定 |
| `--from LANG` | | 入力言語を指定（デフォルト: English\|Japanese） |
| `--to LANG` | | 出力言語を指定 |
| `--interactive` | `-i` | インタラクティブモードを有効化 |
| `--no-stream` | | バッチ処理モードを有効化 |
| `--precision {4bit,8bit,bf16}` | `-p` | モデルの精度を指定（デフォルト: 4bit） |
| `--http-server HOST:PORT` | | HTTPサーバーを使用 |

### サブコマンド

| サブコマンド | 説明 |
|--------------|------|
| `server` | ローカルMCPサーバーを起動 |
| `http-server` | HTTPサーバーを起動 |
| `show-claude-config` | Claude Desktop用のMCP設定を表示 |

## 設定

### 環境変数

| 環境変数 | 説明 | デフォルト値 |
|----------|------|-------------|
| `PLAMO_HTTP_SERVER` | デフォルトのHTTPサーバーアドレス | なし |
| `PLAMO_TRANSLATE_CLI_TEMP` | テキスト生成の温度 | 0.0 |
| `PLAMO_TRANSLATE_CLI_TOP_P` | Top-pサンプリング確率 | 0.98 |
| `PLAMO_TRANSLATE_CLI_TOP_K` | Top-kサンプリング数 | 0 |
| `PLAMO_TRANSLATE_CLI_REPETITION_PENALTY` | 繰り返しペナルティ | なし |
| `PLAMO_TRANSLATE_CLI_REPETITION_CONTEXT_SIZE` | 繰り返しペナルティのコンテキストサイズ | なし |

### HTTPサーバー用環境変数

```bash
# HTTPサーバーのデフォルト設定
export PLAMO_HTTP_SERVER=localhost:8080

# モデル設定
export PLAMO_TRANSLATE_CLI_MODEL_NAME=mlx-community/plamo-2-translate
export PLAMO_TRANSLATE_CLI_TEMP=0.1
export PLAMO_TRANSLATE_CLI_TOP_P=0.95
```

### Ubuntu/Linux環境での便利な設定

Ubuntu等のLinux環境でuvを使用している場合、以下の設定を`~/.bashrc`や`~/.zshrc`に追加すると便利です：

```bash
# ~/.bashrcまたは~/.zshrcに追加
export PLAMO_HTTP_SERVER=192.168.xx.xx:9000  # Macサーバーのアドレスに変更
alias plamo-translate='/path/to/plamo-translate-cli/.venv/bin/plamo-translate'

# 設定を反映
source ~/.bashrc  # または source ~/.zshrc
```

この設定により、以下のようにシンプルに使用できます：

```bash
# 短縮形で使用可能
plamo-translate --input '家計は火の車だ'
echo '家計は火の車だ' | plamo-translate
plamo-translate --interactive
```

## 使用例

### 1. 日常的な翻訳作業

```bash
# ファイルの翻訳
cat README.md | plamo-translate --from English --to Japanese > README_JP.md

# エラーメッセージの翻訳
./my_program 2>&1 | plamo-translate
```

### 2. 開発作業での活用

```bash
# コマンドのヘルプを日本語で確認
git --help | plamo-translate

# ログファイルの翻訳
tail -f app.log | plamo-translate
```

### 3. ネットワーク環境での活用

```bash
# リモートサーバーのMacで翻訳サーバーを起動
ssh mac-server "plamo-translate http-server"

# ローカルのLinuxマシンから翻訳
export PLAMO_HTTP_SERVER=mac-server:8080
echo "複雑なエラーメッセージ" | plamo-translate
```

## トラブルシューティング

### よくある問題

1. **モデルの読み込みに時間がかかる**
   - 初回起動時は数分かかる場合があります
   - サーバーモードを使用することで、2回目以降の起動を高速化できます

2. **HTTPサーバーに接続できない**
   - サーバーが起動しているか確認：`plamo-translate --http-server HOST:PORT --help`
   - ファイアウォールの設定を確認
   - ポートが使用中でないか確認

3. **Python 3.13での依存関係エラー**
   - sentencepieceを先にインストール：
     ```bash
     pip install git+https://github.com/google/sentencepiece.git@2734490#subdirectory=python
     ```

### デバッグ

```bash
# サーバーの状態確認
plamo-translate --http-server localhost:8080 --input "test" --verbose

# ローカルサーバーの状態確認
plamo-translate server --log-level DEBUG
```

## Claude Desktopとの連携

PLaMo TranslateはMCP（Model Context Protocol）サーバーとしても動作し、Claude Desktopから利用可能です：

```bash
# MCPサーバーを起動
plamo-translate server

# Claude Desktop用の設定を表示
plamo-translate show-claude-config
```

出力された設定をClaude Desktopの設定ファイル（`~/Library/Application Support/Claude/claude_desktop_config.json`）に追加することで、Claude Desktop内から翻訳機能を使用できます。

## まとめ

PLaMo Translate CLIは、シンプルなコマンドライン翻訳から、ネットワーク経由でのマルチマシン翻訳環境まで、様々な用途に対応できる柔軟な翻訳ツールです。開発作業、文書翻訳、多言語環境でのコミュニケーション支援など、幅広い場面で活用できます。

## 使い方メモ
* [plamo-translate-cliコマンドをUbuntuで使いたい](https://zenn.dev/robustonian/scraps/b98b74938567c5)
