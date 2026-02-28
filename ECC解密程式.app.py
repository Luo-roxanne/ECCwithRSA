{\rtf1\ansi\ansicpg950\cocoartf2577
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset136 PingFangTC-Regular;\f2\fnil\fcharset0 AppleColorEmoji;
}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import hashlib\
import time\
\
# --- ECC secp256k1 
\f1 \'b0\'d1\'bc\'c6
\f0  ---\
P_BITCOIN = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F\
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, \
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)\
\
def ecc_mul(k, P, p):\
    res = None; temp = P\
    while k:\
        if k & 1:\
            if res is None: res = temp\
            else:\
                m = (temp[1] - res[1]) * pow(temp[0] - res[0], p - 2, p)\
                x3 = (m * m - res[0] - temp[0]) % p\
                y3 = (m * (res[0] - x3) - res[1]) % p\
                res = (x3, y3)\
        m = (3 * temp[0] * temp[0]) * pow(2 * temp[1], p - 2, p)\
        nx = (m * m - 2 * temp[0]) % p\
        ny = (m * (temp[0] - nx) - temp[1]) % p\
        temp = (nx, ny); k >>= 1\
    return res\
\
def stretch_key(data_str, iterations=100000):\
    res = data_str.encode()\
    for _ in range(iterations):\
        res = hashlib.sha256(res).digest()\
    return int(res.hex(), 16)\
\
def xor_decrypt(hex_data, key_int):\
    key_bytes = hashlib.sha256(str(key_int).encode()).digest()\
    data_bytes = bytes.fromhex(hex_data)\
    return "".join(chr(b ^ key_bytes[i % len(key_bytes)]) for i, b in enumerate(data_bytes))\
