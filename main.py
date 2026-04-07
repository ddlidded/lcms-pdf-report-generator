#!/usr/bin/env python3
"""
LCMS Untargeted Metabolomics Report PDF Generator
A GUI application for generating LCMS PDF reports with customizable themes.

Author: NinjaTech AI
Version: 1.0.0
"""

import sys
import os
import json
import webbrowser
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QScrollArea, QFileDialog, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QTextEdit, QSplitter, QFrame, QStatusBar, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

from weasyprint import HTML, CSS


# ============================================================================
# THEME CONFIGURATIONS
# ============================================================================

THEMES = {
    "Modern Light": {
        "name": "Modern Light Executive Dashboard",
        "bg": "#f8fafc",
        "surface": "#ffffff",
        "text": "#1e293b",
        "muted": "#64748b",
        "accent": "#0d9488",
        "accent2": "#3b82f6",
        "border": "#e2e8f0",
        "card": "#ffffff",
        "up_color": "#10b981",
        "down_color": "#ef4444"
    },
    "Clinical Clean": {
        "name": "Clinical Clean Publication Style",
        "bg": "#ffffff",
        "surface": "#ffffff",
        "text": "#111827",
        "muted": "#6b7280",
        "accent": "#059669",
        "accent2": "#2563eb",
        "border": "#d1d5db",
        "card": "#f9fafb",
        "up_color": "#059669",
        "down_color": "#dc2626"
    },
    "Dark Analytics": {
        "name": "Dark Modern Analytics Theme",
        "bg": "#0f172a",
        "surface": "#1e293b",
        "text": "#f1f5f9",
        "muted": "#94a3b8",
        "accent": "#14b8a6",
        "accent2": "#8b5cf6",
        "border": "#334155",
        "card": "#1e293b",
        "up_color": "#34d399",
        "down_color": "#f87171"
    },
    "Biotech Premium": {
        "name": "Biotech Premium Report",
        "bg": "#f0fdf4",
        "surface": "#ffffff",
        "text": "#14532d",
        "muted": "#166534",
        "accent": "#16a34a",
        "accent2": "#0ea5e9",
        "border": "#bbf7d0",
        "card": "#ffffff",
        "up_color": "#16a34a",
        "down_color": "#dc2626"
    },
    "Journal Figure": {
        "name": "Journal Figure-Forward Style",
        "bg": "#ffffff",
        "surface": "#ffffff",
        "text": "#000000",
        "muted": "#4b5563",
        "accent": "#b91c1c",
        "accent2": "#1d4ed8",
        "border": "#d1d5db",
        "card": "#f3f4f6",
        "up_color": "#b91c1c",
        "down_color": "#1d4ed8"
    },
    "Minimal White": {
        "name": "Minimal White Research Style",
        "bg": "#ffffff",
        "surface": "#ffffff",
        "text": "#1f2937",
        "muted": "#6b7280",
        "accent": "#374151",
        "accent2": "#6b7280",
        "border": "#e5e7eb",
        "card": "#fafafa",
        "up_color": "#059669",
        "down_color": "#dc2626"
    },
    "Data Dense": {
        "name": "Data-Dense Scientific Report",
        "bg": "#f9fafb",
        "surface": "#ffffff",
        "text": "#111827",
        "muted": "#4b5563",
        "accent": "#0284c7",
        "accent2": "#7c3aed",
        "border": "#e5e7eb",
        "card": "#ffffff",
        "up_color": "#0891b2",
        "down_color": "#c2410c"
    },
    "Corporate Pro": {
        "name": "Corporate Professional Style",
        "bg": "#f3f4f6",
        "surface": "#ffffff",
        "text": "#1f2937",
        "muted": "#4b5563",
        "accent": "#1e40af",
        "accent2": "#0369a1",
        "border": "#d1d5db",
        "card": "#ffffff",
        "up_color": "#059669",
        "down_color": "#dc2626"
    },
    "Gradient SaaS": {
        "name": "Gradient Modern SaaS Style",
        "bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "surface": "rgba(255,255,255,0.95)",
        "text": "#1f2937",
        "muted": "#6b7280",
        "accent": "#7c3aed",
        "accent2": "#ec4899",
        "border": "#e5e7eb",
        "card": "#ffffff",
        "up_color": "#10b981",
        "down_color": "#f43f5e"
    },
    "Academic": {
        "name": "Academic Publication Supplement",
        "bg": "#ffffff",
        "surface": "#ffffff",
        "text": "#1a1a1a",
        "muted": "#595959",
        "accent": "#b91c1c",
        "accent2": "#1d4ed8",
        "border": "#d4d4d4",
        "card": "#fafafa",
        "up_color": "#15803d",
        "down_color": "#b91c1c"
    }
}


# ============================================================================
# PDF GENERATION FUNCTIONS
# ============================================================================

