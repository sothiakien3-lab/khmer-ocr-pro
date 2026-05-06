import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import re
from io import BytesIO

# Cấu hình giao diện chuẩn Dashboard
st.set_page_config(page_title="Khmer ID OCR Pro", layout="wide")

# CSS để giao diện chuyên nghiệp hơn
st.markdown("""
    <style>
    .stApp { background-color: #121212; }
    [data-testid="stMetricValue"] { font-size: 1.5rem; color: #00ff00; }
    .stTab { background-color: #1e1e1e; border-radius: 10px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_reader():
    return easyocr.Reader(['km', 'en'])

reader = load_reader()

st.title("🇰🇭 Hệ thống Quét & Phân tích CCCD Khmer")
st.write("Giải pháp vận hành đa nền tảng: Máy tính & Điện thoại")

# Giao diện chia 2 cột
col_img, col_data = st.columns([1, 1.2])

with col_img:
    st.subheader("📸 Hình ảnh thẻ")
    # Hỗ trợ chụp trực tiếp từ camera điện thoại hoặc tải file
    uploaded_file = st.file_uploader("Tải ảnh hoặc Chụp trực tiếp", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        
        if st.button("🚀 BẮT ĐẦU QUÉT", type="primary"):
            with st.spinner('Đang phân tích dữ liệu...'):
                img_arr = np.array(img)
                results = reader.readtext(img_arr)
                raw_text = " ".join([res[1] for res in results])
                lines = [res[1] for res in results]
                
                # Logic phân tích chuyên sâu
                st.session_state['data'] = {
                    "id_num": "".join(re.findall(r'\d+', lines[0])) if lines else "",
                    "name_en": next((x for x in lines if re.match(r'^[A-Z\s]+$', x) and len(x) > 3), ""),
                    "name_km": lines[1] if len(lines) > 1 else "",
                    "gender": "Nam" if "ប្រុស" in raw_text else "Nữ" if "ស្រី" in raw_text else "",
                    "height": "".join(re.findall(r'\d+', re.search(r'\d+\s*(cm|m)', raw_text).group()) if re.search(r'\d+\s*(cm|m)', raw_text) else ""),
                    "pob": raw_text.split("ខេត្ត")[-1].strip().split(" ")[0] if "ខេត្ត" in raw_text else "",
                    "address": " ".join(lines[-3:]) if len(lines) > 3 else ""
                }

with col_data:
    st.subheader("📝 Kiểm tra & Hiệu chỉnh")
    if 'data' in st.session_state:
        d = st.session_state['data']
        tab1, tab2 = st.tabs(["👤 Thông tin cá nhân", "📍 Địa chỉ cư trú"])
        
        with tab1:
            c1, c2 = st.columns(2)
            id_num = c1.text_input("Số CCCD (Dòng trên cùng)", d['id_num'])
            name_en = c2.text_input("Họ và Tên (Latin)", d['name_en'])
            
            c3, c4 = st.columns(2)
            name_km = c3.text_input("Họ và Tên (Khmer)", d['name_km'])
            gender = c4.selectbox("Giới tính", ["Nam", "Nữ"], index=0 if d['gender']=="Nam" else 1)
            
            c5, c6 = st.columns(2)
            height = c5.text_input("Chiều cao (Số Latin)", d['height'])
            pob = c6.text_input("Nơi sinh (Tên Tỉnh)", d['pob'])

        with tab2:
            address = st.text_area("Địa chỉ cư trú (Đầy đủ)", d['address'])

        # Xuất dữ liệu
        final_df = pd.DataFrame([{
            "Số CCCD": id_num, "Họ tên Latin": name_en, "Họ tên Khmer": name_km,
            "Giới tính": gender, "Chiều cao": height, "Nơi sinh": pob, "Địa chỉ": address
        }])
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 TẢI FILE EXCEL KẾT QUẢ",
            data=output.getvalue(),
            file_name="Ket_qua_OCR.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("Hệ thống sẵn sàng. Vui lòng tải ảnh lên để bắt đầu.")