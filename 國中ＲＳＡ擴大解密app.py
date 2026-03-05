import streamlit as st
import base64
import math
import pandas as pd  # 用於呈現漂亮的表格

# --- Streamlit 網頁介面設定 ---
st.set_page_config(page_title="RSA 秘密資訊還原系統", page_icon="🔓", layout="wide")

st.title("🔓 RSA 秘密資訊還原系統 — 學生資料庫模式")
st.write("利用私鑰 (d, n) 進行模冪運算，並將還原後的長字串自動解析為編號表格。")

# 1. 側邊欄：金鑰輸入
st.sidebar.header("🔑 私鑰參數輸入")
d_input = st.sidebar.text_area("秘密金鑰 (d):", height=150)
n_input = st.sidebar.text_area("模數 (n):", height=150)

# 2. 主畫面：密文輸入與解析設定
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📦 密文輸入")
    cipher_base64 = st.text_area("請貼上 Base64 密文:", height=100)

with col2:
    st.subheader("📋 格式解析設定")
    st.info("請設定每一位學生資料的總長度，以便系統自動拆解與編號。")
    # 範例：手機(10) + 身分證(10) + 生日(7) = 27 字元
    split_len = st.number_input("每筆學生資料長度 (字元數):", min_value=1, value=27)

# 3. 執行解密
if st.button("🚀 執行解密並產出表格"):
    if not d_input or not n_input or not cipher_base64:
        st.error("請完整填寫金鑰 d、n 與密文！")
    else:
        try:
            d = int(d_input.strip())
            n = int(n_input.strip())
            
            # --- 核心解密運算 ---
            decoded_bytes = base64.b64decode(cipher_base64)
            full_bit_stream = "".join([bin(b)[2:].zfill(8) for b in decoded_bytes])
            
            c_bits_len = math.ceil(math.log2(n))
            k = math.floor(math.log2(n))
            
            c_list = [int(full_bit_stream[i:i+c_bits_len], 2) for i in range(0, (len(full_bit_stream) // c_bits_len) * c_bits_len, c_bits_len)]
            
            with st.spinner('正在進行大數運算還原中...'):
                m_list = [pow(c, d, n) for c in c_list]
            
            decrypted_bit_stream = "".join([bin(m)[2:].zfill(k) for m in m_list])
            
            # 轉回文字
            raw_text = ""
            for i in range(0, (len(decrypted_bit_stream) // 7) * 7, 7):
                char_code = int(decrypted_bit_stream[i:i+7], 2)
                if char_code == 0: continue
                raw_text += chr(char_code)
            
            # --- 表格化邏輯 ---
            st.success("🔓 解密還原成功！")
            
            # 將長字串切割成清單
            student_data = [raw_text[i:i+split_len] for i in range(0, len(raw_text), split_len) if len(raw_text[i:i+split_len]) == split_len]
            
            if student_data:
                # 建立 DataFrame 增加編號
                df = pd.DataFrame({
                    "序號": range(1, len(student_data) + 1),
                    "原始加密資訊": student_data
                })
                
                # 如果你想更精細，可以根據固定位置再拆分手機、身分證
                # 例如：手機=前10碼, 身分證=中間10碼, 生日=最後
                st.subheader("📊 解析結果表格")
                st.table(df) # 或者使用 st.dataframe(df) 可以互動縮放
                
                st.write(f"💡 系統偵測到共 **{len(student_data)}** 筆完整的學生紀錄。")
            else:
                st.warning("解密出的字串長度不足以進行分塊，請檢查解析長度設定。")
                st.text(f"原始還原文字：{raw_text}")

        except Exception as e:
            st.error(f"解析失敗，請確保金鑰正確且格式一致。錯誤訊息：{e}")

# 教育意義區
st.divider()
st.write("🧪 **科展演示建議**：你可以展示當 $n$ 或 $d$ 修改了任何一個數字，整個表格會瞬間變成亂碼，這能證明 RSA 在『資料完整性』上的嚴謹性。")
