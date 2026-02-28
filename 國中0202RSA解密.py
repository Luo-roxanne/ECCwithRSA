import streamlit as st
import base64
import math
import pandas as pd

def days_to_date(n_day_str):
    """將一年中的第 n 天還原為 MMDD 格式 (引用自你的原始邏輯)"""
    month_days = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    try:
        total_days = int(n_day_str)
        m = 1
        while m < len(month_days) and total_days > month_days[m]:
            total_days -= month_days[m]
            m += 1
        return f"{m:02d}{total_days:02d}"
    except:
        return "Unknown"

def rsa_batch_decrypt(n, d, b64_input):
    """核心 RSA 位元流解密邏輯"""
    # 1. 自動推算區塊參數
    k = math.floor(math.log2(n))           
    c_bits_len = math.ceil(math.log2(n))    

    # 2. Base64 轉位元串
    try:
        byte_data = base64.b64decode(b64_input)
        all_bits = "".join([bin(b)[2:].zfill(8) for b in byte_data])
        
        # 3. 逐塊解密：M = C^d mod n
        m_bits_stream = ""
        for i in range(0, (len(all_bits) // c_bits_len) * c_bits_len, c_bits_len):
            chunk = all_bits[i:i+c_bits_len]
            c = int(chunk, 2)
            m = pow(c, d, n)
            m_bits_stream += bin(m)[2:].zfill(k)
        
        # 4. 位元流轉 ASCII (7-bit)
        decoded_text = ""
        for i in range(0, (len(m_bits_stream) // 7) * 7, 7):
            char_code = int(m_bits_stream[i:i+7], 2)
            if char_code == 0: continue 
            decoded_text += chr(char_code)
        
        return decoded_text
    except Exception as e:
        return None

# --- Streamlit 介面 ---
st.set_page_config(page_title="RSA 班級資料解密系統", layout="wide")

st.title("🔐 RSA 班級個資自動還原系統")
st.markdown("本系統採用 **RSA 位元流加密技術**，支援大數金鑰與生日天數自動換算。")

# 側邊欄設定
with st.sidebar:
    st.header("🔑 金鑰參數設定")
    e_str = st.text_input("公開金鑰 e (大數)", placeholder="貼上 e...")
    n_str = st.text_input("公開金鑰 n (大數)", placeholder="貼上 n...")
    d_str = st.text_input("秘密金鑰 d (大數)", type="password", placeholder="貼上 d...")
    st.info("💡 解密僅需 n 與 d，但保留 e 欄位以符合對稱性。")

# 主畫面輸入
b64_cipher = st.text_area("📋 請貼上 Base64 密文串", height=150)

if st.button("🚀 開始執行全班解密"):
    if n_str and d_str and b64_cipher:
        try:
            # 轉換大整數
            n_val = int(n_str.strip())
            d_val = int(d_str.strip())
            
            with st.spinner("🔒 正在解碼位元流並還原資料結構..."):
                full_text = rsa_batch_decrypt(n_val, d_val, b64_cipher)
            
            if full_text:
                # 5. 資料表格化 (依照每人 23 碼邏輯：10電話 + 10身分證 + 3天數)
                student_data = []
                for i in range(0, (len(full_text) // 23) * 23, 23):
                    chunk = full_text[i:i+23]
                    phone = chunk[0:10]
                    id_card = chunk[10:20]
                    day_n = chunk[20:23]
                    
                    student_data.append({
                        "座號": (i // 23) + 1,
                        "手機號碼": phone,
                        "身分證字號": id_card,
                        "生日 (MMDD)": days_to_date(day_n)
                    })
                
                if student_data:
                    st.success(f"✅ 成功！已識別出 {len(student_data)} 位同學資料。")
                    df = pd.DataFrame(student_data)
                    st.table(df) # 使用 table 避免數字格式跑掉
                else:
                    st.warning("⚠️ 解碼後的長度不足 23 碼。")
                    st.code(full_text)
            else:
                st.error("❌ 解密失敗，請檢查金鑰與密文。")
                
        except ValueError:
            st.error("❌ 金鑰欄位必須是純數字。")
    else:
        st.warning("⚠️ 請完整填寫金鑰與密文。")

st.divider()
st.caption("技術原理：$M = C^d \pmod{n}$ 位元流還原 | 7-bit ASCII 編碼")