def generate_bar_graph_svg(metabolite, colors, control_group="Control", treatment_group="Treatment"):
    """Generate an SVG bar graph for a metabolite"""
    control_mean = 0.35 if metabolite.get('direction', 'up') == 'up' else 0.75
    control_sd = 0.08
    treatment_mean = control_mean * float(metabolite.get('fc', 2.0))
    treatment_sd = 0.10
    
    max_val = max(control_mean + control_sd, treatment_mean + treatment_sd)
    scale = 80 / max_val
    
    control_height = control_mean * scale
    treatment_height = treatment_mean * scale
    
    bar_width = 50
    gap = 30
    start_x = 50
    
    return f'''
<svg viewBox="0 0 180 120" class="bar-graph-svg">
    <rect x="30" y="10" width="140" height="85" fill="#fafafa" stroke="{colors['border']}"/>
    <line x1="30" y1="31" x2="170" y2="31" stroke="#e5e7eb" stroke-dasharray="2"/>
    <line x1="30" y1="52" x2="170" y2="52" stroke="#e5e7eb" stroke-dasharray="2"/>
    <line x1="30" y1="73" x2="170" y2="73" stroke="#e5e7eb" stroke-dasharray="2"/>
    
    <rect x="{start_x}" y="{95 - control_height}" width="{bar_width}" height="{control_height}" fill="{colors['accent']}" rx="3"/>
    <rect x="{start_x + bar_width + gap}" y="{95 - treatment_height}" width="{bar_width}" height="{treatment_height}" fill="{colors['accent2']}" rx="3"/>
    
    <path d="M {start_x + bar_width + 5} {20} L {start_x + bar_width + 10} {15} L {start_x + bar_width + gap - 5} {15} L {start_x + bar_width + gap} {20}" fill="none" stroke="{colors['text']}" stroke-width="1"/>
    <text x="{start_x + bar_width + gap/2 + 5}" y="12" font-size="8" fill="{colors['text']}" text-anchor="middle">**</text>
    
    <text x="{start_x + bar_width/2}" y="108" font-size="8" fill="{colors['muted']}" text-anchor="middle">{control_group}</text>
    <text x="{start_x + bar_width + gap + bar_width/2}" y="108" font-size="8" fill="{colors['muted']}" text-anchor="middle">{treatment_group}</text>
    
    <text x="8" y="55" font-size="7" fill="{colors['muted']}" text-anchor="middle" transform="rotate(-90 8 55)">Relative Abundance</text>
</svg>'''


def generate_volcano_svg(colors):
    """Generate SVG volcano plot"""
    return f'''
<svg viewBox="0 0 200 180" width="180" height="160">
    <rect x="30" y="10" width="160" height="140" fill="#fafafa" stroke="{colors['border']}"/>
    <line x1="30" y1="150" x2="190" y2="150" stroke="{colors['text']}" stroke-width="1"/>
    <line x1="30" y1="10" x2="30" y2="150" stroke="{colors['text']}" stroke-width="1"/>
    <circle cx="160" cy="40" r="3" fill="{colors['up_color']}"/>
    <circle cx="170" cy="50" r="3" fill="{colors['up_color']}"/>
    <circle cx="155" cy="60" r="3" fill="{colors['up_color']}"/>
    <circle cx="175" cy="45" r="3" fill="{colors['up_color']}"/>
    <circle cx="50" cy="45" r="3" fill="{colors['down_color']}"/>
    <circle cx="40" cy="55" r="3" fill="{colors['down_color']}"/>
    <circle cx="55" cy="65" r="3" fill="{colors['down_color']}"/>
    <circle cx="110" cy="120" r="2" fill="{colors['muted']}"/>
    <circle cx="100" cy="130" r="2" fill="{colors['muted']}"/>
    <circle cx="120" cy="125" r="2" fill="{colors['muted']}"/>
    <circle cx="95" cy="135" r="2" fill="{colors['muted']}"/>
    <circle cx="115" cy="115" r="2" fill="{colors['muted']}"/>
    <text x="110" y="170" font-size="8" fill="{colors['muted']}" text-anchor="middle">log₂(Fold Change)</text>
    <text x="10" y="80" font-size="8" fill="{colors['muted']}" text-anchor="middle" transform="rotate(-90 10 80)">-log₁₀(p-value)</text>
</svg>'''


def generate_heatmap_svg(colors):
    """Generate SVG heatmap"""
    cells = ""
    rows = [
        [colors['up_color'], colors['accent'], "#6ee7b7", "#a7f3d0", colors['up_color']],
        [colors['down_color'], "#fca5a5", colors['up_color'], colors['accent'], "#6ee7b7"],
        ["#6ee7b7", colors['down_color'], "#fca5a5", colors['up_color'], colors['accent']],
        ["#a7f3d0", "#6ee7b7", colors['up_color'], colors['down_color'], "#fca5a5"],
        ["#fca5a5", colors['up_color'], colors['accent'], "#6ee7b7", "#a7f3d0"],
    ]
    
    for row_idx, row in enumerate(rows):
        for col_idx, color in enumerate(row):
            x = 40 + col_idx * 30
            y = 20 + row_idx * 25
            cells += f'<rect x="{x}" y="{y}" width="28" height="23" fill="{color}"/>\n'
    
    return f'''
<svg viewBox="0 0 200 180" width="180" height="160">
    <rect x="30" y="10" width="160" height="140" fill="#fafafa" stroke="{colors['border']}"/>
    {cells}
</svg>'''


