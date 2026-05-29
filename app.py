import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. APIキーの設定
# ==========================================
GOOGLE_API_KEY = "AIzaSyC1bLg0NY_igMhMBQhUuRvMrmEGLdodQjU"  
genai.configure(api_key=GOOGLE_API_KEY)

# ==========================================
# 2. データの読み込みとシステムプロンプトの構築
# ==========================================
def load_knowledge_base():
    try:
        with open("kashima_data.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "エラー: kashima_data.txt が見つかりません。"

kashima_data = load_knowledge_base()

SYSTEM_PROMPT = f"""
あなたはJリーグサポーターの遠征をトータルでサポートする、経験豊富で頼れる専属ナビゲーター「サポナビ」です。
既存の乗換アプリのような「駅名と時間の単純な羅列」や、一般的なAIのような機械的な長文は絶対に避けてください。
遠征の楽しさと苦労を誰よりも理解しているサポ仲間として、優しくフレンドリーな口調（「〜だよ！」「〜だから気をつけてね！」）で話しかけてください。

【最重要コンセプト：一番イライラしない、疲れないサポート】
ユーザーから出発駅を伝えられたら、以下の「攻略データ」をベースに、単なる移動経路だけでなく「トータルで一番疲れないための立ち回り」を以下のセットで回答してください。

1. 【寄り添い】既存アプリの検索（最短ルート）に潜む罠（混雑や本数の少なさ）を指摘し、共感する。
2. 【ルート表記】「駅名(路線) → 駅名...」のフォーマットで見やすく提示する。
3. 【買い出し・構内移動】乗り換えで歩かないための車両位置や、無人駅トラップを避けるための「成田駅での買い出し推奨」などを具体的にアドバイスする。
4. 【外部連携】正確なダイヤでの失敗を防ぐため、最後に必ず「具体的な電車の時間は、Googleマップや乗換アプリで『〇〇駅〜〇〇駅』で検索して確認してみてね！」と誘導する。

【鹿島スタジアム攻略データ】
{kashima_data}
"""

# ==========================================
# 3. Streamlit UIの構築
# ==========================================
st.set_page_config(page_title="サポナビ", page_icon="⚽")
st.title("⚽ サポナビ AI")
st.write("既存アプリとは一線を画す、「一番イライラしない、疲れないルート」を提案する専属ナビゲーター。")
st.caption("※現在はMVPデモ版のため「カシマサッカースタジアム」への案内のみ対応しています。")

# 現在の最新モデル「gemini-2.5-flash」を使用
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = [
        {"role": "assistant", "content": "お疲れ様！今度の遠征はどこから出発する？一番疲れない最高のルートと立ち回りを案内するよ！"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("例：柏駅から鹿島神宮に行きたい"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"エラーが発生しました。詳細: {e}")