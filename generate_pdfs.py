#!/usr/bin/env python3
"""
LCMS Untargeted Metabolomics Report PDF Generator

A flexible Python script for generating professional LCMS PDF reports
with customizable design options matching the example previews.

Usage:
    python generate_pdfs.py --help
    python generate_pdfs.py --theme light --output report.pdf
    python generate_pdfs.py --all-themes --output-dir ./reports

Author: NinjaTech AI
Version: 1.0.0
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from weasyprint import HTML, CSS


# =============================================================================
# THEME CONFIGURATIONS - Matching the 10 example PDF themes
# =============================================================================

THEMES = {
    "light": {
        "name": "Modern Light Executive Dashboard",
        "description": "Clean white background with teal/blue accents",
        "bg": "#f8fafc",
        "surface": "#ffffff",
        "text": "#1e293b",
        "muted": "#64748b",
        "accent": "#0d9488",
        "accent2": "#3b82f6",
        "border": "#e2e8f0",
        "card": "#ffffff",
        "up_color": "#10b981",
        "down_color": "#ef4444",
        "header_gradient": "linear-gradient(90deg, #0d9488, #3b82f6)",
        "table_header_bg": "#0d9488",
    },
    "clinical": {
        "name": "Clinical Clean Publication Style",
        "description": "Medical publication style with green accents",
        "bg": "#ffffff",
        "surface": "#ffffff",
        "text": "#111827",
        "muted": "#6b7280",
        "accent": "#059669",
        "accent2": "#2563eb",
        "border": "#d1d5db",
        "card": "#f9fafb",
        "up_color": "#059669",
        "down_color": "#dc2626",
        "header_gradient": "linear-gradient(90deg, #059669, #2563eb)",
        "table_header_bg": "#059669",
    },
    "dark": {
        "name": "Dark Modern Analytics Theme",
        "description": "Dark background with vibrant teal/purple accents",
        "bg": "#0f172a",
        "surface": "#1e293b",
        "text": "#f1f5f9",
        "muted": "#94a3b8",
        "accent": "#14b8a6",
        "accent2": "#8b5cf6",
        "border": "#334155",
        "card": "#1e293b",
        "up_color": "#34d399",
        "down_color": "#f87171",
        "header_gradient": "linear-gradient(90deg, #14b8a6, #8b5cf6)",
        "table_header_bg": "#14b8a6",
    },
    "biotech": {
        "name": "Biotech Premium Report",
        "description": "Green biotech aesthetic with cyan accents",
        "bg": "#f0fdf4",
        "surface": "#ffffff",
        "text": "#14532d",
        "muted": "#166534",
        "accent": "#16a34a",
        "accent2": "#0ea5e9",
        "border": "#bbf7d0",
        "card": "#ffffff",
        "up_color": "#16a34a",
        "down_color": "#dc2626",
        "header_gradient": "linear-gradient(90deg, #16a34a, #0ea5e9)",
        "table_header_bg": "#16a34a",
    },
    "journal": {
        "name": "Journal Figure-Forward Style",
        "description": "Publication-ready with red/blue accents",
        "bg": "#ffffff",
        "surface": "#ffffff",
        "text": "#000000",
        "muted": "#4b5563",
        "accent": "#b91c1c",
        "accent2": "#1d4ed8",
        "border": "#d1d5db",
        "card": "#f3f4f6",
        "up_color": "#b91c1c",
        "down_color": "#1d4ed8",
        "header_gradient": "linear-gradient(90deg, #b91c1c, #1d4ed8)",
        "table_header_bg": "#b91c1c",
    },
    "minimal": {
        "name": "Minimal White Research Style",
        "description": "Ultra-clean minimal design with gray accents",
        "bg": "#ffffff",
        "surface": "#ffffff",
        "text": "#1f2937",
        "muted": "#6b7280",
        "accent": "#374151",
        "accent2": "#6b7280",
        "border": "#e5e7eb",
        "card": "#fafafa",
        "up_color": "#059669",
        "down_color": "#dc2626",
        "header_gradient": "linear-gradient(90deg, #374151, #6b7280)",
        "table_header_bg": "#374151",
    },
    "scientific": {
        "name": "Data-Dense Scientific Report",
        "description": "Compact information-rich layout with blue/purple",
        "bg": "#f9fafb",
        "surface": "#ffffff",
        "text": "#111827",
        "muted": "#4b5563",
        "accent": "#0284c7",
        "accent2": "#7c3aed",
        "border": "#e5e7eb",
        "card": "#ffffff",
        "up_color": "#0891b2",
        "down_color": "#c2410c",
        "header_gradient": "linear-gradient(90deg, #0284c7, #7c3aed)",
        "table_header_bg": "#0284c7",
    },
    "corporate": {
        "name": "Corporate Professional Style",
        "description": "Business professional with dark blue accents",
        "bg": "#f3f4f6",
        "surface": "#ffffff",
        "text": "#1f2937",
        "muted": "#4b5563",
        "accent": "#1e40af",
        "accent2": "#0369a1",
        "border": "#d1d5db",
        "card": "#ffffff",
        "up_color": "#059669",
        "down_color": "#dc2626",
        "header_gradient": "linear-gradient(90deg, #1e40af, #0369a1)",
        "table_header_bg": "#1e40af",
    },
    "gradient": {
        "name": "Gradient Modern SaaS Style",
        "description": "Modern gradient purple/pink theme",
        "bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "surface": "rgba(255,255,255,0.95)",
        "text": "#1f2937",
        "muted": "#6b7280",
        "accent": "#7c3aed",
        "accent2": "#ec4899",
        "border": "#e5e7eb",
        "card": "#ffffff",
        "up_color": "#10b981",
        "down_color": "#f43f5e",
        "header_gradient": "linear-gradient(90deg, #7c3aed, #ec4899)",
        "table_header_bg": "#7c3aed",
    },
    "academic": {
        "name": "Academic Publication Supplement",
        "description": "Traditional academic with red/blue accents",
        "bg": "#ffffff",
        "surface": "#ffffff",
        "text": "#1a1a1a",
        "muted": "#595959",
        "accent": "#b91c1c",
        "accent2": "#1d4ed8",
        "border": "#d4d4d4",
        "card": "#fafafa",
        "up_color": "#15803d",
        "down_color": "#b91c1c",
        "header_gradient": "linear-gradient(90deg, #b91c1c, #1d4ed8)",
        "table_header_bg": "#b91c1c",
    },
}


# =============================================================================
# DESIGN CUSTOMIZATION OPTIONS
# =============================================================================

DEFAULT_DESIGN_OPTIONS = {
    # Layout options
    "metabolites_per_page": 4,
    "show_summary_page": True,
    "show_global_plots": True,
    "show_volcano_plot": True,
    "show_heatmap": True,
    "show_pca_plot": True,
    
    # Metabolite card options
    "show_bar_graph": True,
    "show_chromatogram": True,
    "show_ms2_spectrum": True,
    "show_mirror_plot": True,
    "show_annotation_footer": True,
    
    # Typography
    "title_font_size": "22px",
    "heading_font_size": "18px",
    "body_font_size": "11px",
    "small_font_size": "9px",
    "font_family": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    
    # Spacing
    "page_margin": "15mm",
    "card_gap": "8px",
    "section_gap": "15px",
    
    # Footer
    "show_footer": True,
    "footer_text": "{company_name} | Study: {study_id} | Generated: {date}",
    
    # Logo
    "logo_width": "100px",
    "logo_height": "45px",
    "show_logo_placeholder": True,
    
    # Plot heights
    "global_plot_height": "200px",
    "metabolite_plot_height": "55px",
}


# =============================================================================
# SAMPLE DATA
# =============================================================================

DEFAULT_STUDY_DATA = {
    "study_id": "LCMS-2024-0142",
    "batch_name": "Batch A",
    "instrument": "Q-Exactive Plus",
    "analyst": "Dr. Sarah Chen",
    "matrix": "Plasma",
    "generated_on": "2024-01-15",
    "sample_count": "48",
    "feature_count": "2,847",
    "significant_count": "156",
    "polarity": "ESI+",
    "normalization": "PQN",
    "blank_threshold": "3x",
    "qc_status": "PASS",
    "median_cv": "12.4%",
    "drift_corrected": "Yes",
    "injection_monitoring": "Stable",
    "company_name": "Your Company Name",
    "footer_text": "Confidential - For internal use only",
    "control_group": "Control",
    "treatment_group": "Treatment",
}

DEFAULT_METABOLITES = [
    {
        "id": "FT-00184",
        "name": "L-Carnitine",
        "formula": "C7H15NO3",
        "mz": 162.1130,
        "rt": 5.42,
        "fc": 3.42,
        "fdr": 0.001,
        "direction": "up",
        "confidence": "Level 2",
        "database": "HMDB0000062",
        "pathway": "Fatty acid metabolism",
        "adduct": "[M+H]+",
        "mass_error": "1.2 ppm",
        "rt_predicted": "5.38 min",
        "match_score": "87%",
        "log2fc": 1.77,
        "log10pval": 3.0
    },
    {
        "id": "FT-00721",
        "name": "Phosphocholine",
        "formula": "C5H14NO4P",
        "mz": 184.0739,
        "rt": 8.91,
        "fc": 2.87,
        "fdr": 0.003,
        "direction": "up",
        "confidence": "Level 2",
        "database": "HMDB0001565",
        "pathway": "Glycerophospholipid metabolism",
        "adduct": "[M+H]+",
        "mass_error": "0.8 ppm",
        "rt_predicted": "8.85 min",
        "match_score": "92%",
        "log2fc": 1.52,
        "log10pval": 2.52
    },
    {
        "id": "FT-01345",
        "name": "Taurine",
        "formula": "C2H7NO3S",
        "mz": 126.0219,
        "rt": 3.15,
        "fc": 0.45,
        "fdr": 0.008,
        "direction": "down",
        "confidence": "Level 1",
        "database": "HMDB0000251",
        "pathway": "Bile acid metabolism",
        "adduct": "[M+H]+",
        "mass_error": "0.5 ppm",
        "rt_predicted": "3.12 min",
        "match_score": "98%",
        "log2fc": -1.15,
        "log10pval": 2.10
    },
    {
        "id": "FT-02089",
        "name": "Hypoxanthine",
        "formula": "C5H4N4O",
        "mz": 137.0459,
        "rt": 6.78,
        "fc": 4.12,
        "fdr": 0.012,
        "direction": "up",
        "confidence": "Level 2",
        "database": "HMDB0000157",
        "pathway": "Purine metabolism",
        "adduct": "[M+H]+",
        "mass_error": "1.5 ppm",
        "rt_predicted": "6.72 min",
        "match_score": "85%",
        "log2fc": 2.04,
        "log10pval": 1.92
    },
    {
        "id": "FT-00312",
        "name": "Sphingomyelin (d18:1/16:0)",
        "formula": "C39H81N2O6P",
        "mz": 703.5734,
        "rt": 12.34,
        "fc": 2.15,
        "fdr": 0.021,
        "direction": "up",
        "confidence": "Level 3",
        "database": "LMSP03010004",
        "pathway": "Sphingolipid metabolism",
        "adduct": "[M+H]+",
        "mass_error": "2.1 ppm",
        "rt_predicted": "12.28 min",
        "match_score": "72%",
        "log2fc": 1.10,
        "log10pval": 1.68
    },
    {
        "id": "FT-00876",
        "name": "Glutathione (oxidized)",
        "formula": "C20H32N6O12S2",
        "mz": 612.1520,
        "rt": 9.87,
        "fc": 0.62,
        "fdr": 0.035,
        "direction": "down",
        "confidence": "Level 2",
        "database": "HMDB0003337",
        "pathway": "Glutathione metabolism",
        "adduct": "[M+H]+",
        "mass_error": "1.8 ppm",
        "rt_predicted": "9.82 min",
        "match_score": "88%",
        "log2fc": -0.69,
        "log10pval": 1.46
    },
]


# =============================================================================
# SVG GENERATION FUNCTIONS
# =============================================================================

def generate_bar_graph_svg(metabolite: Dict, colors: Dict, 
                           control_group: str = "Control", 
                           treatment_group: str = "Treatment") -> str:
    """Generate SVG bar graph for a metabolite"""
    direction = metabolite.get('direction', 'up')
    fc = float(metabolite.get('fc', 2.0))
    
    # Simulated values based on direction
    control_mean = 0.35 if direction == 'up' else 0.75
    control_sd = 0.08
    treatment_mean = control_mean * fc
    treatment_sd = 0.10
    
    max_val = max(control_mean + control_sd, treatment_mean + treatment_sd)
    scale = 80 / max_val if max_val > 0 else 1
    
    control_height = control_mean * scale
    treatment_height = treatment_mean * scale
    
    bar_width = 50
    gap = 30
    start_x = 50
    
    return f'''
<svg viewBox="0 0 180 120" class="bar-graph-svg">
    <rect x="30" y="10" width="140" height="85" fill="#fafafa" stroke="{colors['border']}"/>
    <line x1="30" y1="31" x2="170" y2="31" stroke="{colors['border']}" stroke-dasharray="2" opacity="0.5"/>
    <line x1="30" y1="52" x2="170" y2="52" stroke="{colors['border']}" stroke-dasharray="2" opacity="0.5"/>
    <line x1="30" y1="73" x2="170" y2="73" stroke="{colors['border']}" stroke-dasharray="2" opacity="0.5"/>
    
    <!-- Control bar -->
    <rect x="{start_x}" y="{95 - control_height}" width="{bar_width}" height="{control_height}" 
          fill="{colors['accent']}" rx="3"/>
    
    <!-- Treatment bar -->
    <rect x="{start_x + bar_width + gap}" y="{95 - treatment_height}" width="{bar_width}" height="{treatment_height}" 
          fill="{colors['accent2']}" rx="3"/>
    
    <!-- Significance bracket -->
    <path d="M {start_x + bar_width + 5} {25} L {start_x + bar_width + 10} {20} L {start_x + bar_width + gap - 5} {20} L {start_x + bar_width + gap} {25}" 
          fill="none" stroke="{colors['text']}" stroke-width="1"/>
    <text x="{start_x + bar_width + gap/2 + 5}" y="17" font-size="8" fill="{colors['text']}" text-anchor="middle">**</text>
    
    <!-- X-axis labels -->
    <text x="{start_x + bar_width/2}" y="108" font-size="8" fill="{colors['muted']}" text-anchor="middle">{control_group}</text>
    <text x="{start_x + bar_width + gap + bar_width/2}" y="108" font-size="8" fill="{colors['muted']}" text-anchor="middle">{treatment_group}</text>
    
    <!-- Y-axis label -->
    <text x="8" y="55" font-size="7" fill="{colors['muted']}" text-anchor="middle" transform="rotate(-90 8 55)">Rel. Abundance</text>
</svg>'''


def generate_volcano_svg(colors: Dict, metabolites: List[Dict] = None) -> str:
    """Generate SVG volcano plot"""
    # Use metabolite data if available, otherwise use sample points
    if metabolites:
        points_html = ""
        for met in metabolites:
            log2fc = met.get('log2fc', 0)
            log10pval = met.get('log10pval', 1)
            direction = met.get('direction', 'up')
            
            # Scale to plot area
            x = 110 + log2fc * 25  # Center at 110, scale by 25
            y = 150 - log10pval * 40  # Invert Y, scale by 40
            
            color = colors['up_color'] if direction == 'up' else colors['down_color']
            if log10pval < 1.3:  # Not significant
                color = colors['muted']
                points_html += f'<circle cx="{x}" cy="{y}" r="2" fill="{color}"/>\n'
            else:
                points_html += f'<circle cx="{x}" cy="{y}" r="3" fill="{color}"/>\n'
    else:
        # Sample data
        points_html = f'''
        <!-- Upregulated -->
        <circle cx="160" cy="40" r="3" fill="{colors['up_color']}"/>
        <circle cx="170" cy="50" r="3" fill="{colors['up_color']}"/>
        <circle cx="155" cy="60" r="3" fill="{colors['up_color']}"/>
        <circle cx="175" cy="45" r="3" fill="{colors['up_color']}"/>
        <!-- Downregulated -->
        <circle cx="50" cy="45" r="3" fill="{colors['down_color']}"/>
        <circle cx="40" cy="55" r="3" fill="{colors['down_color']}"/>
        <circle cx="55" cy="65" r="3" fill="{colors['down_color']}"/>
        <!-- Non-significant -->
        <circle cx="110" cy="120" r="2" fill="{colors['muted']}"/>
        <circle cx="100" cy="130" r="2" fill="{colors['muted']}"/>
        <circle cx="120" cy="125" r="2" fill="{colors['muted']}"/>
        <circle cx="95" cy="135" r="2" fill="{colors['muted']}"/>
        <circle cx="115" cy="115" r="2" fill="{colors['muted']}"/>
        '''
    
    return f'''
<svg viewBox="0 0 200 180" width="180" height="160">
    <rect x="30" y="10" width="160" height="140" fill="#fafafa" stroke="{colors['border']}"/>
    
    <!-- Axes -->
    <line x1="30" y1="150" x2="190" y2="150" stroke="{colors['text']}" stroke-width="1"/>
    <line x1="30" y1="10" x2="30" y2="150" stroke="{colors['text']}" stroke-width="1"/>
    
    <!-- Significance threshold line -->
    <line x1="30" y1="90" x2="190" y2="90" stroke="{colors['muted']}" stroke-dasharray="4" opacity="0.5"/>
    
    {points_html}
    
    <!-- Labels -->
    <text x="110" y="170" font-size="8" fill="{colors['muted']}" text-anchor="middle">log₂(Fold Change)</text>
    <text x="10" y="80" font-size="8" fill="{colors['muted']}" text-anchor="middle" transform="rotate(-90 10 80)">-log₁₀(p-value)</text>
</svg>'''


def generate_heatmap_svg(colors: Dict) -> str:
    """Generate SVG heatmap"""
    # Generate a 5x5 heatmap grid
    cell_colors = [
        [colors['up_color'], colors['accent'], "#6ee7b7", "#a7f3d0", colors['up_color']],
        [colors['down_color'], "#fca5a5", colors['up_color'], colors['accent'], "#6ee7b7"],
        ["#6ee7b7", colors['down_color'], "#fca5a5", colors['up_color'], colors['accent']],
        ["#a7f3d0", "#6ee7b7", colors['up_color'], colors['down_color'], "#fca5a5"],
        ["#fca5a5", colors['up_color'], colors['accent'], "#6ee7b7", "#a7f3d0"],
    ]
    
    cells = ""
    for row_idx, row in enumerate(cell_colors):
        for col_idx, color in enumerate(row):
            x = 40 + col_idx * 30
            y = 20 + row_idx * 25
            cells += f'<rect x="{x}" y="{y}" width="28" height="23" fill="{color}"/>\n'
    
    return f'''
<svg viewBox="0 0 200 180" width="180" height="160">
    <rect x="30" y="10" width="160" height="140" fill="#fafafa" stroke="{colors['border']}"/>
    {cells}
    
    <!-- Labels -->
    <text x="50" y="168" font-size="6" fill="{colors['muted']}" text-anchor="middle">S1</text>
    <text x="80" y="168" font-size="6" fill="{colors['muted']}" text-anchor="middle">S2</text>
    <text x="110" y="168" font-size="6" fill="{colors['muted']}" text-anchor="middle">S3</text>
    <text x="140" y="168" font-size="6" fill="{colors['muted']}" text-anchor="middle">S4</text>
    <text x="170" y="168" font-size="6" fill="{colors['muted']}" text-anchor="middle">S5</text>
</svg>'''


def generate_pca_svg(colors: Dict) -> str:
    """Generate SVG PCA plot"""
    return f'''
<svg viewBox="0 0 200 180" width="180" height="160">
    <rect x="30" y="10" width="160" height="140" fill="#fafafa" stroke="{colors['border']}"/>
    
    <!-- Grid lines -->
    <line x1="30" y1="80" x2="190" y2="80" stroke="{colors['border']}" stroke-dasharray="3"/>
    <line x1="110" y1="10" x2="110" y2="150" stroke="{colors['border']}" stroke-dasharray="3"/>
    
    <!-- Control group points -->
    <circle cx="70" cy="60" r="5" fill="{colors['accent']}"/>
    <circle cx="80" cy="70" r="5" fill="{colors['accent']}"/>
    <circle cx="65" cy="75" r="5" fill="{colors['accent']}"/>
    <circle cx="75" cy="55" r="5" fill="{colors['accent']}"/>
    <circle cx="85" cy="65" r="5" fill="{colors['accent']}"/>
    
    <!-- Treatment group points -->
    <circle cx="140" cy="90" r="5" fill="{colors['accent2']}"/>
    <circle cx="150" cy="100" r="5" fill="{colors['accent2']}"/>
    <circle cx="135" cy="105" r="5" fill="{colors['accent2']}"/>
    <circle cx="145" cy="85" r="5" fill="{colors['accent2']}"/>
    <circle cx="155" cy="95" r="5" fill="{colors['accent2']}"/>
    
    <!-- Legend -->
    <circle cx="50" cy="165" r="4" fill="{colors['accent']}"/>
    <text x="60" y="168" font-size="7" fill="{colors['muted']}">Control</text>
    <circle cx="110" cy="165" r="4" fill="{colors['accent2']}"/>
    <text x="120" y="168" font-size="7" fill="{colors['muted']}">Treatment</text>
    
    <!-- Axis labels -->
    <text x="110" y="175" font-size="7" fill="{colors['muted']}" text-anchor="middle">PC1</text>
    <text x="15" y="80" font-size="7" fill="{colors['muted']}" text-anchor="middle" transform="rotate(-90 15 80)">PC2</text>
</svg>'''


# =============================================================================
# CSS GENERATION
# =============================================================================

def generate_css(colors: Dict, options: Dict) -> str:
    """Generate CSS styles for the PDF"""
    
    bg_style = f"background: {colors['bg']};" if 'gradient' in colors['bg'] or colors['bg'].startswith('linear') else f"background-color: {colors['bg']};"
    
    return f'''
<style>
    /* Reset and Base */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    body {{
        font-family: {options.get('font_family', "'Segoe UI', sans-serif")};
        {bg_style}
        color: {colors['text']};
        font-size: {options.get('body_font_size', '11px')};
        line-height: 1.4;
    }}
    
    /* Page Setup */
    @page {{
        size: letter;
        margin: {options.get('page_margin', '15mm')};
        @bottom-center {{
            content: element(footer);
        }}
    }}
    
    .page-break {{
        page-break-before: always;
    }}
    
    /* Header */
    .header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: {options.get('section_gap', '15px')};
    }}
    
    .header-title h1 {{
        font-size: {options.get('title_font_size', '22px')};
        color: {colors['accent']};
        margin-bottom: 3px;
    }}
    
    .header-title p {{
        color: {colors['muted']};
        font-size: {options.get('small_font_size', '10px')};
    }}
    
    /* Logo */
    .logo-placeholder {{
        width: {options.get('logo_width', '100px')};
        height: {options.get('logo_height', '45px')};
        border: 2px dashed {colors['border']};
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: {colors['muted']};
        font-size: 9px;
        text-align: center;
        background: {colors['card']};
    }}
    
    .logo-placeholder img {{
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }}
    
    /* Summary Grid */
    .summary-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-bottom: {options.get('section_gap', '15px')};
    }}
    
    .summary-card {{
        background: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }}
    
    .summary-card .value {{
        font-size: 24px;
        font-weight: 700;
        color: {colors['accent']};
    }}
    
    .summary-card .label {{
        font-size: 9px;
        color: {colors['muted']};
        text-transform: uppercase;
    }}
    
    /* Data Tables */
    .data-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: {options.get('section_gap', '15px')};
    }}
    
    .data-table th {{
        background: {colors['table_header_bg']};
        color: white;
        padding: 8px;
        text-align: left;
        font-size: 9px;
        text-transform: uppercase;
    }}
    
    .data-table td {{
        padding: 8px;
        border-bottom: 1px solid {colors['border']};
        font-size: 10px;
    }}
    
    .data-table tr:nth-child(even) {{
        background: {colors['card']};
    }}
    
    /* Global Plots */
    .plots-header {{
        text-align: center;
        margin-bottom: {options.get('section_gap', '15px')};
    }}
    
    .plots-header h2 {{
        font-size: {options.get('heading_font_size', '18px')};
        color: {colors['text']};
    }}
    
    .three-plots-row {{
        display: flex;
        gap: {options.get('section_gap', '15px')};
        margin-bottom: {options.get('section_gap', '15px')};
    }}
    
    .plot-box {{
        flex: 1;
        background: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        overflow: hidden;
    }}
    
    .plot-title {{
        background: {colors['header_gradient']};
        color: white;
        padding: 6px 10px;
        font-size: 10px;
        font-weight: 600;
    }}
    
    .plot-content {{
        height: {options.get('global_plot_height', '200px')};
        display: flex;
        align-items: center;
        justify-content: center;
        background: #fafafa;
    }}
    
    /* Metabolite Cards */
    .metabolite-page {{
        display: flex;
        flex-direction: column;
        gap: {options.get('card_gap', '8px')};
        padding: 5px 0;
    }}
    
    .metabolite-card {{
        background: {colors['card']};
        border: 1px solid {colors['border']};
        border-radius: 6px;
        overflow: hidden;
        page-break-inside: avoid;
    }}
    
    .met-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 10px;
        background: {colors['header_gradient']};
        color: white;
    }}
    
    .met-card-title {{
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    .met-card-title h3 {{
        font-size: 11px;
        margin: 0;
        color: white;
    }}
    
    .met-card-id {{
        background: rgba(255,255,255,0.2);
        padding: 1px 5px;
        border-radius: 3px;
        font-size: 7px;
        font-weight: 600;
    }}
    
    .met-card-formula {{
        font-size: 8px;
        opacity: 0.9;
        font-family: 'Courier New', monospace;
    }}
    
    .met-card-badge {{
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 8px;
        font-weight: 600;
    }}
    
    .badge-up {{
        background: rgba(16, 185, 129, 0.3);
    }}
    
    .badge-down {{
        background: rgba(239, 68, 68, 0.3);
    }}
    
    .met-card-info {{
        display: flex;
        gap: 12px;
        padding: 3px 10px;
        background: {colors['card']};
        border-bottom: 1px solid {colors['border']};
        font-size: 7px;
        color: {colors['muted']};
    }}
    
    .met-card-info strong {{
        color: {colors['text']};
    }}
    
    .met-card-plots {{
        display: flex;
        gap: 4px;
        padding: 4px;
    }}
    
    .met-plot-box {{
        flex: 1;
        border: 1px solid {colors['border']};
        border-radius: 4px;
        overflow: hidden;
        background: white;
    }}
    
    .met-plot-title {{
        background: {colors['card']};
        padding: 2px 5px;
        font-size: 6px;
        font-weight: 600;
        color: {colors['muted']};
        text-transform: uppercase;
        border-bottom: 1px solid {colors['border']};
    }}
    
    .met-plot-content {{
        height: {options.get('metabolite_plot_height', '55px')};
        display: flex;
        align-items: center;
        justify-content: center;
        background: #fafafa;
    }}
    
    .met-plot-content img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}
    
    .met-plot-content.bar-plot {{
        padding: 3px;
    }}
    
    .met-plot-content.bar-plot svg {{
        width: 100%;
        height: 100%;
    }}
    
    .mirror-mini {{
        flex-direction: column;
        padding: 0;
    }}
    
    .mirror-mini img {{
        height: 25px;
        width: 100%;
        object-fit: cover;
    }}
    
    .mirror-mini-divider {{
        height: 1px;
        background: {colors['accent']};
    }}
    
    .met-card-footer {{
        display: flex;
        gap: 10px;
        padding: 3px 10px;
        background: {colors['card']};
        border-top: 1px solid {colors['border']};
        font-size: 6px;
        color: {colors['muted']};
    }}
    
    .met-card-footer strong {{
        color: {colors['text']};
    }}
    
    /* Footer */
    #footer {{
        position: running(footer);
        text-align: center;
        font-size: 8px;
        color: {colors['muted']};
        border-top: 1px solid {colors['border']};
        padding-top: 5px;
    }}
</style>'''


# =============================================================================
# HTML GENERATION
# =============================================================================

def generate_metabolite_card_html(met: Dict, colors: Dict, options: Dict,
                                   data: Dict, image_paths: Dict) -> str:
    """Generate HTML for a single metabolite card"""
    
    direction = met.get('direction', 'up')
    direction_color = colors['up_color'] if direction == 'up' else colors['down_color']
    direction_text = '↑ Up' if direction == 'up' else '↓ Down'
    badge_class = 'badge-up' if direction == 'up' else 'badge-down'
    
    # Generate bar graph if enabled
    bar_graph_html = ""
    if options.get('show_bar_graph', True):
        bar_graph = generate_bar_graph_svg(
            met, colors,
            data.get('control_group', 'Control'),
            data.get('treatment_group', 'Treatment')
        )
        bar_graph_html = f'''
        <div class="met-plot-box">
            <div class="met-plot-title">Relative Abundance</div>
            <div class="met-plot-content bar-plot">{bar_graph}</div>
        </div>'''
    
    # Chromatogram
    chromatogram_html = ""
    if options.get('show_chromatogram', True):
        chrom_url = image_paths.get('chromatogram')
        if chrom_url:
            chromatogram_html = f'''
            <div class="met-plot-box">
                <div class="met-plot-title">Chromatogram</div>
                <div class="met-plot-content"><img src="{chrom_url}" alt="EIC"></div>
            </div>'''
        else:
            chromatogram_html = f'''
            <div class="met-plot-box">
                <div class="met-plot-title">Chromatogram</div>
                <div class="met-plot-content" style="color:{colors['muted']};font-size:8px;">EIC Placeholder</div>
            </div>'''
    
    # MS2 Spectrum
    ms2_html = ""
    if options.get('show_ms2_spectrum', True):
        ms2_url = image_paths.get('ms2')
        if ms2_url:
            ms2_html = f'''
            <div class="met-plot-box">
                <div class="met-plot-title">MS2 Spectrum</div>
                <div class="met-plot-content"><img src="{ms2_url}" alt="MS2"></div>
            </div>'''
        else:
            ms2_html = f'''
            <div class="met-plot-box">
                <div class="met-plot-title">MS2 Spectrum</div>
                <div class="met-plot-content" style="color:{colors['muted']};font-size:8px;">MS2 Placeholder</div>
            </div>'''
    
    # Mirror Plot
    mirror_html = ""
    if options.get('show_mirror_plot', True):
        ms2_url = image_paths.get('ms2')
        if ms2_url:
            mirror_html = f'''
            <div class="met-plot-box">
                <div class="met-plot-title">Mirror Plot</div>
                <div class="met-plot-content mirror-mini">
                    <img src="{ms2_url}" alt="Sample">
                    <div class="mirror-mini-divider"></div>
                    <img src="{ms2_url}" alt="Library">
                </div>
            </div>'''
        else:
            mirror_html = f'''
            <div class="met-plot-box">
                <div class="met-plot-title">Mirror Plot</div>
                <div class="met-plot-content mirror-mini">
                    <div style="height:50%;display:flex;align-items:center;justify-content:center;color:{colors['muted']};font-size:7px;">Sample</div>
                    <div class="mirror-mini-divider"></div>
                    <div style="height:50%;display:flex;align-items:center;justify-content:center;color:{colors['muted']};font-size:7px;">Library</div>
                </div>
            </div>'''
    
    # Footer
    footer_html = ""
    if options.get('show_annotation_footer', True):
        footer_html = f'''
        <div class="met-card-footer">
            <span><strong>Level:</strong> {met.get('confidence', 'Level 2')}</span>
            <span><strong>DB:</strong> {met.get('database', 'HMDB')}</span>
            <span><strong>Match:</strong> {met.get('match_score', '85%')}</span>
            <span><strong>Pathway:</strong> {met.get('pathway', 'Unknown')}</span>
        </div>'''
    
    return f'''
<div class="metabolite-card">
    <div class="met-card-header">
        <div class="met-card-title">
            <span class="met-card-id">{met.get('id', 'FT-00000')}</span>
            <h3>{met.get('name', 'Unknown')}</h3>
            <span class="met-card-formula">{met.get('formula', 'C0H0')}</span>
        </div>
        <div class="met-card-badge {badge_class}">{direction_text}</div>
    </div>
    
    <div class="met-card-info">
        <span><strong>m/z:</strong> {met.get('mz', 0)}</span>
        <span><strong>RT:</strong> {met.get('rt', 0)} min</span>
        <span><strong>FC:</strong> <span style="color: {direction_color};">{met.get('fc', 1)}</span></span>
        <span><strong>FDR:</strong> {met.get('fdr', 0.05)}</span>
        <span><strong>Adduct:</strong> {met.get('adduct', '[M+H]+')}</span>
    </div>
    
    <div class="met-card-plots">
        {bar_graph_html}
        {chromatogram_html}
        {ms2_html}
        {mirror_html}
    </div>
    
    {footer_html}
</div>'''


def generate_full_html(data: Dict, metabolites: List[Dict], colors: Dict, 
                       options: Dict, image_paths: Dict = None) -> str:
    """Generate complete HTML for the PDF report"""
    
    if image_paths is None:
        image_paths = {}
    
    css = generate_css(colors, options)
    
    # Logo HTML
    logo_path = image_paths.get('logo')
    if logo_path:
        logo_html = f'<img src="{logo_path}" alt="Logo">'
    elif options.get('show_logo_placeholder', True):
        logo_html = '[Logo Placeholder]<br>Add your logo here'
    else:
        logo_html = ''
    
    # Summary page HTML
    summary_html = ""
    if options.get('show_summary_page', True):
        summary_html = f'''
<!-- Summary Page -->
<div class="header">
    <div class="header-title">
        <h1>LCMS Untargeted Metabolomics Report</h1>
        <p>Study: {data.get('study_id', 'N/A')} | Generated: {data.get('generated_on', datetime.now().strftime('%Y-%m-%d'))}</p>
    </div>
    <div class="logo-placeholder">
        {logo_html}
    </div>
</div>

<div class="summary-grid">
    <div class="summary-card">
        <div class="value">{data.get('sample_count', '0')}</div>
        <div class="label">Samples</div>
    </div>
    <div class="summary-card">
        <div class="value">{data.get('feature_count', '0')}</div>
        <div class="label">Features</div>
    </div>
    <div class="summary-card">
        <div class="value">{data.get('significant_count', '0')}</div>
        <div class="label">Significant</div>
    </div>
    <div class="summary-card">
        <div class="value">{data.get('median_cv', '0%')}</div>
        <div class="label">Median CV</div>
    </div>
</div>

<table class="data-table">
    <tr>
        <th>Instrument</th>
        <th>Polarity</th>
        <th>Matrix</th>
        <th>Normalization</th>
        <th>QC Status</th>
    </tr>
    <tr>
        <td>{data.get('instrument', 'N/A')}</td>
        <td>{data.get('polarity', 'N/A')}</td>
        <td>{data.get('matrix', 'N/A')}</td>
        <td>{data.get('normalization', 'N/A')}</td>
        <td>{data.get('qc_status', 'N/A')}</td>
    </tr>
</table>

<table class="data-table">
    <tr>
        <th>Analyst</th>
        <th>Batch</th>
        <th>Blank Threshold</th>
        <th>Drift Corrected</th>
        <th>Injection Status</th>
    </tr>
    <tr>
        <td>{data.get('analyst', 'N/A')}</td>
        <td>{data.get('batch_name', 'N/A')}</td>
        <td>{data.get('blank_threshold', 'N/A')}</td>
        <td>{data.get('drift_corrected', 'N/A')}</td>
        <td>{data.get('injection_monitoring', 'N/A')}</td>
    </tr>
</table>

<div class="page-break"></div>
'''
    
    # Global plots HTML
    global_plots_html = ""
    if options.get('show_global_plots', True):
        volcano_html = ""
        heatmap_html = ""
        pca_html = ""
        
        if options.get('show_volcano_plot', True):
            volcano_svg = generate_volcano_svg(colors, metabolites)
            volcano_html = f'''
            <div class="plot-box">
                <div class="plot-title">Volcano Plot</div>
                <div class="plot-content">{volcano_svg}</div>
            </div>'''
        
        if options.get('show_heatmap', True):
            heatmap_svg = generate_heatmap_svg(colors)
            heatmap_html = f'''
            <div class="plot-box">
                <div class="plot-title">Heatmap</div>
                <div class="plot-content">{heatmap_svg}</div>
            </div>'''
        
        if options.get('show_pca_plot', True):
            pca_svg = generate_pca_svg(colors)
            pca_html = f'''
            <div class="plot-box">
                <div class="plot-title">PCA Plot</div>
                <div class="plot-content">{pca_svg}</div>
            </div>'''
        
        global_plots_html = f'''
<!-- Global Plots Page -->
<div class="plots-header">
    <h2>Global Analysis Plots</h2>
</div>

<div class="three-plots-row">
    {volcano_html}
    {heatmap_html}
    {pca_html}
</div>

<div class="page-break"></div>
'''
    
    # Metabolite cards HTML (4 per page)
    mets_per_page = options.get('metabolites_per_page', 4)
    metabolite_html = ""
    
    for i, met in enumerate(metabolites):
        metabolite_html += generate_metabolite_card_html(met, colors, options, data, image_paths)
        
        # Add page break after every N metabolites
        if (i + 1) % mets_per_page == 0 and i < len(metabolites) - 1:
            metabolite_html += '<div class="page-break"></div>\n'
    
    # Footer
    footer_text = options.get('footer_text', '{company_name} | Study: {study_id} | Generated: {date}')
    footer_formatted = footer_text.format(
        company_name=data.get('company_name', ''),
        study_id=data.get('study_id', ''),
        date=data.get('generated_on', datetime.now().strftime('%Y-%m-%d'))
    )
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LCMS Report - {data.get('study_id', 'Unknown')}</title>
    {css}
</head>
<body>
    {summary_html}
    {global_plots_html}
    
    <!-- Metabolite Pages -->
    <div class="metabolite-page">
        {metabolite_html}
    </div>
    
    <!-- Footer -->
    <div id="footer">
        {footer_formatted}
    </div>
</body>
</html>'''


# =============================================================================
# PDF GENERATION
# =============================================================================

def generate_pdf(output_path: str, data: Dict, metabolites: List[Dict],
                 theme: str = "light", options: Dict = None, 
                 image_paths: Dict = None) -> str:
    """
    Generate a single PDF report.
    
    Args:
        output_path: Path to save the PDF
        data: Study metadata dictionary
        metabolites: List of metabolite dictionaries
        theme: Theme name (light, dark, clinical, etc.)
        options: Design customization options
        image_paths: Dictionary of image paths (logo, chromatogram, ms2)
    
    Returns:
        Path to the generated PDF
    """
    if options is None:
        options = DEFAULT_DESIGN_OPTIONS.copy()
    
    if image_paths is None:
        image_paths = {}
    
    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}. Available: {list(THEMES.keys())}")
    
    colors = THEMES[theme]
    
    # Generate HTML
    html_content = generate_full_html(data, metabolites, colors, options, image_paths)
    
    # Generate PDF
    html = HTML(string=html_content, base_url=os.getcwd())
    html.write_pdf(output_path)
    
    return output_path


def generate_all_themes(output_dir: str, data: Dict, metabolites: List[Dict],
                        options: Dict = None, image_paths: Dict = None) -> List[str]:
    """
    Generate PDFs for all available themes.
    
    Args:
        output_dir: Directory to save PDFs
        data: Study metadata dictionary
        metabolites: List of metabolite dictionaries
        options: Design customization options
        image_paths: Dictionary of image paths
    
    Returns:
        List of paths to generated PDFs
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    
    for i, (theme_key, theme_config) in enumerate(THEMES.items()):
        output_filename = f"layout_{i+1:02d}_{theme_key}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            generate_pdf(output_path, data, metabolites, theme_key, options, image_paths)
            generated_files.append(output_path)
            print(f"  ✓ Generated: {output_filename}")
        except Exception as e:
            print(f"  ✗ Failed: {output_filename} - {str(e)}")
    
    return generated_files


