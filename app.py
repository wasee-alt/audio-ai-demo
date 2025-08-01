
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def load_product_database(path="audio_product_data.csv"):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return None

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

def draw_layout(width, length, speakers, coverage_radius):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, width)
    ax.set_ylim(0, length)
    ax.set_title("Speaker Layout")
    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Length (m)")
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.add_patch(patches.Rectangle((0, 0), width, length, linewidth=1, edgecolor='black', facecolor='whitesmoke'))
    for (x, y) in speakers:
        ax.add_patch(patches.Circle((x, y), coverage_radius, alpha=0.2, color='lightblue'))
        ax.plot(x, y, 'ro')
        ax.text(x + 0.2, y + 0.2, 'SPK', fontsize=8)
    return fig

st.set_page_config(page_title="AI Audio Designer", layout="centered")
st.title("🎛️ AI Audio System Designer")

with st.form("audio_form"):
    st.subheader("📝 Room Information")
    room_type = st.selectbox("Room Type", ["Restaurant", "Meeting Room", "Retail Shop", "Live Venue", "Church"])
    room_width = st.number_input("Room Width (meters)", 1, 100, 12)
    room_length = st.number_input("Room Length (meters)", 1, 100, 20)
    spacing = st.slider("Speaker Spacing (m)", 2, 10, 6)
    coverage_radius = st.slider("Coverage Radius (m)", 2, 10, 5)
    budget = st.number_input("Estimated Budget (THB)", 10000, 1000000, 100000)
    submitted = st.form_submit_button("Generate Design")

if submitted:
    st.success("Generating system design...")
    speakers = suggest_speaker_positions(room_width, room_length, spacing)
    fig = draw_layout(room_width, room_length, speakers, coverage_radius)
    st.subheader("📍 Speaker Layout")
    st.pyplot(fig)
    st.info(f"Suggested number of speakers: {len(speakers)}")
    df = load_product_database()
    if df is not None:
        st.subheader("🔊 Recommended Products")
        rec_speakers = df[df["Type"].str.contains("Full-range|Ceiling|Line Array", case=False)].head(len(speakers))
        st.dataframe(rec_speakers[["Model", "Brand", "Type", "Power (W)", "Coverage Angle", "Price (THB)", "Stock"]])
        total_cost = rec_speakers["Price (THB)"].sum()
        st.metric("💰 Estimated Total Cost", f"{total_cost:,.0f} THB")
        if total_cost > budget:
            st.warning("⚠️ Your estimated cost is higher than your budget.")
        else:
            st.success("✅ Estimated cost is within budget.")
    else:
        st.error("Product database not found or invalid.")