\
# --- APP 
\f1 \'a4\'b6\'ad\'b1\'b3\'5d\'ad\'70
\f0  ---\
st.set_page_config(page_title="ECC 
\f1 \'ad\'78\'a8\'c6\'af\'c5\'b8\'d1\'b1\'4b\'a4\'75\'a8\'e3
\f0 ", page_icon="
\f2 \uc0\u55357 \u56592 
\f0 ")\
st.title("
\f2 \uc0\u55357 \u56592 
\f0  ECC 
\f1 \'a7\'e5\'a6\'b8\'b8\'ea\'ae\'c6\'b8\'d1\'b1\'4b\'a8\'74\'b2\'ce
\f0 ")\
st.markdown("
\f1 \'bd\'d0\'bf\'e9\'a4\'4a\'a5\'bf\'bd\'54\'aa\'ba\'b5\'6f\'b0\'5f\'a4\'48\'b8\'ea\'b0\'54\'a5\'48\'b8\'d1\'c2\'ea\'a5\'fe\'af\'5a\'ad\'d3\'b8\'ea\'a1\'43
\f0 ")\
\
with st.sidebar:\
    st.header("
\f2 \uc0\u55357 \u56593 
\f0  
\f1 \'a6\'77\'a5\'fe\'c5\'e7\'c3\'d2
\f0 ")\
    master_id = st.text_input("
\f1 \'bf\'e9\'a4\'4a\'b5\'6f\'b0\'5f\'a4\'48\'a8\'ad\'a4\'c0\'c3\'d2
\f0  (
\f1 \'a8\'70\'c6\'5f
\f0 )", type="password", help="
\f1 \'a5\'ce\'a9\'f3
\f0  10 
\f1 \'b8\'55\'a6\'b8\'a9\'d4\'a6\'f9\'b9\'42\'ba\'e2
\f0 ")\
    master_phone = st.text_input("
\f1 \'bf\'e9\'a4\'4a\'b5\'6f\'b0\'5f\'a4\'48\'b9\'71\'b8\'dc
\f0  (
\f1 \'c0\'48\'be\'f7\'bc\'c6
\f0 )", help="
\f1 \'a5\'ce\'a9\'f3
\f0  ECC 
\f1 \'c2\'49\'ad\'bc\'b0\'be\'b2\'be
\f0 ")\
\
raw_cipher = st.text_area("
\f2 \uc0\u55357 \u56523 
\f0  
\f1 \'bd\'d0\'b6\'4b\'a4\'57\'a5\'5b\'b1\'4b\'b1\'4b\'a4\'e5\'a6\'ea
\f0  (
\f1 \'a5\'48\'b3\'72\'b8\'b9\'b9\'6a\'b6\'7d
\f0 )", height=150)\
\
if st.button("
\f2 \uc0\u55357 \u56960 
\f0  
\f1 \'b6\'7d\'a9\'6c\'b8\'d1\'b1\'4b\'a8\'c3\'c5\'e7\'c3\'d2
\f0 "):\
    if master_id and master_phone and raw_cipher:\
        try:\
            progress_bar = st.progress(0)\
            status_text = st.empty()\
            \
            # 1. 
\f1 \'b0\'f5\'a6\'e6\'a9\'d4\'a6\'f9
\f0  (
\f1 \'bc\'d2\'c0\'c0\'b6\'69\'ab\'d7\'b1\'f8\'bc\'57\'a5\'5b\'bb\'f6\'a6\'a1\'b7\'50
\f0 )\
            status_text.text("
\f2 \uc0\u9889 
\f0  
\f1 \'a5\'bf\'a6\'62\'b0\'f5\'a6\'e6
\f0  10 
\f1 \'b8\'55\'a6\'b8\'b1\'4b\'c6\'5f\'a9\'d4\'a6\'f9
\f0 ...")\
            progress_bar.progress(30)\
            priv_key = stretch_key(master_id) % P_BITCOIN\
            \
            # 2. ECC 
\f1 \'b9\'42\'ba\'e2
\f0 \
            status_text.text("
\f2 \uc0\u9881 \u65039 
\f0  
\f1 \'a5\'bf\'a6\'62\'ad\'70\'ba\'e2\'a4\'f1\'af\'53\'b9\'f4\'be\'f2\'b6\'ea\'a6\'b1\'bd\'75\'c2\'49
\f0 ...")\
            progress_bar.progress(60)\
            k_random = int(hashlib.sha256(master_phone.encode()).hexdigest(), 16) % P_BITCOIN\
            pub_point = ecc_mul(priv_key, G, P_BITCOIN)\
            shared_secret_point = ecc_mul(k_random, pub_point, P_BITCOIN)\
            shared_key_val = shared_secret_point[0]\
            \
            # 3. 
\f1 \'a7\'e5\'a6\'b8
\f0  XOR 
\f1 \'b8\'d1\'b1\'4b
\f0 \
            status_text.text("
\f2 \uc0\u55357 \u56595 
\f0  
\f1 \'a5\'bf\'a6\'62\'c1\'d9\'ad\'ec\'b8\'ea\'ae\'c6\'aa\'ed\'ae\'e6
\f0 ...")\
            progress_bar.progress(90)\
            cipher_blocks = raw_cipher.split(",")\
            results = []\
            \
            for i, hex_val in enumerate(cipher_blocks):\
                decrypted_24 = xor_decrypt(hex_val.strip(), shared_key_val)\
                results.append(\{\
                    "
\f1 \'ae\'79\'b8\'b9
\f0 ": i + 1,\
                    "
\f1 \'b9\'71\'b8\'dc
\f0 ": decrypted_24[0:10],\
                    "
\f1 \'a8\'ad\'a4\'c0\'c3\'d2
\f0 ": decrypted_24[10:20],\
                    "
\f1 \'a5\'cd\'a4\'e9
\f0 ": decrypted_24[20:24]\
                \})\
            \
            progress_bar.progress(100)\
            status_text.text("
\f2 \uc0\u9989 
\f0  
\f1 \'b8\'d1\'b1\'4b\'a7\'b9\'a6\'a8\'a1\'49
\f0 ")\
            \
            # 4. 
\f1 \'c5\'e3\'a5\'dc\'b5\'b2\'aa\'47\'aa\'ed\'ae\'e6
\f0 \
            st.success(f"
\f1 \'a6\'a8\'a5\'5c\'c1\'d9\'ad\'ec
\f0  \{len(results)\} 
\f1 \'b5\'a7\'b8\'ea\'ae\'c6
\f0 ")\
            st.table(results)\
            \
        except Exception as e:\
            st.error(f"
\f2 \uc0\u10060 
\f0  
\f1 \'b8\'d1\'b1\'4b\'a5\'a2\'b1\'d1\'a1\'47\'b8\'ea\'b0\'54\'a4\'a3\'a5\'bf\'bd\'54\'a9\'ce\'b1\'4b\'a4\'e5\'b7\'6c\'b7\'b4\'a1\'43
\f0 ")\
    else:\
        st.warning("
\f2 \uc0\u9888 \u65039 
\f0  
\f1 \'bd\'d0\'a7\'b9\'be\'e3\'b6\'f1\'bc\'67\'a9\'d2\'a6\'b3\'c4\'e6\'a6\'ec\'a1\'43
\f0 ")}