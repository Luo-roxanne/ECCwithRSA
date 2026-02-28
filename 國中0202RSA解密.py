import streamlit as st
import base64
import math
import pandas as pd

def rsa_decrypt_logic(e, n, d, b64_input):
    """
    完全依照國中0202RSA解密.py邏輯
    修正：確保位元流讀取到最末端，不遺漏最後兩位學生
    """
    # 1. 自動推算參數
    k = math.floor(math.log2(n))       # 明文區塊位元數
    c_bits_len = math.ceil(math.log2(n)) # 密文區塊位元數

    # 2. Base64 轉回位元串
    try:
        byte_data = base64.b64decode(b64_input)
        all_bits = "".join([bin(b)[2:].zfill(8) for b in byte_data])
    except:
        return "B64_ERROR"

    # 3. 逐塊解密
    original_bits = ""
    # 修正：使用 len(all_bits) - c_bits_len + 1 確保最後一塊只要夠長就讀取
    for i in range(0, len(all_bits), c_bits_len):
        chunk = all_bits[i:i+c_bits_len]
        if len(chunk) < c_bits_len:
            # 如果剩餘位元不足一個密文區塊，可能是 Base64 補位，跳過
            break
        
        c = int(chunk, 2)
        # 核心解密：m = c^d mod n
        m = pow(c, d, n)
        # 還原為 k 位元並補齊
        original_bits += bin(m)[2:].zfill(k)

    # 4. 位元串轉回 ASCII (每 7 bits 一個字元)
    decoded_str = ""
    for i in range(0, len(original_bits), 7):
        char_bits = original_bits[i:i+7]
        if len(char_bits) < 7: break
        char_code = int(char_bits, 2)
        if char_code == 0: continue 
        decoded_str += chr(char_code)
    
    return decoded_str

# --- Streamlit 介面 ---
st.set_page_config(page_title="RSA 全班資料還原工具", layout="wide")

st.title("🔐 RSA 26人全班資料解密系統")
st.markdown("已修正位元偏移邏輯，支援超長整數 $e, n, d$ 輸入。")

# 側邊欄輸入
with st.sidebar:
    st.header("🔑 RSA 金鑰密鑰")
    # 使用 text_input 接收超長數字字串
    e_str = st.text_input("請輸入公開金鑰 e")
    n_str = st.text_input("請輸入公開金鑰 n")
    d_str = st.text_input("請輸入秘密金鑰 d", type="password")
    st.write("---")
    st.info("💡 提示：若 26 人資料不齊，請檢查加密時的補位設定。")

# 主畫面
b64_cipher = st.text_area("📋 請貼上 Base64 密文", height=200)

if st.button("🚀 執行全量解密"):
    if e_str and n_str and d_str and b64_cipher:
        try:
            # 轉換為大整數
            e_val = int("".join(e_str.split())) # 去除空格
            n_val = int("".join(n_str.split()))
            d_val = int("".join(d_str.split()))
            
            with st.spinner("🔒 正在進行大數模冪運算與位元還原..."):
                full_raw_text = rsa_decrypt_logic(e_val, n_val, d_val, b64_cipher)
            
            if full_raw_text == "B64_ERROR":
                st.error("❌ Base64 格式錯誤。")
            elif full_raw_text:
                # 5. 強制以 24 碼為單位切分 (全班 26 人)
                student_data = []
                # 修正：不使用嚴格整除，確保讀取到字串末尾
                for i in range(0, len(full_raw_text), 24):
                    person = full_raw_text[i:i+24]
                    if len(person) < 24: continue # 剩餘不足 24 碼的捨棄
                    
                    student_data.append({
                        "座號": (i // 24) + 1,
                        "手機號碼": person[0:10],
                        "身分證字號": person[10:20],
                        "出生月日": person[20:24]
                    })
                
                if student_data:
                    st.success(f"✅ 解密成功！偵測到 {len(student_data)} 位同學資料。")
                    df = pd.DataFrame(student_data)
                    st.table(df) # table 格式最能防止數字變形
                else:
                    st.warning("⚠️ 解碼出的字元不足以組成一位同學的資料(24碼)。")
                    st.text("原始解碼預覽：")
                    st.code(full_raw_text)
            else:
                st.error("❌ 解密結果為空，請檢查金鑰。")
                
        except ValueError:
            st.error("❌ 金鑰格式錯誤，請確保只輸入數字。")
        except Exception as err:
            st.error(f"❌ 執行錯誤：{err}")
    else:
        st.warning("⚠️ 請完整填寫 e, n, d 與密文。")

st.divider()
st.caption("本程式針對 26 人批次加密產生的 ASCII 位元流進行優化還原。")
