"""
MediGuide AI — Find Nearby Healthcare Providers (India National Care Network).
Global & Regional Geospatial Care Discovery powered by OpenStreetMap & Verified Health Registries.

Features:
- High-Accuracy HTML5 Device GPS (Hardware sensor, works worldwide)
- Intelligent Clinical Triage Routing (Pre-filters specialty when arriving from Symptom Assessment)
- Contextual City & Locality Precision Anchors (Dynamic based on selected city)
- Zero Mismatches: Strict clinical specialty taxonomy matching
- Strict Radius Enforcement (Guaranteed <= selected radius)
"""

import sys
import importlib
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

for _mod in list(sys.modules.keys()):
    if _mod.startswith("src.") or _mod == "src":
        try:
            importlib.reload(sys.modules[_mod])
        except Exception:
            pass

st.set_page_config(
    page_title="Find Nearby Healthcare — MediGuide AI",
    page_icon="📍",
    layout="wide"
)

from src.ui_components import apply_theme, render_sidebar
from src.config import SUPPORTED_COUNTRIES, get_active_country
from src.geocoding_service import geocoding_service
from src.provider_search import provider_search_service
from src.specialty_recommender import SPECIALTY_CATALOG

apply_theme()
render_sidebar()

country_cfg = get_active_country()
country_name = country_cfg.get("name", "India")
country_code = country_cfg.get("code", "in")

# Page Header
st.title("📍 Find Nearby Healthcare Providers (India)")
st.markdown(
    f"Search for hospitals, specialized clinics, and medical doctors across **India**. "
    f"Powered by OpenStreetMap geospatial data and curated regional facility directories."
)

# ==========================================
# 🩺 CLINICAL TRIAGE PRE-POPULATION
# ==========================================
# Check if user arrived from Symptom Assistant with a recommended specialty
is_from_assistant = st.session_state.get("specialty_from_assistant", False)
target_spec_raw = st.session_state.get("target_specialty", "All")
patient_name = st.session_state.get("target_patient_name", "Patient")

# Build complete, deduplicated specialty list
all_specialty_names = ["All"]
for s in SPECIALTY_CATALOG:
    if s.specialty not in all_specialty_names:
        all_specialty_names.append(s.specialty)

# Determine default dropdown index
spec_index = 0
if is_from_assistant and target_spec_raw and target_spec_raw != "All":
    target_clean = target_spec_raw.lower().strip()
    for idx, name in enumerate(all_specialty_names):
        name_clean = name.lower().strip()
        if target_clean in name_clean or name_clean in target_clean:
            spec_index = idx
            break

# If coming from assistant, show clinical routing banner with 1-click clear
if is_from_assistant and spec_index > 0:
    matched_spec = all_specialty_names[spec_index]
    c_info, c_clear = st.columns([4, 1.2])
    with c_info:
        st.info(
            f"🩺 **Clinical Triage Routing Active:** Specialty pre-filtered to **{matched_spec}** "
            f"based on recent assessment for **{patient_name}**."
        )
    with c_clear:
        if st.button("✕ View All Specialties", use_container_width=True):
            st.session_state["specialty_from_assistant"] = False
            st.session_state["target_specialty"] = "All"
            st.rerun()

# Handle incoming query parameters from HTML5 GPS sensor
if "live_loc" in st.query_params:
    st.session_state["preset_loc"] = st.query_params["live_loc"]
if "live_lat" in st.query_params and "live_lon" in st.query_params:
    try:
        st.session_state["live_lat"] = float(st.query_params["live_lat"])
        st.session_state["live_lon"] = float(st.query_params["live_lon"])
        st.session_state["is_device_gps"] = True
    except (ValueError, TypeError):
        pass

# Default search location fallback
default_loc = country_cfg.get("default_locality", "New Delhi, Delhi, India")
if "preset_loc" in st.session_state and st.session_state["preset_loc"]:
    default_loc = st.session_state["preset_loc"]

