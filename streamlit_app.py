#!/usr/bin/env python3
"""
LCMS PDF Report Generator — Streamlit Web Application
Uses pure-Python ReportLab for PDF generation. No system libraries needed.
Compatible with Streamlit Cloud.

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from copy import deepcopy

from pdf_generator import (
    THEMES,
    DEFAULT_STUDY_DATA,
    DEFAULT_METABOLITES,
    generate_pdf_bytes,
)

# Page config
st.set_page_config(
    page_title="LCMS PDF Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stDeployButton { display: none; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0d9488;
        margin-bottom: 0.2rem;
    }
    .main-sub {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0d9488;
        border-bottom: 2px solid #0d9488;
        padding-bottom: 4px;
        margin: 1rem 0 0.75rem 0;
    }
    .stat-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .stat-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0d9488;
        line-height: 1.1;
    }
    .stat-lbl {
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


# Session state initialization
def init_state():
    if "study_data" not in st.session_state:
        st.session_state.study_data = deepcopy(DEFAULT_STUDY_DATA)
    if "metabolites" not in st.session_state:
        st.session_state.metabolites = deepcopy(DEFAULT_METABOLITES)
    if "selected_theme" not in st.session_state:
        st.session_state.selected_theme = "light"
    if "options" not in st.session_state:
        st.session_state.options = {
            "include_cover": True,
            "include_summary": True,
            "include_metabolites": True,
            "include_table": True,
            "metabolites_per_page": 4,
        }
    if "page" not in st.session_state:
        st.session_state.page = "home"

init_state()


# Helpers
def theme_swatch(theme_key):
    t = THEMES[theme_key]
    cols = [t["header_bg"], t["accent"], t["up_color"], t["down_color"], t["card_bg"]]
    swatches = "".join(
        f'<span style="display:inline-block;width:16px;height:16px;'
        f'background:{c};border-radius:3px;margin-right:3px;'
        f'border:1px solid #ccc;vertical-align:middle;"></span>'
        for c in cols
    )
    return swatches


def get_metabolites_df():
    mets = st.session_state.metabolites
    return pd.DataFrame([{
        "name":    m.get("name", ""),
        "formula": m.get("formula", ""),
        "mz":      float(m.get("mz", 0.0)),
        "rt":      float(m.get("rt", 0.0)),
        "fc":      float(m.get("fc", 0.0)),
        "pvalue":  float(m.get("pvalue", 1.0)),
        "padj":    float(m.get("padj", 1.0)),
        "hmdb":    m.get("hmdb", ""),
        "pathway": m.get("pathway", ""),
    } for m in mets])


def df_to_metabolites(df):
    return df.to_dict(orient="records")


def nav_button(label, page_key, icon=""):
    current = st.session_state.page == page_key
    btn = st.sidebar.button(
        f"{icon} {label}",
        key=f"nav_{page_key}",
        use_container_width=True,
        type="primary" if current else "secondary",
    )
    if btn:
        st.session_state.page = page_key
        st.rerun()


# Sidebar
with st.sidebar:
    st.markdown("### 📊 LCMS Generator")
    st.divider()

    nav_button("Home",        "home",        "🏠")
    nav_button("Study Info",  "study_info",  "📋")
    nav_button("Metabolites", "metabolites", "🧪")
    nav_button("Design",      "design",      "🎨")
    nav_button("Generate",    "generate",    "📄")

    st.divider()

    mets  = st.session_state.metabolites
    n_sig = sum(1 for m in mets if m.get("pvalue", 1) < 0.05)
    n_up  = sum(1 for m in mets if m.get("fc", 0) > 0 and m.get("pvalue", 1) < 0.05)
    n_dn  = sum(1 for m in mets if m.get("fc", 0) < 0 and m.get("pvalue", 1) < 0.05)

    st.markdown("**Quick Stats**")
    c1, c2 = st.columns(2)
    c1.metric("Total",  len(mets))
    c2.metric("Sig.",   n_sig)
    c1.metric("Up",     n_up)
    c2.metric("Down",   n_dn)

    st.divider()
    theme_name = THEMES[st.session_state.selected_theme]["name"]
    st.markdown(f"**Theme:** {theme_name}")
    st.markdown(theme_swatch(st.session_state.selected_theme), unsafe_allow_html=True)

    st.divider()
    st.markdown("**Data Management**")

    uploaded = st.file_uploader("Load JSON", type=["json"], key="json_upload",
                                label_visibility="collapsed")
    if uploaded:
        try:
            payload = json.load(uploaded)
            if "study_data"  in payload:
                st.session_state.study_data  = payload["study_data"]
            if "metabolites" in payload:
                st.session_state.metabolites = payload["metabolites"]
            st.success("Loaded!")
        except Exception as e:
            st.error(f"Error: {e}")

    export_payload = json.dumps({
        "study_data":  st.session_state.study_data,
        "metabolites": st.session_state.metabolites,
    }, indent=2)
    st.download_button(
        "📥 Export JSON",
        data=export_payload,
        file_name="lcms_data.json",
        mime="application/json",
        use_container_width=True,
    )

    if st.button("🔄 Reset Defaults", use_container_width=True):
        st.session_state.study_data  = deepcopy(DEFAULT_STUDY_DATA)
        st.session_state.metabolites = deepcopy(DEFAULT_METABOLITES)
        st.rerun()


# PAGE: HOME
def page_home():
    st.markdown('<div class="main-title">📊 LCMS PDF Report Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-sub">Generate professional LCMS Untargeted Metabolomics reports with customizable themes</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🎨 **10 Themes**\n\nChoose from 10 professionally designed color themes matching various publication styles.")
    with col2:
        st.info("⚙️ **Customizable**\n\nCustomize every aspect including fonts, colors, layout, and content sections.")
    with col3:
        st.info("📈 **Rich Visualizations**\n\nAuto-generate volcano plots, heatmaps, PCA plots, and bar graphs.")

    st.markdown('<div class="section-header">Quick Start</div>', unsafe_allow_html=True)
    qa, qb, qc = st.columns(3)
    with qa:
        st.markdown("**1️⃣ Study Info**\n\nFill in your study metadata.")
        if st.button("Go to Study Info", use_container_width=True):
            st.session_state.page = "study_info"; st.rerun()
    with qb:
        st.markdown("**2️⃣ Add Metabolites**\n\nEnter metabolite data or load from JSON.")
        if st.button("Go to Metabolites", use_container_width=True):
            st.session_state.page = "metabolites"; st.rerun()
    with qc:
        st.markdown("**3️⃣ Generate PDF**\n\nChoose a theme and generate your report!")
        if st.button("Go to Generate", use_container_width=True):
            st.session_state.page = "generate"; st.rerun()

    st.markdown('<div class="section-header">Theme Gallery</div>', unsafe_allow_html=True)

    theme_keys = list(THEMES.keys())
    rows = [theme_keys[i:i+5] for i in range(0, len(theme_keys), 5)]
    for row in rows:
        cols = st.columns(5)
        for col, tk in zip(cols, row):
            t = THEMES[tk]
            with col:
                selected = st.session_state.selected_theme == tk
                border = "3px solid #0d9488" if selected else "2px solid #e2e8f0"
                color_divs = "".join(
                    f'<div style="width:18px;height:18px;border-radius:4px;background:{c};border:1px solid rgba(0,0,0,0.1);"></div>'
                    for c in [t["header_bg"], t["accent2"], t["up_color"], t["down_color"]]
                )
                st.markdown(
                    f'<div style="border:{border};border-radius:10px;padding:10px;'
                    f'background:{t["card_bg"]};text-align:center;">'
                    f'<div style="font-weight:700;font-size:12px;color:{t["text"]};margin-bottom:4px;">'
                    f'{t["name"]}</div>'
                    f'<div style="font-size:10px;color:{t["subtext"]};margin-bottom:6px;">'
                    f'{t["subtitle"]}</div>'
                    f'<div style="display:flex;justify-content:center;gap:3px;">'
                    + "".join(
                        f'<div style="width:18px;height:18px;border-radius:4px;'
                        f'background:{c};border:1px solid rgba(0,0,0,0.1);"></div>'
                        for c in [t["header_bg"], t["accent2"], t["up_color"], t["down_color"]]
                    )
                    + '</div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Select", key=f"sel_{tk}", use_container_width=True):
                    st.session_state.selected_theme = tk
                    st.rerun()


# PAGE: STUDY INFO
def page_study_info():
    st.markdown('<div class="main-title">📋 Study Information</div>', unsafe_allow_html=True)
    st.markdown("Fill in the metadata that will appear on the report cover page and header.")

    sd = st.session_state.study_data

    with st.form("study_info_form"):
        st.markdown('<div class="section-header">Report Title</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        title    = c1.text_input("Report Title", value=sd.get("title", ""))
        study_id = c2.text_input("Study ID",     value=sd.get("study_id", ""))
        subtitle = st.text_input("Subtitle",      value=sd.get("subtitle", ""))

        st.markdown('<div class="section-header">Authors and Institution</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        author      = c1.text_input("Author(s)",   value=sd.get("author", ""))
        institution = c2.text_input("Institution", value=sd.get("institution", ""))

        c1, c2 = st.columns(2)
        date    = c1.text_input("Date",         value=sd.get("date", datetime.now().strftime("%B %d, %Y")))
        samples = c2.text_input("Sample Count", value=sd.get("samples", ""))

        st.markdown('<div class="section-header">Experimental Groups</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        group1 = c1.text_input("Group 1 Name", value=sd.get("group1", "Control"))
        group2 = c2.text_input("Group 2 Name", value=sd.get("group2", "Treatment"))

        st.markdown('<div class="section-header">Instrument Details</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        instrument = c1.text_input("Instrument",  value=sd.get("instrument", ""))
        ionization = c2.text_input("Ionization",  value=sd.get("ionization", "ESI+ / ESI-"))
        resolution = c3.text_input("Resolution",  value=sd.get("resolution", "120,000 FWHM"))

        st.markdown('<div class="section-header">Study Description</div>', unsafe_allow_html=True)
        description = st.text_area("Description", value=sd.get("description", ""), height=100)

        submitted = st.form_submit_button("💾 Save Study Info", type="primary", use_container_width=True)
        if submitted:
            st.session_state.study_data.update({
                "title": title, "study_id": study_id, "subtitle": subtitle,
                "author": author, "institution": institution, "date": date,
                "samples": samples, "group1": group1, "group2": group2,
                "instrument": instrument, "ionization": ionization,
                "resolution": resolution, "description": description,
            })
            st.success("✅ Study info saved!")


# PAGE: METABOLITES
def page_metabolites():
    st.markdown('<div class="main-title">🧪 Metabolite Data</div>', unsafe_allow_html=True)
    st.markdown("Edit your metabolite list below. Each row represents one metabolite feature.")

    mets  = st.session_state.metabolites
    n_sig = sum(1 for m in mets if m.get("pvalue", 1) < 0.05)
    n_up  = sum(1 for m in mets if m.get("fc", 0) > 0 and m.get("pvalue", 1) < 0.05)
    n_dn  = sum(1 for m in mets if m.get("fc", 0) < 0 and m.get("pvalue", 1) < 0.05)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-box"><div class="stat-val">{len(mets)}</div><div class="stat-lbl">Total Features</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-box"><div class="stat-val">{n_sig}</div><div class="stat-lbl">Significant (p<0.05)</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#dc2626;">{n_up}</div><div class="stat-lbl">Up-regulated</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#2563eb;">{n_dn}</div><div class="stat-lbl">Down-regulated</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Data Editor</div>', unsafe_allow_html=True)
    st.markdown("Edit values directly. Add rows with the **+** button at the bottom.")

    df = get_metabolites_df()
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "name":    st.column_config.TextColumn("Name", width="medium"),
            "formula": st.column_config.TextColumn("Formula", width="small"),
            "mz":      st.column_config.NumberColumn("m/z",      format="%.4f", min_value=0),
            "rt":      st.column_config.NumberColumn("RT (min)", format="%.2f",  min_value=0),
            "fc":      st.column_config.NumberColumn("FC (log2)", format="%.2f"),
            "pvalue":  st.column_config.NumberColumn("p-value",  format="%.4f", min_value=0, max_value=1),
            "padj":    st.column_config.NumberColumn("p-adj",    format="%.4f", min_value=0, max_value=1),
            "hmdb":    st.column_config.TextColumn("HMDB ID",  width="small"),
            "pathway": st.column_config.TextColumn("Pathway",  width="medium"),
        },
        key="met_editor",
        height=400,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Changes", type="primary", use_container_width=True):
            st.session_state.metabolites = df_to_metabolites(edited_df)
            st.success(f"✅ Saved {len(edited_df)} metabolites!")
            st.rerun()
    with col2:
        if st.button("➕ Add Example Row", use_container_width=True):
            st.session_state.metabolites.append({
                "name": "New Metabolite", "formula": "C6H12O6", "mz": 180.0634,
                "rt": 5.0, "fc": 1.5, "pvalue": 0.03, "padj": 0.08,
                "hmdb": "HMDB0000000", "pathway": "Unknown",
            })
            st.rerun()

    st.markdown('<div class="section-header">Field Guide</div>', unsafe_allow_html=True)
    st.markdown("""
