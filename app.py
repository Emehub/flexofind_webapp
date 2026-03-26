"""
Technician Proximity Finder
─────────────────────────────────────────────────────────────────────────────
Admin dashboard that locates and ranks field technicians by distance from a
customer request location. Uses Geopy's geodesic formula for accuracy and
Nominatim for address-to-coordinate geocoding.

Run:  streamlit run app.py
"""

import base64
import time

import pandas as pd
import streamlit as st
from geopy.distance import geodesic
from geopy.geocoders import Nominatim


def _logo_base64(path: str = "Logo.jpeg") -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Technician Proximity Finder",
    page_icon="Logo.jpeg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Theme Definitions ───────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "accent":        "#00d4ff",
        "bg":            "#0e1117",
        "card_bg":       "#1a1f2e",
        "sidebar_bg":    "#0c1018",
        "info_bg":       "#131820",
        "border":        "#2a3f54",
        "header_border": "#1e2d3d",
        "text":          "#fafafa",
        "subtext":       "#8892a4",
        "section_text":  "#c9d1d9",
        "closest_bg":    "linear-gradient(135deg, #0d2137 0%, #0a1628 100%)",
        "eyebrow":       "#5a6a7e",
    },
    "light": {
        "accent":        "#0077cc",
        "bg":            "#f5f7fa",
        "card_bg":       "#ffffff",
        "sidebar_bg":    "#eef1f6",
        "info_bg":       "#f0f4f8",
        "border":        "#c8d4e0",
        "header_border": "#d0dae6",
        "text":          "#0d1117",
        "subtext":       "#4a5568",
        "section_text":  "#1a202c",
        "closest_bg":    "linear-gradient(135deg, #e8f4fd 0%, #dbeeff 100%)",
        "eyebrow":       "#5a7a9e",
    },
}


