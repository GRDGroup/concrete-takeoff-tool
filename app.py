import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt

st.title("Concrete, Rebar, XPS, Drain & Finish Takeoff Tool")

st.markdown("Enter data for each component below. The app will calculate volumes, rebar, pricing, and output a structured dataset row. You can enter multiple components before downloading the final dataset.")

project_name = st.text_input("Project Name")
estimator_name = st.text_input("Estimator")

component = st.selectbox("Component Type", [
    "Foundation Wall", "Linear Footing", "Spread Footing",
    "Interior Slab", "Garage Slab", "French Drain", "XPS Insulation",
    "Vapor Barrier", "Flatwork Finish"
])

length_ft = st.number_input("Length (ft)", min_value=0.0, value=0.0)
height_ft = st.number_input("Height / Depth (ft)", min_value=0.0, value=0.0)
thickness_in = st.number_input("Thickness (inches)", min_value=0.0, value=0.0)
area_override = st.number_input("Square Footage Override (for slabs)", min_value=0.0, value=0.0)
qty = st.number_input("Quantity (if applicable)", min_value=1, value=1)
include_overage = st.checkbox("Apply 10% overage for structural / 5% for slabs", value=True)
include_xps = st.checkbox("Include XPS Foam for Component", value=False)
xps_r_value = st.selectbox("XPS R-Value", ["R-5", "R-10"])
xps_price = 1.41 if xps_r_value == "R-10" else 0.71

# Pricing Inputs
st.markdown("### Pricing")
concrete_zone = st.selectbox("Concrete Zone", ["Zone A - $185", "Zone B - $195", "Zone C - $205", "Zone D - $215"])
concrete_price_per_cy = int(concrete_zone.split("$")[-1])
rebar_price_per_ft = st.selectbox("Rebar Pricing", ["#4 - $0.45", "#5 - $0.55", "#6 - $0.60"])
rebar_cost = float(rebar_price_per_ft.split("$")[-1])
material_markup = st.slider("Material Markup %", min_value=0, max_value=50, value=25)

# Flatwork Finish Price
finish_price = st.selectbox("Flatwork Finish Rate (per SF)", [
    "$8.25", "$8.50", "$8.75", "$9.00", "$9.25", "$9.50", "$10.00"
])
finish_rate = float(finish_price.replace("$", ""))

# Vapor Barrier Pricing
vapor_options = {
    "Stego 6 mil": 0.18,
    "Stego 10 mil": 0.25,
    "10 mil plastic": 0.12,
    "5 mil plastic": 0.09
}
vapor_type = st.selectbox("Vapor Barrier Type", list(vapor_options.keys()))
vapor_price = vapor_options[vapor_type]

