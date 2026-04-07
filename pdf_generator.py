"""
LCMS PDF Report Generator - Pure Python PDF Engine
Uses ReportLab only — no system library dependencies.
Compatible with Streamlit Cloud.
"""

import math
import random
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.graphics.shapes import (
    Drawing, Rect, Circle, Line, String, Polygon, Path, Group
)
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus.flowables import Flowable

# ─────────────────────────────────────────────
# THEME DEFINITIONS
# ─────────────────────────────────────────────

THEMES = {
    "light": {
        "name": "Modern Light",
        "subtitle": "Executive Dashboard",
        "style": "Light",
        "bg": "#FFFFFF",
        "header_bg": "#0d9488",
        "header_text": "#FFFFFF",
        "accent": "#0d9488",
        "accent2": "#0891b2",
        "text": "#1e293b",
        "subtext": "#64748b",
        "border": "#e2e8f0",
        "card_bg": "#f8fafc",
        "up_color": "#ef4444",
        "down_color": "#3b82f6",
        "ns_color": "#94a3b8",
        "table_header": "#0d9488",
        "table_alt": "#f0fdfa",
    },
    "minimal": {
        "name": "Minimal",
        "subtitle": "White Research Style",
        "style": "Minimal",
        "bg": "#FFFFFF",
        "header_bg": "#18181b",
        "header_text": "#FFFFFF",
        "accent": "#18181b",
        "accent2": "#52525b",
        "text": "#18181b",
        "subtext": "#71717a",
        "border": "#e4e4e7",
        "card_bg": "#fafafa",
        "up_color": "#dc2626",
        "down_color": "#2563eb",
        "ns_color": "#a1a1aa",
        "table_header": "#18181b",
        "table_alt": "#f4f4f5",
    },
    "clinical": {
        "name": "Clinical",
        "subtitle": "Clean Publication Style",
        "style": "Clinical",
        "bg": "#FFFFFF",
        "header_bg": "#1d4ed8",
        "header_text": "#FFFFFF",
        "accent": "#1d4ed8",
        "accent2": "#0891b2",
        "text": "#1e3a5f",
        "subtext": "#64748b",
        "border": "#bfdbfe",
        "card_bg": "#eff6ff",
        "up_color": "#dc2626",
        "down_color": "#2563eb",
        "ns_color": "#93c5fd",
        "table_header": "#1d4ed8",
        "table_alt": "#dbeafe",
    },
    "scientific": {
        "name": "Scientific",
        "subtitle": "Data-Dense Scientific Report",
        "style": "Scientific",
        "bg": "#FFFFFF",
        "header_bg": "#7c3aed",
        "header_text": "#FFFFFF",
        "accent": "#7c3aed",
        "accent2": "#a855f7",
        "text": "#1e1b4b",
        "subtext": "#6b7280",
        "border": "#ddd6fe",
        "card_bg": "#faf5ff",
        "up_color": "#dc2626",
        "down_color": "#2563eb",
        "ns_color": "#c4b5fd",
        "table_header": "#7c3aed",
        "table_alt": "#ede9fe",
    },
    "dark": {
        "name": "Dark",
        "subtitle": "Modern Analytics Theme",
        "style": "Dark",
        "bg": "#0f172a",
        "header_bg": "#1e293b",
        "header_text": "#f1f5f9",
        "accent": "#38bdf8",
        "accent2": "#818cf8",
        "text": "#f1f5f9",
        "subtext": "#94a3b8",
        "border": "#334155",
        "card_bg": "#1e293b",
        "up_color": "#f87171",
        "down_color": "#60a5fa",
        "ns_color": "#475569",
        "table_header": "#1e293b",
        "table_alt": "#1a2744",
    },
    "corporate": {
        "name": "Corporate",
        "subtitle": "Professional Style",
        "style": "Corporate",
        "bg": "#FFFFFF",
        "header_bg": "#0f4c81",
        "header_text": "#FFFFFF",
        "accent": "#0f4c81",
        "accent2": "#c8a951",
        "text": "#0f2137",
        "subtext": "#4a6080",
        "border": "#cad5e2",
        "card_bg": "#f0f4f9",
        "up_color": "#c0392b",
        "down_color": "#0f4c81",
        "ns_color": "#95a5a6",
        "table_header": "#0f4c81",
        "table_alt": "#e8eef5",
    },
    "biotech": {
        "name": "Biotech",
        "subtitle": "Premium Report",
        "style": "Biotech",
        "bg": "#FFFFFF",
        "header_bg": "#065f46",
        "header_text": "#FFFFFF",
        "accent": "#065f46",
        "accent2": "#d97706",
        "text": "#064e3b",
        "subtext": "#6b7280",
        "border": "#a7f3d0",
        "card_bg": "#ecfdf5",
        "up_color": "#dc2626",
        "down_color": "#2563eb",
        "ns_color": "#6ee7b7",
        "table_header": "#065f46",
        "table_alt": "#d1fae5",
    },
    "gradient": {
        "name": "Gradient",
        "subtitle": "Modern SaaS Style",
        "style": "Gradient",
        "bg": "#FFFFFF",
        "header_bg": "#6d28d9",
        "header_text": "#FFFFFF",
        "accent": "#6d28d9",
        "accent2": "#db2777",
        "text": "#1e1b4b",
        "subtext": "#6b7280",
        "border": "#e9d5ff",
        "card_bg": "#fdf4ff",
        "up_color": "#db2777",
        "down_color": "#6d28d9",
        "ns_color": "#c4b5fd",
        "table_header": "#6d28d9",
        "table_alt": "#f5f3ff",
    },
    "journal": {
        "name": "Journal",
        "subtitle": "Figure-Forward Style",
        "style": "Journal",
        "bg": "#FFFFFF",
        "header_bg": "#1a1a1a",
        "header_text": "#FFFFFF",
        "accent": "#c41e3a",
        "accent2": "#1a6b3c",
        "text": "#1a1a1a",
        "subtext": "#555555",
        "border": "#d1d1d1",
        "card_bg": "#f7f7f7",
        "up_color": "#c41e3a",
        "down_color": "#1a6b3c",
        "ns_color": "#999999",
        "table_header": "#1a1a1a",
        "table_alt": "#f0f0f0",
    },
    "academic": {
        "name": "Academic",
        "subtitle": "Publication Supplement",
        "style": "Academic",
        "bg": "#FFFEF7",
        "header_bg": "#4a2c6e",
        "header_text": "#FFFFFF",
        "accent": "#4a2c6e",
        "accent2": "#b45309",
        "text": "#2d1b4e",
        "subtext": "#6b5b6e",
        "border": "#d8b4fe",
        "card_bg": "#fdf4ff",
        "up_color": "#b91c1c",
        "down_color": "#1d4ed8",
        "ns_color": "#9ca3af",
        "table_header": "#4a2c6e",
        "table_alt": "#f5f0ff",
    },
}

