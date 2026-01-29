📖 概要
Amazonと楽天市場の商品ページを定期的に巡回し、「価格の変動」や「在庫の復活」を自動で監視するWebアプリケーションです。

「欲しい商品があるけれど、常にサイトを見ていられない」「再入荷のタイミングを逃したくない」という課題を解決するために開発しました。
Pythonのフレームワーク Streamlit を使用し、ブラウザ上で直感的に操作できるダッシュボード形式にしています。


🌟特徴
マルチサイト対応: Amazonと楽天市場の両方に対応。URLを入力するだけで自動的にサイトを判別します。
監視モード：PRICEモード：指定した金額以下になったら画面で強調表示
　　　　　　STOCKモード：「在庫あり」「かごに追加」などの文言を検知して画面でお知らせ
設定の外部化：監視対象リストを `config.json` で管理。プログラムを書き換えずに監視対象の追加・削除が可能です。
Bot検知回避：スクレイピング対策が厳しいサイトでもデータを取得できるよう、人間らしい挙動（Human-like behavior）を実装しています。


🛠 使用技術
Language: Python 3.12
Frontend: Streamlit
Scraping: Playwright (Browser Automation)
Version Control: Git / GitHub


🔧 インストールと実行方法
1. リポジトリのクローン
git clone https://github.com/あなたのユーザー名/ecsite-checker.git
cd ecsite-checker

2. 依存ライブラリのインストール
pip install -r requirements.txt

3. Playwright用ブラウザのセットアップ
playwright install

4. アプリの起動
python -m streamlit run app.py


💡 工夫した点・技術的なこだわり
1. 動的なWebサイトへの対応
Amazonなどの最近のECサイトは、JavaScriptを使用して動的に価格や在庫情報を表示しているため、従来の BeautifulSoup や Requests では正確な情報が取得できないことがありました。
そこで、実際のブラウザ（Chromium）をプログラムから操作できる Playwright を採用し、ユーザーが見ている画面と同じデータを確実に取得できるようにしました。

2. Bot対策の回避
開発当初、頻繁にアクセスブロック（Bot検知）に遭いました。これを解決するために logic.py で以下の工夫を行いました。
・ヘッドレスモードの無効化 (headless=False): あえてブラウザ画面を表示させることで、一般的なユーザーの利用に見せかけています。
・User-Agentの偽装: プログラムからのアクセスではなく、WindowsのChromeからのアクセスとしてリクエストを送っています。
・ランダムな待機時間: time.sleep(random.uniform(2, 5)) を導入し、機械的な一定間隔のアクセスにならないようにしました。

3. Windows環境での非同期処理エラーの解決
Windows環境で Streamlit と Playwright を同時に動作させると、イベントループの仕様の違いにより NotImplementedError が発生する問題に直面しました。
これに対し、app.py の冒頭で asyncio.WindowsProactorEventLoopPolicy を明示的に設定することで、Windows環境でも安定して動作するように対応しました。

4. 拡張性を意識した設計
将来的に「ヨドバシカメラ」や「Yahoo!ショッピング」など他のサイトにも対応できるよう、サイト判定ロジックを check_site 関数として分離しました。
URLに基づいて適切な専用関数へ処理を振り分ける設計になっています。


📝 今後の展望
・LINE通知機能: 画面を見なくても、スマホに通知が来るようにしたい。
・クラウドデプロイ: 自分のPCを落としても24時間監視できるようにしたい。
・推移グラフ: 価格の変動履歴をグラフで表示する機能を追加したい。


