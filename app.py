# app.py — ผู้ช่วยออกแบบระบบเสียงด้วย AI (รองรับแปลน, สเกล, เลือกประเภทลำโพง, โลโก้)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO
import numpy as np

st.set_page_config(page_title="AI Audio Designer", layout="centered")
st.image("https://proplugin.com/pub/media/logo/websites/1/logo.svg", width=200)
st.title("🎛️ ผู้ช่วยออกแบบระบบเสียงด้วย AI")

# โหลดฐานข้อมูลสินค้า
def load_product_database(path="audio_product_data.csv"):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดฐานข้อมูล: {e}")
        return None

# ประมวลผลตำแหน่งลำโพง
def suggest_speaker_positions(room_w, room_l, spacing):
    positions = []
    x = spacing / 2
    while x < room_w:
        y = spacing / 2
        while y < room_l:
            positions.append((x, y))
            y += spacing
        x += spacing
    return positions

# วาดแผนผัง
def draw_layout(width, length, speakers, coverage_radius):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, width)
    ax.set_ylim(0, length)
    ax.set_title("แผนผังตำแหน่งลำโพง")
    ax.set_xlabel("ความกว้าง (เมตร)")
    ax.set_ylabel("ความยาว (เมตร)")
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.add_patch(patches.Rectangle((0, 0), width, length, linewidth=1, edgecolor='black', facecolor='whitesmoke'))
    for (x, y) in speakers:
        ax.add_patch(patches.Circle((x, y), coverage_radius, alpha=0.2, color='lightblue'))
        ax.plot(x, y, 'ro')
        ax.text(x + 0.2, y + 0.2, 'ลำโพง', fontsize=8)
    return fig

with st.form("audio_form"):
    st.subheader("📝 ข้อมูลพื้นที่ติดตั้ง")
    room_type = st.selectbox("ประเภทสถานที่", ["ร้านอาหาร", "ห้องประชุม", "ร้านค้า", "สถานที่แสดงสด", "โบสถ์"])
    use_case = st.selectbox("ลักษณะการใช้งานของระบบเสียง", ["เปิดเพลงพื้นหลัง (BGM)", "เสียงพูด", "ดนตรีสด", "ดีเจ / ปาร์ตี้", "การประกาศหลายโซน"])
    room_width = st.number_input("ความกว้างของห้อง (เมตร)", 1, 100, 12)
    room_length = st.number_input("ความยาวของห้อง (เมตร)", 1, 100, 20)
    spacing = st.slider("ระยะห่างระหว่างลำโพง (เมตร)", 2, 10, 6)
    coverage_radius = st.slider("รัศมีการครอบคลุมของลำโพง (เมตร)", 2, 10, 5)
    budget = st.number_input("งบประมาณโดยประมาณ (บาท)", 10000, 1000000, 100000)
    spk_type = st.selectbox("เลือกประเภทของลำโพงที่ต้องการ", ["Full-range", "Ceiling", "Line Array"])
    
    st.markdown("---")
    st.subheader("📐 อัปโหลดแบบแปลน (ไม่บังคับ)")
    uploaded_file = st.file_uploader("อัปโหลดไฟล์ภาพแบบแปลน (PNG/JPG)", type=["png", "jpg", "jpeg"])
    scale_length = st.number_input("ความยาวจริงของเส้นอ้างอิงในแบบแปลน (เมตร)", 1, 100, 10)
    scale_pixel = st.number_input("จำนวนพิกเซลของเส้นอ้างอิงในภาพ (จากการวัด)", 1, 5000, 1000)
    submitted = st.form_submit_button("สร้างระบบเสียง")

if submitted:
    st.success("กำลังประมวลผลการออกแบบระบบเสียง...")
    scale_factor = scale_length / scale_pixel  # เมตรต่อพิกเซล
    speakers = suggest_speaker_positions(room_width, room_length, spacing)
    fig = draw_layout(room_width, room_length, speakers, coverage_radius)

    if uploaded_file:
        st.subheader("🖼️ แบบแปลนที่อัปโหลด")
        img = Image.open(uploaded_file)
        st.image(img, caption="แบบแปลนจากผู้ใช้งาน", use_column_width=True)
        st.caption(f"สเกล: 1 พิกเซล = {scale_factor:.4f} เมตร")

    st.subheader("📍 ผังตำแหน่งลำโพง")
    st.pyplot(fig)
    st.info(f"แนะนำให้ใช้ลำโพงจำนวน: {len(speakers)} ตัว")

    df = load_product_database()
    if df is not None:
        st.subheader("🔊 อุปกรณ์ที่แนะนำ")
        if use_case == "เปิดเพลงพื้นหลัง (BGM)":
            type_filter = "Ceiling"
        elif use_case == "เสียงพูด":
            type_filter = "Full-range"
        elif use_case == "ดนตรีสด":
            type_filter = "Full-range|Line Array"
        elif use_case == "ดีเจ / ปาร์ตี้":
            type_filter = "Line Array|Subwoofer"
        elif use_case == "การประกาศหลายโซน":
            type_filter = "Ceiling|Paging"
        else:
            type_filter = spk_type  # fallback

        filtered = df[df["Type"].str.contains(type_filter, case=False)].head(len(speakers)).head(len(speakers))
        st.dataframe(filtered[["Model", "Brand", "Type", "Power (W)", "Coverage Angle", "Price (THB)", "Stock"]])
        total_cost = filtered["Price (THB)"].sum()
        st.metric("💰 ราคารวมโดยประมาณ", f"{total_cost:,.0f} บาท")
        if total_cost > budget:
            st.warning("⚠️ ระบบเสียงที่แนะนำเกินงบประมาณที่ตั้งไว้")
        else:
            st.success("✅ ระบบเสียงที่แนะนำอยู่ภายใต้งบประมาณ")
    else:
        st.error("ไม่สามารถโหลดฐานข้อมูลสินค้าได้")