| Column | Description |
|--------|-------------|
| **name** | Metabolite name |
| **formula** | Molecular formula (e.g., C6H12O6) |
| **m/z** | Mass-to-charge ratio |
| **RT (min)** | Retention time in minutes |
| **FC** | Log2 fold change (positive = up-regulated) |
| **p-value** | Raw p-value from statistical test |
| **p-adj** | Adjusted p-value (FDR/BH corrected) |
| **HMDB ID** | HMDB database identifier |
| **Pathway** | Metabolic pathway classification |
""")


# PAGE: DESIGN
def page_design():
    st.markdown('<div class="main-title">🎨 Design Options</div>', unsafe_allow_html=True)
    st.markdown("Customize the look and content of your PDF report.")

    opts = st.session_state.options

    st.markdown('<div class="section-header">Theme Selection</div>', unsafe_allow_html=True)
    theme_keys   = list(THEMES.keys())
    theme_labels = {k: f"{THEMES[k]['name']} — {THEMES[k]['subtitle']}" for k in theme_keys}

    selected = st.radio(
        "Select Theme",
        options=theme_keys,
        format_func=lambda k: theme_labels[k],
        index=theme_keys.index(st.session_state.selected_theme),
        label_visibility="collapsed",
    )
    st.session_state.selected_theme = selected

    t = THEMES[selected]
    swatch_divs = "".join(
        f'<div style="width:28px;height:28px;border-radius:5px;background:{c};'
        f'border:1px solid rgba(0,0,0,0.1);"></div>'
        for c in [t["header_bg"], t["accent"], t["accent2"], t["up_color"], t["down_color"], t["card_bg"]]
    )
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;padding:10px;'
        f'background:{t["card_bg"]};border-radius:8px;border:1px solid {t["border"]};margin-top:6px;">'
        + swatch_divs
        + f'<span style="color:{t["text"]};font-weight:600;font-size:13px;margin-left:8px;">{t["name"]}</span>'
        + '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown('<div class="section-header">Layout Options</div>', unsafe_allow_html=True)
    mpp = st.selectbox(
        "Metabolites per page",
        options=[1, 2, 4, 6],
        index=[1, 2, 4, 6].index(opts.get("metabolites_per_page", 4)),
        help="How many metabolite cards per page",
    )
    st.session_state.options["metabolites_per_page"] = mpp

    st.divider()

    st.markdown('<div class="section-header">Content Sections</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        inc_cover = st.checkbox("Include Cover Page",         value=opts.get("include_cover", True))
        inc_sum   = st.checkbox("Include Summary Page",       value=opts.get("include_summary", True))
    with c2:
        inc_mets  = st.checkbox("Include Metabolite Details", value=opts.get("include_metabolites", True))
        inc_table = st.checkbox("Include Results Table",      value=opts.get("include_table", True))

    st.session_state.options.update({
        "include_cover":       inc_cover,
        "include_summary":     inc_sum,
        "include_metabolites": inc_mets,
        "include_table":       inc_table,
    })

    st.success("✅ Design options are applied automatically.")

    st.divider()
    st.markdown('<div class="section-header">Pages Preview</div>', unsafe_allow_html=True)
    sections = []
    if inc_cover: sections.append(("Cover Page",         "Study metadata, description, institution"))
    if inc_sum:   sections.append(("Summary Statistics", "Volcano plot, heatmap, PCA, key stats"))
    if inc_mets:  sections.append(("Metabolite Details", f"{mpp} metabolites/page with bar graphs"))
    if inc_table: sections.append(("Results Table",      "Full tabulated results"))

    if sections:
        for i, (title, desc) in enumerate(sections):
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;'
                f'background:#f8fafc;border-radius:6px;margin-bottom:4px;border-left:3px solid #0d9488;">'
                f'<span style="font-weight:700;color:#0d9488;min-width:20px;">{i+1}</span>'
                f'<div><div style="font-weight:600;font-size:13px;">{title}</div>'
                f'<div style="font-size:11px;color:#64748b;">{desc}</div></div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.warning("No sections selected — the PDF will be empty!")


# PAGE: GENERATE
def page_generate():
    st.markdown('<div class="main-title">📄 Generate PDF</div>', unsafe_allow_html=True)
    st.markdown("Review your settings and generate your LCMS PDF report.")

    sd        = st.session_state.study_data
    mets      = st.session_state.metabolites
    theme_key = st.session_state.selected_theme
    opts      = st.session_state.options
    t         = THEMES[theme_key]

    sections = []
    if opts.get("include_cover"):       sections.append("Cover")
    if opts.get("include_summary"):     sections.append("Summary")
    if opts.get("include_metabolites"): sections.append(f"Metabolites ({opts.get('metabolites_per_page',4)}/page)")
    if opts.get("include_table"):       sections.append("Table")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Report Summary</div>', unsafe_allow_html=True)
        st.markdown(f"**Title:** {sd.get('title','')}")
        st.markdown(f"**Study ID:** {sd.get('study_id','')}")
        st.markdown(f"**Author:** {sd.get('author','')}")
        st.markdown(f"**Institution:** {sd.get('institution','')}")
        st.markdown(f"**Groups:** {sd.get('group1','Control')} vs {sd.get('group2','Treatment')}")
        st.markdown(f"**Samples:** {sd.get('samples','')}")

    with col2:
        st.markdown('<div class="section-header">Generation Settings</div>', unsafe_allow_html=True)
        st.markdown(f"**Theme:** {t['name']} — {t['subtitle']}")
        st.markdown(f"**Metabolites:** {len(mets)} features")
        st.markdown(f"**Sections:** {', '.join(sections) if sections else 'None'}")
        st.markdown(theme_swatch(theme_key), unsafe_allow_html=True)

    st.divider()

    # Single theme
    st.markdown('<div class="section-header">Generate — Selected Theme</div>', unsafe_allow_html=True)

    if st.button(f"🚀 Generate PDF ({t['name']})", type="primary", use_container_width=True):
        if not mets:
            st.error("No metabolite data. Please add metabolites first.")
        elif not sections:
            st.error("No content sections selected. Enable at least one in Design.")
        else:
            with st.spinner(f"Generating {t['name']} PDF…"):
                try:
                    pdf_bytes = generate_pdf_bytes(
                        theme_key=theme_key,
                        study_data=deepcopy(sd),
                        metabolites=deepcopy(mets),
                        options=deepcopy(opts),
                    )
                    filename = (
                        f"lcms_report_{theme_key}_"
                        f"{sd.get('study_id','report').replace(' ','-')}.pdf"
                    )
                    st.success(f"✅ PDF generated! ({len(pdf_bytes)/1024:.0f} KB)")
                    st.download_button(
                        label=f"⬇️ Download {t['name']} PDF",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary",
                    )
                except Exception as e:
                    st.error(f"Generation failed: {e}")
                    st.exception(e)

    st.divider()

    # Batch generation
    st.markdown('<div class="section-header">Batch Generate — All 10 Themes</div>', unsafe_allow_html=True)
    st.markdown("Generate a PDF for every theme at once. This may take 30–60 seconds.")

    if st.button("⚡ Generate All 10 Themes", use_container_width=True):
        if not mets:
            st.error("No metabolite data.")
        elif not sections:
            st.error("No content sections selected.")
        else:
            progress = st.progress(0)
            status   = st.empty()
            results  = {}

            for i, (tk, td) in enumerate(THEMES.items()):
                status.info(f"Generating {td['name']}…")
                try:
                    pdf_bytes = generate_pdf_bytes(
                        theme_key=tk,
                        study_data=deepcopy(sd),
                        metabolites=deepcopy(mets),
                        options=deepcopy(opts),
                    )
                    results[tk] = (pdf_bytes, td["name"], True, "")
                except Exception as e:
                    results[tk] = (None, td["name"], False, str(e))
                progress.progress((i + 1) / len(THEMES))

            status.empty()
            progress.empty()

            ok   = {k: v for k, v in results.items() if v[2]}
            fail = {k: v for k, v in results.items() if not v[2]}

            st.success(f"✅ Generated {len(ok)} / {len(THEMES)} PDFs successfully!")
            for k, (_, name, _, err) in fail.items():
                st.warning(f"{name}: {err}")

            st.markdown("**Download Individual Themes:**")
            dl_cols = st.columns(5)
            for i, (tk, (pdf_bytes, name, ok_flag, _)) in enumerate(results.items()):
                with dl_cols[i % 5]:
                    if ok_flag:
                        st.download_button(
                            label=f"⬇️ {name}",
                            data=pdf_bytes,
                            file_name=f"lcms_report_{tk}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"dl_{tk}",
                        )
                    else:
                        st.error(f"Failed: {name}")


# Router
page = st.session_state.page
if   page == "home":        page_home()
elif page == "study_info":  page_study_info()
elif page == "metabolites": page_metabolites()
elif page == "design":      page_design()
elif page == "generate":    page_generate()
else:                       page_home()