def generate_pca_svg(colors):
    """Generate SVG PCA plot"""
    return f'''
<svg viewBox="0 0 200 180" width="180" height="160">
    <rect x="30" y="10" width="160" height="140" fill="#fafafa" stroke="{colors['border']}"/>
    <line x1="30" y1="80" x2="190" y2="80" stroke="{colors['border']}" stroke-dasharray="3"/>
    <line x1="110" y1="10" x2="110" y2="150" stroke="{colors['border']}" stroke-dasharray="3"/>
    <circle cx="70" cy="60" r="5" fill="{colors['accent']}"/>
    <circle cx="80" cy="70" r="5" fill="{colors['accent']}"/>
    <circle cx="65" cy="75" r="5" fill="{colors['accent']}"/>
    <circle cx="75" cy="55" r="5" fill="{colors['accent']}"/>
    <circle cx="85" cy="65" r="5" fill="{colors['accent']}"/>
    <circle cx="140" cy="90" r="5" fill="{colors['accent2']}"/>
    <circle cx="150" cy="100" r="5" fill="{colors['accent2']}"/>
    <circle cx="135" cy="105" r="5" fill="{colors['accent2']}"/>
    <circle cx="145" cy="85" r="5" fill="{colors['accent2']}"/>
    <circle cx="155" cy="95" r="5" fill="{colors['accent2']}"/>
    <circle cx="50" cy="165" r="4" fill="{colors['accent']}"/>
    <text x="60" y="168" font-size="7" fill="{colors['muted']}">Control</text>
    <circle cx="110" cy="165" r="4" fill="{colors['accent2']}"/>
    <text x="120" y="168" font-size="7" fill="{colors['muted']}">Treatment</text>
    <text x="110" y="175" font-size="7" fill="{colors['muted']}" text-anchor="middle">PC1</text>
    <text x="15" y="80" font-size="7" fill="{colors['muted']}" text-anchor="middle" transform="rotate(-90 15 80)">PC2</text>
</svg>'''


def generate_metabolite_card(met, colors, data, chromatogram_path, ms2_path):
    """Generate a single metabolite card HTML"""
    direction_color = colors['up_color'] if met.get('direction', 'up') == 'up' else colors['down_color']
    direction_text = '↑ Up' if met.get('direction', 'up') == 'up' else '↓ Down'
    badge_class = 'badge-up' if met.get('direction', 'up') == 'up' else 'badge-down'
    
    bar_graph = generate_bar_graph_svg(met, colors, data.get('control_group', 'Control'), data.get('treatment_group', 'Treatment'))
    
    # Handle image paths
    chromatogram_url = f"file://{chromatogram_path}" if chromatogram_path else "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='50'%3E%3Crect fill='%23f0f0f0' width='100' height='50'/%3E%3Ctext x='50' y='30' text-anchor='middle' fill='%23999' font-size='8'%3ENo Image%3C/text%3E%3C/svg%3E"
    ms2_url = f"file://{ms2_path}" if ms2_path else "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='50'%3E%3Crect fill='%23f0f0f0' width='100' height='50'/%3E%3Ctext x='50' y='30' text-anchor='middle' fill='%23999' font-size='8'%3ENo Image%3C/text%3E%3C/svg%3E"
    
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
        <div class="met-plot-box">
            <div class="met-plot-title">Relative Abundance</div>
            <div class="met-plot-content bar-plot">{bar_graph}</div>
        </div>
        <div class="met-plot-box">
            <div class="met-plot-title">Chromatogram</div>
            <div class="met-plot-content"><img src="{chromatogram_url}" alt="EIC"></div>
        </div>
        <div class="met-plot-box">
            <div class="met-plot-title">MS2 Spectrum</div>
            <div class="met-plot-content"><img src="{ms2_url}" alt="MS2"></div>
        </div>
        <div class="met-plot-box">
            <div class="met-plot-title">Mirror Plot</div>
            <div class="met-plot-content mirror-mini">
                <img src="{ms2_url}" alt="Sample">
                <div class="mirror-mini-divider"></div>
                <img src="{ms2_url}" alt="Library">
            </div>
        </div>
    </div>
    
    <div class="met-card-footer">
        <span><strong>Level:</strong> {met.get('confidence', 'Level 2')}</span>
        <span><strong>DB:</strong> {met.get('database', 'HMDB')}</span>
        <span><strong>Match:</strong> {met.get('match_score', '85%')}</span>
        <span><strong>Pathway:</strong> {met.get('pathway', 'Unknown')}</span>
    </div>
</div>'''


def get_base_css(colors):
    """Get base CSS for the PDF"""
    bg_style = f"background: {colors['bg']};" if 'gradient' in colors['bg'] or colors['bg'].startswith('linear') else f"background-color: {colors['bg']};"
    
    return f'''
