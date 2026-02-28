import streamlit as st
import base64
import math
import pandas as pd

def rsa_decrypt_logic(n, d, b64_input):
    """依照國中0202RSA解密.py邏輯，並強化位元流讀取完整性"""
    # 1. 自動推算參數 (這是最關鍵的，必須與加密端完全一致)
    k = math.floor(math.log2(n))
    c_bits_len = math.ceil(math.log2(n))

    # 2. Base64 轉回位元串
    try:
        byte_data = base64.b64decode(b64_input)
        # 將 byte 轉成完整的 8 位元字串
        all_bits = "".join([bin(b)[2:].zfill(8) for b in byte_data])
    except:
        return "ERROR_B64"

    # 3. 逐塊讀取密文 C (包含剩餘不足一塊的部分處理)
    original_bits = ""
    # 這裡放寬判斷，確保盡可能讀取到最後一個區塊
    for i in range(0, len(all_bits), c_bits_len):
        chunk = all_bits[i:i+c_bits_len]
        if len(chunk) < c_bits_len:
            # 如果剩餘位元不足一個加密區塊長度，通常是末尾補位，予以跳過
            break
        
        c = int(chunk, 2)
        # 核心解密：M = C^d mod n
        try:
            m = pow(c, d, n)
            # 還原為 k 位元的明文段
            original_bits += bin(m)[2:].zfill(k)
        except:
            continue

    # 4. 位元串轉回 ASCII 字元 (每 7 位元一組)
    decoded_str = ""
    for i in range(0, len(original_bits), 7):
        char_bits = original_bits[i:i+7]
        if len(char_bits) < 7: break
        char_code = int(char_bits, 2)
        if char_code == 0: continue # 忽略末端填充的空位元
        decoded_str += chr(char_code)
    
    return decoded_str

# --- Streamlit 介面介面 ---
st.set_page_config(page_title="RSA 班級資料全解密", page_icon="🔑", layout="wide")

st.title("🔑 RSA 班級個資全解密系統")
st.markdown("本系統已修正位元流切分邏輯，確保 26 位學生資料完整還原。")

# 側邊欄輸入金鑰
with st.sidebar:
    st.header("⚙️ RSA 金鑰設定 (請輸入大數)")
    e_str = st.text_input("請輸入公開金鑰 e", placeholder="輸入長數字 e...")
    n_str = st.text_input("請輸入公開金鑰 n", placeholder="輸入長數字 n...")
    d_str = st.text_input("請輸入秘密金鑰 d", placeholder="輸入長數字 d...", type="password")
    st.info(f"💡 e 雖然不參與 $M=C^d \pmod n$ 運算，但保留欄位供校驗使用。")

# 主畫面
b64_text = st.text_area("📋 請貼上 Base64 密文串", height=150)

if st.button("🚀 執行全班資料還原"):
    if n_str and d_str and b64_text:
        try:
            # 轉換為大整數
            n_val = int(n_str.strip())
            d_val = int(d_str.strip())
            
            with st.spinner("🔒 正在解碼 7-bit ASCII 位元流..."):
                full_raw_data = rsa_decrypt_logic(n_val, d_val, b64_text)
            
            if full_raw_data == "ERROR_B64":
                st.error("❌ Base64 格式錯誤，請檢查密文是否複製完整。")
            elif full_raw_data:
                # 5. 表格化處理 (每 24 碼為一人)
                student_list = []
                # 使用 len(full_raw_data) 判斷，確保最後兩位不被漏掉
                for i in range(0, len(full_raw_data), 24):
                    chunk = full_raw_data[i:i+24]
                    if len(chunk) < 24: continue # 不足 24 碼的不算一人
                    
                    student_list.append({
                        "座號": (i // 24) + 1,
                        "手機號碼": chunk[0:10],
                        "身分證字號": chunk[10:20],
                        "出生月日": chunk[20:24]
                    })
                
                if student_list:
                    st.success(f"✅ 解密完成！成功還原 {len(student_list)} 位同學資料。")
                    df = pd.DataFrame(student_list)
                    st.table(df) # 使用 st.table 確保手機號碼與身分證不會被科學記號簡化
                else:
                    st.warning("⚠️ 解密成功但格式不符。")
                    st.write("**原始解密內容預覽：**")
                    st.code(full_raw_data)
            else:
                st.error("❌ 解碼結果為空。請確認 n 與 d 是否與加密時一致。")
                
        except ValueError:
            st.error("❌ 金鑰格式錯誤，請確保輸入的是純數字。")
    else:
        st.warning("⚠️ 請填寫金鑰 n, d 與密文。")

st.divider()
st.caption("提示：若結果仍為亂碼，請確認加密端與解密端的 n (模數) 是否完全相同。")