DEFAULT_STUDY_DATA = {
    "title": "LCMS Untargeted Metabolomics Study Report",
    "subtitle": "Comparative Analysis of Metabolic Profiles",
    "study_id": "STUDY-2024-001",
    "author": "Research Team",
    "institution": "Research Institution",
    "date": datetime.now().strftime("%B %d, %Y"),
    "group1": "Control",
    "group2": "Treatment",
    "samples": "24 samples (12 per group)",
    "instrument": "Orbitrap Eclipse Tribrid Mass Spectrometer",
    "ionization": "ESI+ / ESI-",
    "resolution": "120,000 FWHM",
    "description": (
        "This report presents the results of an untargeted metabolomics analysis "
        "comparing metabolic profiles between experimental groups. Samples were processed "
        "using standard LCMS protocols with quality control measures applied throughout."
    ),
}

DEFAULT_METABOLITES = [
    {"name": "Glutamine",       "formula": "C5H10N2O3",  "mz": 146.0691, "rt": 1.23,  "fc": 2.45,  "pvalue": 0.001,  "padj": 0.005,  "hmdb": "HMDB0000641",  "pathway": "Amino Acid",    "up": True},
    {"name": "Citric Acid",     "formula": "C6H8O7",     "mz": 192.0270, "rt": 2.87,  "fc": -1.89, "pvalue": 0.003,  "padj": 0.012,  "hmdb": "HMDB0000094",  "pathway": "TCA Cycle",     "up": False},
    {"name": "Palmitic Acid",   "formula": "C16H32O2",   "mz": 256.2402, "rt": 14.56, "fc": 3.12,  "pvalue": 0.0005, "padj": 0.002,  "hmdb": "HMDB0000220",  "pathway": "Fatty Acid",    "up": True},
    {"name": "Tryptophan",      "formula": "C11H12N2O2", "mz": 204.0899, "rt": 5.67,  "fc": -2.34, "pvalue": 0.008,  "padj": 0.025,  "hmdb": "HMDB0000929",  "pathway": "Amino Acid",    "up": False},
    {"name": "Glucose-6-P",     "formula": "C6H13O9P",   "mz": 260.0297, "rt": 1.56,  "fc": 1.78,  "pvalue": 0.02,   "padj": 0.055,  "hmdb": "HMDB0001401",  "pathway": "Glycolysis",    "up": True},
    {"name": "Sphingomyelin",   "formula": "C39H79N2O6P","mz": 702.5694, "rt": 17.23, "fc": 2.91,  "pvalue": 0.0001, "padj": 0.0008, "hmdb": "HMDB0001348",  "pathway": "Sphingolipid",  "up": True},
]

# ─────────────────────────────────────────────
# COLOR UTILITY
# ─────────────────────────────────────────────

