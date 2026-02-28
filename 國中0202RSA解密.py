import streamlit as st
import base64
import math
import pandas as pd

def rsa_decrypt_logic(n, d, b64_input):
    """完全移植自國中0202RSA解碼邏輯"""
    # 1. 自動推算參數
    k = math.floor(math.log2(n))
    c_bits_len = math.ceil(math.log2(n))

    # 2. Base64 轉回位元串
    byte_data = base64.b64decode(b64_input)
    all_bits = "".join([bin(b)[2:].zfill(8) for b in byte_data])

    # 3. 每 c_bits_len 取出一組密文 C 並解碼回位元流
    original_bits = ""
    for i in range(0, (len(all_bits) // c_bits_len) * c_bits_len, c_bits_len):
        chunk = all_bits[i:i+c_bits_len]
        if len(chunk) < c_bits_len: break
        c = int(chunk, 2)
        m = pow(c, d, n)
        original_bits += bin(m)[2:].zfill(k)

    # 4. 位元串轉回 ASCII 字元 (每 7 位元一組)
    decoded_str = ""
    for i in range(0, (len(original_bits) // 7) * 7, 7):
        char_bits = original_bits[i:i+7]
        char_code = int(char_bits, 2)
        if char_code == 0: continue 
        decoded_str += chr(char_code)
    
    return decoded_str

# --- Streamlit 介面介面 ---
st.set_page_config(page_title="RSA 班級資料解密系統", page_icon="📊", layout="wide")

st.title("📊 RSA 班級個資自動還原系統")
st.markdown("本系統將解密後的資料自動格式化為表格，方便核對與管理。")

# 側邊欄輸入金鑰 (使用 text_input 支援超長數字)
with st.sidebar:
    st.header("🔑 RSA 密鑰設定")
    n_str = st.text_input("請輸入公開金鑰 n", placeholder="貼上超長數字 n...")
    d_str = st.text_input("請輸入秘密金鑰 d", placeholder="貼上超長數字 d...", type="password")
    st.info("💡 提示：本程式會自動計算 $k$ 值與位元長度。")

# 主畫面輸入密文
st.subheader("📥 密文輸入")
b64_text = st.text_area("請貼上 Base64 加密字串", height=150)

if st.button("🚀 執行批次解密並產生表格"):
    if n_str and d_str and b64_text:
        try:
            # 轉換大整數
            n_val = int(n_str.strip())
            d_val = int(d_str.strip())
            
            with st.spinner("🔒 正在進行 RSA 位元流解碼..."):
                full_raw_data = rsa_decrypt_logic(n_val, d_val, b64_text)
            
            if full_raw_data:
                # 5. 自動切分資料並建立列表 (每 24 碼為一人)
                # 結構：10碼電話 + 10碼身分證 + 4碼生日
                student_list = []
                for i in range(0, (len(full_raw_data) // 24) * 24, 24):
                    chunk = full_raw_data[i:i+24]
                    student_list.append({
                        "座號": (i // 24) + 1,
                        "手機號碼": chunk[0:10],
                        "身分證字號": chunk[10:20],
                        "出生月日": chunk[20:24]
                    })
                
                if student_list:
                    st.success(f"✅ 成功解密！偵測到 {len(student_list)} 位同學資料。")
                    
                    # 6. 顯示表格 (使用 st.dataframe 讓表格可以縮放或下載)
                    df = pd.DataFrame(student_list)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # 提供 CSV 下載功能 (科展加分項)
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 下載解密結果 (CSV)",
                        data=csv,
                        file_name="解密結果.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("⚠️ 解密出的字串長度不足以構成一筆完整資料 (24碼)。")
                    st.text(f"原始解密內容：{full_raw_data}")
            else:
                st.error("❌ 無法解碼出任何字元，請檢查金鑰與密文是否對應。")
                
        except ValueError:
            st.error("❌ 格式錯誤：金鑰欄位必須全部為數字。")
        except Exception as err:
            st.error(f"❌ 執行中出錯：{err}")
    else:
        st.warning("⚠️ 請完整填寫金鑰 n, d 與密文內容。")

st.divider()
st.caption("本工具針對 7-bit ASCII 位元流進行優化還原。")
