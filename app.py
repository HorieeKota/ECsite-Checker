import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import json
import logic

# 設定
CONFIG_FILE = "config.json"

st.title("📦 Amazon ＆ 楽天 監視パネル")

# 1. config.json の読み込み
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
    items = config.get("check_list", [])
    st.write(f"監視対象: {len(items)} 件")
except FileNotFoundError:
    st.error("config.json が見つかりません！")
    items = []

# 2. 更新ボタン
if st.button("今すぐチェック開始"):
    
    # プログレスバー（進捗）
    progress_bar = st.progress(0)
    
    for i, item in enumerate(items):
        st.subheader(f"🔍 {item['name']} を確認中...")
        
        # logic.py の関数を呼び出す
        # check_site に変えることで、Amazonか楽天かを自動判断します
        res = logic.check_site(item['url'], item['check_type'])

        # 結果の判定と表示
        if res["status"] == "success":
            current_val = res["value"]
            target_val = item['target_value']
            
            # --- 価格の判定 ---
            if item['check_type'] == "PRICE":
                st.write(f"現在価格: **{current_val}円** (目標: {target_val}円以下)")
                if current_val <= target_val:
                    st.success("🎉 値下がりしています！買い時です！")
                else:
                    st.warning("まだ目標より高いです。")

            # --- 在庫の判定 ---
            elif item['check_type'] == "STOCK":
                st.write(f"現在の状況: **{current_val}**")
                if target_val in current_val:
                    st.success("🎉 在庫条件と一致しました！")
                else:
                    st.warning("まだ条件と一致しません。")
        else:
            st.error(f"取得失敗: {res['message']}")
        
        # 進捗更新
        progress_bar.progress((i + 1) / len(items))
        st.divider() # 線を引く

    st.success("✅ 全てのチェックが完了しました")