def hex_to_rgb(hex_color):
    """Convert hex color string to ReportLab Color."""
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(c*2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return colors.Color(r/255, g/255, b/255)

def rl_color(hex_str):
    try:
        return hex_to_rgb(hex_str)
    except Exception:
        return colors.black


# ─────────────────────────────────────────────
# SVG-LIKE DRAWINGS USING REPORTLAB GRAPHICS
# ─────────────────────────────────────────────

def make_volcano_drawing(metabolites, theme, width=180, height=130):
    """Draw a volcano plot."""
    d = Drawing(width, height)
    pad = 22
    plot_w = width - pad - 8
    plot_h = height - pad - 12

    bg = rl_color(theme["card_bg"])
    d.add(Rect(0, 0, width, height, fillColor=bg, strokeColor=None))

    # Axes
    ax_color = rl_color(theme["border"])
    d.add(Line(pad, pad, pad, pad + plot_h, strokeColor=ax_color, strokeWidth=0.8))
    d.add(Line(pad, pad, pad + plot_w, pad, strokeColor=ax_color, strokeWidth=0.8))

    # Axis labels
    lc = rl_color(theme["subtext"])
    d.add(String(pad + plot_w/2, 2, "log2(FC)", fontSize=5, fillColor=lc, textAnchor='middle'))
    d.add(String(6, pad + plot_h/2, "-log10(p)", fontSize=5, fillColor=lc, textAnchor='middle'))

    # Threshold lines
    sig_y = pad + plot_h * 0.65
    fc_x_pos = pad + plot_w * 0.65
    fc_x_neg = pad + plot_w * 0.35
    tl = rl_color(theme["subtext"])
    d.add(Line(pad, sig_y, pad + plot_w, sig_y, strokeColor=tl, strokeWidth=0.5, strokeDashArray=[2, 2]))
    d.add(Line(fc_x_pos, pad, fc_x_pos, pad + plot_h, strokeColor=tl, strokeWidth=0.5, strokeDashArray=[2, 2]))
    d.add(Line(fc_x_neg, pad, fc_x_neg, pad + plot_h, strokeColor=tl, strokeWidth=0.5, strokeDashArray=[2, 2]))

    rng = random.Random(42)
    up_c = rl_color(theme["up_color"])
    dn_c = rl_color(theme["down_color"])
    ns_c = rl_color(theme["ns_color"])

    # Add background scatter
    for _ in range(60):
        x = rng.uniform(pad + 4, pad + plot_w - 4)
        y = rng.uniform(pad + 4, pad + plot_h * 0.6)
        d.add(Circle(x, y, 1.5, fillColor=ns_c, strokeColor=None))

    # Plot metabolites
    fcs = [m.get("fc", 0) for m in metabolites]
    fc_range = max(abs(min(fcs)), abs(max(fcs)), 1)
    for m in metabolites:
        fc = m.get("fc", 0)
        pv = m.get("pvalue", 0.05)
        log_p = -math.log10(max(pv, 1e-10))
        nx = (fc / (fc_range * 2) + 0.5)
        ny = min(log_p / 8, 0.98)
        px = pad + nx * plot_w
        py = pad + ny * plot_h
        sig = pv < 0.05 and abs(fc) > 1
        c = up_c if (fc > 0 and sig) else dn_c if (fc < 0 and sig) else ns_c
        d.add(Circle(px, py, 2.5 if sig else 1.8, fillColor=c, strokeColor=None))

    # Title
    tc = rl_color(theme["text"])
    d.add(String(width/2, height - 8, "Volcano Plot", fontSize=6.5, fillColor=tc, textAnchor='middle', fontName='Helvetica-Bold'))

    return d


def make_heatmap_drawing(metabolites, theme, width=180, height=130):
    """Draw a heatmap."""
    d = Drawing(width, height)
    bg = rl_color(theme["card_bg"])
    d.add(Rect(0, 0, width, height, fillColor=bg, strokeColor=None))

    tc = rl_color(theme["text"])
    d.add(String(width/2, height - 8, "Metabolite Heatmap", fontSize=6.5, fillColor=tc, textAnchor='middle', fontName='Helvetica-Bold'))

    n_met = min(len(metabolites), 8)
    n_samples = 8
    pad_l, pad_b = 52, 18
    cell_w = (width - pad_l - 6) / n_samples
    cell_h = (height - pad_b - 18) / max(n_met, 1)

    accent = rl_color(theme["accent"])
    up_c = rl_color(theme["up_color"])
    dn_c = rl_color(theme["down_color"])

    rng = random.Random(7)
    groups = ["C"] * 4 + ["T"] * 4

    for gi, g in enumerate(groups):
        gx = pad_l + gi * cell_w + cell_w / 2
        sc = rl_color(theme["subtext"])
        d.add(String(gx, pad_b - 10, g, fontSize=4.5, fillColor=sc, textAnchor='middle'))

    for mi in range(n_met):
        m = metabolites[mi]
        name = m.get("name", f"Met {mi+1}")
        if len(name) > 12:
            name = name[:11] + "…"
        gy = pad_b + mi * cell_h + cell_h / 2
        lc = rl_color(theme["subtext"])
        d.add(String(pad_l - 3, gy - 2, name, fontSize=4.5, fillColor=lc, textAnchor='end'))

        for si in range(n_samples):
            is_treatment = si >= 4
            fc = m.get("fc", 0)
            base = 0.5 + (fc / 6) * (1 if is_treatment else -0.5) + rng.uniform(-0.15, 0.15)
            base = max(0, min(1, base))
            if base > 0.6:
                r_mix = up_c.red * base + 1 * (1 - base)
                g_mix = up_c.green * base + 1 * (1 - base)
                b_mix = up_c.blue * base + 1 * (1 - base)
            else:
                t = 1 - base / 0.6
                r_mix = dn_c.red * t + 1 * (1 - t)
                g_mix = dn_c.green * t + 1 * (1 - t)
                b_mix = dn_c.blue * t + 1 * (1 - t)
            cell_color = colors.Color(r_mix, g_mix, b_mix)
            cx = pad_l + si * cell_w
            cy = pad_b + mi * cell_h
            d.add(Rect(cx, cy, cell_w - 0.5, cell_h - 0.5, fillColor=cell_color, strokeColor=None))

    return d


def make_pca_drawing(metabolites, theme, width=180, height=130):
    """Draw a PCA scatter plot."""
    d = Drawing(width, height)
    bg = rl_color(theme["card_bg"])
    d.add(Rect(0, 0, width, height, fillColor=bg, strokeColor=None))

    pad = 22
    plot_w = width - pad - 8
    plot_h = height - pad - 12

    ax_color = rl_color(theme["border"])
    d.add(Line(pad, pad, pad, pad + plot_h, strokeColor=ax_color, strokeWidth=0.8))
    d.add(Line(pad, pad, pad + plot_w, pad, strokeColor=ax_color, strokeWidth=0.8))

    lc = rl_color(theme["subtext"])
    d.add(String(pad + plot_w/2, 2, "PC1 (34.2%)", fontSize=5, fillColor=lc, textAnchor='middle'))

    tc = rl_color(theme["text"])
    d.add(String(width/2, height - 8, "PCA Score Plot", fontSize=6.5, fillColor=tc, textAnchor='middle', fontName='Helvetica-Bold'))

    ctrl_c = rl_color(theme["down_color"])
    treat_c = rl_color(theme["up_color"])

    rng = random.Random(99)
    for i in range(12):
        # Control cluster (left)
        x = pad + plot_w * (0.25 + rng.uniform(-0.1, 0.1))
        y = pad + plot_h * (0.5 + rng.uniform(-0.2, 0.2))
        d.add(Circle(x, y, 3.5, fillColor=ctrl_c, strokeColor=colors.white, strokeWidth=0.5))

    for i in range(12):
        # Treatment cluster (right)
        x = pad + plot_w * (0.72 + rng.uniform(-0.1, 0.1))
        y = pad + plot_h * (0.5 + rng.uniform(-0.2, 0.2))
        d.add(Circle(x, y, 3.5, fillColor=treat_c, strokeColor=colors.white, strokeWidth=0.5))

    # Legend
    lx = pad + plot_w * 0.05
    d.add(Circle(lx, pad + 8, 3, fillColor=ctrl_c, strokeColor=None))
    d.add(String(lx + 6, pad + 5.5, "Control", fontSize=4.5, fillColor=lc))
    d.add(Circle(lx, pad + 18, 3, fillColor=treat_c, strokeColor=None))
    d.add(String(lx + 6, pad + 15.5, "Treatment", fontSize=4.5, fillColor=lc))

    return d


def make_bar_drawing(metabolite, theme, width=180, height=130):
    """Draw a bar graph for a metabolite."""
    d = Drawing(width, height)
    bg = rl_color(theme["card_bg"])
    d.add(Rect(0, 0, width, height, fillColor=bg, strokeColor=None))

    tc = rl_color(theme["text"])
    name = metabolite.get("name", "Metabolite")
    d.add(String(width/2, height - 8, f"{name} – Intensity", fontSize=6.5, fillColor=tc, textAnchor='middle', fontName='Helvetica-Bold'))

    pad_l, pad_b = 28, 24
    plot_w = width - pad_l - 10
    plot_h = height - pad_b - 18

    ax_color = rl_color(theme["border"])
    d.add(Line(pad_l, pad_b, pad_l, pad_b + plot_h, strokeColor=ax_color, strokeWidth=0.8))
    d.add(Line(pad_l, pad_b, pad_l + plot_w, pad_b, strokeColor=ax_color, strokeWidth=0.8))

    ctrl_c = rl_color(theme["down_color"])
    treat_c = rl_color(theme["up_color"])
    lc = rl_color(theme["subtext"])

    rng = random.Random(hash(name) % 100)
    n_ctrl = 4
    n_treat = 4
    bar_w = plot_w / (n_ctrl + n_treat + 2) * 0.9
    gap = plot_w / (n_ctrl + n_treat + 2)

    fc = metabolite.get("fc", 1)
    ctrl_mean = 0.4
    treat_mean = min(0.85, max(0.1, 0.4 * (2 ** (fc / 3))))

    max_val = max(ctrl_mean, treat_mean) * 1.3
    scale = plot_h / max_val

    for i in range(n_ctrl):
        h = (ctrl_mean + rng.uniform(-0.06, 0.06)) * scale
        x = pad_l + (i + 0.5) * gap
        d.add(Rect(x, pad_b, bar_w, h, fillColor=ctrl_c, strokeColor=None))

    for i in range(n_treat):
        h = (treat_mean + rng.uniform(-0.06, 0.06)) * scale
        x = pad_l + (n_ctrl + 1 + i + 0.5) * gap
        d.add(Rect(x, pad_b, bar_w, h, fillColor=treat_c, strokeColor=None))

    # Labels
    ctrl_x = pad_l + (n_ctrl / 2) * gap
    treat_x = pad_l + (n_ctrl + 1 + n_treat / 2) * gap
    d.add(String(ctrl_x, pad_b - 10, "Control", fontSize=4.5, fillColor=lc, textAnchor='middle'))
    d.add(String(treat_x, pad_b - 10, "Treatment", fontSize=4.5, fillColor=lc, textAnchor='middle'))

    # Y axis ticks
    for tick in [0.25, 0.5, 0.75, 1.0]:
        ty = pad_b + tick * plot_h
        if ty < pad_b + plot_h:
            d.add(Line(pad_l - 3, ty, pad_l, ty, strokeColor=ax_color, strokeWidth=0.5))
            d.add(String(pad_l - 4, ty - 2, f"{tick * max_val:.2f}", fontSize=3.5, fillColor=lc, textAnchor='end'))

    return d


# ─────────────────────────────────────────────
# FLOWABLES
# ─────────────────────────────────────────────

class DrawingFlowable(Flowable):
    """Wraps a ReportLab Drawing for use in platypus."""
    def __init__(self, drawing):
        super().__init__()
        self.drawing = drawing
        self.width = drawing.width
        self.height = drawing.height

    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)

    def wrap(self, avail_w, avail_h):
        return self.width, self.height