# =============================================================================
# CLI INTERFACE
# =============================================================================

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="LCMS PDF Report Generator - Generate professional LCMS metabolomics reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single PDF with default theme
  python generate_pdfs.py --output report.pdf
  
  # Generate with specific theme
  python generate_pdfs.py --theme dark --output dark_report.pdf
  
  # Generate all 10 theme variations
  python generate_pdfs.py --all-themes --output-dir ./reports
  
  # Use custom data file
  python generate_pdfs.py --data my_study.json --output report.pdf
  
  # Customize design options
  python generate_pdfs.py --metabolites-per-page 3 --output report.pdf

Available Themes:
  light      - Modern Light Executive Dashboard
  clinical   - Clinical Clean Publication Style
  dark       - Dark Modern Analytics Theme
  biotech    - Biotech Premium Report
  journal    - Journal Figure-Forward Style
  minimal    - Minimal White Research Style
  scientific - Data-Dense Scientific Report
  corporate  - Corporate Professional Style
  gradient   - Gradient Modern SaaS Style
  academic   - Academic Publication Supplement
        """
    )
    
    # Output options
    parser.add_argument('-o', '--output', type=str, default='lcms_report.pdf',
                        help='Output PDF filename (default: lcms_report.pdf)')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Output directory for batch generation')
    
    # Theme options
    parser.add_argument('-t', '--theme', type=str, default='light',
                        choices=list(THEMES.keys()),
                        help='Color theme (default: light)')
    parser.add_argument('--all-themes', action='store_true',
                        help='Generate PDFs for all available themes')
    
    # Data options
    parser.add_argument('-d', '--data', type=str, default=None,
                        help='JSON file with study data and metabolites')
    parser.add_argument('--use-sample-data', action='store_true',
                        help='Use built-in sample data')
    
    # Image options
    parser.add_argument('--logo', type=str, default=None,
                        help='Path to logo image file')
    parser.add_argument('--chromatogram', type=str, default=None,
                        help='Path to chromatogram placeholder image')
    parser.add_argument('--ms2', type=str, default=None,
                        help='Path to MS2 spectrum placeholder image')
    
    # Design customization
    parser.add_argument('--metabolites-per-page', type=int, default=4,
                        help='Number of metabolites per page (default: 4)')
    parser.add_argument('--title-font-size', type=str, default='22px',
                        help='Title font size (default: 22px)')
    parser.add_argument('--no-summary', action='store_true',
                        help='Hide summary page')
    parser.add_argument('--no-global-plots', action='store_true',
                        help='Hide global plots page')
    parser.add_argument('--no-volcano', action='store_true',
                        help='Hide volcano plot')
    parser.add_argument('--no-heatmap', action='store_true',
                        help='Hide heatmap')
    parser.add_argument('--no-pca', action='store_true',
                        help='Hide PCA plot')
    parser.add_argument('--no-bar-graph', action='store_true',
                        help='Hide bar graphs in metabolite cards')
    parser.add_argument('--no-annotation-footer', action='store_true',
                        help='Hide annotation footer in metabolite cards')
    
    # Info
    parser.add_argument('--list-themes', action='store_true',
                        help='List available themes and exit')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    
    return parser


def list_themes():
    """Print available themes"""
    print("\nAvailable Themes:")
    print("=" * 60)
    for key, config in THEMES.items():
        print(f"  {key:12} - {config['name']}")
    print("=" * 60)


def load_data_from_file(filepath: str) -> tuple:
    """Load study data and metabolites from JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    metabolites = data.pop('metabolites', [])
    return data, metabolites


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # List themes and exit
    if args.list_themes:
        list_themes()
        return 0
    
    print("\nLCMS PDF Report Generator")
    print("=" * 60)
    
    # Load data
    if args.data:
        print(f"Loading data from: {args.data}")
        data, metabolites = load_data_from_file(args.data)
    elif args.use_sample_data:
        print("Using built-in sample data...")
        data = DEFAULT_STUDY_DATA.copy()
        metabolites = DEFAULT_METABOLITES.copy()
    else:
        # Use defaults
        data = DEFAULT_STUDY_DATA.copy()
        data['generated_on'] = datetime.now().strftime('%Y-%m-%d')
        metabolites = DEFAULT_METABOLITES.copy()
    
    if args.verbose:
        print(f"Study ID: {data.get('study_id')}")
        print(f"Metabolites: {len(metabolites)}")
    
    # Prepare image paths
    image_paths = {}
    if args.logo:
        image_paths['logo'] = os.path.abspath(args.logo)
    if args.chromatogram:
        image_paths['chromatogram'] = os.path.abspath(args.chromatogram)
    if args.ms2:
        image_paths['ms2'] = os.path.abspath(args.ms2)
    
    # Prepare options
    options = DEFAULT_DESIGN_OPTIONS.copy()
    options['metabolites_per_page'] = args.metabolites_per_page
    options['title_font_size'] = args.title_font_size
    options['show_summary_page'] = not args.no_summary
    options['show_global_plots'] = not args.no_global_plots
    options['show_volcano_plot'] = not args.no_volcano
    options['show_heatmap'] = not args.no_heatmap
    options['show_pca_plot'] = not args.no_pca
    options['show_bar_graph'] = not args.no_bar_graph
    options['show_annotation_footer'] = not args.no_annotation_footer
    
    # Generate PDFs
    if args.all_themes:
        output_dir = args.output_dir or './lcms_reports'
        print(f"\nGenerating all {len(THEMES)} theme variations...")
        print(f"Output directory: {output_dir}\n")
        
        generated = generate_all_themes(output_dir, data, metabolites, options, image_paths)
        
        print(f"\n{'=' * 60}")
        print(f"Generated {len(generated)} PDF files in: {output_dir}")
    else:
        output_path = args.output
        
        print(f"\nGenerating PDF with theme: {args.theme}")
        print(f"Output: {output_path}\n")
        
        try:
            generate_pdf(output_path, data, metabolites, args.theme, options, image_paths)
            print(f"✓ PDF generated: {output_path}")
        except Exception as e:
            print(f"✗ Error generating PDF: {str(e)}")
            return 1
    
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())