import streamlit as st
import base64
import math

# --- Streamlit 網頁介面 ---
st.set_page_config(page_title="RSA 解密演示系統", page_icon="🔓")

st.title("🔓 RSA 秘密資訊解密系統")
st.write("本工具模擬接收端，利用秘密金鑰 (Private Key) 將密文還原為原始資料。")

# 1. 輸入區
st.sidebar.header("🔑 私鑰參數輸入")
st.info("請輸入加密端產生的秘密參數，以進行數學運算。")

# 使用 text_area 因為 d 和 n 可能非常長
d_input = st.sidebar.text_area("秘密金鑰 (d):", height=150)
n_input = st.sidebar.text_area("模數 (n):", height=150)

st.subheader("📦 密文輸入")
cipher_base64 = st.text_area("請貼上 Base64 密文:", placeholder="例如: e4FAbxWpoHkom...")

# 2. 解密執行
if st.button("🚀 執行解密還原"):
    if not d_input or not n_input or not cipher_base64:
        st.error("請完整填寫秘密金鑰 d、模數 n 與密文！")
    else:
        try:
            # 將輸入轉回整數
            d = int(d_input.strip())
            n = int(n_input.strip())
            
            # --- 解密核心邏輯 ---
            # 1. Base64 轉回位元流
            decoded_bytes = base64.b64decode(cipher_base64)
            # 將 bytearray 轉回 01 字串
            full_bit_stream = "".join([bin(b)[2:].zfill(8) for b in decoded_bytes])
            
            # 2. 依照 n 的長度切分區塊
            c_bits_len = math.ceil(math.log2(n))
            k = math.floor(math.log2(n))
            
            # 取得原始密文清單 (每 c_bits_len 為一個加密塊)
            c_list = []
            for i in range(0, (len(full_bit_stream) // c_bits_len) * c_bits_len, c_bits_len):
                c_list.append(int(full_bit_stream[i:i+c_bits_len], 2))
            
            # 3. 核心數學運算：M = C^d mod n
            with st.spinner('正在進行大數模冪運算 (ModPow)...'):
                m_list = [pow(c, d, n) for c in c_list]
            
            # 4. 轉回字串
            # 將每個 M 轉回 k 位元的二進制，再合併
            decrypted_bit_stream = "".join([bin(m)[2:].zfill(k) for m in m_list])
            
            # 依照 7-bit (ASCII) 轉回字元
            result_str = ""
            for i in range(0, (len(decrypted_bit_stream) // 7) * 7, 7):
                char_code = int(decrypted_bit_stream[i:i+7], 2)
                if char_code == 0: continue # 移除填充的零
                result_str += chr(char_code)
            
            # 3. 顯示結果
            st.success("🔓 解密成功！")
            st.subheader("📄 還原之原始資料")
            st.code(result_str, language="text")
            
            st.balloons() # 增加成功氛圍

        except ValueError:
            st.error("金鑰格式錯誤，請確保 d 與 n 為純數字。")
        except Exception as e:
            st.error(f"解密失敗：{str(e)}")

# 4. 教育補充
with st.expander("📝 為什麼解密需要 d 和 n？"):
    st.write("""
    根據 RSA 數學原理，解密公式為：
    **M ≡ C^d (mod n)**
    
    其中：
    - **C** 是你貼上的密文。
    - **d** 是你的秘密金鑰。
    - **n** 是模數（由兩個大質數相乘所得）。
    
    這個運算非常巨大，但因為只有你持有正確的 d，所以只有你能還原出原始的 M (明文)。
    """)
