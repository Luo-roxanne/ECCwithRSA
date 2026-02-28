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
    # 依照你的檔案邏輯：根據 c_bits_len 拆分
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
            continue  # 忽略補位的 0
        decoded_str += chr(char_code)
    
    return decoded_str

# --- Streamlit 介面 ---
st.set_page_config(page_title="RSA 位元流解密工具", page_icon="🔑")

st.title("🔑 RSA 位元流解密系統")
st.markdown("此工具完全採用你提供的 **RSA 分段位元解密** 邏輯。")

# 側邊欄輸入金鑰
with st.sidebar:
    st.header("⚙️ 金鑰設定")
    e_val = st.number_input("請輸入公開金鑰 e", value=0, step=1)
    n_val = st.number_input("請輸入公開金鑰 n", value=0, step=1)
    d_val = st.number_input("請輸入秘密金鑰 d", value=0, step=1)

# 主畫面輸入密文
st.subheader("📋 密文解碼")
b64_text = st.text_area("請貼上 Base64 密文串", height=150, placeholder="例如: sYp4A...")

if st.button("🚀 執行 RSA 解密"):
    if e_val and n_val and d_val and b64_text:
        try:
            with st.spinner("正在進行模數運算與位元還原..."):
                result = rsa_decrypt_logic(e_val, n_val, d_val, b64_text)
            
            if result:
                st.success("✅ 解密還原成功！")
                st.info(f"**解密結果：** {result}")
                
                # 科展分析數據
                k_val = math.floor(math.log2(n_val))
                st.write(f"---")
                st.caption(f"系統分析：此加密採用了 {k_val}-bit 分段區塊。")
            else:
                st.warning("⚠️ 解密結果為空，請確認金鑰與密文是否成對。")
                
        except Exception as err:
            st.error(f"❌ 解密失敗：格式錯誤或參數不正確。")
            st.caption(f"錯誤訊息: {err}")
    else:
        st.warning("⚠️ 請完整輸入 e, n, d 以及密文。")

st.divider()
st.caption("本系統依照 RSA 數學原理 $M = C^d \pmod{n}$ 進行位元流還原。")