# ==========================================
# 🛰️ UNIVERSAL HIGH-PRECISION GPS SENSOR
# ==========================================
gps_component_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .gps-card {
            background: #f0fdfa;
            border: 1px solid #0d9488;
            border-radius: 8px;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
        }
        .gps-info { flex: 1; min-width: 260px; }
        .gps-title { font-weight: 700; color: #0f766e; font-size: 14px; display: flex; align-items: center; gap: 6px; }
        .gps-desc { font-size: 12px; color: #475569; margin-top: 2px; }
        .gps-btn {
            background: #0d9488;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 13px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        .gps-btn:hover { background: #0f766e; }
        .gps-btn:disabled { background: #94a3b8; cursor: not-allowed; }
        #status-msg { font-size: 12px; margin-top: 6px; width: 100%; display: none; }
    </style>
</head>
<body>
    <div class="gps-card">
        <div class="gps-info">
            <div class="gps-title">
                <span>🛰️ High-Precision Device GPS Sensor</span>
            </div>
            <div class="gps-desc">
                Uses your device's built-in GPS / Wi-Fi triangulation directly. Works in any city or town worldwide.
            </div>
        </div>
        <button id="gpsBtn" class="gps-btn" onclick="captureExactGPS()">
            📡 Detect My Current Location
        </button>
        <div id="status-msg"></div>
    </div>

    <script>
    function captureExactGPS() {
        const btn = document.getElementById('gpsBtn');
        const status = document.getElementById('status-msg');
        status.style.display = 'block';

        if (!navigator.geolocation) {
            status.innerHTML = '❌ Geolocation is not supported by your current browser.';
            status.style.color = '#dc2626';
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '🛰️ Acquiring GPS...';
        status.innerHTML = '📡 Requesting device satellite coordinates (High Accuracy)...';
        status.style.color = '#0284c7';

        navigator.geolocation.getCurrentPosition(
            async function(pos) {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const acc = Math.round(pos.coords.accuracy);

                status.innerHTML = `✅ Location Fixed: ${lat.toFixed(4)}, ${lon.toFixed(4)} (±${acc}m accuracy). Resolving address...`;
                status.style.color = '#0f766e';

                let locName = 'Current Location';
                try {
                    const resp = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
                    if (resp.ok) {
                        const data = await resp.json();
                        if (data && data.display_name) {
                            locName = data.display_name.split(',').slice(0, 3).join(',').trim();
                        }
                    }
                } catch(e) {
                    console.log(e);
                }

                try {
                    const url = new URL(window.top.location.href);
                    url.searchParams.set('live_lat', lat.toFixed(5));
                    url.searchParams.set('live_lon', lon.toFixed(5));
                    url.searchParams.set('live_loc', locName);
                    url.searchParams.set('gps_active', '1');
                    window.top.location.href = url.toString();
                } catch(err) {
                    status.innerHTML = `✅ Coordinates: ${lat.toFixed(5)}, ${lon.toFixed(5)}`;
                }
            },
            function(err) {
                btn.disabled = false;
                btn.innerHTML = '📡 Detect My Current Location';
                let reason = 'Unable to acquire GPS signal.';
                if (err.code === 1) reason = 'Location permission was denied. Please allow location in your browser address bar.';
                else if (err.code === 2) reason = 'Position unavailable. Please search manually below.';
                else if (err.code === 3) reason = 'GPS request timed out.';
                status.innerHTML = '⚠️ ' + reason;
                status.style.color = '#b45309';
            },
            { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
        );
    }
    </script>
</body>
</html>
"""

components.html(gps_component_html, height=80)

# If device GPS is active, show confirmation
if st.session_state.get("is_device_gps") and "live_lat" in st.session_state:
    st.success(
        f"✅ **GPS Position Active:** `{st.session_state['live_lat']:.4f}° N, {st.session_state['live_lon']:.4f}° E` "
        f"— Anchor: **{st.session_state.get('preset_loc', 'Current Device Location')}**"
    )

# ==========================================
# 🔍 SEARCH BAR & REGIONAL CONTROLS
# ==========================================
col_input, col_btn = st.columns([4, 1.2])
with col_input:
    location_query = st.text_input(
        f"Enter City, Town, Locality or Landmark ({country_name}):",
        value=default_loc,
        placeholder="e.g. New Delhi, Mumbai, Bengaluru, Patna, Muzaffarpur, Kolkata, Lucknow, Hyderabad"
    )
with col_btn:
    st.write("")
    st.write("")
    search_button = st.button("🔍 Search Providers", type="primary", use_container_width=True)

# Dynamic Popular Region Presets for Active Country
preset_regions = country_cfg.get("popular_regions", [])
if preset_regions:
    st.markdown(f"<div style='font-size:0.85rem; color:#475569; margin-bottom:4px; font-weight:600;'>⚡ Quick City Presets ({country_name}):</div>", unsafe_allow_html=True)
    chip_cols = st.columns(min(len(preset_regions), 8))
    for i, reg in enumerate(preset_regions[:8]):
        with chip_cols[i]:
            clean_short = reg.split(",")[0].strip()
            if st.button(f"📍 {clean_short}", key=f"chip_reg_{i}", use_container_width=True):
                st.session_state["preset_loc"] = reg
                if "live_lat" in st.session_state:
                    del st.session_state["live_lat"]
                if "live_lon" in st.session_state:
                    del st.session_state["live_lon"]
                st.session_state["is_device_gps"] = False
                location_query = reg
                st.rerun()

# ==========================================
# 📍 UNIVERSAL INDIAN HEALTHCARE HUBS & DISTRICT ANCHORS
# Dynamically displayed across all major Indian cities & metro areas
# ==========================================
INDIAN_HEALTHCARE_HUBS = {
    "delhi": {
        "city_title": "New Delhi / NCR",
        "hubs": [
            ("AIIMS Ansari Nagar", 28.5672, 77.2100, "AIIMS Ansari Nagar, New Delhi"),
            ("Saket Medical Corridor", 28.5284, 77.2120, "Saket, New Delhi"),
            ("Connaught Place Hub", 28.6315, 77.2167, "Connaught Place, New Delhi"),
            ("Safdarjung Hospital", 28.5694, 77.2078, "Safdarjung, New Delhi"),
            ("Okhla / Escorts Heart", 28.5583, 77.2831, "Okhla Road, New Delhi"),
            ("Rajinder Nagar / Ganga Ram", 28.6393, 77.1896, "Old Rajinder Nagar, New Delhi"),
            ("Rohini Medical Hub", 28.7159, 77.1190, "Rohini, New Delhi"),
            ("Dwarka Sector 12", 28.5921, 77.0460, "Dwarka Sector 12, New Delhi")
        ]
    },
    "mumbai": {
        "city_title": "Mumbai MMR",
        "hubs": [
            ("Parel (KEM / Tata)", 19.0033, 72.8422, "Parel, Mumbai, Maharashtra"),
            ("Bandra West (Lilavati)", 19.0520, 72.8290, "Bandra West, Mumbai, Maharashtra"),
            ("Andheri West (Kokilaben)", 19.1310, 72.8250, "Andheri West, Mumbai, Maharashtra"),
            ("Mahim West (Hinduja)", 19.0330, 72.8400, "Mahim West, Mumbai, Maharashtra"),
            ("Marine Lines (Bombay Hosp)", 18.9410, 72.8280, "Marine Lines, Mumbai, Maharashtra"),
            ("Powai / Hiranandani", 19.1197, 72.9051, "Powai, Mumbai, Maharashtra"),
            ("Dadar East (Aditya Jyot)", 19.0180, 72.8510, "Dadar East, Mumbai, Maharashtra"),
            ("Fort / St. George", 18.9410, 72.8360, "Fort, Mumbai, Maharashtra")
        ]
    },
    "bengaluru": {
        "city_title": "Bengaluru",
        "hubs": [
            ("Old Airport Rd (Manipal)", 12.9592, 77.6496, "HAL Old Airport Road, Bengaluru"),
            ("Bannerghatta Rd (Fortis)", 12.8950, 77.5980, "Bannerghatta Road, Bengaluru"),
            ("Indiranagar 100 Feet Rd", 12.9784, 77.6408, "Indiranagar, Bengaluru"),
            ("Bommasandra Health City", 12.8130, 77.6910, "Bommasandra, Bengaluru"),
            ("Whitefield (Sankara Eye)", 12.9640, 77.7120, "Whitefield, Bengaluru"),
            ("Hosur Road (NIMHANS)", 12.9405, 77.5968, "Hosur Road, Bengaluru"),
            ("Rajajinagar (Nethralaya)", 12.9915, 77.5530, "Rajajinagar, Bengaluru"),
            ("Victoria Hosp / KR Market", 12.9620, 77.5750, "K.R. Market, Bengaluru")
        ]
    },
    "patna": {
        "city_title": "Patna",
        "hubs": [
            ("AIIMS Phulwari Sharif", 25.5606, 85.0444, "AIIMS Patna, Bihar"),
            ("Bailey Road / Raja Bazar", 25.6095, 85.0863, "Bailey Road, Patna, Bihar"),
            ("PMCH / Ashok Rajpath", 25.6200, 85.1580, "PMCH, Ashok Rajpath, Patna, Bihar"),
            ("Kankarbagh Doctors Colony", 25.5960, 85.1550, "Kankarbagh, Patna, Bihar"),
            ("Boring Road (ASG Eye)", 25.6180, 85.1150, "Boring Road, Patna, Bihar"),
            ("South Gandhi Maidan", 25.6150, 85.1430, "Gandhi Maidan, Patna, Bihar"),
            ("Rajendra Nagar", 25.6020, 85.1610, "Rajendra Nagar, Patna, Bihar"),
            ("IGIMS Sheikhpura", 25.6120, 85.0870, "Sheikhpura, Patna, Bihar")
        ]
    },
    "muzaffarpur": {
        "city_title": "Muzaffarpur",
        "hubs": [
            ("Juran Chhapra (Medical Hub)", 26.1260, 85.3810, "Juran Chhapra, Muzaffarpur, Bihar"),
            ("Maripur / Jaiswal Eye", 26.1175, 85.3710, "Maripur, Muzaffarpur, Bihar"),
            ("SKMCH & Hospital", 26.1550, 85.3980, "SKMCH, Muzaffarpur, Bihar"),
            ("Sadar Hospital Road", 26.1215, 85.3850, "Sadar Hospital, Muzaffarpur, Bihar"),
            ("Bhagwanpur Chowk (NH-28)", 26.1150, 85.3520, "Bhagwanpur Chowk, Muzaffarpur, Bihar"),
            ("Aghoria Bazar Chowk", 26.1105, 85.3710, "Aghoria Bazar, Muzaffarpur, Bihar"),
            ("Motijheel & Sutapatti", 26.1210, 85.3790, "Motijheel, Muzaffarpur, Bihar"),
            ("Zero Mile / Ahiyapur", 26.1460, 85.4050, "Zero Mile, Muzaffarpur, Bihar")
        ]
    },
    "kolkata": {
        "city_title": "Kolkata",
        "hubs": [
            ("EM Bypass (Apollo)", 22.5680, 88.4030, "EM Bypass, Kolkata, West Bengal"),
            ("Bhowanipore (SSKM Apex)", 22.5390, 88.3440, "Bhowanipore, Kolkata, West Bengal"),
            ("Alipore (BM Birla Heart)", 22.5310, 88.3320, "Alipore, Kolkata, West Bengal"),
            ("Salt Lake (Susrut Eye)", 22.5850, 88.4110, "Salt Lake, Kolkata, West Bengal"),
            ("College Street Medical", 22.5740, 88.3610, "College Street, Kolkata, West Bengal"),
            ("Park Street Hub", 22.5510, 88.3520, "Park Street, Kolkata, West Bengal")
        ]
    },
    "lucknow": {
        "city_title": "Lucknow",
        "hubs": [
            ("Chowk (KGMU Apex)", 26.8690, 80.9150, "Chowk, Lucknow, Uttar Pradesh"),
            ("Shaheed Path (Medanta)", 26.7910, 80.9950, "Amar Shaheed Path, Lucknow, Uttar Pradesh"),
            ("Gomti Nagar (RMLIMS)", 26.8610, 81.0020, "Gomti Nagar, Lucknow, Uttar Pradesh"),
            ("Raebareli Rd (SGPGI)", 26.7450, 80.9410, "SGPGI Raebareli Road, Lucknow, Uttar Pradesh"),
            ("Hazratganj Central", 26.8480, 80.9450, "Hazratganj, Lucknow, Uttar Pradesh"),
            ("Kaiserbagh Eye Centre", 26.8530, 80.9290, "Kaiserbagh, Lucknow, Uttar Pradesh")
        ]
    },
    "hyderabad": {
        "city_title": "Hyderabad",
        "hubs": [
            ("Banjara Hills (LV Prasad)", 17.4265, 78.4325, "Banjara Hills, Hyderabad, Telangana"),
            ("Jubilee Hills (Apollo)", 17.4156, 78.4130, "Jubilee Hills, Hyderabad, Telangana"),
            ("Gachibowli / Hitec (AIG)", 17.4401, 78.3610, "Gachibowli, Hyderabad, Telangana"),
            ("Somajiguda (Yashoda/NIMS)", 17.4280, 78.4590, "Somajiguda, Hyderabad, Telangana"),
            ("Secunderabad (KIMS)", 17.4420, 78.4860, "Secunderabad, Hyderabad, Telangana")
        ]
    }
}

loc_lower = location_query.lower()
active_hub_key = None
if "delhi" in loc_lower or "ncr" in loc_lower:
    active_hub_key = "delhi"
elif "mumbai" in loc_lower or "bombay" in loc_lower:
    active_hub_key = "mumbai"
elif "bengaluru" in loc_lower or "bangalore" in loc_lower:
    active_hub_key = "bengaluru"
elif "patna" in loc_lower:
    active_hub_key = "patna"
elif "muzaffarpur" in loc_lower:
    active_hub_key = "muzaffarpur"
elif "kolkata" in loc_lower or "calcutta" in loc_lower:
    active_hub_key = "kolkata"
elif "lucknow" in loc_lower:
    active_hub_key = "lucknow"
elif "hyderabad" in loc_lower or "secunderabad" in loc_lower:
    active_hub_key = "hyderabad"

if active_hub_key:
    hub_info = INDIAN_HEALTHCARE_HUBS[active_hub_key]
    st.markdown(
        f"<div style='font-size:0.85rem; color:#334155; margin: 8px 0 4px 0; font-weight:600; display:flex; align-items:center; gap:6px;'>"
        f"<span>🏥</span> Prominent Medical Districts & Hubs in <strong>{hub_info['city_title']}</strong>:</div>",
        unsafe_allow_html=True
    )
    hubs_list = hub_info["hubs"]
    num_cols = min(len(hubs_list), 4)
    hcols = st.columns(num_cols)
    for idx, (label, hlat, hlon, hname) in enumerate(hubs_list):
        with hcols[idx % num_cols]:
            if st.button(f"📌 {label}", key=f"hub_btn_{active_hub_key}_{idx}", use_container_width=True):
                st.session_state["live_lat"] = hlat
                st.session_state["live_lon"] = hlon
                st.session_state["preset_loc"] = hname
                st.session_state["is_device_gps"] = True
                st.rerun()

# Advanced Coordinate Calibrator Expander
with st.expander("🛰️ Manual Lat / Lon Coordinate Entry (Advanced)", expanded=False):
    c_lat, c_lon, c_lock = st.columns([2, 2, 1.5])
    with c_lat:
        in_lat = st.number_input(
            "Latitude (°N):",
            value=float(st.session_state.get("live_lat", 28.6139)),
            format="%.5f",
            step=0.001
        )
    with c_lon:
        in_lon = st.number_input(
            "Longitude (°E):",
            value=float(st.session_state.get("live_lon", 77.2090)),
            format="%.5f",
            step=0.001
        )
    with c_lock:
        st.write("")
        st.write("")
        if st.button("📌 Lock Coordinates", type="secondary", use_container_width=True):
            st.session_state["live_lat"] = in_lat
            st.session_state["live_lon"] = in_lon
            rev_name = geocoding_service.reverse_geocode(in_lat, in_lon) or f"Custom GPS ({in_lat:.4f}, {in_lon:.4f})"
            st.session_state["preset_loc"] = rev_name
            st.session_state["is_device_gps"] = True
            st.rerun()

st.markdown("---")

# ==========================================
# 🎯 SEARCH FILTERS (SPECIALTY, TYPE, RADIUS)
# ==========================================
scol1, scol2, scol3 = st.columns([2, 1.5, 1.5])
with scol1:
    selected_specialty = st.selectbox(
        "Filter by Medical Specialty:",
        all_specialty_names,
        index=spec_index,
        help="Filters providers strictly matching this clinical discipline."
    )
with scol2:
    facility_type = st.selectbox("Facility Type:", ["All", "Hospital", "Clinic", "Doctor", "Pharmacy"], index=0)
with scol3:
    radius_km = st.slider("Strict Search Radius (km):", min_value=1, max_value=35, value=15, help="Only facilities strictly within this exact distance will be displayed.")

# ==========================================
# 🏥 EXECUTION & RESULTS RENDERING
# ==========================================
if location_query:
    with st.spinner(f"Searching healthcare facilities within {radius_km} km of '{location_query}'..."):
        # Use exact coordinates if calibrated
        if "live_lat" in st.session_state and "live_lon" in st.session_state:
            lat = float(st.session_state["live_lat"])
            lon = float(st.session_state["live_lon"])
            display_name = st.session_state.get("preset_loc", location_query)
            coords = (lat, lon, display_name)
        else:
            coords = geocoding_service.geocode_location(location_query, country_code=country_code)

        if not coords:
            st.error(
                f"Could not resolve geographic coordinates for '{location_query}'. "
                f"Please verify spelling or select one of the quick city presets above."
            )
        else:
            lat, lon, display_name = coords

            st.markdown(
                f"<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px; margin-bottom:14px; font-size:0.9rem;'>"
                f"📍 <b>Active Search Location:</b> <b>{display_name}</b> (<code>{lat:.4f}° N, {lon:.4f}° E</code>) • "
                f"Specialty Filter: <b>{selected_specialty}</b> • Proximity Limit: <b>&le; {radius_km} km</b>"
                f"</div>",
                unsafe_allow_html=True
            )

            # Query multi-strategy provider service with strict distance and specialty enforcement
            providers = provider_search_service.search_providers(
                latitude=lat,
                longitude=lon,
                radius_km=float(radius_km),
                specialty_filter=selected_specialty if selected_specialty != "All" else None,
                facility_type_filter=facility_type if facility_type != "All" else None,
                location_query=location_query,
                country_code=country_code
            )

            # MAP & RESULTS DISPLAY
            if providers:
                st.markdown(f"### Found **{len(providers)}** facilities matching your search (Sorted by Proximity)")

                # Map visualization
                map_data = []
                for p in providers:
                    map_data.append({
                        "name": p.name,
                        "lat": p.latitude,
                        "lon": p.longitude,
                        "type": p.provider_type
                    })
                map_data.append({
                    "name": f"Search Center ({display_name})",
                    "lat": lat,
                    "lon": lon,
                    "type": "Search Center"
                })

                df_map = pd.DataFrame(map_data)
                st.map(df_map, latitude="lat", longitude="lon", size=22, zoom=12)

                st.markdown("---")
                st.markdown("#### 🏥 Healthcare Facility Listings:")

                # 2-column cards layout
                for i in range(0, len(providers), 2):
                    pcol1, pcol2 = st.columns(2)
                    pair = providers[i:i+2]

                    for pidx, p in enumerate(pair):
                        target_col = pcol1 if pidx == 0 else pcol2
                        with target_col:
                            phone_html = f"📞 <b>Phone:</b> <a href='tel:{p.phone}' style='color:#0d9488;'>{p.phone}</a>" if p.phone else "📞 <span style='color:#94a3b8;'>Phone not listed in public registry</span>"
                            web_html = f"🌐 <a href='{p.website}' target='_blank' style='color:#0d9488;'>Official Website</a>" if p.website else "🌐 <span style='color:#94a3b8;'>Website not listed</span>"
                            directions_btn = f"<a href='{p.directions_url}' target='_blank' style='display:inline-block; margin-top:8px; padding:6px 14px; background:#0d9488; color:white; border-radius:6px; text-decoration:none; font-weight:600; font-size:0.85rem;'>🗺️ Get Directions ({p.distance_km} km)</a>"

                            badge_color = "#2563eb" if p.provider_type == "Hospital" else ("#059669" if p.provider_type == "Pharmacy" else "#0d9488")

                            st.markdown(
                                f"""
                                <div class="provider-card" style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:14px; box-shadow:0 1px 4px rgba(0,0,0,0.06);">
                                    <div style="display:flex; justify-content:space-between; align-items:start;">
                                        <div style="font-weight:700; font-size:1.05rem; color:#0f172a;">{p.name}</div>
                                        <span style="background:{badge_color}; color:white; font-size:0.75rem; font-weight:bold; padding:2px 8px; border-radius:12px;">{p.provider_type}</span>
                                    </div>
                                    <div style="font-size:0.88rem; color:#0d9488; font-weight:600; margin-top:4px;">🩺 {p.specialty}</div>
                                    <div style="font-size:0.84rem; color:#475569; margin-top:4px;">📍 {p.address}</div>
                                    <div style="font-size:0.86rem; color:#0f766e; font-weight:bold; margin-top:6px;">
                                        📏 Proximity: <b>{p.distance_km} km</b> away
                                    </div>
                                    <div style="font-size:0.82rem; margin-top:4px;">{phone_html}</div>
                                    <div style="font-size:0.82rem; margin-top:4px;">{web_html}</div>
                                    {directions_btn}
                                    <div style="font-size:0.72rem; color:#94a3b8; margin-top:10px; border-top:1px solid #f1f5f9; padding-top:6px;">
                                        Source: {p.data_source} • { 'Curated Regional Registry' if p.is_verified else 'OpenStreetMap Community Node' }
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
            else:
                st.warning(
                    f"No healthcare facilities matching specialty '**{selected_specialty}**' were found strictly within **{radius_km} km** of **{display_name}**.\n\n"
                    "**Clinical Recommendations:**\n"
                    f"• Try increasing the search radius slider above (e.g. 20–35 km).\n"
                    "• Switch specialty filter to 'All' or 'General Physician / Internal Medicine' for primary medical care.\n"
                    f"• In an acute emergency, please call **{country_cfg.get('emergency_number')}** immediately."
                )

st.markdown("---")
st.caption(
    "Data Source: OpenStreetMap contributors under ODbL license & National Healthcare Registries. "
    "MediGuide AI strictly computes Haversine distance and clinical taxonomy verification."
)
