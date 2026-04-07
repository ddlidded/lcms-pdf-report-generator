#!/usr/bin/env python3
"""
LCMS PDF Report Generator - Streamlit Web Application

A modern web interface for generating LCMS Untargeted Metabolomics PDF reports
with customizable design options.

Run with: streamlit run streamlit_app.py

Author: NinjaTech AI
Version: 1.0.0
"""

import streamlit as st
import os
import json
import tempfile
import base64
from datetime import datetime
from pathlib import Path
from io import BytesIO

# Import the PDF generation module
from generate_pdfs import (
    THEMES, 
    DEFAULT_DESIGN_OPTIONS,
    DEFAULT_STUDY_DATA,
    DEFAULT_METABOLITES,
    generate_pdf,
    generate_all_themes,
    generate_full_html
)

from weasyprint import HTML


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="LCMS PDF Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0d9488;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .theme-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.5rem;
    }
    .theme-card:hover {
        border-color: #0d9488;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .theme-preview {
        height: 60px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stat-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #0d9488;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
    }
    .success-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .download-btn {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        background: #0d9488;
        color: white;
        border-radius: 0.5rem;
        text-decoration: none;
        font-weight: 600;
    }
    .download-btn:hover {
        background: #0f766e;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_pdf_download_link(pdf_bytes, filename, text):
    """Generate a download link for PDF"""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-btn">{text}</a>'
    return href


def render_theme_preview(theme_key, colors):
    """Render a theme preview card"""
    bg_style = f"background: {colors['bg']};" if 'gradient' in colors['bg'] or colors['bg'].startswith('linear') else f"background-color: {colors['bg']};"
    
    return f"""
    <div class="theme-preview" style="{bg_style} border: 2px solid {colors['border']};">
        <div style="color: {colors['text']};">
            <div style="font-weight: bold; font-size: 12px;">{colors['name']}</div>
            <div style="display: flex; gap: 5px; margin-top: 5px; justify-content: center;">
                <div style="width: 20px; height: 10px; background: {colors['accent']}; border-radius: 2px;"></div>
                <div style="width: 20px; height: 10px; background: {colors['accent2']}; border-radius: 2px;"></div>
                <div style="width: 20px; height: 10px; background: {colors['up_color']}; border-radius: 2px;"></div>
                <div style="width: 20px; height: 10px; background: {colors['down_color']}; border-radius: 2px;"></div>
            </div>
        </div>
    </div>
    """


def display_pdf_preview(pdf_bytes):
    """Display PDF preview using base64 encoding"""
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600" type="application/pdf"></iframe>'


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if 'study_data' not in st.session_state:
    st.session_state.study_data = DEFAULT_STUDY_DATA.copy()
    st.session_state.study_data['generated_on'] = datetime.now().strftime('%Y-%m-%d')

if 'metabolites' not in st.session_state:
    st.session_state.metabolites = DEFAULT_METABOLITES.copy()

if 'design_options' not in st.session_state:
    st.session_state.design_options = DEFAULT_DESIGN_OPTIONS.copy()

if 'generated_pdfs' not in st.session_state:
    st.session_state.generated_pdfs = {}

if 'logo_bytes' not in st.session_state:
    st.session_state.logo_bytes = None

if 'chromatogram_bytes' not in st.session_state:
    st.session_state.chromatogram_bytes = None

if 'ms2_bytes' not in st.session_state:
    st.session_state.ms2_bytes = None


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 LCMS PDF Report Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Generate professional LCMS Untargeted Metabolomics reports with customizable themes</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/pdf.png", width=80)
        st.title("Settings")
        
        # Navigation
        page = st.radio(
            "Navigate",
            ["🏠 Home", "📋 Study Info", "🧪 Metabolites", "🎨 Design", "📄 Generate"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Quick Stats
        st.markdown("### Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Metabolites", len(st.session_state.metabolites))
        with col2:
            st.metric("Theme", st.session_state.get('selected_theme', 'light').title())
        
        st.divider()
        
        # Load/Save Data
        st.markdown("### Data Management")
        uploaded_json = st.file_uploader("Load JSON Data", type=['json'], key="json_uploader")
        if uploaded_json:
            try:
                data = json.load(uploaded_json)
                if 'metabolites' in data:
                    st.session_state.metabolites = data.pop('metabolites')
                    st.session_state.study_data.update(data)
                    st.success("Data loaded successfully!")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
        
        if st.button("📥 Export JSON", use_container_width=True):
            export_data = {**st.session_state.study_data, 'metabolites': st.session_state.metabolites}
            json_str = json.dumps(export_data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"lcms_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.study_data = DEFAULT_STUDY_DATA.copy()
            st.session_state.metabolites = DEFAULT_METABOLITES.copy()
            st.session_state.design_options = DEFAULT_DESIGN_OPTIONS.copy()
            st.rerun()
    
    # Page Content
    if page == "🏠 Home":
        render_home_page()
    elif page == "📋 Study Info":
        render_study_info_page()
    elif page == "🧪 Metabolites":
        render_metabolites_page()
    elif page == "🎨 Design":
        render_design_page()
    elif page == "📄 Generate":
        render_generate_page()


def render_home_page():
    """Render the home page"""
    st.markdown("## Welcome to LCMS PDF Report Generator")
    
    st.markdown("""
    This application helps you generate professional PDF reports for LCMS Untargeted 
    Metabolomics studies. Create beautiful, publication-ready reports with customizable 
    themes and design options.
    """)
    
    # Features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎨 10 Themes
        Choose from 10 professionally designed color themes matching various 
        publication styles.
        """)
    
    with col2:
        st.markdown("""
        ### ⚙️ Customizable
        Customize every aspect of your report including fonts, colors, 
        layout, and content.
        """)
    
    with col3:
        st.markdown("""
        ### 📊 Rich Visualizations
        Automatically generate volcano plots, heatmaps, PCA plots, 
        and bar graphs.
        """)
    
    st.divider()
    
    # Quick Start
    st.markdown("## Quick Start")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("1️⃣ **Enter Study Info**\n\nFill in your study metadata on the Study Info page.")
    
    with col2:
        st.info("2️⃣ **Add Metabolites**\n\nEnter your metabolite data or load from JSON.")
    
    with col3:
        st.info("3️⃣ **Generate PDF**\n\nChoose a theme and generate your report!")
    
    st.divider()
    
    # Theme Preview Gallery
    st.markdown("## Theme Gallery")
    
    cols = st.columns(5)
    for i, (theme_key, colors) in enumerate(THEMES.items()):
        with cols[i % 5]:
            st.markdown(render_theme_preview(theme_key, colors), unsafe_allow_html=True)
            st.caption(f"**{theme_key.title()}**")


def render_study_info_page():
    """Render the study information input page"""
    st.markdown("## 📋 Study Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Basic Information")
        
        study_id = st.text_input("Study ID", value=st.session_state.study_data.get('study_id', ''))
        batch_name = st.text_input("Batch Name", value=st.session_state.study_data.get('batch_name', ''))
        instrument = st.selectbox(
            "Instrument",
            ['Q-Exactive Plus', 'Q-Exactive HF', 'Orbitrap Exploris', 'Q-TOF', 'Triple Quad', 'Other'],
            index=['Q-Exactive Plus', 'Q-Exactive HF', 'Orbitrap Exploris', 'Q-TOF', 'Triple Quad', 'Other'].index(
                st.session_state.study_data.get('instrument', 'Q-Exactive Plus')
            ) if st.session_state.study_data.get('instrument') in ['Q-Exactive Plus', 'Q-Exactive HF', 'Orbitrap Exploris', 'Q-TOF', 'Triple Quad', 'Other'] else 0
        )
        analyst = st.text_input("Analyst", value=st.session_state.study_data.get('analyst', ''))
        matrix = st.selectbox(
            "Matrix",
            ['Plasma', 'Serum', 'Urine', 'Tissue', 'CSF', 'Saliva', 'Other'],
            index=['Plasma', 'Serum', 'Urine', 'Tissue', 'CSF', 'Saliva', 'Other'].index(
                st.session_state.study_data.get('matrix', 'Plasma')
            ) if st.session_state.study_data.get('matrix') in ['Plasma', 'Serum', 'Urine', 'Tissue', 'CSF', 'Saliva', 'Other'] else 0
        )
        polarity = st.selectbox(
            "Polarity",
            ['ESI+', 'ESI-', 'Both'],
            index=['ESI+', 'ESI-', 'Both'].index(
                st.session_state.study_data.get('polarity', 'ESI+')
            ) if st.session_state.study_data.get('polarity') in ['ESI+', 'ESI-', 'Both'] else 0
        )
    
    with col2:
        st.markdown("### Analysis Parameters")
        
        sample_count = st.number_input("Sample Count", min_value=1, value=int(st.session_state.study_data.get('sample_count', 48)))
        feature_count = st.text_input("Feature Count", value=st.session_state.study_data.get('feature_count', '2,847'))
        significant_count = st.text_input("Significant Features", value=st.session_state.study_data.get('significant_count', '156'))
        normalization = st.selectbox(
            "Normalization",
            ['PQN', 'TIC', 'Median', 'None', 'Other'],
            index=['PQN', 'TIC', 'Median', 'None', 'Other'].index(
                st.session_state.study_data.get('normalization', 'PQN')
            ) if st.session_state.study_data.get('normalization') in ['PQN', 'TIC', 'Median', 'None', 'Other'] else 0
        )
        median_cv = st.text_input("Median CV", value=st.session_state.study_data.get('median_cv', '12.4%'))
        qc_status = st.selectbox(
            "QC Status",
            ['PASS', 'WARN', 'FAIL'],
            index=['PASS', 'WARN', 'FAIL'].index(
                st.session_state.study_data.get('qc_status', 'PASS')
            ) if st.session_state.study_data.get('qc_status') in ['PASS', 'WARN', 'FAIL'] else 0
        )
    
    st.divider()
    
    st.markdown("### Experimental Groups")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        control_group = st.text_input("Control Group Name", value=st.session_state.study_data.get('control_group', 'Control'))
    
    with col2:
        treatment_group = st.text_input("Treatment Group Name", value=st.session_state.study_data.get('treatment_group', 'Treatment'))
    
    with col3:
        company_name = st.text_input("Company/Institution Name", value=st.session_state.study_data.get('company_name', ''))
    
    st.divider()
    
    st.markdown("### Additional Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        blank_threshold = st.text_input("Blank Threshold", value=st.session_state.study_data.get('blank_threshold', '3x'))
        drift_corrected = st.text_input("Drift Corrected", value=st.session_state.study_data.get('drift_corrected', 'Yes'))
    
    with col2:
        injection_monitoring = st.text_input("Injection Monitoring", value=st.session_state.study_data.get('injection_monitoring', 'Stable'))
    
    # Update session state
    if st.button("💾 Save Study Information", type="primary", use_container_width=True):
        st.session_state.study_data = {
            'study_id': study_id,
            'batch_name': batch_name,
            'instrument': instrument,
            'analyst': analyst,
            'matrix': matrix,
            'polarity': polarity,
            'sample_count': str(sample_count),
            'feature_count': feature_count,
            'significant_count': significant_count,
            'normalization': normalization,
            'median_cv': median_cv,
            'qc_status': qc_status,
            'control_group': control_group,
            'treatment_group': treatment_group,
            'company_name': company_name,
            'blank_threshold': blank_threshold,
            'drift_corrected': drift_corrected,
            'injection_monitoring': injection_monitoring,
            'generated_on': datetime.now().strftime('%Y-%m-%d')
        }
        st.success("Study information saved!")


def render_metabolites_page():
    """Render the metabolites management page"""
    st.markdown("## 🧪 Metabolite Data")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Metabolite", use_container_width=True):
            new_met = {
                'id': f'FT-{len(st.session_state.metabolites)+1:05d}',
                'name': '',
                'formula': '',
                'mz': 0.0,
                'rt': 0.0,
                'fc': 1.0,
                'fdr': 0.05,
                'direction': 'up',
                'confidence': 'Level 2',
                'database': '',
                'pathway': '',
                'adduct': '[M+H]+',
                'match_score': '85%'
            }
            st.session_state.metabolites.append(new_met)
            st.rerun()
    
    with col2:
        if st.button("📋 Load Sample Data", use_container_width=True):
            st.session_state.metabolites = DEFAULT_METABOLITES.copy()
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.metabolites = []
            st.rerun()
    
    with col4:
        # CSV Upload
        uploaded_csv = st.file_uploader("📁 Upload CSV", type=['csv'], key="csv_uploader", label_visibility="collapsed")
        if uploaded_csv:
            try:
                import pandas as pd
                df = pd.read_csv(uploaded_csv)
                st.session_state.metabolites = df.to_dict('records')
                st.success(f"Loaded {len(st.session_state.metabolites)} metabolites from CSV")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading CSV: {str(e)}")
    
    st.divider()
    
    # Metabolite data editor
    if st.session_state.metabolites:
        st.markdown(f"### Metabolite List ({len(st.session_state.metabolites)} entries)")
        
        # Convert to dataframe for editing
        import pandas as pd
        df = pd.DataFrame(st.session_state.metabolites)
        
        # Configure columns
        column_config = {
            'id': st.column_config.TextColumn('ID', width='small'),
            'name': st.column_config.TextColumn('Name', width='medium'),
            'formula': st.column_config.TextColumn('Formula', width='small'),
            'mz': st.column_config.NumberColumn('m/z', format='%.4f', width='small'),
            'rt': st.column_config.NumberColumn('RT (min)', format='%.2f', width='small'),
            'fc': st.column_config.NumberColumn('FC', format='%.2f', width='small'),
            'fdr': st.column_config.NumberColumn('FDR', format='%.4f', width='small'),
            'direction': st.column_config.SelectColumn('Direction', options=['up', 'down'], width='small'),
            'adduct': st.column_config.TextColumn('Adduct', width='small'),
            'confidence': st.column_config.SelectColumn('Level', options=['Level 1', 'Level 2', 'Level 3', 'Level 4'], width='small'),
            'database': st.column_config.TextColumn('Database', width='medium'),
            'match_score': st.column_config.TextColumn('Match %', width='small'),
            'pathway': st.column_config.TextColumn('Pathway', width='medium'),
        }
        
        # Filter columns that exist
        available_columns = {k: v for k, v in column_config.items() if k in df.columns}
        
        edited_df = st.data_editor(
            df,
            column_config=available_columns,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True
        )
        
        # Update session state
        st.session_state.metabolites = edited_df.to_dict('records')
        
    else:
        st.info("No metabolites added yet. Click 'Add Metabolite' or 'Load Sample Data' to get started.")
    
    # Summary statistics
    if st.session_state.metabolites:
        st.divider()
        st.markdown("### Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            up_count = sum(1 for m in st.session_state.metabolites if m.get('direction') == 'up')
            st.metric("Upregulated", up_count, delta=None)
        
        with col2:
            down_count = sum(1 for m in st.session_state.metabolites if m.get('direction') == 'down')
            st.metric("Downregulated", down_count, delta=None)
        
        with col3:
            avg_fc = sum(float(m.get('fc', 1)) for m in st.session_state.metabolites) / len(st.session_state.metabolites)
            st.metric("Avg Fold Change", f"{avg_fc:.2f}")
        
        with col4:
            level1_count = sum(1 for m in st.session_state.metabolites if m.get('confidence') == 'Level 1')
            st.metric("Level 1 IDs", level1_count)


def render_design_page():
    """Render the design customization page"""
    st.markdown("## 🎨 Design Options")
    
    # Theme Selection
    st.markdown("### Theme Selection")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        theme_options = list(THEMES.keys())
        selected_theme = st.selectbox(
            "Choose Theme",
            theme_options,
            index=theme_options.index(st.session_state.get('selected_theme', 'light')),
            format_func=lambda x: f"{x.title()} - {THEMES[x]['name']}"
        )
        st.session_state.selected_theme = selected_theme
        
        # Theme preview
        colors = THEMES[selected_theme]
        st.markdown(render_theme_preview(selected_theme, colors), unsafe_allow_html=True)
        st.caption(colors['description'])
    
    with col2:
        # Color palette display
        st.markdown("#### Color Palette")
        palette_cols = st.columns(8)
        color_names = ['accent', 'accent2', 'up_color', 'down_color', 'text', 'muted', 'border', 'card']
        for i, (name, color) in enumerate({k: colors[k] for k in color_names if k in colors}.items()):
            with palette_cols[i]:
                st.markdown(f"""
                <div style="background-color: {color}; height: 60px; border-radius: 8px; margin-bottom: 5px; border: 1px solid #e2e8f0;"></div>
                <div style="font-size: 10px; text-align: center; color: #64748b;">{name}</div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Layout Options
    st.markdown("### Layout Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        metabolites_per_page = st.slider(
            "Metabolites per Page",
            min_value=1,
            max_value=6,
            value=st.session_state.design_options.get('metabolites_per_page', 4)
        )
        
        page_margin = st.select_slider(
            "Page Margin",
            options=['10mm', '12mm', '15mm', '18mm', '20mm'],
            value=st.session_state.design_options.get('page_margin', '15mm')
        )
        
        card_gap = st.select_slider(
            "Card Spacing",
            options=['4px', '6px', '8px', '10px', '12px'],
            value=st.session_state.design_options.get('card_gap', '8px')
        )
    
    with col2:
        global_plot_height = st.select_slider(
            "Global Plot Height",
            options=['150px', '175px', '200px', '225px', '250px'],
            value=st.session_state.design_options.get('global_plot_height', '200px')
        )
        
        metabolite_plot_height = st.select_slider(
            "Metabolite Plot Height",
            options=['45px', '50px', '55px', '60px', '65px'],
            value=st.session_state.design_options.get('metabolite_plot_height', '55px')
        )
    
    st.divider()
    
    # Typography
    st.markdown("### Typography")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        title_font_size = st.select_slider(
            "Title Font Size",
            options=['18px', '20px', '22px', '24px', '26px'],
            value=st.session_state.design_options.get('title_font_size', '22px')
        )
    
    with col2:
        body_font_size = st.select_slider(
            "Body Font Size",
            options=['9px', '10px', '11px', '12px', '13px'],
            value=st.session_state.design_options.get('body_font_size', '11px')
        )
    
    with col3:
        font_family = st.selectbox(
            "Font Family",
            ["'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
             "'Arial', sans-serif",
             "'Helvetica', sans-serif",
             "'Roboto', sans-serif",
             "'Times New Roman', serif"],
            index=0
        )
    
    st.divider()
    
    # Content Options
    st.markdown("### Content Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        show_summary = st.checkbox("Show Summary Page", value=st.session_state.design_options.get('show_summary_page', True))
        show_global_plots = st.checkbox("Show Global Plots Page", value=st.session_state.design_options.get('show_global_plots', True))
        show_volcano = st.checkbox("Show Volcano Plot", value=st.session_state.design_options.get('show_volcano_plot', True))
        show_heatmap = st.checkbox("Show Heatmap", value=st.session_state.design_options.get('show_heatmap', True))
        show_pca = st.checkbox("Show PCA Plot", value=st.session_state.design_options.get('show_pca_plot', True))
    
    with col2:
        show_bar_graph = st.checkbox("Show Bar Graph", value=st.session_state.design_options.get('show_bar_graph', True))
        show_chromatogram = st.checkbox("Show Chromatogram", value=st.session_state.design_options.get('show_chromatogram', True))
        show_ms2 = st.checkbox("Show MS2 Spectrum", value=st.session_state.design_options.get('show_ms2_spectrum', True))
        show_mirror = st.checkbox("Show Mirror Plot", value=st.session_state.design_options.get('show_mirror_plot', True))
        show_footer = st.checkbox("Show Annotation Footer", value=st.session_state.design_options.get('show_annotation_footer', True))
    
    st.divider()
    
    # Images
    st.markdown("### Custom Images")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Logo**")
        logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'svg'], key="logo_upload", label_visibility="collapsed")
        if logo_file:
            st.session_state.logo_bytes = logo_file.read()
            st.image(st.session_state.logo_bytes, width=100)
        if st.button("Clear Logo"):
            st.session_state.logo_bytes = None
            st.rerun()
    
    with col2:
        st.markdown("**Chromatogram**")
        chrom_file = st.file_uploader("Upload Chromatogram", type=['png', 'jpg', 'svg'], key="chrom_upload", label_visibility="collapsed")
        if chrom_file:
            st.session_state.chromatogram_bytes = chrom_file.read()
            st.image(st.session_state.chromatogram_bytes, width=100)
        if st.button("Clear Chromatogram"):
            st.session_state.chromatogram_bytes = None
            st.rerun()
    
    with col3:
        st.markdown("**MS2 Spectrum**")
        ms2_file = st.file_uploader("Upload MS2", type=['png', 'jpg', 'svg'], key="ms2_upload", label_visibility="collapsed")
        if ms2_file:
            st.session_state.ms2_bytes = ms2_file.read()
            st.image(st.session_state.ms2_bytes, width=100)
        if st.button("Clear MS2"):
            st.session_state.ms2_bytes = None
            st.rerun()
    
    # Save options
    if st.button("💾 Save Design Options", type="primary", use_container_width=True):
        st.session_state.design_options = {
            'metabolites_per_page': metabolites_per_page,
            'page_margin': page_margin,
            'card_gap': card_gap,
            'global_plot_height': global_plot_height,
            'metabolite_plot_height': metabolite_plot_height,
            'title_font_size': title_font_size,
            'body_font_size': body_font_size,
            'font_family': font_family,
            'show_summary_page': show_summary,
            'show_global_plots': show_global_plots,
            'show_volcano_plot': show_volcano,
            'show_heatmap': show_heatmap,
            'show_pca_plot': show_pca,
            'show_bar_graph': show_bar_graph,
            'show_chromatogram': show_chromatogram,
            'show_ms2_spectrum': show_ms2,
            'show_mirror_plot': show_mirror,
            'show_annotation_footer': show_footer,
        }
        st.success("Design options saved!")


def render_generate_page():
    """Render the PDF generation page"""
    st.markdown("## 📄 Generate PDF Report")
    
    # Check if data is ready
    if not st.session_state.metabolites:
        st.warning("⚠️ No metabolite data found. Please add metabolites on the Metabolites page.")
        return
    
    # Preview info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Study ID", st.session_state.study_data.get('study_id', 'N/A'))
    with col2:
        st.metric("Metabolites", len(st.session_state.metabolites))
    with col3:
        st.metric("Theme", st.session_state.get('selected_theme', 'light').title())
    with col4:
        st.metric("Per Page", st.session_state.design_options.get('metabolites_per_page', 4))
    
    st.divider()
    
    # Generation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Generate Single PDF")
        
        selected_theme = st.selectbox(
            "Theme",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.get('selected_theme', 'light')),
            key="gen_theme_single"
        )
        
        if st.button("📄 Generate PDF", type="primary", use_container_width=True, key="gen_single"):
            with st.spinner("Generating PDF..."):
                try:
                    # Create temp file for output
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                        output_path = tmp.name
                    
                    # Generate PDF
                    generate_pdf(
                        output_path,
                        st.session_state.study_data,
                        st.session_state.metabolites,
                        selected_theme,
                        st.session_state.design_options
                    )
                    
                    # Read PDF
                    with open(output_path, 'rb') as f:
                        pdf_bytes = f.read()
                    
                    # Store for download
                    st.session_state.generated_pdfs[selected_theme] = pdf_bytes
                    
                    # Cleanup
                    os.unlink(output_path)
                    
                    st.success(f"✅ PDF generated successfully!")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_bytes,
                        file_name=f"LCMS_Report_{st.session_state.study_data.get('study_id', 'report')}_{selected_theme}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
    
    with col2:
        st.markdown("### Generate All Themes")
        
        if st.button("📚 Generate All 10 Themes", type="secondary", use_container_width=True, key="gen_all"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            generated_files = []
            
            for i, theme_key in enumerate(THEMES.keys()):
                status_text.text(f"Generating {theme_key.title()}... ({i+1}/{len(THEMES)})")
                progress_bar.progress((i + 1) / len(THEMES))
                
                try:
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                        output_path = tmp.name
                    
                    generate_pdf(
                        output_path,
                        st.session_state.study_data,
                        st.session_state.metabolites,
                        theme_key,
                        st.session_state.design_options
                    )
                    
                    with open(output_path, 'rb') as f:
                        pdf_bytes = f.read()
                    
                    st.session_state.generated_pdfs[theme_key] = pdf_bytes
                    generated_files.append(theme_key)
                    
                    os.unlink(output_path)
                    
                except Exception as e:
                    st.warning(f"Failed to generate {theme_key}: {str(e)}")
            
            status_text.text("Done!")
            st.success(f"✅ Generated {len(generated_files)} PDF files!")
    
    # Download all generated PDFs
    if st.session_state.generated_pdfs:
        st.divider()
        st.markdown("### 📥 Download Generated PDFs")
        
        cols = st.columns(5)
        for i, (theme_key, pdf_bytes) in enumerate(st.session_state.generated_pdfs.items()):
            with cols[i % 5]:
                st.download_button(
                    label=f"📥 {theme_key.title()}",
                    data=pdf_bytes,
                    file_name=f"LCMS_Report_{theme_key}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )


# =============================================================================
# RUN APPLICATION
# =============================================================================

if __name__ == "__main__":
    main()