class ColorRect(Flowable):
    """A colored rectangle flowable."""
    def __init__(self, width, height, fill_color, stroke_color=None, radius=3):
        super().__init__()
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.stroke_color = stroke_color
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.fill_color)
        if self.stroke_color:
            self.canv.setStrokeColor(self.stroke_color)
            self.canv.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=1)
        else:
            self.canv.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)

    def wrap(self, avail_w, avail_h):
        return self.width, self.height


# ─────────────────────────────────────────────
# PAGE TEMPLATE CALLBACKS
# ─────────────────────────────────────────────

def make_page_callback(theme, study_data, total_pages_ref):
    """Returns an onPage callback that draws the running header/footer."""
    accent = rl_color(theme["header_bg"])
    header_text_c = rl_color(theme["header_text"])
    subtext_c = rl_color(theme["subtext"])
    border_c = rl_color(theme["border"])
    bg_c = rl_color(theme["bg"])
    text_c = rl_color(theme["text"])
    w, h = A4

    def on_page(canv, doc):
        canv.saveState()
        # Background
        canv.setFillColor(bg_c)
        canv.rect(0, 0, w, h, fill=1, stroke=0)

        # Top header bar (not first page)
        if doc.page > 1:
            canv.setFillColor(accent)
            canv.rect(0, h - 22*mm, w, 22*mm, fill=1, stroke=0)
            canv.setFillColor(header_text_c)
            canv.setFont("Helvetica-Bold", 10)
            canv.drawString(15*mm, h - 13*mm, study_data.get("title", "LCMS Report")[:55])
            canv.setFont("Helvetica", 8)
            canv.drawRightString(w - 15*mm, h - 13*mm, study_data.get("study_id", ""))

        # Footer
        canv.setFillColor(accent)
        canv.rect(0, 0, w, 12*mm, fill=1, stroke=0)
        canv.setFillColor(header_text_c)
        canv.setFont("Helvetica", 7)
        canv.drawString(15*mm, 4*mm, f"{study_data.get('institution', '')}  |  {study_data.get('date', '')}")
        canv.drawRightString(w - 15*mm, 4*mm, f"Page {doc.page}")

        canv.restoreState()

    return on_page


