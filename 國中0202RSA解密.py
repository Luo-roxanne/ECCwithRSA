import streamlit as st
import base64
import math

def rsa_decrypt_logic(e, n, d, b64_input):
    """完全移植自國中0202RSA解密.py的邏輯"""
    # 1. 自動推算參數
    k = math.floor(math.log2(n))
    c_bits_len = math.ceil(math.log2(n))

    # 2. Base64 轉回位元串
    byte_data = base64.b64decode(b64_input)
    all_bits = "".join([bin(b)[2:].zfill(8) for b in byte_data])

    # 3. 每 c_bits_len 取出一組密文 C 並解密
    original_bits = ""
    for i in range(0, (len(all_bits) // c_bits_len) * c_bits_len, c_bits_len):
        chunk = all_bits[i:i+c_bits_len]
        if len(chunk) < c_bits_len: 
            break
        c = int(chunk, 2)
        m = pow(c, d, n)
        original_bits += bin(m)[2:].zfill(k)

    # 4. 位元串轉回 ASCII 字元 (每 7 位元一組)
    decoded_str = ""
    for i in range(0, (len(original_bits) // 7) * 7, 7):
        char_bits = original_bits[i:i+7]
        char_code = int(char_bits, 2)
        if char_code == 0: 
            continue 
        decoded_str += chr(char_code)
    
    return decoded_str

# --- Streamlit 介面 ---
st.set_page_config(page_title="RSA 大數解密工具", page_icon="🔑")

st.title("🔑 RSA 大數解密系統 (支援超長金鑰)")
st.markdown("針對科展需求優化，支援 1024-bit 以上的 RSA 金鑰輸入。")

# 側邊欄輸入金鑰 (改用 text_input 以支援超大整數)
with st.sidebar:
    st.header("⚙️ 金鑰設定")
    e_str = st.text_input("請輸入公開金鑰 e", placeholder="貼上超長數字...")
    n_str = st.text_input("請輸入公開金鑰 n", placeholder="貼上超長數字...")
    d_str = st.text_input("請輸入秘密金鑰 d", placeholder="貼上超長數字...", type="password")

# 主畫面輸入密文
st.subheader("📋 密文解碼")
b64_text = st.text_area("請貼上 Base64 密文串", height=150)

if st.button("🚀 執行 RSA 大數解密"):
    if e_str and n_str and d_str and b64_text:
        try:
            # 將文字轉回大整數
            e_val = int(e_str.strip())
            n_val = int(n_str.strip())
            d_val = int(d_str.strip())
            
            with st.spinner("正在處理大數模數冪運算..."):
                result = rsa_decrypt_logic(e_val, n_val, d_val, b64_text)
            
            if result:
                st.success("✅ 解密還原成功！")
                st.code(result, language=None)
            else:
                st.warning("⚠️ 解密結果為空，請確認參數。")
                
        except ValueError:
            st.error("❌ 格式錯誤：金鑰欄位只能包含數字。")
        except Exception as err:
            st.error(f"❌ 解密失敗：{err}")
    else:
        st.warning("⚠️ 請完整填寫 e, n, d 以及密文。")

st.divider()
st.caption("支援高精確度整數運算，不受 Python 浮點數長度限制。")
