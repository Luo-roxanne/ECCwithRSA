import base64
import math

def decrypt_system():
    print("--- RSA 位元流解密系統 ---")
    e = int(input("請輸入公開金鑰 e: "))
    n = int(input("請輸入公開金鑰 n: "))
    d = int(input("請輸入秘密金鑰 d: "))
    b64_input = input("請輸入 Base64 密文: ")

    # 1. 自動推算參數
    k = math.floor(math.log2(n))       # 當初加密時的區塊大小
    c_bits_len = math.ceil(math.log2(n)) # 加密後數字的位元長度

    # 2. Base64 轉回位元串
    byte_data = base64.b64decode(b64_input)
    all_bits = "".join([bin(b)[2:].zfill(8) for b in byte_data])

    # 3. 每 c_bits_len 取出一組密文 C 並解密
    # 注意：我們只取前 (10*7 向上取 k 倍數後轉換成 c_bits) 的長度
    # 比較簡單的做法是根據 c_bits_len 拆分
    original_bits = ""
    for i in range(0, (len(all_bits) // c_bits_len) * c_bits_len, c_bits_len):
        chunk = all_bits[i:i+c_bits_len]
        if len(chunk) < c_bits_len: break
        c = int(chunk, 2)
        m = pow(c, d, n)
        original_bits += bin(m)[2:].zfill(k)

    # 4. 還原身分證字號 (取前 70 位，每 7 位一個字元)
    id_bits = original_bits[:70]
    final_id = ""
    for i in range(0, 70, 7):
        final_id += chr(int(id_bits[i:i+7], 2))

    print(f"\n>>> 解密成功！原始身分證字號為: {final_id}")

decrypt_system()
