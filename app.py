import streamlit as st
import pandas as pd
import math

st.title("Concrete & Rebar Takeoff Tool")

st.markdown("Enter data for each component below. The app will calculate volumes and rebar, and output a structured dataset row.")

component = st.selectbox("Component Type", ["Foundation Wall", "Linear Footing", "Spread Footing", "Interior Slab", "Garage Slab"])

length_ft = st.number_input("Length (ft)", min_value=0.0, value=0.0)
height_ft = st.number_input("Height / Depth (ft)", min_value=0.0, value=0.0)
thickness_in = st.number_input("Thickness (inches)", min_value=0.0, value=0.0)
qty = st.number_input("Quantity (for spread footings only)", min_value=1, value=1)
include_overage = st.checkbox("Apply 10% overage for structural / 5% for slabs", value=True)

if st.button("Calculate"):
    thickness_ft = thickness_in / 12 if thickness_in > 0 else 0.0
    volume_cy = 0.0
    rebar_lf = 0.0

    if component in ["Foundation Wall", "Interior Slab", "Garage Slab"]:
        area = length_ft * height_ft
        volume_cy = (length_ft * height_ft * thickness_ft) / 27
        if include_overage:
            volume_cy *= 1.10 if component == "Foundation Wall" else 1.05
        if "Slab" in component:
            rebar_lf = length_ft * height_ft * 0.25  # 18" OC each way
        else:
            h_bars = math.ceil(height_ft / 1) * length_ft
            v_bars = math.ceil(length_ft / 1.5) * height_ft
            rebar_lf = h_bars + v_bars

    elif component == "Linear Footing":
        volume_cy = (length_ft * height_ft * thickness_ft) / 27
        if include_overage:
            volume_cy *= 1.10
        rebar_lf = length_ft * 2  # Approx. 2 bars per LF

    elif component == "Spread Footing":
        volume_per = (length_ft * height_ft * thickness_ft) / 27
        volume_cy = volume_per * qty
        if include_overage:
            volume_cy *= 1.10

    st.markdown("### Results")
    result = pd.DataFrame([{
        "Component": component,
        "Length_ft": length_ft,
        "Height_ft": height_ft,
        "Thickness_in": thickness_in,
        "Quantity": qty,
        "Concrete_CY": round(volume_cy, 2),
        "Rebar_LF": round(rebar_lf, 2) if rebar_lf > 0 else "-"
    }])
    st.dataframe(result)

    # Optionally allow saving the row
    if "takeoff_data" not in st.session_state:
        st.session_state.takeoff_data = pd.DataFrame()

    if st.button("Add to Project Dataset"):
        st.session_state.takeoff_data = pd.concat([st.session_state.takeoff_data, result], ignore_index=True)

if "takeoff_data" in st.session_state and not st.session_state.takeoff_data.empty:
    st.markdown("## Project Takeoff Summary")
    st.dataframe(st.session_state.takeoff_data)
    st.download_button("Download CSV", st.session_state.takeoff_data.to_csv(index=False), file_name="takeoff_dataset.csv")