if st.button("Calculate"):
    thickness_ft = thickness_in / 12 if thickness_in > 0 else 0.0
    volume_cy = 0.0
    rebar_lf = 0.0
    xps_sf = 0.0
    xps_cost = 0.0
    drain_cost = 0.0
    vapor_cost = 0.0
    finish_cost = 0.0
    total_cost = 0.0
    total_sale = 0.0
    raw_total = 0.0
    rock_volume_cy = 0.0
    drain_fabric_lf = 0.0
    drain_pipe_lf = 0.0

    slab_area = area_override if area_override > 0 else length_ft * height_ft

    if component in ["Foundation Wall", "Interior Slab", "Garage Slab"]:
        volume_cy = (slab_area * thickness_ft) / 27
        if include_overage:
            volume_cy *= 1.10 if component == "Foundation Wall" else 1.05
        if "Slab" in component:
            rebar_lf = slab_area * 0.25
        else:
            h_bars = math.ceil(height_ft / 1) * length_ft
            v_bars = math.ceil(length_ft / 1.5) * height_ft
            rebar_lf = h_bars + v_bars
        if include_xps:
            xps_sf = slab_area if "Slab" in component else length_ft * height_ft
            xps_cost = xps_sf * xps_price
            raw_total += xps_cost

    elif component == "Linear Footing":
        volume_cy = (length_ft * height_ft * thickness_ft) / 27
        if include_overage:
            volume_cy *= 1.10
        rebar_lf = length_ft * 2

    elif component == "Spread Footing":
        volume_per = (length_ft * height_ft * thickness_ft) / 27
        volume_cy = volume_per * qty
        if include_overage:
            volume_cy *= 1.10

    elif component == "XPS Insulation":
        xps_sf = slab_area
        xps_cost = xps_sf * xps_price
        raw_total = xps_cost
        total_sale = raw_total * (1 + material_markup / 100)

    elif component == "French Drain":
        rock_volume_cy = (2 * 2 * length_ft) / 27 * 1.10
        drain_fabric_lf = length_ft
        drain_pipe_lf = length_ft
        rock_cost = rock_volume_cy * 33
        fabric_cost = (length_ft / 360) * 946
        pipe_cost = (length_ft / 100) * 177
        raw_total = rock_cost + fabric_cost + pipe_cost
        total_sale = raw_total * (1 + material_markup / 100)
        drain_cost = raw_total

    elif component == "Vapor Barrier":
        vapor_area = slab_area
        raw_total = vapor_area * vapor_price
        total_sale = raw_total * (1 + material_markup / 100)
        vapor_cost = raw_total

    elif component == "Flatwork Finish":
        raw_total = slab_area * finish_rate
        total_sale = raw_total * (1 + material_markup / 100)
        finish_cost = raw_total

    if component not in ["XPS Insulation", "French Drain", "Vapor Barrier", "Flatwork Finish"]:
        concrete_cost = volume_cy * concrete_price_per_cy
        rebar_cost_total = rebar_lf * rebar_cost if rebar_lf != 0 else 0
        raw_total += concrete_cost + rebar_cost_total
        total_sale = raw_total * (1 + material_markup / 100)

    st.markdown("### Results")
    result = pd.DataFrame([{
        "Project": project_name,
        "Estimator": estimator_name,
        "Component": component,
        "Length_ft": length_ft,
        "Height_ft": height_ft,
        "Thickness_in": thickness_in,
        "Quantity": qty,
        "Concrete_CY": round(volume_cy, 2) if component not in ["French Drain"] and volume_cy > 0 else 0,
        "Rebar_LF": round(rebar_lf, 2) if rebar_lf > 0 else 0,
        "XPS_SF": round(xps_sf, 2) if xps_sf > 0 else 0,
        "XPS_R_Value": xps_r_value if include_xps else "-",
        "XPS_Cost": round(xps_cost, 2) if xps_cost > 0 else 0,
        "Rock_CY": round(rock_volume_cy, 2) if component == "French Drain" else 0,
        "Drain_Fabric_LF": round(drain_fabric_lf, 2) if component == "French Drain" else 0,
        "Drain_Pipe_LF": round(drain_pipe_lf, 2) if component == "French Drain" else 0,
        "Vapor_Type": vapor_type if component == "Vapor Barrier" else "-",
        "Vapor_Cost": round(vapor_cost, 2) if vapor_cost else 0,
        "Finish_Cost": round(finish_cost, 2) if finish_cost else 0,
        "Concrete_Cost": round(concrete_cost, 2) if component not in ["XPS Insulation", "French Drain", "Vapor Barrier", "Flatwork Finish"] else 0,
        "Rebar_Cost": round(rebar_cost_total, 2) if rebar_lf > 0 else 0,
        "Drain_Cost": round(drain_cost, 2) if component == "French Drain" else 0,
        "Total_Cost": round(raw_total, 2),
        "Sale_Price": round(total_sale, 2)
    }])
    st.dataframe(result)

    if "takeoff_data" not in st.session_state:
        st.session_state.takeoff_data = pd.DataFrame()

    if st.button("Add to Project Dataset"):
        st.session_state.takeoff_data = pd.concat([st.session_state.takeoff_data, result], ignore_index=True)

if "takeoff_data" in st.session_state and not st.session_state.takeoff_data.empty:
    st.markdown("## Project Takeoff Summary")
    st.dataframe(st.session_state.takeoff_data)
    st.download_button("Download CSV", st.session_state.takeoff_data.to_csv(index=False), file_name="takeoff_dataset.csv")

    # SUMMARY VISUALIZATION
    st.markdown("### 📊 Project Summary Dashboard")
    summary = st.session_state.takeoff_data
    total_concrete = summary["Concrete_CY"].sum()
    total_rebar = summary["Rebar_LF"].sum()
    total_xps = summary["XPS_SF"].sum()
    total_drain = summary["Rock_CY"].sum()
    total_cost = summary["Total_Cost"].sum()
    total_sale = summary["Sale_Price"].sum()
    margin = total_sale - total_cost
    margin_pct = (margin / total_sale * 100) if total_sale > 0 else 0

    st.metric("Total Concrete (CY)", round(total_concrete, 2))
    st.metric("Total Rebar (LF)", round(total_rebar, 2))
    st.metric("Total XPS (SF)", round(total_xps, 2))
    st.metric("Total Drain Rock (CY)", round(total_drain, 2))
    st.metric("Total Cost", f"${round(total_cost, 2):,.2f}")
    st.metric("Sale Price", f"${round(total_sale, 2):,.2f}")
    st.metric("Margin", f"${round(margin, 2):,.2f} ({round(margin_pct, 1)}%)")

    fig, ax = plt.subplots()
    ax.bar(["Concrete", "Rebar", "XPS", "Drain"], [total_concrete, total_rebar, total_xps, total_drain], color=["#6699CC", "#FF9966", "#88CC88", "#CC6666"])
    ax.set_ylabel("Total Quantity")
    ax.set_title("Material Summary")
    st.pyplot(fig)



