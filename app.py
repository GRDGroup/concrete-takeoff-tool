import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt

# Sidebar Navigation
page = st.sidebar.selectbox("Select Page", ["Estimator", "Materials Summary"])

# --------------------------------
# Estimator Page
# --------------------------------
if page == "Estimator":
    st.title("Concrete, Rebar, XPS, Drain & Finish Takeoff Tool")

    # Set defaults
    wall_horizontal_spacing = 18
    wall_vertical_spacing = 18
    wall_rebar_size = "#4"
    slab_horizontal_spacing = 24
    slab_vertical_spacing = 24
    slab_rebar_size = "#4"
    footing_num_bars = 2
    footing_rebar_size = "#4"

    # User Inputs
    project_name = st.text_input("Project Name")
    estimator_name = st.text_input("Estimator")

    component = st.selectbox("Component Type", [
        "Foundation Wall", "Linear Footing", "Spread Footing",
        "Interior Slab", "Garage Slab", "Exterior Flatwork",
        "French Drain", "Big Foot Pier", "Sono Tube",
        "XPS Insulation", "Vapor Barrier", "Flatwork Finish", "Concrete Jump"
    ])

    length_ft = st.number_input("Length (ft)", min_value=0.0, value=0.0)
    height_ft = st.number_input("Height / Depth (ft)", min_value=0.0, value=0.0)
    thickness_in = st.number_input("Thickness (inches)", min_value=0.0, value=0.0)
    area_override = st.number_input("Square Footage Override (for slabs)", min_value=0.0, value=0.0)
    qty = st.number_input("Quantity (if applicable)", min_value=1, value=1)
    include_overage = st.checkbox("Apply 10% overage for structural / 5% for slabs", value=True)

    # Rebar Spacing Inputs
    st.markdown("### General Rebar Spacing Setup (Default if Plan Not Specific)")
    wall_spacing_in = st.selectbox("Default Wall Rebar Spacing (inches)", [12, 18, 24])
    slab_spacing_in = st.selectbox("Default Slab Rebar Spacing (inches)", [12, 18, 24])


    # Detailed Rebar Inputs
    if component in ["Foundation Wall", "Interior Slab", "Garage Slab", "Exterior Flatwork"]:
        st.markdown("### Specific Rebar Layout by Component (Per Engineering or Plan)")
        if component == "Foundation Wall":
            wall_horizontal_spacing = st.number_input("Horizontal Rebar Spacing for Wall (inches)", min_value=1, value=18)
            wall_vertical_spacing = st.number_input("Vertical Rebar Spacing for Wall (inches)", min_value=1, value=18)
            wall_rebar_size = st.selectbox("Wall Rebar Size", ["#3", "#4", "#5", "#6"])
        if component in ["Interior Slab", "Garage Slab", "Exterior Flatwork"]:
            slab_horizontal_spacing = st.number_input("Horizontal Rebar Spacing for Flatwork (inches)", min_value=1, value=24)
            slab_vertical_spacing = st.number_input("Vertical Rebar Spacing for Flatwork (inches)", min_value=1, value=24)
            slab_rebar_size = st.selectbox("Flatwork Rebar Size", ["#3", "#4", "#5", "#6"])

    elif component == "Linear Footing":
        st.markdown("### Footing Rebar Details")
        footing_num_bars = st.number_input("Number of Bars in Footing", min_value=1, value=4)
        footing_rebar_size = st.selectbox("Footing Rebar Size", ["#3", "#4", "#5", "#6"])

    # XPS Foam Inputs
    include_xps = st.checkbox("Include XPS Foam for Component", value=False)
    xps_r_value = st.selectbox("XPS R-Value", ["R-5", "R-10"])
    xps_price = 1.5 if xps_r_value == "R-5" else 3.0

    # Pricing Inputs
    st.markdown("### Pricing")
    concrete_zone = st.selectbox("Concrete Zone", ["Zone A - $185", "Zone B - $195", "Zone C - $205", "Zone D - $215"])
    concrete_price_per_cy = int(concrete_zone.split("$")[-1])
    rebar_price_per_ft = st.selectbox("Rebar Pricing", ["#4 - $0.45", "#5 - $0.55", "#6 - $0.60"])
    rebar_cost = float(rebar_price_per_ft.split("$")[-1])
    material_markup = st.slider("Material Markup %", min_value=0, max_value=50, value=25)

    finish_price = st.selectbox("Flatwork Finish Rate (per SF)", [
        "$8.25", "$8.50", "$8.75", "$9.00", "$9.25", "$9.50", "$10.00"
    ])
    finish_rate = float(finish_price.replace("$", ""))

    vapor_options = {
        "Stego 6 mil": 0.18,
        "Stego 10 mil": 0.25,
        "10 mil plastic": 0.12,
        "5 mil plastic": 0.09
    }
    vapor_type = st.selectbox("Vapor Barrier Type", list(vapor_options.keys()))
    vapor_price = vapor_options[vapor_type]

    # Calculate Button
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

        # Rebar calculations
        spacing_wall_h_ft = wall_horizontal_spacing / 12
        spacing_wall_v_ft = wall_vertical_spacing / 12
        spacing_slab_h_ft = slab_horizontal_spacing / 12
        spacing_slab_v_ft = slab_vertical_spacing / 12

        if component == "Foundation Wall":
            horiz_bars = math.ceil(length_ft / spacing_wall_h_ft)
            vert_bars = math.ceil(height_ft / spacing_wall_v_ft)
            total_bars = horiz_bars + vert_bars
            overlap_ft = (total_bars * (24 / 12))
            corner_overlap_ft = 4 * (18 / 12)
            rebar_lf = (horiz_bars * length_ft) + (vert_bars * height_ft) + overlap_ft + corner_overlap_ft

        elif component in ["Interior Slab", "Garage Slab", "Exterior Flatwork"]:
            horiz_bars = math.ceil(length_ft / spacing_slab_h_ft)
            vert_bars = math.ceil(height_ft / spacing_slab_v_ft)
            total_bars = horiz_bars + vert_bars
            overlap_ft = (total_bars * (24 / 12))
            corner_overlap_ft = 4 * (18 / 12)
            rebar_lf = (horiz_bars * length_ft) + (vert_bars * height_ft) + overlap_ft + corner_overlap_ft

        elif component == "Linear Footing":
            rebar_lf = footing_num_bars * length_ft
            overlap_ft = footing_num_bars * (24 / 12)
            rebar_lf += overlap_ft

        # Concrete Volume Calcs
        if component in ["Foundation Wall", "Interior Slab", "Garage Slab", "Exterior Flatwork"]:
            volume_cy = (slab_area * thickness_ft) / 27
            if include_overage:
                volume_cy *= 1.10 if component == "Foundation Wall" else 1.05
            if include_xps:
                xps_sf = slab_area
                xps_cost = xps_sf * xps_price
                raw_total += xps_cost

        elif component == "Linear Footing":
            volume_cy = (length_ft * height_ft * thickness_ft) / 27
            if include_overage:
                volume_cy *= 1.10

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

        # Expansion Joint Rolls
        expansion_joint_rolls = 0
        expansion_joint_cost = 0

        if component in ["Interior Slab", "Garage Slab", "Exterior Flatwork"]:
            perimeter_ft = (2 * length_ft) + (2 * height_ft)
            expansion_joint_rolls = math.ceil(perimeter_ft / 45)
            expansion_joint_cost = expansion_joint_rolls * 25
            raw_total += expansion_joint_cost

        # Output Results
        st.markdown("### Results")
        result = pd.DataFrame([{
            "Project": project_name,
            "Estimator": estimator_name,
            "Component": component,
            "Length_ft": length_ft,
            "Height_ft": height_ft,
            "Thickness_in": thickness_in,
            "Quantity": qty,
            "Concrete_CY": round(volume_cy, 2),
            "Rebar_LF": round(rebar_lf, 2),
            "XPS_SF": round(xps_sf, 2),
            "XPS_Cost": round(xps_cost, 2),
            "Total_Cost": round(raw_total, 2),
            "Sale_Price": round(total_sale, 2)
        }])

        if "takeoff_data" not in st.session_state:
            st.session_state.takeoff_data = pd.DataFrame()

        st.session_state.takeoff_data = pd.concat([st.session_state.takeoff_data, result], ignore_index=True)

# --------------------------------
# Materials Summary Page
# --------------------------------
if page == "Materials Summary":
    st.title("📦 Materials & Concrete Summary")

    if "takeoff_data" not in st.session_state or st.session_state.takeoff_data.empty:
        st.warning("No takeoff data available yet. Please add items first in the Estimator tab.")
    else:
        df = st.session_state.takeoff_data
        st.subheader("Concrete Volumes")
        st.metric("Total Concrete CY", round(df["Concrete_CY"].sum(), 2))
        st.metric("Total Rebar LF", round(df["Rebar_LF"].sum(), 2))
        st.metric("Total XPS SF", round(df["XPS_SF"].sum(), 2))

        st.subheader("Cost Summary")
        materials_cost = df["Total_Cost"].sum()
        sale_total = df["Sale_Price"].sum()
        margin_amount = sale_total - materials_cost
        margin_percent = (margin_amount / sale_total * 100) if sale_total else 0

        st.metric("Total Material Cost", f"${round(materials_cost,2):,}")
        st.metric("Total Sale Price", f"${round(sale_total,2):,}")
        st.metric("Profit Margin", f"${round(margin_amount,2):,} ({round(margin_percent,1)}%)")