# ─────────────────────────────────────────────
# CONTENT BUILDERS
# ─────────────────────────────────────────────

def build_cover_page(theme, study_data, elements, styles):
    """Build a cover page."""
    accent = rl_color(theme["accent"])
    accent2 = rl_color(theme["accent2"])
    header_bg = rl_color(theme["header_bg"])
    header_text = rl_color(theme["header_text"])
    text_c = rl_color(theme["text"])
    sub_c = rl_color(theme["subtext"])
    bg_c = rl_color(theme["bg"])
    border_c = rl_color(theme["border"])
    card_bg = rl_color(theme["card_bg"])
    w, _ = A4

    cover_title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=26,
        textColor=header_text,
        alignment=TA_CENTER,
        spaceAfter=6,
        leading=32,
    )
    cover_sub_style = ParagraphStyle(
        'CoverSub',
        fontName='Helvetica',
        fontSize=13,
        textColor=colors.Color(1, 1, 1, 0.85),
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    label_style = ParagraphStyle(
        'Label',
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=sub_c,
        spaceAfter=2,
    )
    value_style = ParagraphStyle(
        'Value',
        fontName='Helvetica',
        fontSize=10,
        textColor=text_c,
        spaceAfter=8,
    )

    # Header banner drawing
    banner_h = 90 * mm
    banner_d = Drawing(w - 30*mm, banner_h)
    banner_d.add(Rect(0, 0, w - 30*mm, banner_h, fillColor=header_bg, strokeColor=None, rx=6, ry=6))
    # Accent stripe
    banner_d.add(Rect(0, 0, w - 30*mm, 8, fillColor=accent2, strokeColor=None))

    elements.append(Spacer(1, 10*mm))
    elements.append(DrawingFlowable(banner_d))

    # Overlay text on banner (use absolute positioning via Table)
    title_text = study_data.get("title", "LCMS Metabolomics Report")
    subtitle_text = study_data.get("subtitle", "Untargeted Metabolomics Analysis")

    # We use a Table to overlay text on the banner space
    # Re-draw with text in a table
    elements.pop()  # remove drawing

    title_para = Paragraph(f'<font color="white"><b>{title_text}</b></font>', cover_title_style)
    sub_para = Paragraph(f'<font color="#dddddd">{subtitle_text}</font>', cover_sub_style)
    id_para = Paragraph(f'<font color="#aaaaaa">Study ID: {study_data.get("study_id", "")}</font>',
                        ParagraphStyle('SmID', fontName='Helvetica', fontSize=9,
                                       textColor=colors.Color(0.8, 0.8, 0.8), alignment=TA_CENTER))

    banner_table = Table(
        [[title_para], [sub_para], [id_para]],
        colWidths=[w - 30*mm]
    )
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), header_bg),
        ('TOPPADDING', (0, 0), (0, 0), 20),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 18),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [header_bg]),
        ('ROUNDEDCORNERS', [6]),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 8*mm))

    # Metadata grid
    meta = [
        ("Author", study_data.get("author", "")),
        ("Institution", study_data.get("institution", "")),
        ("Date", study_data.get("date", "")),
        ("Group 1", study_data.get("group1", "Control")),
        ("Group 2", study_data.get("group2", "Treatment")),
        ("Samples", study_data.get("samples", "")),
        ("Instrument", study_data.get("instrument", "")),
        ("Ionization", study_data.get("ionization", "")),
    ]

    meta_rows = []
    for i in range(0, len(meta), 2):
        row = []
        for j in range(2):
            if i + j < len(meta):
                k, v = meta[i + j]
                cell = [
                    Paragraph(k.upper(), label_style),
                    Paragraph(v, value_style),
                ]
            else:
                cell = [Spacer(1, 1)]
            row.append(cell)
        meta_rows.append(row)

    meta_table = Table(meta_rows, colWidths=[(w - 30*mm) / 2 - 4] * 2, hAlign='LEFT')
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), card_bg),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, border_c),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 6*mm))

    # Description box
    desc_style = ParagraphStyle(
        'Desc',
        fontName='Helvetica',
        fontSize=9,
        textColor=text_c,
        leading=14,
        leftIndent=0,
        rightIndent=0,
    )
    desc = study_data.get("description", "")
    if desc:
        desc_table = Table(
            [[Paragraph(desc, desc_style)]],
            colWidths=[w - 30*mm]
        )
        desc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), card_bg),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, accent),
        ]))
        elements.append(desc_table)

    elements.append(PageBreak())