<style>
    :root {{
        --bg: {colors['bg']};
        --surface: {colors['surface']};
        --text: {colors['text']};
        --muted: {colors['muted']};
        --accent: {colors['accent']};
        --accent2: {colors['accent2']};
        --border: {colors['border']};
        --card: {colors['card']};
        --up-color: {colors['up_color']};
        --down-color: {colors['down_color']};
    }}
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        {bg_style}
        color: var(--text);
        font-size: 11px;
        line-height: 1.4;
    }}
    
    @page {{
        size: letter;
        margin: 15mm 15mm 20mm 15mm;
        @bottom-center {{
            content: element(footer);
        }}
    }}
    
    .page-break {{
        page-break-before: always;
    }}
    
    .header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 15px;
    }}
    
    .header-title h1 {{
        font-size: 22px;
        color: var(--accent);
        margin-bottom: 3px;
    }}
    
    .header-title p {{
        color: var(--muted);
        font-size: 10px;
    }}
    
    .logo-placeholder {{
        width: 100px;
        height: 45px;
        border: 2px dashed var(--border);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--muted);
        font-size: 9px;
        text-align: center;
        background: var(--card);
    }}
    
    .logo-placeholder img {{
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }}
    
    .summary-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-bottom: 15px;
    }}
    
    .summary-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }}
    
    .summary-card .value {{
        font-size: 24px;
        font-weight: 700;
        color: var(--accent);
    }}
    
    .summary-card .label {{
        font-size: 9px;
        color: var(--muted);
        text-transform: uppercase;
    }}
    
    .data-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 15px;
    }}
    
    .data-table th {{
        background: var(--accent);
        color: white;
        padding: 8px;
        text-align: left;
        font-size: 9px;
        text-transform: uppercase;
    }}
    
    .data-table td {{
        padding: 8px;
        border-bottom: 1px solid var(--border);
        font-size: 10px;
    }}
    
    .data-table tr:nth-child(even) {{
        background: var(--card);
    }}
    
    .plots-header {{
        text-align: center;
        margin-bottom: 15px;
    }}
    
    .plots-header h2 {{
        font-size: 18px;
        color: var(--text);
    }}
    
    .three-plots-row {{
        display: flex;
        gap: 15px;
        margin-bottom: 15px;
    }}
    
    .plot-box {{
        flex: 1;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }}
    
    .plot-title {{
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        color: white;
        padding: 6px 10px;
        font-size: 10px;
        font-weight: 600;
    }}
    
    .plot-content {{
        height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #fafafa;
    }}
    
    .metabolite-page {{
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 5px 0;
    }}
    
    .metabolite-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 6px;
        overflow: hidden;
        page-break-inside: avoid;
    }}
    
    .met-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 10px;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
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
        background: var(--card);
        border-bottom: 1px solid var(--border);
        font-size: 7px;
        color: var(--muted);
    }}
    
    .met-card-info strong {{
        color: var(--text);
    }}
    
    .met-card-plots {{
        display: flex;
        gap: 4px;
        padding: 4px;
    }}
    
    .met-plot-box {{
        flex: 1;
        border: 1px solid var(--border);
        border-radius: 4px;
        overflow: hidden;
        background: white;
    }}
    
    .met-plot-title {{
        background: var(--card);
        padding: 2px 5px;
        font-size: 6px;
        font-weight: 600;
        color: var(--muted);
        text-transform: uppercase;
        border-bottom: 1px solid var(--border);
    }}
    
    .met-plot-content {{
        height: 55px;
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
        background: var(--accent);
    }}
    
    .met-card-footer {{
        display: flex;
        gap: 10px;
        padding: 3px 10px;
        background: var(--card);
        border-top: 1px solid var(--border);
        font-size: 6px;
        color: var(--muted);
    }}
    
    .met-card-footer strong {{
        color: var(--text);
    }}
    
    #footer {{
        position: running(footer);
        text-align: center;
        font-size: 8px;
        color: var(--muted);
        border-top: 1px solid var(--border);
        padding-top: 5px;
    }}
</style>'''


def generate_full_html(data, metabolites, colors, logo_path=None, chromatogram_path=None, ms2_path=None):
    """Generate complete HTML for the PDF report"""
    
    css = get_base_css(colors)
    
    # Logo HTML
    if logo_path:
        logo_html = f'<img src="file://{logo_path}" alt="Logo">'
    else:
        logo_html = '[Logo Placeholder]<br>Add your logo here'
    
    # Generate volcano, heatmap, PCA SVGs
    volcano_svg = generate_volcano_svg(colors)
    heatmap_svg = generate_heatmap_svg(colors)
    pca_svg = generate_pca_svg(colors)
    
    # Generate metabolite cards (4 per page)
    metabolite_html = ""
    for i, met in enumerate(metabolites):
        metabolite_html += generate_metabolite_card(met, colors, data, chromatogram_path, ms2_path)
        
        # Add page break after every 4 metabolites (except the last)
        if (i + 1) % 4 == 0 and i < len(metabolites) - 1:
            metabolite_html += '<div class="page-break"></div>\n'
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LCMS Report - {data.get('study_id', 'Unknown')}</title>
    {css}
</head>
<body>
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
    
    <!-- Global Plots Page -->
    <div class="plots-header">
        <h2>Global Analysis Plots</h2>
    </div>
    
    <div class="three-plots-row">
        <div class="plot-box">
            <div class="plot-title">Volcano Plot</div>
            <div class="plot-content">{volcano_svg}</div>
        </div>
        <div class="plot-box">
            <div class="plot-title">Heatmap</div>
            <div class="plot-content">{heatmap_svg}</div>
        </div>
        <div class="plot-box">
            <div class="plot-title">PCA Plot</div>
            <div class="plot-content">{pca_svg}</div>
        </div>
    </div>
    
    <div class="page-break"></div>
    
    <!-- Metabolite Pages -->
    <div class="metabolite-page">
        {metabolite_html}
    </div>
    
    <!-- Footer -->
    <div id="footer">
        {data.get('company_name', 'Company Name')} | Study: {data.get('study_id', 'N/A')} | Generated: {data.get('generated_on', datetime.now().strftime('%Y-%m-%d'))}
    </div>
</body>
</html>'''


# ============================================================================
# GUI APPLICATION
# ============================================================================

