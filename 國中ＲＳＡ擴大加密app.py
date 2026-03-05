import tkinter as tk
from tkinter import scrolledtext, messagebox
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

# --- APP 介面邏輯 ---
def run_encryption():
    try:
        p_bits = int(entry_p.get())
        q_bits = int(entry_q.get())
        input_data = entry_data.get("1.0", tk.END).strip()
        
        if not input_data:
            messagebox.showwarning("提醒", "請輸入要加密的資料！")
            return

        # 1. 生成金鑰
        e = 65537
        while True:
            p = generate_prime(p_bits)
            q = generate_prime(q_bits)
            phi = (p - 1) * (q - 1)
            if math.gcd(e, phi) == 1: break
        
        n = p * q
        d = pow(e, -1, phi)

        # 2. 分塊加密
        bit_stream = "".join([bin(ord(c))[2:].zfill(7) for c in input_data])
        k = math.floor(math.log2(n))
        padding_needed = (k - (len(bit_stream) % k)) % k
        bit_stream_padded = bit_stream + ("0" * padding_needed)
        m_list = [int(bit_stream_padded[i:i+k], 2) for i in range(0, len(bit_stream_padded), k)]
        c_list = [pow(m, e, n) for m in m_list]

        # 3. 轉 Base64
        c_bits_len = math.ceil(math.log2(n))
        encrypted_bits = "".join([bin(c)[2:].zfill(c_bits_len) for c in c_list])
        b64_padding = (8 - (len(encrypted_bits) % 8)) % 8
        final_bits = encrypted_bits + ("0" * b64_padding)
        byte_arr = bytearray([int(final_bits[i:i+8], 2) for i in range(0, len(final_bits), 8)])
        encoded_msg = base64.b64encode(byte_arr).decode('utf-8')

        # 4. 顯示結果
        text_d.delete("1.0", tk.END)
        text_d.insert(tk.END, str(d))
        
        text_cipher.delete("1.0", tk.END)
        text_cipher.insert(tk.END, encoded_msg)

    except Exception as e:
        messagebox.showerror("錯誤", f"發生問題：{str(e)}\n請檢查位元數是否輸入正確。")

# --- 建立視窗 ---
root = tk.Tk()
root.title("RSA 長字串加密安全 APP (科展演示版)")
root.geometry("600x700")

# 配置與輸入
frame_input = tk.LabelFrame(root, text=" 1. 設定位元與原文 ", padx=10, pady=10)
frame_input.pack(padx=10, pady=10, fill="x")

tk.Label(frame_input, text="P 位元數:").grid(row=0, column=0)
entry_p = tk.Entry(frame_input)
entry_p.insert(0, "512")
entry_p.grid(row=0, column=1)

tk.Label(frame_input, text="Q 位元數:").grid(row=0, column=2, padx=5)
entry_q = tk.Entry(frame_input)
entry_q.insert(0, "512")
entry_q.grid(row=0, column=3)

tk.Label(frame_input, text="輸入原文 (手機+身分證+生日):").grid(row=1, column=0, columnspan=4, sticky="w", pady=(10,0))
entry_data = tk.Text(frame_input, height=5)
entry_data.pack(fill="x", pady=5) # 修正：因為上方用了 grid，這裡改用 pack 或調整 grid
entry_data.grid(row=2, column=0, columnspan=4)

btn_run = tk.Button(root, text="🔒 開始執行 RSA 加密", command=run_encryption, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
btn_run.pack(pady=10)

# 輸出結果
frame_output = tk.LabelFrame(root, text=" 2. 秘密輸出 (加密結果) ", padx=10, pady=10)
frame_output.pack(padx=10, pady=10, fill="both", expand=True)

tk.Label(frame_output, text="秘密金鑰 (d):").pack(anchor="w")
text_d = scrolledtext.ScrolledText(frame_output, height=8)
text_d.pack(fill="x", pady=5)

tk.Label(frame_output, text="Base64 密文:").pack(anchor="w", pady=(10,0))
text_cipher = scrolledtext.ScrolledText(frame_output, height=8)
text_cipher.pack(fill="both", expand=True, pady=5)

root.mainloop()