def build_summary_page(theme, study_data, metabolites, elements, styles):
    """Build a summary statistics page."""
    accent = rl_color(theme["accent"])
    accent2 = rl_color(theme["accent2"])
    text_c = rl_color(theme["text"])
    sub_c = rl_color(theme["subtext"])
    border_c = rl_color(theme["border"])
    card_bg = rl_color(theme["card_bg"])
    up_c = rl_color(theme["up_color"])
    dn_c = rl_color(theme["down_color"])
    w, _ = A4

    h2_style = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=14,
                               textColor=rl_color(theme["header_text"]),
                               backColor=accent, borderPad=8,
                               spaceBefore=0, spaceAfter=0, leading=20)

    elements.append(Spacer(1, 5*mm))
    heading_table = Table([[Paragraph("📊 Summary Statistics", h2_style)]], colWidths=[w - 30*mm])
    heading_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), accent),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(heading_table)
    elements.append(Spacer(1, 5*mm))

    n_up = sum(1 for m in metabolites if m.get("fc", 0) > 0 and m.get("pvalue", 1) < 0.05)
    n_dn = sum(1 for m in metabolites if m.get("fc", 0) < 0 and m.get("pvalue", 1) < 0.05)
    n_sig = sum(1 for m in metabolites if m.get("pvalue", 1) < 0.05)
    n_total = len(metabolites)

    stat_style = ParagraphStyle('StatVal', fontName='Helvetica-Bold', fontSize=20,
                                 textColor=accent, alignment=TA_CENTER)
    stat_lbl = ParagraphStyle('StatLbl', fontName='Helvetica', fontSize=8,
                               textColor=sub_c, alignment=TA_CENTER)

    stats = [
        (str(n_total), "Total Features"),
        (str(n_sig), "Significant (p<0.05)"),
        (str(n_up), "Up-regulated"),
        (str(n_dn), "Down-regulated"),
    ]

    stat_cells = [[Paragraph(v, stat_style), Paragraph(l, stat_lbl)] for v, l in stats]

    stat_table = Table(
        [stat_cells],
        colWidths=[(w - 30*mm) / 4] * 4
    )
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), card_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_c),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_c),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(stat_table)
    elements.append(Spacer(1, 5*mm))

    # Global plots row
    plot_w = (w - 30*mm - 4*mm) / 2
    plot_h_px = 130

    volcano = make_volcano_drawing(metabolites, theme, width=float(plot_w), height=plot_h_px)
    heatmap = make_heatmap_drawing(metabolites, theme, width=float(plot_w), height=plot_h_px)
    pca = make_pca_drawing(metabolites, theme, width=float(plot_w), height=plot_h_px)

    plot_table = Table(
        [[DrawingFlowable(volcano), DrawingFlowable(heatmap)]],
        colWidths=[plot_w, plot_w]
    )
    plot_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), card_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_c),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_c),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(plot_table)
    elements.append(Spacer(1, 3*mm))

    pca_table = Table([[DrawingFlowable(pca)]], colWidths=[w - 30*mm])
    pca_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), card_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_c),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(pca_table)
    elements.append(PageBreak())


