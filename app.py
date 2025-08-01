# app.py — AI Audio Designer (Updated: Remove st_canvas, add wall speaker option)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO
import numpy as np
import math

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

# วาดแผนผังแบบกราฟิก
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

st.subheader("📝 ข้อมูลพื้นที่ติดตั้ง")
with st.form("audio_form"):
    room_type = st.selectbox("ประเภทสถานที่", ["ร้านอาหาร", "ห้องประชุม", "ร้านค้า", "สถานที่แสดงสด", "โบสถ์"])
    use_case = st.selectbox("ลักษณะการใช้งานของระบบเสียง", ["เปิดเพลงพื้นหลัง (BGM)", "เสียงพูด", "ดนตรีสด", "ดีเจ / ปาร์ตี้", "การประกาศหลายโซน"])
    speaker_mount = st.selectbox("ลักษณะการติดตั้งลำโพง", ["ลำโพงติดเพดาน (Ceiling)", "ลำโพงตั้งพื้น / แขวน (Wall-mounted)"])
    room_width = st.number_input("ความกว้างของห้อง (เมตร)", min_value=1.0, value=12.0, step=0.1)
    room_length = st.number_input("ความยาวของห้อง (เมตร)", min_value=1.0, value=20.0, step=0.1)
    spacing = st.slider("ระยะห่างระหว่างลำโพง (เมตร)", 2, 10, 6)
    budget = st.number_input("งบประมาณโดยประมาณ (บาท)", min_value=0, value=100000, step=1000)
    uploaded_file = st.file_uploader("อัปโหลดแปลน (ไม่บังคับ)", type=["png", "jpg", "jpeg"])
    submitted = st.form_submit_button("สร้างระบบเสียง")

if submitted:
    st.success("กำลังประมวลผลการออกแบบระบบเสียง...")
    speakers = suggest_speaker_positions(room_width, room_length, spacing)

    st.subheader("📍 ผังตำแหน่งลำโพง")
    coverage_radius = 2.5
    fig = draw_layout(room_width, room_length, speakers, coverage_radius)
    st.pyplot(fig)
    st.info(f"แนะนำให้ใช้ลำโพงจำนวน: {len(speakers)} ตัว")

    df = load_product_database()
    if df is not None:
        st.subheader("🔊 อุปกรณ์ที่แนะนำ")

        if use_case == "เปิดเพลงพื้นหลัง (BGM)":
            type_filter = "Ceiling" if "เพดาน" in speaker_mount else "Wall"
            min_spl = 85
        elif use_case == "เสียงพูด":
            type_filter = "Full-range"
            min_spl = 90
        elif use_case == "ดนตรีสด":
            type_filter = "Full-range|Line Array"
            min_spl = 100
        elif use_case == "ดีเจ / ปาร์ตี้":
            type_filter = "Line Array|Subwoofer"
            min_spl = 105
        elif use_case == "การประกาศหลายโซน":
            type_filter = "Ceiling|Paging"
            min_spl = 85
        else:
            type_filter = "Full-range"
            min_spl = 90

        filtered = df[df["Type"].str.contains(type_filter, case=False, na=False)]
        filtered = filtered[pd.to_numeric(filtered["Max SPL (dB)"], errors='coerce') >= min_spl]
        filtered = filtered.head(len(speakers))

        st.dataframe(filtered[["Model", "Brand", "Type", "Power (W)", "Coverage Angle", "Price (THB)", "Stock"]])
        total_cost = filtered["Price (THB)"].sum()
        st.metric("💰 ราคารวมโดยประมาณ", f"{total_cost:,.0f} บาท")
        if total_cost > budget:
            st.warning("⚠️ ระบบเสียงที่แนะนำเกินงบประมาณที่ตั้งไว้")
        else:
            st.success("✅ ระบบเสียงที่แนะนำอยู่ภายใต้งบประมาณ")
    else:
        st.error("ไม่สามารถโหลดฐานข้อมูลสินค้าได้")
