import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MECHMIND AI — Industrial Suite", page_icon="⚙️", layout="wide")

# Sidebar Configuration
st.sidebar.title("⚙️ MECHMIND AI")
st.sidebar.markdown("**Industrial Design Suite** | Developer: Chaitanya")
st.sidebar.markdown("---")

module = st.sidebar.radio(
    "Select Engineering Module",
    [
        "Spur Gear Suite (Lewis & Dynamic)", 
        "Shaft Design (ASME & von Mises)", 
        "Bearing Selection (ISO 281)", 
        "Fastener & Joint Analysis", 
        "Comprehensive Material DB"
    ]
)

st.title("⚙️ MECHMIND AI — Heavy Machinery CAD/CAE Engine")
st.caption("Standardized Machine Design Algorithms | Industrial Standards")

# =========================================================
# 1. SPUR GEAR SUITE (Lewis & Dynamic Analysis)
# =========================================================
if module == "Spur Gear Suite (Lewis & Dynamic)":
    st.header("⚙️ Heavy-Duty Spur Gear Analysis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        power = st.number_input("Power Transmitted (kW)", value=30.0, step=5.0)
        speed_p = st.number_input("Pinion Speed (RPM)", value=1440.0, step=50.0)
        gear_ratio = st.number_input("Desired Gear Ratio ($i$)", value=3.5, step=0.1)
    with col2:
        teeth_p = st.number_input("Pinion Teeth ($Z_p$)", value=18, step=1)
        module_m = st.number_input("Module ($m$) [mm]", value=5.0, step=0.5)
        face_width = st.number_input("Face Width ($b$) [mm]", value=50.0, step=5.0)
    with col3:
        pressure_angle = st.selectbox("Pressure Angle ($\phi$)", [20, 14.5, 25])
        allowable_bending = st.number_input("Allowable Bending Stress (MPa)", value=220.0, step=10.0)
        surface_hardness = st.number_input("Brinell Hardness (BHN)", value=300, step=10)

    if st.button("Run Industrial Gear Analysis"):
        teeth_g = math.ceil(teeth_p * gear_ratio)
        actual_ratio = teeth_g / teeth_p
        
        pcd_p = teeth_p * module_m
        pcd_g = teeth_g * module_m
        center_dist = (pcd_p + pcd_g) / 2
        
        # Power & Torque
        torque_p = (9550 * power * 1000) / speed_p if speed_p > 0 else 0  # N-mm
        tangential_force = (2 * torque_p) / pcd_p if pcd_p > 0 else 0  # N
        pitch_velocity = (math.pi * pcd_p * speed_p) / (60 * 1000)  # m/s
        
        # Velocity Factor (Barth Factor)
        cv = 6 / (6 + pitch_velocity) if pitch_velocity <= 13 else 5.6 / (5.6 + math.sqrt(pitch_velocity))
        
        # Lewis Factor Analysis
        y_lewis = 0.154 - (0.912 / teeth_p) if pressure_angle == 20 else 0.124 - (0.684 / teeth_p)
        bending_stress = tangential_force / (cv * face_width * module_m * y_lewis) if (cv * face_width * module_m * y_lewis) > 0 else 0
        
        # Wear Load (Buckingham Equation)
        k_wear = 0.16 * ((surface_hardness / 100) ** 2)
        q_factor = (2 * teeth_g) / (teeth_p + teeth_g)
        wear_load_capacity = pcd_p * face_width * q_factor * k_wear

        st.success("Analysis Complete!")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pinion / Gear PCD", f"{pcd_p:.1f} / {pcd_g:.1f} mm")
        c2.metric("Center Distance", f"{center_dist:.1f} mm")
        c3.metric("Pitch Line Velocity", f"{pitch_velocity:.2f} m/s")
        c4.metric("Tangential Load ($F_t$)", f"{tangential_force:.1f} N")

        m1, m2, m3 = st.columns(3)
        m1.metric("Pinion Torque", f"{(torque_p/1000):.2f} N·m")
        m2.metric("Induced Stress ($\sigma_b$)", f"{bending_stress:.2f} MPa")
        m3.metric("Wear Capacity ($W_w$)", f"{wear_load_capacity:.1f} N")

        if bending_stress <= allowable_bending:
            st.success(f"✅ Design Safe against Fatigue Bending ($\sigma_b$ < {allowable_bending} MPa)")
        else:
            st.error("⚠️ Design Unsafe in Bending! Increase module or face width.")

# =========================================================
# 2. SHAFT DESIGN (ASME Code & von Mises Stress)
# =========================================================
elif module == "Shaft Design (ASME & von Mises)":
    st.header("🌀 Heavy Machinery Shaft Sizing (ASME & Distortion Energy)")
    
    col1, col2 = st.columns(2)
    with col1:
        torque_input = st.number_input("Applied Torque ($T$) [N·m]", value=850.0, step=50.0)
        bending_moment = st.number_input("Applied Bending Moment ($M$) [N·m]", value=1200.0, step=50.0)
        axial_force = st.number_input("Axial Force ($F_a$) [N]", value=5000.0, step=500.0)
    with col2:
        allowable_shear = st.number_input("Allowable Shear ($\tau_{allow}$) [MPa]", value=45.0, step=5.0)
        kb = st.number_input("Fatigue Bending Factor ($K_b$)", value=1.75, step=0.05)
        kt = st.number_input("Fatigue Torsion Factor ($K_t$)", value=1.25, step=0.05)

    if st.button("Calculate Minimum Shaft Size"):
        t_eq = math.sqrt((kb * bending_moment)**2 + (kt * torque_input)**2)  # N-m
        t_eq_nmm = t_eq * 1000
        
        # Diameter based on ASME Shear Code
        dia_asme = ((16 * t_eq_nmm) / (math.pi * allowable_shear)) ** (1/3)
        recommended_dia = math.ceil(dia_asme / 5) * 5  # Rounded to standard 5mm increment
        
        # Stress Verification on Recommended Diameter
        area = (math.pi * (recommended_dia**2)) / 4
        z_modulus = (math.pi * (recommended_dia**3)) / 32
        zp_modulus = (math.pi * (recommended_dia**3)) / 16
        
        sigma_bending = (bending_moment * 1000) / z_modulus
        sigma_axial = axial_force / area
        sigma_total_normal = sigma_bending + sigma_axial
        tau_shear = (torque_input * 1000) / zp_modulus
        
        # von Mises Equivalent Stress
        von_mises = math.sqrt((sigma_total_normal**2) + 3*(tau_shear**2))

        st.success("Calculations Finalized!")
        c1, c2, c3 = st.columns(3)
        c1.metric("Equivalent Torque ($T_e$)", f"{t_eq:.2f} N·m")
        c2.metric("Min. Required Dia (ASME)", f"{dia_asme:.2f} mm")
        c3.metric("Standard Industrial Dia", f"{recommended_dia} mm")

        m1, m2 = st.columns(2)
        m1.metric("Induced Shear Stress ($\tau$)", f"{tau_shear:.2f} MPa")
        m2.metric("von Mises Stress ($\sigma_v$)", f"{von_mises:.2f} MPa")

# =========================================================
# 3. BEARING SELECTION (ISO 281 Standard)
# =========================================================
elif module == "Bearing Selection (ISO 281)":
    st.header("⭕ Industrial Bearing Life Calculation")
    
    col1, col2 = st.columns(2)
    with col1:
        radial_load = st.number_input("Radial Load ($F_r$) [kN]", value=12.5, step=0.5)
        axial_load = st.number_input("Axial Load ($F_a$) [kN]", value=4.2, step=0.2)
        operating_speed = st.number_input("Speed (RPM)", value=1750.0, step=50.0)
    with col2:
        c_dynamic = st.number_input("Basic Dynamic Rating ($C$) [kN]", value=48.0, step=2.0)
        bearing_type = st.selectbox("Bearing Category", ["Deep Groove Ball", "Cylindrical Roller", "Tapered Roller"])
        reliability = st.selectbox("Reliability Level (%)", [90, 95, 99])

    rel_factors = {90: 1.0, 95: 0.62, 99: 0.21}

    if st.button("Calculate Bearing Life"):
        x_factor, y_factor = (0.56, 1.45) if bearing_type == "Deep Groove Ball" else (0.4, 1.5)
        p_eq = (x_factor * radial_load) + (y_factor * axial_load)
        
        p_exponent = 3.0 if "Ball" in bearing_type else (10/3)
        a1 = rel_factors[reliability]
        
        l10_mr = (c_dynamic / p_eq) ** p_exponent if p_eq > 0 else 0
        l10a_mr = a1 * l10_mr
        l10_hours = (l10a_mr * 10**6) / (60 * operating_speed) if operating_speed > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Equiv. Dynamic Load ($P$)", f"{p_eq:.2f} kN")
        c2.metric(f"L10a Life ({reliability}% Rel.)", f"{l10a_mr:.2f} MR")
        c3.metric("Operating Life (Hours)", f"{int(l10_hours)} Hrs")

# =========================================================
# 4. FASTENER & JOINT ANALYSIS
# =========================================================
elif module == "Fastener & Joint Analysis":
    st.header("🔩 High-Strength Fastener Sizing & Tightening Torque")
    
    col1, col2 = st.columns(2)
    with col1:
        shear_load = st.number_input("Joint Shear Force (N)", value=15000.0, step=1000.0)
        tensile_load = st.number_input("Joint Tensile Force (N)", value=8000.0, step=500.0)
        num_bolts = st.number_input("Number of Bolts", value=4, step=1)
    with col2:
        bolt_grade = st.selectbox("Property Class", ["8.8", "10.9", "12.9"])
        bolt_size = st.selectbox("Metric Thread Size", ["M8", "M10", "M12", "M16", "M20", "M24"])
        friction_coeff = st.number_input("Nut/Thread Friction ($\mu$)", value=0.15, step=0.01)

    bolt_specs = {
        "M8": {"area": 36.6, "dia": 8},
        "M10": {"area": 58.0, "dia": 10},
        "M12": {"area": 84.3, "dia": 12},
        "M16": {"area": 157.0, "dia": 16},
        "M20": {"area": 245.0, "dia": 20},
        "M24": {"area": 353.0, "dia": 24}
    }
    yield_specs = {"8.8": 640, "10.9": 900, "12.9": 1080}

    if st.button("Analyze Fastener Performance"):
        area = bolt_specs[bolt_size]["area"]
        dia = bolt_specs[bolt_size]["dia"]
        sy = yield_specs[bolt_grade]
        
        per_bolt_shear = shear_load / num_bolts
        per_bolt_tensile = tensile_load / num_bolts
        
        sigma_t = per_bolt_tensile / area
        tau_s = per_bolt_shear / area
        von_mises_bolt = math.sqrt(sigma_t**2 + 3*(tau_s**2))
        
        fos = sy / von_mises_bolt if von_mises_bolt > 0 else 0
        
        # Tightening Torque Calculation (T = K * F * d)
        preload_force = 0.75 * area * sy  # 75% Proof load
        tightening_torque = (0.2 * preload_force * dia) / 1000  # N-m

        c1, c2, c3 = st.columns(3)
        c1.metric("Eq. Stress per Bolt", f"{von_mises_bolt:.2f} MPa")
        c2.metric("Factor of Safety (FOS)", f"{fos:.2f}")
        c3.metric("Tightening Torque", f"{tightening_torque:.1f} N·m")

        if fos >= 2.0:
            st.success("✅ Fastener Design Conforms to Safety Limits")
        else:
            st.error("⚠️ Insufficient FOS! Add more bolts or upgrade bolt size/grade.")

# =========================================================
# 5. COMPREHENSIVE MATERIAL DATABASE
# =========================================================
elif module == "Comprehensive Material DB":
    st.header("📚 Advanced Industrial Material Matrix")

    materials_data = {
        "Structural Steel (A36)": {"Type": "Ferrous", "Yield (MPa)": 250, "UTS (MPa)": 400, "Modulus (GPa)": 200, "Density (kg/m³)": 7850},
        "Medium Carbon Steel (EN8 / C45)": {"Type": "Ferrous", "Yield (MPa)": 450, "UTS (MPa)": 650, "Modulus (GPa)": 207, "Density (kg/m³)": 7850},
        "Alloy Steel (4140 / 42CrMo4)": {"Type": "Ferrous", "Yield (MPa)": 655, "UTS (MPa)": 850, "Modulus (GPa)": 210, "Density (kg/m³)": 7850},
        "Stainless Steel (SS316)": {"Type": "Ferrous", "Yield (MPa)": 290, "UTS (MPa)": 580, "Modulus (GPa)": 193, "Density (kg/m³)": 8000},
        "Aluminum 6061-T6": {"Type": "Non-Ferrous", "Yield (MPa)": 276, "UTS (MPa)": 310, "Modulus (GPa)": 68.9, "Density (kg/m³)": 2700},
        "Aluminum 7075-T6": {"Type": "Non-Ferrous", "Yield (MPa)": 503, "UTS (MPa)": 572, "Modulus (GPa)": 71.0, "Density (kg/m³)": 2810},
        "Titanium Grade 5 (Ti-6Al-4V)": {"Type": "Aerospace Alloy", "Yield (MPa)": 880, "UTS (MPa)": 950, "Modulus (GPa)": 113.8, "Density (kg/m³)": 4430},
        "Inconel 718": {"Type": "Superalloy", "Yield (MPa)": 1100, "UTS (MPa)": 1375, "Modulus (GPa)": 200, "Density (kg/m³)": 8190},
        "Ductile Cast Iron (65-45-12)": {"Type": "Cast Iron", "Yield (MPa)": 310, "UTS (MPa)": 450, "Modulus (GPa)": 169, "Density (kg/m³)": 7100},
        "PEEK Polymer": {"Type": "Polymer", "Yield (MPa)": 100, "UTS (MPa)": 110, "Modulus (GPa)": 4.1, "Density (kg/m³)": 1320}
    }

    df = pd.DataFrame(materials_data).T
    
    selected_mat = st.selectbox("Search & View Material Properties", df.index.tolist())
    mat_info = df.loc[selected_mat]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Category", mat_info["Type"])
    m2.metric("Yield Strength", f"{mat_info['Yield (MPa)']} MPa")
    m3.metric("UTS", f"{mat_info['UTS (MPa)']} MPa")
    m4.metric("Young's Modulus", f"{mat_info['Modulus (GPa)']} GPa")

    st.markdown("---")
    st.subheader("Full Material Specification Sheet")
    st.dataframe(df, use_container_width=True)