def build_metabolite_pages(theme, metabolites, elements, styles, per_page=4):
    """Build per-metabolite detail pages (4 per page)."""
    accent = rl_color(theme["accent"])
    text_c = rl_color(theme["text"])
    sub_c = rl_color(theme["subtext"])
    border_c = rl_color(theme["border"])
    card_bg = rl_color(theme["card_bg"])
    up_c = rl_color(theme["up_color"])
    dn_c = rl_color(theme["down_color"])
    w, _ = A4

    h2_style = ParagraphStyle('H2met', fontName='Helvetica-Bold', fontSize=13,
                               textColor=rl_color(theme["header_text"]),
                               leading=18)

    label_style = ParagraphStyle('MetLabel', fontName='Helvetica-Bold', fontSize=7,
                                  textColor=sub_c, spaceAfter=1)
    value_style = ParagraphStyle('MetValue', fontName='Helvetica', fontSize=8,
                                  textColor=text_c, spaceAfter=2)

    for page_start in range(0, len(metabolites), per_page):
        page_mets = metabolites[page_start:page_start + per_page]

        elements.append(Spacer(1, 5*mm))
        pg_num = page_start // per_page + 1
        heading_table = Table(
            [[Paragraph(f"🧪 Metabolite Details — Page {pg_num}", h2_style)]],
            colWidths=[w - 30*mm]
        )
        heading_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), accent),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(heading_table)
        elements.append(Spacer(1, 3*mm))

        # Grid: 2 metabolites per row
        for row_start in range(0, len(page_mets), 2):
            row_mets = page_mets[row_start:row_start + 2]
            card_cells = []

            for m in row_mets:
                name = m.get("name", "Unknown")
                formula = m.get("formula", "")
                mz = m.get("mz", 0)
                rt = m.get("rt", 0)
                fc = m.get("fc", 0)
                pval = m.get("pvalue", 1)
                padj = m.get("padj", 1)
                hmdb = m.get("hmdb", "")
                pathway = m.get("pathway", "")

                is_up = fc > 0
                sig_color = up_c if (is_up and pval < 0.05) else dn_c if pval < 0.05 else sub_c
                direction = "↑ Up" if (is_up and pval < 0.05) else "↓ Down" if pval < 0.05 else "NS"

                card_w = (w - 30*mm - 4*mm) / 2
                bar_d = make_bar_drawing(m, theme, width=float(card_w - 8), height=100)

                name_style = ParagraphStyle('MName', fontName='Helvetica-Bold', fontSize=9,
                                             textColor=text_c)
                dir_style = ParagraphStyle('MDir', fontName='Helvetica-Bold', fontSize=7,
                                            textColor=sig_color)

                meta_data = [
                    ["Formula", formula, "m/z", f"{mz:.4f}"],
                    ["RT (min)", f"{rt:.2f}", "FC", f"{fc:+.2f}"],
                    ["p-value", f"{pval:.4f}", "p-adj", f"{padj:.4f}"],
                    ["HMDB", hmdb, "Pathway", pathway],
                ]

                meta_table = Table(meta_data, colWidths=[card_w * 0.18, card_w * 0.3, card_w * 0.18, card_w * 0.3])
                meta_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('TEXTCOLOR', (0, 0), (0, -1), sub_c),
                    ('TEXTCOLOR', (2, 0), (2, -1), sub_c),
                    ('TEXTCOLOR', (1, 0), (1, -1), text_c),
                    ('TEXTCOLOR', (3, 0), (3, -1), text_c),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ]))

                card_content = [
                    [Paragraph(name, name_style)],
                    [Paragraph(direction, dir_style)],
                    [DrawingFlowable(bar_d)],
                    [meta_table],
                ]

                card_table = Table(card_content, colWidths=[card_w - 8])
                card_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), card_bg),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))

                outer_table = Table([[card_table]], colWidths=[card_w])
                outer_table.setStyle(TableStyle([
                    ('BOX', (0, 0), (-1, -1), 1, border_c),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ]))

                card_cells.append(outer_table)

            if len(card_cells) == 1:
                card_cells.append(Spacer(1, 1))

            row_table = Table([card_cells], colWidths=[(w - 30*mm) / 2] * 2)
            row_table.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(row_table)
            elements.append(Spacer(1, 2*mm))

        elements.append(PageBreak())