class PDFGeneratorWorker(QThread):
    """Background worker for PDF generation"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, html_content, output_path):
        super().__init__()
        self.html_content = html_content
        self.output_path = output_path
    
    def run(self):
        try:
            self.progress.emit(50)
            html = HTML(string=self.html_content)
            html.write_pdf(self.output_path)
            self.progress.emit(100)
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))


class MetaboliteTableModel(QTableWidget):
    """Table widget for managing metabolite data"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
    
    def setup_table(self):
        headers = ['ID', 'Name', 'Formula', 'm/z', 'RT', 'FC', 'FDR', 'Direction', 'Adduct', 'Confidence', 'Database', 'Match %', 'Pathway']
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setAlternatingRowColors(True)
    
    def add_metabolite(self, met_data=None):
        row = self.rowCount()
        self.insertRow(row)
        
        defaults = {
            'id': f'FT-{row+1:05d}',
            'name': '',
            'formula': '',
            'mz': 0.0,
            'rt': 0.0,
            'fc': 1.0,
            'fdr': 0.05,
            'direction': 'up',
            'adduct': '[M+H]+',
            'confidence': 'Level 2',
            'database': '',
            'match_score': '85%',
            'pathway': ''
        }
        
        if met_data:
            defaults.update(met_data)
        
        items = [
            defaults['id'],
            defaults['name'],
            defaults['formula'],
            str(defaults['mz']),
            str(defaults['rt']),
            str(defaults['fc']),
            str(defaults['fdr']),
            defaults['direction'],
            defaults['adduct'],
            defaults['confidence'],
            defaults['database'],
            defaults['match_score'],
            defaults['pathway']
        ]
        
        for col, value in enumerate(items):
            item = QTableWidgetItem(str(value))
            self.setItem(row, col, item)
    
    def get_metabolites(self):
        metabolites = []
        for row in range(self.rowCount()):
            met = {}
            met['id'] = self.item(row, 0).text() if self.item(row, 0) else ''
            met['name'] = self.item(row, 1).text() if self.item(row, 1) else ''
            met['formula'] = self.item(row, 2).text() if self.item(row, 2) else ''
            try:
                met['mz'] = float(self.item(row, 3).text()) if self.item(row, 3) else 0.0
            except ValueError:
                met['mz'] = 0.0
            try:
                met['rt'] = float(self.item(row, 4).text()) if self.item(row, 4) else 0.0
            except ValueError:
                met['rt'] = 0.0
            try:
                met['fc'] = float(self.item(row, 5).text()) if self.item(row, 5) else 1.0
            except ValueError:
                met['fc'] = 1.0
            try:
                met['fdr'] = float(self.item(row, 6).text()) if self.item(row, 6) else 0.05
            except ValueError:
                met['fdr'] = 0.05
            met['direction'] = self.item(row, 7).text() if self.item(row, 7) else 'up'
            met['adduct'] = self.item(row, 8).text() if self.item(row, 8) else '[M+H]+'
            met['confidence'] = self.item(row, 9).text() if self.item(row, 9) else 'Level 2'
            met['database'] = self.item(row, 10).text() if self.item(row, 10) else ''
            met['match_score'] = self.item(row, 11).text() if self.item(row, 11) else '85%'
            met['pathway'] = self.item(row, 12).text() if self.item(row, 12) else ''
            metabolites.append(met)
        return metabolites
    
    def load_metabolites(self, metabolites):
        self.setRowCount(0)
        for met in metabolites:
            self.add_metabolite(met)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCMS PDF Report Generator")
        self.setGeometry(100, 100, 1400, 900)
        
        # Data storage
        self.study_data = {}
        self.metabolites = []
        self.logo_path = None
        self.chromatogram_path = None
        self.ms2_path = None
        self.output_dir = str(Path.home() / 'Documents')
        
        self.setup_ui()
        self.load_defaults()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Study Info & Settings
        left_panel = self.create_left_panel()
        
        # Center panel - Metabolite Table
        center_panel = self.create_center_panel()
        
        # Right panel - Preview & Generate
        right_panel = self.create_right_panel()
        
        # Add panels to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600, 400])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def create_left_panel(self):
        """Create left panel with study info inputs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Study Information Group
        study_group = QGroupBox("Study Information")
        study_layout = QFormLayout()
        
        self.study_id_input = QLineEdit()
        self.study_id_input.setPlaceholderText("e.g., LCMS-2024-0142")
        study_layout.addRow("Study ID:", self.study_id_input)
        
        self.batch_input = QLineEdit()
        self.batch_input.setPlaceholderText("e.g., Batch A")
        study_layout.addRow("Batch:", self.batch_input)
        
        self.instrument_input = QComboBox()
        self.instrument_input.addItems(['Q-Exactive Plus', 'Q-Exactive HF', 'Orbitrap Exploris', 'Q-TOF', 'Triple Quad', 'Other'])
        self.instrument_input.setEditable(True)
        study_layout.addRow("Instrument:", self.instrument_input)
        
        self.analyst_input = QLineEdit()
        self.analyst_input.setPlaceholderText("e.g., Dr. Sarah Chen")
        study_layout.addRow("Analyst:", self.analyst_input)
        
        self.matrix_input = QComboBox()
        self.matrix_input.addItems(['Plasma', 'Serum', 'Urine', 'Tissue', 'CSF', 'Saliva', 'Other'])
        self.matrix_input.setEditable(True)
        study_layout.addRow("Matrix:", self.matrix_input)
        
        self.polarity_input = QComboBox()
        self.polarity_input.addItems(['ESI+', 'ESI-', 'Both'])
        study_layout.addRow("Polarity:", self.polarity_input)
        
        study_group.setLayout(study_layout)
        layout.addWidget(study_group)
        
        # Analysis Parameters Group
        params_group = QGroupBox("Analysis Parameters")
        params_layout = QFormLayout()
        
        self.sample_count_input = QSpinBox()
        self.sample_count_input.setRange(1, 10000)
        self.sample_count_input.setValue(48)
        params_layout.addRow("Sample Count:", self.sample_count_input)
        
        self.feature_count_input = QLineEdit("2,847")
        params_layout.addRow("Feature Count:", self.feature_count_input)
        
        self.significant_count_input = QLineEdit("156")
        params_layout.addRow("Significant Features:", self.significant_count_input)
        
        self.normalization_input = QComboBox()
        self.normalization_input.addItems(['PQN', 'TIC', 'Median', 'None', 'Other'])
        self.normalization_input.setEditable(True)
        params_layout.addRow("Normalization:", self.normalization_input)
        
        self.median_cv_input = QLineEdit("12.4%")
        params_layout.addRow("Median CV:", self.median_cv_input)
        
        self.qc_status_input = QComboBox()
        self.qc_status_input.addItems(['PASS', 'WARN', 'FAIL'])
        params_layout.addRow("QC Status:", self.qc_status_input)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Group Names Group
        groups_group = QGroupBox("Experimental Groups")
        groups_layout = QFormLayout()
        
        self.control_group_input = QLineEdit("Control")
        groups_layout.addRow("Control Group:", self.control_group_input)
        
        self.treatment_group_input = QLineEdit("Treatment")
        groups_layout.addRow("Treatment Group:", self.treatment_group_input)
        
        groups_group.setLayout(groups_layout)
        layout.addWidget(groups_group)
        
        # Company/Logo Group
        company_group = QGroupBox("Company & Branding")
        company_layout = QVBoxLayout()
        
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("Your Company Name")
        company_layout.addWidget(QLabel("Company Name:"))
        company_layout.addWidget(self.company_name_input)
        
        logo_btn_layout = QHBoxLayout()
        self.logo_btn = QPushButton("Select Logo")
        self.logo_btn.clicked.connect(self.select_logo)
        self.clear_logo_btn = QPushButton("Clear")
        self.clear_logo_btn.clicked.connect(self.clear_logo)
        logo_btn_layout.addWidget(self.logo_btn)
        logo_btn_layout.addWidget(self.clear_logo_btn)
        company_layout.addLayout(logo_btn_layout)
        
        self.logo_label = QLabel("No logo selected")
        self.logo_label.setStyleSheet("color: gray; font-style: italic;")
        company_layout.addWidget(self.logo_label)
        
        company_group.setLayout(company_layout)
        layout.addWidget(company_group)
        
        layout.addStretch()
        
        return panel
    
    def create_center_panel(self):
        """Create center panel with metabolite table"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>Metabolite Data</b>"))
        
        # Table buttons
        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(self.add_metabolite_row)
        header_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_metabolite_row)
        header_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_metabolites)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.metabolite_table = MetaboliteTableModel()
        layout.addWidget(self.metabolite_table)
        
        # Import/Export buttons
        io_layout = QHBoxLayout()
        
        import_json_btn = QPushButton("Import JSON")
        import_json_btn.clicked.connect(self.import_json)
        io_layout.addWidget(import_json_btn)
        
        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(self.export_json)
        io_layout.addWidget(export_json_btn)
        
        load_sample_btn = QPushButton("Load Sample Data")
        load_sample_btn.clicked.connect(self.load_sample_data)
        io_layout.addWidget(load_sample_btn)
        
        layout.addLayout(io_layout)
        
        return panel
    
    def create_right_panel(self):
        """Create right panel with theme selection and generation"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Theme Selection Group
        theme_group = QGroupBox("Report Theme")
        theme_layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        
        # Theme preview
        self.theme_preview = QLabel()
        self.theme_preview.setMinimumHeight(60)
        self.theme_preview.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")
        theme_layout.addWidget(self.theme_preview)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Image Settings Group
        images_group = QGroupBox("Placeholder Images")
        images_layout = QVBoxLayout()
        
        chrom_btn_layout = QHBoxLayout()
        self.chrom_btn = QPushButton("Select Chromatogram")
        self.chrom_btn.clicked.connect(self.select_chromatogram)
        chrom_btn_layout.addWidget(self.chrom_btn)
        self.chrom_label = QLabel("Default")
        self.chrom_label.setStyleSheet("color: gray;")
        chrom_btn_layout.addWidget(self.chrom_label)
        images_layout.addLayout(chrom_btn_layout)
        
        ms2_btn_layout = QHBoxLayout()
        self.ms2_btn = QPushButton("Select MS2 Spectrum")
        self.ms2_btn.clicked.connect(self.select_ms2)
        ms2_btn_layout.addWidget(self.ms2_btn)
        self.ms2_label = QLabel("Default")
        self.ms2_label.setStyleSheet("color: gray;")
        ms2_btn_layout.addWidget(self.ms2_label)
        images_layout.addLayout(ms2_btn_layout)
        
        images_group.setLayout(images_layout)
        layout.addWidget(images_group)
        
        # Generation Group
        gen_group = QGroupBox("Generate Report")
        gen_layout = QVBoxLayout()
        
        # Output directory
        out_layout = QHBoxLayout()
        out_layout.addWidget(QLabel("Output:"))
        self.output_label = QLabel(self.output_dir)
        self.output_label.setWordWrap(True)
        out_layout.addWidget(self.output_label)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.select_output_dir)
        out_layout.addWidget(browse_btn)
        gen_layout.addLayout(out_layout)
        
        # Generate button
        self.generate_btn = QPushButton("📄 Generate PDF Report")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d9488;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0f766e;
            }
            QPushButton:pressed {
                background-color: #115e59;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_pdf)
        gen_layout.addWidget(self.generate_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        gen_layout.addWidget(self.progress_bar)
        
        # Generate all themes
        self.generate_all_btn = QPushButton("Generate All 10 Themes")
        self.generate_all_btn.clicked.connect(self.generate_all_themes)
        gen_layout.addWidget(self.generate_all_btn)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        # Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        
        open_output_btn = QPushButton("Open Output Folder")
        open_output_btn.clicked.connect(self.open_output_folder)
        actions_layout.addWidget(open_output_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        # Update theme preview
        self.on_theme_changed(self.theme_combo.currentText())
        
        return panel
    
    def load_defaults(self):
        """Load default values"""
        self.study_id_input.setText(f"LCMS-{datetime.now().year}-{datetime.now().month:02d}{datetime.now().day:02d}")
        self.analyst_input.setText("")
        self.company_name_input.setText("")
    
    def on_theme_changed(self, theme_name):
        """Update theme preview when selection changes"""
        if theme_name in THEMES:
            colors = THEMES[theme_name]
            bg = colors['bg']
            if bg.startswith('linear'):
                bg_style = f"background: {bg};"
            else:
                bg_style = f"background-color: {bg};"
            
            self.theme_preview.setStyleSheet(f"""
                {bg_style}
                border: 2px solid {colors['border']};
                border-radius: 8px;
                padding: 10px;
                color: {colors['text']};
            """)
            self.theme_preview.setText(f"<b>{colors['name']}</b><br><span style='color: {colors['muted']}'>Accent: {colors['accent']}</span>")
    
    def select_logo(self):
        """Select logo file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "", "Images (*.png *.jpg *.jpeg *.svg *.bmp)"
        )
        if file_path:
            self.logo_path = file_path
            self.logo_label.setText(os.path.basename(file_path))
            self.logo_label.setStyleSheet("color: green;")
    
    def clear_logo(self):
        """Clear logo selection"""
        self.logo_path = None
        self.logo_label.setText("No logo selected")
        self.logo_label.setStyleSheet("color: gray; font-style: italic;")
    
    def select_chromatogram(self):
        """Select chromatogram image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Chromatogram Image", "", "Images (*.png *.jpg *.jpeg *.svg)"
        )
        if file_path:
            self.chromatogram_path = file_path
            self.chrom_label.setText(os.path.basename(file_path))
            self.chrom_label.setStyleSheet("color: green;")
    
    def select_ms2(self):
        """Select MS2 spectrum image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select MS2 Spectrum Image", "", "Images (*.png *.jpg *.jpeg *.svg)"
        )
        if file_path:
            self.ms2_path = file_path
            self.ms2_label.setText(os.path.basename(file_path))
            self.ms2_label.setStyleSheet("color: green;")
    
    def select_output_dir(self):
        """Select output directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_dir)
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(dir_path)
    
    def add_metabolite_row(self):
        """Add a new metabolite row"""
        self.metabolite_table.add_metabolite()
    
    def remove_metabolite_row(self):
        """Remove selected metabolite rows"""
        selected_rows = set()
        for item in self.metabolite_table.selectedItems():
            selected_rows.add(item.row())
        for row in sorted(selected_rows, reverse=True):
            self.metabolite_table.removeRow(row)
    
    def clear_metabolites(self):
        """Clear all metabolite rows"""
        self.metabolite_table.setRowCount(0)
    
    def load_sample_data(self):
        """Load sample metabolite data"""
        sample_metabolites = [
            {'id': 'FT-00184', 'name': 'L-Carnitine', 'formula': 'C7H15NO3', 'mz': 162.1130, 'rt': 5.42, 'fc': 3.42, 'fdr': 0.001, 'direction': 'up', 'adduct': '[M+H]+', 'confidence': 'Level 2', 'database': 'HMDB0000062', 'match_score': '87%', 'pathway': 'Fatty acid metabolism'},
            {'id': 'FT-00721', 'name': 'Phosphocholine', 'formula': 'C5H14NO4P', 'mz': 184.0739, 'rt': 8.91, 'fc': 2.87, 'fdr': 0.003, 'direction': 'up', 'adduct': '[M+H]+', 'confidence': 'Level 2', 'database': 'HMDB0001565', 'match_score': '92%', 'pathway': 'Glycerophospholipid metabolism'},
            {'id': 'FT-01345', 'name': 'Taurine', 'formula': 'C2H7NO3S', 'mz': 126.0219, 'rt': 3.15, 'fc': 0.45, 'fdr': 0.008, 'direction': 'down', 'adduct': '[M+H]+', 'confidence': 'Level 1', 'database': 'HMDB0000251', 'match_score': '98%', 'pathway': 'Bile acid metabolism'},
            {'id': 'FT-02089', 'name': 'Hypoxanthine', 'formula': 'C5H4N4O', 'mz': 137.0459, 'rt': 6.78, 'fc': 4.12, 'fdr': 0.012, 'direction': 'up', 'adduct': '[M+H]+', 'confidence': 'Level 2', 'database': 'HMDB0000157', 'match_score': '85%', 'pathway': 'Purine metabolism'},
            {'id': 'FT-00312', 'name': 'Sphingomyelin (d18:1/16:0)', 'formula': 'C39H81N2O6P', 'mz': 703.5734, 'rt': 12.34, 'fc': 2.15, 'fdr': 0.021, 'direction': 'up', 'adduct': '[M+H]+', 'confidence': 'Level 3', 'database': 'LMSP03010004', 'match_score': '72%', 'pathway': 'Sphingolipid metabolism'},
            {'id': 'FT-00876', 'name': 'Glutathione (oxidized)', 'formula': 'C20H32N6O12S2', 'mz': 612.1520, 'rt': 9.87, 'fc': 0.62, 'fdr': 0.035, 'direction': 'down', 'adduct': '[M+H]+', 'confidence': 'Level 2', 'database': 'HMDB0003337', 'match_score': '88%', 'pathway': 'Glutathione metabolism'},
        ]
        self.metabolite_table.load_metabolites(sample_metabolites)
        self.statusBar.showMessage("Sample data loaded")
    
    def import_json(self):
        """Import data from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import JSON", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Load study data
                if 'study_id' in data:
                    self.study_id_input.setText(str(data['study_id']))
                if 'batch_name' in data:
                    self.batch_input.setText(str(data['batch_name']))
                if 'instrument' in data:
                    index = self.instrument_input.findText(str(data['instrument']))
                    if index >= 0:
                        self.instrument_input.setCurrentIndex(index)
                if 'analyst' in data:
                    self.analyst_input.setText(str(data['analyst']))
                if 'matrix' in data:
                    index = self.matrix_input.findText(str(data['matrix']))
                    if index >= 0:
                        self.matrix_input.setCurrentIndex(index)
                if 'sample_count' in data:
                    self.sample_count_input.setValue(int(data['sample_count']))
                if 'company_name' in data:
                    self.company_name_input.setText(str(data['company_name']))
                
                # Load metabolites
                if 'metabolites' in data:
                    self.metabolite_table.load_metabolites(data['metabolites'])
                
                self.statusBar.showMessage(f"Imported: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Failed to import JSON: {str(e)}")
    
    def export_json(self):
        """Export current data to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", "", "JSON Files (*.json)"
        )
        if file_path:
            data = self.get_current_data()
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                self.statusBar.showMessage(f"Exported: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Failed to export JSON: {str(e)}")
    
    def get_current_data(self):
        """Get current data from all inputs"""
        return {
            'study_id': self.study_id_input.text(),
            'batch_name': self.batch_input.text(),
            'instrument': self.instrument_input.currentText(),
            'analyst': self.analyst_input.text(),
            'matrix': self.matrix_input.currentText(),
            'polarity': self.polarity_input.currentText(),
            'sample_count': str(self.sample_count_input.value()),
            'feature_count': self.feature_count_input.text(),
            'significant_count': self.significant_count_input.text(),
            'normalization': self.normalization_input.currentText(),
            'median_cv': self.median_cv_input.text(),
            'qc_status': self.qc_status_input.currentText(),
            'company_name': self.company_name_input.text(),
            'control_group': self.control_group_input.text(),
            'treatment_group': self.treatment_group_input.text(),
            'generated_on': datetime.now().strftime('%Y-%m-%d'),
            'metabolites': self.metabolite_table.get_metabolites()
        }
    
    def generate_pdf(self):
        """Generate PDF with current settings"""
        data = self.get_current_data()
        metabolites = data['metabolites']
        
        if not metabolites:
            QMessageBox.warning(self, "No Data", "Please add metabolite data before generating a report.")
            return
        
        # Get theme
        theme_name = self.theme_combo.currentText()
        colors = THEMES[theme_name]
        
        # Generate HTML
        html_content = generate_full_html(
            data, metabolites, colors,
            logo_path=self.logo_path,
            chromatogram_path=self.chromatogram_path,
            ms2_path=self.ms2_path
        )
        
        # Output filename
        safe_study_id = data['study_id'].replace('/', '-').replace('\\', '-')
        output_filename = f"LCMS_Report_{safe_study_id}_{theme_name.replace(' ', '_')}.pdf"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_btn.setEnabled(False)
        self.statusBar.showMessage("Generating PDF...")
        
        # Start worker thread
        self.worker = PDFGeneratorWorker(html_content, output_path)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_pdf_finished)
        self.worker.error.connect(self.on_pdf_error)
        self.worker.start()
    
    def generate_all_themes(self):
        """Generate PDFs for all themes"""
        data = self.get_current_data()
        metabolites = data['metabolites']
        
        if not metabolites:
            QMessageBox.warning(self, "No Data", "Please add metabolite data before generating reports.")
            return
        
        # Create output folder
        safe_study_id = data['study_id'].replace('/', '-').replace('\\', '-')
        output_folder = os.path.join(self.output_dir, f"LCMS_Reports_{safe_study_id}")
        os.makedirs(output_folder, exist_ok=True)
        
        generated_files = []
        
        for i, (theme_name, colors) in enumerate(THEMES.items()):
            self.statusBar.showMessage(f"Generating {theme_name} ({i+1}/{len(THEMES)})...")
            QApplication.processEvents()
            
            # Generate HTML
            html_content = generate_full_html(
                data, metabolites, colors,
                logo_path=self.logo_path,
                chromatogram_path=self.chromatogram_path,
                ms2_path=self.ms2_path
            )
            
            # Output filename
            output_filename = f"layout_{i+1:02d}_{theme_name.replace(' ', '_')}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            try:
                html = HTML(string=html_content)
                html.write_pdf(output_path)
                generated_files.append(output_path)
            except Exception as e:
                QMessageBox.warning(self, "Generation Error", f"Failed to generate {theme_name}: {str(e)}")
        
        self.statusBar.showMessage(f"Generated {len(generated_files)} PDFs in {output_folder}")
        QMessageBox.information(
            self, "Generation Complete",
            f"Generated {len(generated_files)} PDF files:\n\n{output_folder}"
        )
    
    def on_pdf_finished(self, output_path):
        """Handle PDF generation completion"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.statusBar.showMessage(f"PDF saved: {output_path}")
        
        # Ask to open
        reply = QMessageBox.question(
            self, "PDF Generated",
            f"PDF saved to:\n{output_path}\n\nOpen the file?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            webbrowser.open(f'file://{output_path}')
    
    def on_pdf_error(self, error_msg):
        """Handle PDF generation error"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.statusBar.showMessage("Error generating PDF")
        QMessageBox.critical(self, "Error", f"Failed to generate PDF:\n{error_msg}")
    
    def open_output_folder(self):
        """Open output folder in file explorer"""
        webbrowser.open(f'file://{self.output_dir}')


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Dark palette option
    # palette = QPalette()
    # palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # palette.setColor(QPalette.WindowText, Qt.white)
    # app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()