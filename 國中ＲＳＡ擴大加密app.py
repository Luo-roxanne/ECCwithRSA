import streamlit as st
import base64
import math
import secrets

# --- 核心 RSA 數學邏輯 ---
def is_prime(n, k=5):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = secrets.randbelow(n - 4) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def generate_prime(bits):
    while True:
        p = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(p): return p

# --- Streamlit 網頁介面 ---
st.set_page_config(page_title="RSA 加密系統", page_icon="🔒")

st.title("🔒 RSA 長字串加密系統")
st.write("請輸入位元數與全班資料，系統將產生解密所需的秘密參數。")

# 1. 設定區
st.sidebar.header("🔑 金鑰參數設定")
p_bits = st.sidebar.number_input("P 位元數", min_value=128, max_value=2048, value=512, step=1)
q_bits = st.sidebar.number_input("Q 位元數", min_value=128, max_value=2048, value=512, step=1)

# 2. 輸入區
input_data = st.text_area("✍️ 請輸入全班資訊 (手機+身分證+生日):", height=150)

if st.button("🚀 產生金鑰並加密"):
    if not input_data:
        st.error("請輸入原文內容！")
    else:
        with st.spinner('正在進行大數運算...'):
            # 生成金鑰
            e = 65537
            while True:
                p = generate_prime(p_bits)
                q = generate_prime(q_bits)
                phi = (p - 1) * (q - 1)
                if math.gcd(e, phi) == 1: break
            
            n = p * q
            d = pow(e, -1, phi)

            # 分塊加密
            bit_stream = "".join([bin(ord(c))[2:].zfill(7) for c in input_data])
            k = math.floor(math.log2(n))
            padding_needed = (k - (len(bit_stream) % k)) % k
            bit_stream_padded = bit_stream + ("0" * padding_needed)
            m_list = [int(bit_stream_padded[i:i+k], 2) for i in range(0, len(bit_stream_padded), k)]
            c_list = [pow(m, e, n) for m in m_list]

            # 轉 Base64
            c_bits_len = math.ceil(math.log2(n))
            encrypted_bits = "".join([bin(c)[2:].zfill(c_bits_len) for c in c_list])
            b64_padding = (8 - (len(encrypted_bits) % 8)) % 8
            final_bits = encrypted_bits + ("0" * b64_padding)
            byte_arr = bytearray([int(final_bits[i:i+8], 2) for i in range(0, len(final_bits), 8)])
            encoded_msg = base64.b64encode(byte_arr).decode('utf-8')

            # 3. 顯示結果
            st.success("✅ 加密成功！請妥善保存下方資訊以利解密。")
            
            # 使用三個 Tabs 或不同的區塊來展示
            st.subheader("🔑 秘密金鑰 (Private Key d)")
            st.info("這是解密的核心，請勿外洩。")
            st.code(str(d), language="text")
            
            st.subheader("⚙️ 模數 (Modulus n)")
            st.info("解密時也需要用到這個模數。")
            st.code(str(n), language="text")
            
            st.subheader("📦 Base64 密文")
            st.code(encoded_msg, language="text")

            st.write(f"📊 統計：模數長度為 {len(str(n))} 位數，共切分為 {len(c_list)} 個資料塊。")