def build_results_table(theme, metabolites, elements, styles):
    """Build a full results table page."""
    accent = rl_color(theme["accent"])
    text_c = rl_color(theme["text"])
    sub_c = rl_color(theme["subtext"])
    border_c = rl_color(theme["border"])
    card_bg = rl_color(theme["card_bg"])
    table_alt = rl_color(theme["table_alt"])
    header_text = rl_color(theme["header_text"])
    up_c = rl_color(theme["up_color"])
    dn_c = rl_color(theme["down_color"])
    w, _ = A4

    h2_style = ParagraphStyle('H2tbl', fontName='Helvetica-Bold', fontSize=13,
                               textColor=header_text, leading=18)
    elements.append(Spacer(1, 5*mm))
    heading_table = Table([[Paragraph("📋 Complete Results Table", h2_style)]], colWidths=[w - 30*mm])
    heading_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), accent),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(heading_table)
    elements.append(Spacer(1, 4*mm))

    col_names = ["#", "Name", "Formula", "m/z", "RT", "FC", "p-value", "p-adj", "Pathway", "Reg."]
    col_w = [12, 52, 42, 38, 22, 22, 28, 28, 45, 18]
    col_w = [c * mm for c in col_w]

    tbl_header_style = ParagraphStyle('TblH', fontName='Helvetica-Bold', fontSize=7.5,
                                       textColor=header_text)
    tbl_cell_style = ParagraphStyle('TblC', fontName='Helvetica', fontSize=7,
                                     textColor=text_c)

    data = [[Paragraph(c, tbl_header_style) for c in col_names]]
    for i, m in enumerate(metabolites):
        fc = m.get("fc", 0)
        pval = m.get("pvalue", 1)
        is_sig = pval < 0.05
        reg = "↑" if (fc > 0 and is_sig) else "↓" if (fc < 0 and is_sig) else "NS"
        row_style = ParagraphStyle('TblR', fontName='Helvetica', fontSize=7,
                                    textColor=up_c if reg == "↑" else dn_c if reg == "↓" else sub_c)
        row = [
            Paragraph(str(i + 1), tbl_cell_style),
            Paragraph(m.get("name", ""), tbl_cell_style),
            Paragraph(m.get("formula", ""), tbl_cell_style),
            Paragraph(f'{m.get("mz", 0):.4f}', tbl_cell_style),
            Paragraph(f'{m.get("rt", 0):.2f}', tbl_cell_style),
            Paragraph(f'{fc:+.2f}', tbl_cell_style),
            Paragraph(f'{pval:.4f}', tbl_cell_style),
            Paragraph(f'{m.get("padj", 1):.4f}', tbl_cell_style),
            Paragraph(m.get("pathway", ""), tbl_cell_style),
            Paragraph(reg, row_style),
        ]
        data.append(row)

    tbl = Table(data, colWidths=col_w, repeatRows=1)
    row_colors = [('BACKGROUND', (0, 0), (-1, 0), accent)]
    for i in range(1, len(data)):
        bg = table_alt if i % 2 == 0 else rl_color(theme["bg"])
        row_colors.append(('BACKGROUND', (0, i), (-1, i), bg))

    tbl.setStyle(TableStyle([
        *row_colors,
        ('GRID', (0, 0), (-1, -1), 0.4, border_c),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(tbl)
    elements.append(PageBreak())


# ─────────────────────────────────────────────
# MAIN PDF GENERATION FUNCTION
# ─────────────────────────────────────────────

def generate_pdf_bytes(
    theme_key: str = "light",
    study_data: dict = None,
    metabolites: list = None,
    options: dict = None,
) -> bytes:
    """
    Generate a PDF report and return as bytes.
    Compatible with Streamlit Cloud — no system libraries required.
    """
    if study_data is None:
        study_data = DEFAULT_STUDY_DATA.copy()
    if metabolites is None:
        metabolites = DEFAULT_METABOLITES.copy()
    if options is None:
        options = {}

    theme = THEMES.get(theme_key, THEMES["light"])

    buf = BytesIO()
    w, h = A4

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=28*mm,
        bottomMargin=18*mm,
        title=study_data.get("title", "LCMS Report"),
        author=study_data.get("author", ""),
        subject="LCMS Untargeted Metabolomics",
    )

    page_cb = make_page_callback(theme, study_data, {})
    doc.onPage = page_cb

    styles = getSampleStyleSheet()
    elements = []

    # Cover
    if options.get("include_cover", True):
        build_cover_page(theme, study_data, elements, styles)

    # Summary
    if options.get("include_summary", True):
        build_summary_page(theme, study_data, metabolites, elements, styles)

    # Metabolite detail pages
    if options.get("include_metabolites", True):
        per_page = options.get("metabolites_per_page", 4)
        build_metabolite_pages(theme, metabolites, elements, styles, per_page=per_page)

    # Results table
    if options.get("include_table", True):
        build_results_table(theme, metabolites, elements, styles)

    doc.build(elements, onFirstPage=page_cb, onLaterPages=page_cb)

    return buf.getvalue()