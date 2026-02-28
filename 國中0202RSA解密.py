import streamlit as st
import base64
import math
import pandas as pd

def rsa_batch_decrypt(e, n, d, b64_input):
    """
    完全採用「國中0202RSA解密.py」的位元流邏輯
    e: 雖然解密公式不用，但保留作為參數輸入
    """
    # 1. 核心參數計算 (k=明文區塊, c_bits_len=密文區塊)
    k = math.floor(math.log2(n))
    c_bits_len = math.ceil(math.log2(n))

    # 2. Base64 密文轉回位元串
    try:
        byte_data = base64.b64decode(b64_input)
        all_bits = "".join([bin(b)[2:].zfill(8) for b in byte_data])
    except:
        return "B64_ERROR"

    # 3. 逐塊讀取密文並解密：M = C^d mod n
    original_bits = ""
    # 使用迴圈遍歷所有密文區塊
    for i in range(0, (len(all_bits) // c_bits_len) * c_bits_len, c_bits_len):
        chunk = all_bits[i:i+c_bits_len]
        if len(chunk) < c_bits_len: break
        
        c = int(chunk, 2)
        m = pow(c, d, n) # 大數模冪運算
        original_bits += bin(m)[2:].zfill(k)

    # 4. 位元流轉回 ASCII 字元 (7-bit 系統)
    decoded_text = ""
    for i in range(0, (len(original_bits) // 7) * 7, 7):
        char_bits = original_bits[i:i+7]
        char_code = int(char_bits, 2)
        if char_code == 0: continue # 忽略補位的 0
        decoded_text += chr(char_code)
    
    return decoded_text

# --- Streamlit 介面設計 ---
st.set_page_config(page_title="RSA 班級資料還原系統", layout="wide")

st.title("🔐 RSA 批次解密與表格自動還原")
st.markdown("請輸入正確的 **e, n, d** 與 **Base64 密文**。系統將自動計算區塊大小並還原全班名單。")

# 側邊欄：輸入大數金鑰
with st.sidebar:
    st.header("🔑 RSA 金鑰配置")
    # 使用 text_input 支援超長數字輸入
    e_str = st.text_input("請輸入公開金鑰 e (大數)", placeholder="請貼上 e...")
    n_str = st.text_input("請輸入公開金鑰 n (大數)", placeholder="請貼上 n...")
    d_str = st.text_input("請輸入秘密金鑰 d (私鑰)", placeholder="請貼上 d...", type="password")
    st.divider()
    st.info("💡 Python 支援無限長度整數，直接貼上長數字即可。")

# 主畫面：輸入密文
b64_cipher = st.text_area("📋 請貼上 Base64 加密字串", height=200, placeholder="例如: sYp4A2...")

if st.button("🚀 執行全班解密並產生表格"):
    # 檢查是否有空格或換行
    e_str = e_str.strip()
    n_str = n_str.strip()
    d_str = d_str.strip()
    
    if e_str and n_str and d_str and b64_cipher:
        try:
            # 轉換為整數 (大數運算)
            e_val = int(e_str)
            n_val = int(n_str)
            d_val = int(d_str)
            
            with st.spinner("🔒 正在還原位元流並重新排版中..."):
                raw_decoded = rsa_batch_decrypt(e_val, n_val, d_val, b64_cipher)
            
            if raw_decoded == "B64_ERROR":
                st.error("❌ Base64 格式錯誤，請檢查密文是否複製完整。")
            elif raw_decoded:
                # 5. 自動排版：每 24 碼切分為一位同學
                # (10碼電話 + 10碼身分證 + 4碼生日)
                student_list = []
                for i in range(0, (len(raw_decoded) // 24) * 24, 24):
                    chunk = raw_decoded[i:i+24]
                    student_list.append({
                        "座號": (i // 24) + 1,
                        "手機號碼": chunk[0:10],
                        "身分證字號": chunk[10:20],
                        "出生月日": chunk[20:24]
                    })
                
                if student_list:
                    st.success(f"✅ 解密完成！成功還原 {len(student_list)} 位同學資料。")
                    df = pd.DataFrame(student_list)
                    # 使用 st.table 確保數字格式不會跑掉 (例如 09 變成 9)
                    st.table(df)
                else:
                    st.warning("⚠️ 解碼後的長度不足 24 碼，無法構成一位學生的資料。")
                    st.text("原始解碼內容預覽：")
                    st.code(raw_decoded)
            else:
                st.error("❌ 解密失敗。請確認金鑰與密文是否成對。")
                
        except ValueError:
            st.error("❌ 錯誤：金鑰欄位只能輸入純數字，不可有英文字母或特殊符號。")
        except Exception as err:
            st.error(f"❌ 發生非預期錯誤：{err}")
    else:
        st.warning("⚠️ 請完整填寫 e, n, d 以及密文欄位。")

st.divider()
st.caption("技術支援：本系統採用 7-bit ASCII 位元流分段處理技術。")
