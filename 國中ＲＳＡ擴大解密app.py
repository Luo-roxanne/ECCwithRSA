import streamlit as st
import base64
import math
import pandas as pd

# --- 設定網頁標題與佈局 ---
st.set_page_config(page_title="RSA 學生資安管理系統", page_icon="📑", layout="wide")

st.title("📑 RSA 學生個人資料還原系統")
st.write("利用 RSA 私鑰解密並自動解析「手機、身分證、生日(MMDD)」欄位。")

# 1. 側邊欄：輸入解密必要的私鑰參數
st.sidebar.header("🔑 私鑰金鑰配對")
d_input = st.sidebar.text_area("秘密金鑰 (d):", height=150, help="請貼上加密端產生的 d")
n_input = st.sidebar.text_area("模數 (n):", height=150, help="請貼上加密端產生的 n")

# 2. 主畫面：密文與格式設定
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📦 密文貼入")
    cipher_base64 = st.text_area("請貼上加密後的 Base64 密文:", height=120)

with col2:
    st.subheader("⚙️ 欄位解析設定")
    st.info("系統預設：手機(10碼) + 身分證(10碼) + 生日(4碼) = 共24碼")
    phone_len = 10
    id_len = 10
    bday_len = 4
    total_unit_len = phone_len + id_len + bday_len

# 3. 解密與表格化邏輯
if st.button("🚀 執行精確解密"):
    if not d_input or not n_input or not cipher_base64:
        st.error("請檢查 d, n 與密文是否皆已輸入！")
    else:
        try:
            d = int(d_input.strip())
            n = int(n_input.strip())
            
            # --- 核心大數解密 ---
            decoded_bytes = base64.b64decode(cipher_base64)
            full_bit_stream = "".join([bin(b)[2:].zfill(8) for b in decoded_bytes])
            
            c_bits_len = math.ceil(math.log2(n))
            k = math.floor(math.log2(n))
            
            c_list = [int(full_bit_stream[i:i+c_bits_len], 2) for i in range(0, (len(full_bit_stream) // c_bits_len) * c_bits_len, c_bits_len)]
            
            with st.spinner('正在進行 RSA 模冪運算還原中...'):
                m_list = [pow(c, d, n) for c in m_list] if 'm_list' in locals() else [pow(c, d, n) for c in c_list]
            
            decrypted_bit_stream = "".join([bin(m)[2:].zfill(k) for m in m_list])
            
            # 轉回 ASCII 文字
            raw_text = ""
            for i in range(0, (len(decrypted_bit_stream) // 7) * 7, 7):
                char_code = int(decrypted_bit_stream[i:i+7], 2)
                if char_code == 0: continue
                raw_text += chr(char_code)
            
            # --- 欄位拆解邏輯 ---
            st.success("🔓 解密還原成功！資料解析如下：")
            
            # 依照每 24 碼切分
            records = []
            for i in range(0, len(raw_text), total_unit_len):
                chunk = raw_text[i : i + total_unit_len]
                if len(chunk) == total_unit_len:
                    records.append({
                        "手機號碼": chunk[0:10],
                        "身分證字號": chunk[10:20],
                        "生日 (MMDD)": chunk[20:24]
                    })
            
            if records:
                # 建立 DataFrame 並設定索引從 1 開始
                df = pd.DataFrame(records)
                df.index = df.index + 1
                df.index.name = "序號"
                
                # 呈現表格
                st.table(df)
                st.balloons()
            else:
                st.warning("還原文字長度不符欄位設定，請確認加密時的資料順序。")
                st.text(f"解密原文：{raw_text}")

        except Exception as e:
            st.error(f"解析發生錯誤：{e}")

# 教育區域
st.divider()
st.caption("🔍 科展筆記：本程式展示了非對稱加密如何保護結構化資料。在解密端，我們利用程式邏輯將一連串看似隨機的數字還原為具有商業價值的表格資料。")