def inject_theme_css(t: dict) -> None:
    """Inject CSS variables based on the active theme dict."""
    st.markdown(
        f"""
        <style>
            /* ── Layout & page background ── */
            .block-container {{ padding-top: 1.2rem !important; }}
            .stApp,
            .stApp > div,
            div[data-testid="stAppViewContainer"],
            div[data-testid="stAppViewContainer"] > section,
            div[data-testid="stAppViewContainer"] > section > div {{
                background-color: {t['bg']} !important;
            }}

            /* ── App header ── */
            .app-header {{
                text-align: center;
                padding: 1rem 0 0.6rem;
                border-bottom: 1px solid {t['header_border']};
                margin-bottom: 1.4rem;
            }}
            .app-header h1 {{
                font-size: 2.1rem;
                font-weight: 800;
                color: {t['accent']};
                letter-spacing: -0.5px;
                margin: 0;
            }}
            .app-header p {{
                color: {t['subtext']};
                margin: 0.25rem 0 0;
                font-size: 0.92rem;
            }}

            /* ── Metric cards row ── */
            .metric-row {{
                display: flex;
                gap: 0.9rem;
                margin: 0.8rem 0 1.2rem;
            }}
            .metric-card {{
                flex: 1;
                background: {t['card_bg']};
                border: 1px solid {t['border']};
                border-radius: 10px;
                padding: 0.85rem 1rem;
                text-align: center;
            }}
            .metric-card .val {{
                font-size: 1.75rem;
                font-weight: 700;
                color: {t['accent']};
                line-height: 1.2;
            }}
            .metric-card .lbl {{
                font-size: 0.72rem;
                color: {t['subtext']};
                text-transform: uppercase;
                letter-spacing: 0.6px;
                margin-top: 2px;
            }}

            /* ── Closest card ── */
            .closest-card {{
                background: {t['closest_bg']};
                border: 1px solid {t['accent']}30;
                border-left: 4px solid {t['accent']};
                border-radius: 8px;
                padding: 0.9rem 1.4rem;
                margin: 0.5rem 0 1.2rem;
            }}
            .closest-card .eyebrow {{
                font-size: 0.7rem;
                color: {t['eyebrow']};
                text-transform: uppercase;
                letter-spacing: 1.2px;
                margin-bottom: 0.35rem;
            }}
            .closest-card .tech-name {{
                font-size: 1.25rem;
                font-weight: 700;
                color: {t['accent']};
            }}
            .closest-card .tech-detail {{
                color: {t['subtext']};
                font-size: 0.88rem;
                margin-top: 0.2rem;
            }}

            /* ── Section headers ── */
            .section-hdr {{
                font-size: 1rem;
                font-weight: 600;
                color: {t['section_text']};
                margin: 0.4rem 0 0.7rem;
                padding-bottom: 0.3rem;
                border-bottom: 1px solid {t['header_border']};
            }}

            /* ── Info / legend box ── */
            .info-box {{
                background: {t['info_bg']};
                border: 1px solid {t['border']};
                border-radius: 7px;
                padding: 0.6rem 0.9rem;
                font-size: 0.82rem;
                color: {t['subtext']};
                line-height: 1.7;
            }}

            /* ── Sidebar ── */
            section[data-testid="stSidebar"] {{
                background-color: {t['sidebar_bg']} !important;
                border-right: 1px solid {t['header_border']};
            }}

            /* ── DataTable border ── */
            div[data-testid="stDataFrame"] {{
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid {t['border']};
            }}

            /* ── Streamlit native text overrides ── */

            /* Main content area & sidebar: all generic text */
            .stApp, .stApp *,
            section[data-testid="stSidebar"],
            section[data-testid="stSidebar"] * {{
                color: {t['text']};
            }}

            /* Markdown prose */
            .stMarkdown p, .stMarkdown li, .stMarkdown span,
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
            .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
                color: {t['text']} !important;
            }}

            /* Form / widget labels */
            label, .stTextInput label, .stNumberInput label,
            .stSelectbox label, .stMultiSelect label,
            .stRadio label, .stSlider label,
            .stCheckbox label, .stForm label,
            div[data-testid="stWidgetLabel"] p,
            div[data-testid="stWidgetLabel"] span {{
                color: {t['text']} !important;
            }}

            /* Radio & checkbox option text */
            .stRadio div[role="radiogroup"] label,
            .stCheckbox div label {{
                color: {t['text']} !important;
            }}

            /* Text inputs & number inputs */
            .stTextInput input, .stNumberInput input {{
                color: {t['text']} !important;
                background-color: {t['card_bg']} !important;
                border-color: {t['border']} !important;
            }}

            /* Selectbox */
            .stSelectbox div[data-baseweb="select"] > div,
            .stMultiSelect div[data-baseweb="select"] > div {{
                color: {t['text']} !important;
                background-color: {t['card_bg']} !important;
            }}

            /* Dropdown option list */
            ul[data-testid="stSelectboxVirtualDropdown"] li,
            li[role="option"] {{
                color: {t['text']} !important;
                background-color: {t['card_bg']} !important;
            }}

            /* Expander header */
            .streamlit-expanderHeader, .streamlit-expanderHeader p,
            details summary p {{
                color: {t['text']} !important;
            }}

            /* Info / warning / success / error boxes native */
            div[data-testid="stNotification"] p {{
                color: {t['text']} !important;
            }}

            /* Slider value label */
            div[data-testid="stSlider"] p {{
                color: {t['text']} !important;
            }}

            /* Caption text */
            .stCaption, div[data-testid="stCaptionContainer"] p {{
                color: {t['subtext']} !important;
            }}

            /* Subheader and markdown headings at top level */
            h1, h2, h3, h4, h5, h6 {{
                color: {t['section_text']} !important;
            }}

            /* keep accent-coloured values visible  */
            .metric-card .val,
            .closest-card .tech-name,
            .app-header h1 {{
                color: {t['accent']} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ─── Constants ────────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "Available": "#00c957",
    "On-Site":   "#ff4b4b",
    "Off-Duty":  "#7a8694",
}

CSV_PATH = "technicians.csv"
NOMINATIM_USER_AGENT = "tech_proximity_finder_v1_streamlit"


# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_technicians(path: str) -> pd.DataFrame:
    """Load the technicians database from a CSV file."""
    try:
        df = pd.read_csv(path)
        required = {"Tech_ID", "Name", "Phone", "Specialty",
                    "Latitude", "Longitude", "Status"}
        missing = required - set(df.columns)
        if missing:
            st.error(f"CSV is missing columns: {missing}")
            st.stop()
        return df
    except FileNotFoundError:
        st.error(
            f"**{path}** not found. Place `technicians.csv` in the same "
            "directory as `app.py` and restart."
        )
        st.stop()


# ─── Core Business Logic ──────────────────────────────────────────────────────
def calculate_distance(
    tech_lat: float, tech_lon: float,
    req_lat: float,  req_lon: float,
) -> float:
    """
    Return the geodesic distance in kilometres between a technician's base
    location and the customer request coordinates.

    Uses the WGS-84 ellipsoid model (geopy.distance.geodesic) for accuracy
    across large distances. Returns float('inf') on any error so sorting
    still works correctly.
    """
    try:
        return round(geodesic((tech_lat, tech_lon), (req_lat, req_lon)).kilometers, 2)
    except Exception:
        return float("inf")


def geocode_address(address: str) -> tuple[float | None, float | None]:
    """
    Convert a human-readable address string to (latitude, longitude) via
    OpenStreetMap's Nominatim geocoder.

    Returns:
        (lat, lon) on success, (None, None) on failure or no result found.
    """
    address = address.strip()
    if not address:
        return None, None

    try:
        geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT)
        time.sleep(1)  # Nominatim free-tier: max 1 request / second
        location = geolocator.geocode(address, timeout=10)  # type: ignore[arg-type]
        if location:
            return location.latitude, location.longitude  # type: ignore[union-attr]
        return None, None
    except Exception as exc:
        st.sidebar.error(f"Geocoding error: {exc}")
        return None, None


def enrich_with_distances(
    df: pd.DataFrame, req_lat: float, req_lon: float
) -> pd.DataFrame:
    """
    Append a `Distance_km` column to `df` and return a copy sorted
    ascending by that column.
    """
    df = df.copy()
    df["Distance_km"] = df.apply(
        lambda row: calculate_distance(
            row["Latitude"], row["Longitude"], req_lat, req_lon
        ),
        axis=1,
    )
    # Convert km → estimated travel minutes at 30 km/h city speed
    df["Travel_min"] = (df["Distance_km"] / 30 * 60).round(0).astype(int)
    return df.sort_values("Distance_km").reset_index(drop=True)


def apply_filters(
    df: pd.DataFrame,
    specialty: str,
    statuses: list[str],
    max_km: float,
) -> pd.DataFrame:
    """Filter the enriched dataframe by specialty, status list, and max distance."""
    if specialty != "All":
        df = df[df["Specialty"] == specialty]
    if statuses:
        df = df[df["Status"].isin(statuses)]
    df = df[df["Distance_km"] <= max_km * 30 / 60]  # max_km is now max_min
    return df.reset_index(drop=True)


def build_map_df(
    tech_df: pd.DataFrame, req_lat: float, req_lon: float
) -> pd.DataFrame:
    """
    Build a combined lat/lon/color DataFrame for st.map().

    Technicians are coloured by status; the request pin is cyan (#00d4ff).
    """
    rows = tech_df[["Latitude", "Longitude", "Status"]].copy()
    rows.columns = ["lat", "lon", "Status"]
    rows["color"] = rows["Status"].map(STATUS_COLORS).fillna("#7a8694")
    rows = rows.drop(columns=["Status"])

    request_pin = pd.DataFrame([{"lat": req_lat, "lon": req_lon, "color": "#00d4ff"}])
    return pd.concat([rows, request_pin], ignore_index=True)


# ─── Add-Technician Helpers ───────────────────────────────────────────────────
def generate_tech_id(df: pd.DataFrame) -> str:
    """Return the next sequential Tech_ID (e.g. TECH-016) from the existing records."""
    nums = df["Tech_ID"].str.extract(r"TECH-(\d+)")[0].dropna().astype(int)
    return f"TECH-{nums.max() + 1:03d}" if not nums.empty else "TECH-001"


def save_technician(new_row: dict) -> None:
    """Append a new technician record to the CSV file and clear the data cache."""
    try:
        existing = pd.read_csv(CSV_PATH)
        updated  = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
        updated.to_csv(CSV_PATH, index=False)
        st.cache_data.clear()
    except Exception as exc:
        st.error(f"Failed to save technician: {exc}")


def delete_technician(tech_id: str) -> None:
    """Remove the technician with the given Tech_ID from the CSV and clear the cache."""
    try:
        df = pd.read_csv(CSV_PATH)
        df = df[df["Tech_ID"] != tech_id]
        df.to_csv(CSV_PATH, index=False)
        st.cache_data.clear()
    except Exception as exc:
        st.error(f"Failed to delete technician: {exc}")


# ─── Styling helpers ──────────────────────────────────────────────────────────
def _style_status_cell(val: object) -> str:
    """Return a CSS string to colour-code a Status cell."""
    return f"color: {STATUS_COLORS.get(str(val), '#ffffff')}; font-weight: 600;"


def render_styled_table(df: pd.DataFrame, t: dict) -> None:
    """Render the technician results table with colour-coded Status column."""
    display = df[["Tech_ID", "Name", "Phone", "Specialty", "Status", "Travel_min"]].copy()
    display.columns = ["ID", "Name", "Phone", "Specialty", "Status", "ETA (min)"]
    display.index = pd.RangeIndex(1, len(display) + 1)

    styled = (
        display.style
        .map(_style_status_cell, subset=["Status"])
        .format({"ETA (min)": "{} min"})
        .set_properties(**{
            "background-color": t["card_bg"],
            "border-color":     t["border"],
            "color":            t["text"],
        })
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", t["info_bg"]),
                    ("color",            t["subtext"]),
                    ("font-weight",      "600"),
                    ("border-bottom",    f"1px solid {t['border']}"),
                ],
            }
        ])
    )
    st.dataframe(styled, use_container_width=True, height=430)


# ─── UI Sections ──────────────────────────────────────────────────────────────
def render_header(theme_label: str) -> None:
    logo_b64 = _logo_base64()
    st.markdown(
        f"""
        <div class="app-header">
            <img src="data:image/jpeg;base64,{logo_b64}"
                 style="height:72px; width:72px; border-radius:50%; object-fit:cover; margin-bottom:0.5rem;" alt="FlexoFind logo" />
            <h1>Technician Proximity Finder</h1>
            <p>Admin Dispatch Dashboard &nbsp;&middot;&nbsp; Real-time technician location ranking
               &nbsp;&middot;&nbsp; {theme_label.capitalize()} Mode</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_add_technician_form(df: pd.DataFrame) -> None:
    """Expander form for adding a new technician to the database."""
    with st.expander("Add New Technician", expanded=False):
        with st.form("add_tech_form", clear_on_submit=True):
            st.markdown("##### Technician Details")
            name    = st.text_input("Full Name",  placeholder="e.g., Kofi Mensah")
            phone   = st.text_input("Phone",      placeholder="e.g., 0244-123456")

            SPEC_OPTIONS = [
                "Phone Repairs", "Laptop Repairs", "Plumbing Services",
                "Mechanic Services", "Carpentry Works",
            ]
            spec_sel    = st.selectbox("Specialty", SPEC_OPTIONS)
            status = st.selectbox("Status", ["Available", "On-Site", "Off-Duty"])

            st.markdown("##### Location")
            st.caption("Enter an address **or** leave it blank and set coordinates.")
            address = st.text_input(
                "Address  (geocoded)",
                placeholder="e.g., Labone, Accra, Ghana",
            )
            col1, col2 = st.columns(2)
            with col1:
                form_lat = st.number_input(
                    "Latitude",  value=5.60370, format="%.5f",
                    help="Used when Address is blank.",
                )
            with col2:
                form_lon = st.number_input(
                    "Longitude", value=-0.18700, format="%.5f",
                    help="Used when Address is blank.",
                )

            submitted = st.form_submit_button(
                "Save Technician", use_container_width=True
            )

        # ── Post-submit logic (outside form, inside expander) ─────────────────
        if submitted:
            errors    = []
            name      = name.strip()
            phone     = phone.strip()
            address   = address.strip()
            specialty = spec_sel

            if not name:
                errors.append("Full Name is required.")
            if not phone:
                errors.append("Phone is required.")

            lat, lon = form_lat, form_lon
            if address:
                with st.spinner("Geocoding address…"):
                    geo_lat, geo_lon = geocode_address(address)
                if geo_lat is not None:
                    lat, lon = geo_lat, geo_lon
                else:
                    errors.append(
                        f'Could not geocode "{address}". '
                        "Leave the Address blank and use coordinates instead."
                    )

            if errors:
                for err in errors:
                    st.error(err)
            else:
                assert lat is not None and lon is not None
                new_row = {
                    "Tech_ID":   generate_tech_id(df),
                    "Name":      name,
                    "Phone":     phone,
                    "Specialty": specialty,
                    "Latitude":  round(float(lat), 6),
                    "Longitude": round(float(lon), 6),
                    "Status":    status,
                }
                save_technician(new_row)
                st.success(f"{name} saved as **{new_row['Tech_ID']}**")
                st.rerun()


def render_delete_technician_form(df: pd.DataFrame, t: dict) -> None:
    """Expander form for removing a technician from the database."""
    with st.expander("Delete Technician", expanded=False):
        if df.empty:
            st.info("No technicians in the database.")
            return

        # Build label list: "TECH-001 — Kofi Mensah"
        options = [
            f"{row['Tech_ID']} — {row['Name']}"
            for _, row in df.iterrows()
        ]
        selected = st.selectbox(
            "Select technician to remove",
            options=options,
            key="delete_select",
        )

        # Preview card for the selected technician
        tech_id   = selected.split(" — ")[0]
        tech_row  = df[df["Tech_ID"] == tech_id].iloc[0]
        status_c  = STATUS_COLORS.get(tech_row["Status"], "#ffffff")
        st.markdown(
            f"""
            <div style="background:{t['card_bg']}; border:1px solid {t['border']};
                        border-radius:7px; padding:0.7rem 1rem;
                        font-size:0.86rem; margin:0.5rem 0;">
                <b style="color:{t['text']};">{tech_row['Name']}</b><br>
                <span style="color:{t['subtext']};">{tech_row['Specialty']}</span>
                &nbsp;·&nbsp;
                <span style="color:{t['subtext']};">{tech_row['Phone']}</span>
                &nbsp;·&nbsp;
                <span style="color:{status_c}; font-weight:600;">{tech_row['Status']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Two-step confirmation via checkbox to prevent accidental deletes
        confirmed = st.checkbox(
            f"I confirm I want to permanently delete **{tech_row['Name']}**",
            key="delete_confirm",
        )
        if st.button(
            "Delete Technician",
            disabled=not confirmed,
            use_container_width=True,
            type="primary",
            key="delete_btn",
        ):
            delete_technician(tech_id)
            st.success(f"{tech_row['Name']} ({tech_id}) has been removed.")
            # Reset confirmation checkbox state
            st.session_state.pop("delete_confirm", None)
            st.rerun()


def render_sidebar(df: pd.DataFrame) -> dict:
    """
    Render the sidebar controls and return a dict with all user selections.

    Returns keys: req_lat, req_lon, req_label, specialty, statuses, max_km, theme
    """
    state: dict = {}

    with st.sidebar:
        # ── Theme toggle ──────────────────────────────────────────────────────
        theme_choice = st.radio(
            "Theme",
            options=["Dark", "Light"],
            index=0 if st.session_state.get("theme", "dark") == "dark" else 1,
            horizontal=True,
            key="theme_radio",
        )
        state["theme"] = "dark" if theme_choice == "Dark" else "light"
        st.session_state["theme"] = state["theme"]
        t = THEMES[state["theme"]]
        st.markdown("---")

        st.markdown("## Customer Request Location")
        st.markdown("---")

        method = st.radio(
            "Input Method",
            options=["Address Search", "Manual Coordinates"],
            index=0,
            horizontal=False,
        )

        if method == "Address Search":
            address = st.text_input(
                "Search Address",
                placeholder="e.g., Labone, Accra, Ghana",
                help="Geocoded via OpenStreetMap Nominatim (free, rate-limited).",
            )
            if st.button("Find Location", use_container_width=True):
                if address:
                    with st.spinner("Geocoding address…"):
                        lat, lon = geocode_address(address)
                    if lat is not None:
                        st.session_state.update(
                            req_lat=lat, req_lon=lon, req_label=address
                        )
                        st.success(f"Found: {lat:.5f}, {lon:.5f}")
                    else:
                        st.error(
                            "Address not found. Try adding a city or country, "
                            "or switch to Manual Coordinates."
                        )
                else:
                    st.warning("Please enter an address first.")

        else:  # Manual Coordinates
            c1, c2 = st.columns(2)
            with c1:
                manual_lat = st.number_input(
                    "Latitude", value=5.6037, format="%.4f", step=0.001
                )
            with c2:
                manual_lon = st.number_input(
                    "Longitude", value=-0.1870, format="%.4f", step=0.001
                )
            if st.button("Set Location", use_container_width=True):
                if -90.0 <= manual_lat <= 90.0 and -180.0 <= manual_lon <= 180.0:
                    st.session_state.update(
                        req_lat=manual_lat,
                        req_lon=manual_lon,
                        req_label=f"{manual_lat:.4f}, {manual_lon:.4f}",
                    )
                    st.success("Location set.")
                else:
                    st.error(
                        "Invalid coordinates. "
                        "Latitude must be −90 → 90; Longitude −180 → 180."
                    )

        st.markdown("---")
        st.markdown("## Filters")

        specialties = ["All"] + sorted(df["Specialty"].dropna().unique().tolist())
        state["specialty"] = st.selectbox("Specialty", options=specialties)

        state["statuses"] = st.multiselect(
            "Show Status",
            options=["Available", "On-Site", "Off-Duty"],
            default=["Available", "On-Site", "Off-Duty"],
        )

        state["max_km"] = float(
            st.slider("Max Travel Time (min)", min_value=5, max_value=120, value=60, step=5)
        )

        st.markdown("---")
        st.markdown(
            """
            <div class="info-box">
                <b>Available</b> (green) &mdash; ready to dispatch<br>
                <b>On-Site</b> (red) &mdash; currently busy<br>
                <b>Off-Duty</b> (grey) &mdash; unavailable<br>
                <b>Blue pin</b> &mdash; request location (map)
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        render_add_technician_form(df)

        st.markdown("---")
        render_delete_technician_form(df, t)

    # Pull coordinates from session state (set by the buttons above)
    state["req_lat"] = st.session_state.get("req_lat")
    state["req_lon"] = st.session_state.get("req_lon")
    state["req_label"] = st.session_state.get("req_label", "")
    return state


def render_no_location_placeholder(df: pd.DataFrame) -> None:
    """Shown when no request location has been set yet."""
    total  = len(df)
    avail  = (df["Status"] == "Available").sum()
    onsite = (df["Status"] == "On-Site").sum()

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="val">{total}</div>
                <div class="lbl">Total Technicians</div>
            </div>
            <div class="metric-card">
                <div class="val" style="color:#00c957">{avail}</div>
                <div class="lbl">Available</div>
            </div>
            <div class="metric-card">
                <div class="val" style="color:#ff4b4b">{onsite}</div>
                <div class="lbl">On-Site</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.info(
            "Set a Customer Request Location in the sidebar to begin.\n\n"
            "Choose **Address Search** to geocode a street address, or use "
            "**Manual Coordinates** if you already have lat/lon values."
        )


def render_metrics(result_df: pd.DataFrame, req_lat: float, req_lon: float) -> None:
    in_range = len(result_df)
    avail    = (result_df["Status"] == "Available").sum()
    nearest  = f"{int(result_df['Travel_min'].min())} min" if in_range else "—"

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="val">{in_range}</div>
                <div class="lbl">Techs in Range</div>
            </div>
            <div class="metric-card">
                <div class="val" style="color:#00c957">{avail}</div>
                <div class="lbl">Available</div>
            </div>
            <div class="metric-card">
                <div class="val">{nearest}</div>
                <div class="lbl">Nearest Distance</div>
            </div>
            <div class="metric-card">
                <div class="val" style="font-size:1rem; color:#8892a4;">
                    {req_lat:.4f}, {req_lon:.4f}
                </div>
                <div class="lbl">Request Coordinates</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_closest_banner(row: pd.Series, t: dict) -> None:
    status_color = STATUS_COLORS.get(row["Status"], "#ffffff")
    st.markdown(
        f"""
        <div class="closest-card">
            <div class="eyebrow">Closest Technician</div>
            <div class="tech-name">{row["Name"]}</div>
            <div class="tech-detail">
                {row["Specialty"]} &nbsp;&middot;&nbsp;
                {row["Phone"]} &nbsp;&middot;&nbsp;
                <span style="color:{status_color}; font-weight:600;">{row["Status"]}</span>
                &nbsp;&middot;&nbsp;
                <span style="color:{t['accent']}; font-weight:700;">
                    {int(row['Travel_min'])} min away
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_map(tech_df: pd.DataFrame, req_lat: float, req_lon: float, req_label: str) -> None:
    st.markdown('<div class="section-hdr">Map View</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="info-box" style="margin-bottom:0.6rem;">
            <b>Request:</b> {req_label or f"{req_lat:.4f}, {req_lon:.4f}"}
            &nbsp;&middot;&nbsp; Dots coloured by technician status
        </div>
        """,
        unsafe_allow_html=True,
    )
    map_df = build_map_df(tech_df, req_lat, req_lon)
    try:
        st.map(map_df, latitude="lat", longitude="lon", color="color", size=300, zoom=11)
    except TypeError:
        # Fallback: older Streamlit versions that don't support color/size kwargs
        st.map(map_df[["lat", "lon"]], zoom=11)


# ─── Main App ─────────────────────────────────────────────────────────────────
def main() -> None:
    # Resolve theme early so CSS is injected before anything renders
    theme_key  = st.session_state.get("theme", "dark")
    inject_theme_css(THEMES[theme_key])

    df = load_technicians(CSV_PATH)
    ui = render_sidebar(df)

    # Re-inject after sidebar in case theme changed this run
    t = THEMES[ui["theme"]]
    inject_theme_css(t)
    render_header(ui["theme"])

    req_lat: float | None = ui["req_lat"]
    req_lon: float | None = ui["req_lon"]

    # ── No location set yet ────────────────────────────────────────────────────
    if req_lat is None or req_lon is None:
        render_no_location_placeholder(df)
        return

    # ── Compute distances and apply filters ───────────────────────────────────
    enriched = enrich_with_distances(df, req_lat, req_lon)
    result   = apply_filters(enriched, ui["specialty"], ui["statuses"], ui["max_km"])

    render_metrics(result, req_lat, req_lon)

    if len(result) > 0:
        render_closest_banner(result.iloc[0], t)

    # ── Two-column layout: table | map ────────────────────────────────────────
    col_table, col_map = st.columns([3, 2], gap="large")

    with col_table:
        st.markdown(
            '<div class="section-hdr">Technicians - Sorted by Distance</div>',
            unsafe_allow_html=True,
        )
        if len(result) == 0:
            st.warning(
                "No technicians match the current filters within "
                f"**{ui['max_km']} min**. Try adjusting the filters or increasing "
                "the max travel time."
            )
        else:
            render_styled_table(result, t)

    with col_map:
        if len(result) == 0:
            st.markdown('<div class="section-hdr">Map View</div>', unsafe_allow_html=True)
            st.warning("No technicians to display on map.")
        else:
            render_map(result, req_lat, req_lon, ui["req_label"])


# ─── Password Gate ────────────────────────────────────────────────────────────
def check_password() -> bool:
    """Return True only after the correct password has been entered."""
    if st.session_state.get("authenticated"):
        return True

    logo_b64 = _logo_base64()
    st.markdown(
        f"""
        <div style="text-align:center; padding: 3rem 1rem 1rem;">
            <img src="data:image/jpeg;base64,{logo_b64}"
                 style="height:90px; width:90px; border-radius:50%;
                        object-fit:cover; margin-bottom:1rem;" />
            <h2 style="margin:0;">FlexoFind Admin</h2>
            <p style="color:#8892a4; margin-top:0.3rem;">Enter your password to continue</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Password", type="password", label_visibility="collapsed",
                            placeholder="Enter password")
        if st.button("Login", use_container_width=True):
            correct = st.secrets.get("APP_PASSWORD", "flexofind2026")
            if pwd == correct:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
    return False


if check_password():
    main()
