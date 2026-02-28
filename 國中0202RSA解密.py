import streamlit as st
import base64
import math
import pandas as pd

def rsa_batch_decrypt(e, n, d, b64_input):
    """完全移植自國中0202RSA解碼邏輯，但改為動態長度以支援全班資料"""
    # 1. 自動推算參數 (依據 n 的大小決定區塊位元數)
    k = math.floor(math.log2(n))       
    c_bits_len = math.ceil(math.log2(n)) 

    # 2. Base64 轉回位元串
    try:
        byte_data = base64.b64decode(b64_input)
        all_bits = "".join([bin(b)[2:].zfill(8) for b in byte_data])
    except:
        return "B64_ERROR"

    # 3. 每 c_bits_len 取出一組密文並用 d 解密還原為 k 位元
    original_bits = ""
    for i in range(0, (len(all_bits) // c_bits_len) * c_bits_len, c_bits_len):
        chunk = all_bits[i:i+c_bits_len]
        if len(chunk) < c_bits_len: break
        c = int(chunk, 2)
        # 核心解密公式：m = c^d mod n
        m = pow(c, d, n)
        original_bits += bin(m)[2:].zfill(k)

    # 4. 將位元流轉回 ASCII 字元 (修正：不再只取前 70 位，而是全部取回)
    # 每個字元佔 7 bits
    full_text = ""
    for i in range(0, (len(original_bits) // 7) * 7, 7):
        char_bits = original_bits[i:i+7]
        char_code = int(char_bits, 2)
        if char_code == 0: continue # 忽略補位用的空位元
        full_text += chr(char_code)
    
    return full_text

# --- Streamlit 網頁介面 ---
st.set_page_config(page_title="RSA 全班資料還原系統", layout="wide")

st.title("🔐 RSA 批次解密與表格還原系統")
st.markdown("本程式採用 **位元流分段解密** 技術，支援超大金鑰輸入。")

# 側邊欄：輸入大數金鑰 (使用 text_input 避免溢位)
with st.sidebar:
    st.header("🔑 RSA 金鑰配置")
    e_str = st.text_input("請輸入公開金鑰 e (大數)")
    n_str = st.text_input("請輸入公開金鑰 n (大數)")
    d_str = st.text_input("請輸入秘密金鑰 d (大數)", type="password")
    st.info("💡 提示：RSA 金鑰通常超過 100 位數，請直接貼上全文。")

# 主畫面：輸入密文
b64_cipher = st.text_area("📋 請貼上全班 Base64 密文", height=200)

if st.button("🚀 執行全班資料解鎖"):
    if e_str and n_str and d_str and b64_cipher:
        try:
            # 將文字轉為 Python 無限長度整數
            e_val = int(e_str.strip())
            n_val = int(n_str.strip())
            d_val = int(d_str.strip())
            
            with st.spinner("正在進行大數模數冪運算..."):
                decoded_raw = rsa_batch_decrypt(e_val, n_val, d_val, b64_cipher)
            
            if decoded_raw == "B64_ERROR":
                st.error("❌ Base64 格式錯誤，請檢查密文是否完整。")
            elif decoded_raw:
                # 5. 自動將 624 碼還原為 26 位學生的表格 (每人 24 碼)
                student_data = []
                for i in range(0, (len(decoded_raw) // 24) * 24, 24):
                    person = decoded_raw[i:i+24]
                    student_data.append({
                        "座號": (i // 24) + 1,
                        "電話號碼": person[0:10],
                        "身分證字號": person[10:20],
                        "出生月日": person[20:24]
                    })
                
                if student_data:
                    st.success(f"✅ 成功還原 {len(student_data)} 位學生資料！")
                    df = pd.DataFrame(student_data)
                    # 使用 st.table 顯示，防止手機號碼被轉成科學記號
                    st.table(df)
                else:
                    st.warning("⚠️ 解碼出的字串長度不足。")
                    st.code(decoded_raw)
            else:
                st.error("❌ 無法還原資料，請確認金鑰對(n, d)是否正確。")
                
        except ValueError:
            st.error("❌ 金鑰欄位必須是純數字。")
        except Exception as err:
            st.error(f"❌ 發生非預期錯誤: {err}")
    else:
        st.warning("⚠️ 請完整填寫 e, n, d 以及密文。")

st.divider()
st.caption("技術原理：依據 n 決定區塊位元 k，將密文 C 透過 $m = c^d \pmod{n}$ 還原後，以 7-bit ASCII 重新組譯明文。")
