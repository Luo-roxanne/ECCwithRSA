import streamlit as st
import hashlib
import time

# --- ECC secp256k1 參數 ---
P_BITCOIN = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, 
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

def ecc_mul(k, P, p):
    res = None; temp = P
    while k:
        if k & 1:
            if res is None: res = temp
            else:
                m = (temp[1] - res[1]) * pow(temp[0] - res[0], p - 2, p)
                x3 = (m * m - res[0] - temp[0]) % p
                y3 = (m * (res[0] - x3) - res[1]) % p
                res = (x3, y3)
        m = (3 * temp[0] * temp[0]) * pow(2 * temp[1], p - 2, p)
        nx = (m * m - 2 * temp[0]) % p
        ny = (m * (temp[0] - nx) - temp[1]) % p
        temp = (nx, ny); k >>= 1
    return res

def stretch_key(data_str, iterations=100000):
    res = data_str.encode()
    for _ in range(iterations):
        res = hashlib.sha256(res).digest()
    return int(res.hex(), 16)

def xor_decrypt(hex_data, key_int):
    key_bytes = hashlib.sha256(str(key_int).encode()).digest()
    data_bytes = bytes.fromhex(hex_data)
    return "".join(chr(b ^ key_bytes[i % len(key_bytes)]) for i, b in enumerate(data_bytes))

# --- APP 介面設計 ---
st.set_page_config(page_title="ECC 軍事級解密工具", page_icon="🔐")
st.title("🔐 ECC 批次資料解密系統")
st.markdown("請輸入正確的發起人資訊以解鎖全班個資。")

with st.sidebar:
    st.header("🔑 安全驗證")
    master_id = st.text_input("輸入發起人身分證 (私鑰)", type="password", help="用於 10 萬次拉伸運算")
    master_phone = st.text_input("輸入發起人電話 (隨機數)", help="用於 ECC 點乘偏移")

raw_cipher = st.text_area("📋 請貼上加密密文串 (以逗號隔開)", height=150)

if st.button("🚀 開始解密並驗證"):
    if master_id and master_phone and raw_cipher:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 1. 執行拉伸 (模擬進度條增加儀式感)
            status_text.text("⚡ 正在執行 10 萬次密鑰拉伸...")
            progress_bar.progress(30)
            priv_key = stretch_key(master_id) % P_BITCOIN
            
            # 2. ECC 運算
            status_text.text("⚙️ 正在計算比特幣橢圓曲線點...")
            progress_bar.progress(60)
            k_random = int(hashlib.sha256(master_phone.encode()).hexdigest(), 16) % P_BITCOIN
            pub_point = ecc_mul(priv_key, G, P_BITCOIN)
            shared_secret_point = ecc_mul(k_random, pub_point, P_BITCOIN)
            shared_key_val = shared_secret_point[0]
            
            # 3. 批次 XOR 解密
            status_text.text("🔓 正在還原資料表格...")
            progress_bar.progress(90)
            cipher_blocks = raw_cipher.split(",")
            results = []
            
            for i, hex_val in enumerate(cipher_blocks):
                decrypted_24 = xor_decrypt(hex_val.strip(), shared_key_val)
                results.append({
                    "座號": i + 1,
                    "電話": decrypted_24[0:10],
                    "身分證": decrypted_24[10:20],
                    "生日": decrypted_24[20:24]
                })
            
            progress_bar.progress(100)
            status_text.text("✅ 解密完成！")
            
            # 4. 顯示結果表格
            st.success(f"成功還原 {len(results)} 筆資料")
            st.table(results)
            
        except Exception as e:
            st.error(f"❌ 解密失敗：資訊不正確或密文損毀。")
    else:
        st.warning("⚠️ 請完整填寫所有欄位。")