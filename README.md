# LCMS PDF Report Generator

A Python GUI application for generating LCMS Untargeted Metabolomics PDF reports with customizable themes.

![LCMS PDF Generator Screenshot](screenshot.png)

## Features

- **10 Professional Themes**: Choose from 10 different color themes matching various publication styles
- **Customizable Study Information**: Enter study details, analyst info, and experimental parameters
- **Metabolite Data Management**: Add, edit, import, and export metabolite data
- **Logo Branding**: Add your company logo to reports
- **Custom Images**: Use your own chromatogram and MS2 spectrum images
- **Batch Generation**: Generate all 10 theme variations at once
- **JSON Import/Export**: Save and load your data for future use

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
cd lcms_pdf_generator
pip install -r requirements.txt
```

### Additional System Requirements (Linux)

WeasyPrint requires some system libraries. On Debian/Ubuntu:

```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

On Fedora/RHEL:

```bash
sudo dnf install pango gdk-pixbuf2 libffi-devel
```

On macOS (using Homebrew):

```bash
brew install pango gdk-pixbuf libffi
```

## Usage

### Running the Application

```bash
python main.py
```

Or use the launcher script:

```bash
./run.sh
```

### Basic Workflow

1. **Enter Study Information** (left panel)
   - Fill in study ID, batch, instrument, analyst, etc.
   - Set sample count and QC parameters

2. **Add Metabolite Data** (center panel)
   - Click "Add Row" to manually add metabolites
   - Or click "Load Sample Data" for demo data
   - Or "Import JSON" to load from a file

3. **Select Theme** (right panel)
   - Choose from 10 different themes
   - Preview the theme colors

4. **Generate PDF**
   - Click "Generate PDF Report" for single theme
   - Or "Generate All 10 Themes" for batch generation

### Metabolite Data Fields

| Field | Description | Example |
|-------|-------------|---------|
| ID | Feature identifier | FT-00184 |
| Name | Metabolite name | L-Carnitine |
| Formula | Molecular formula | C7H15NO3 |
| m/z | Mass-to-charge ratio | 162.1130 |
| RT | Retention time (min) | 5.42 |
| FC | Fold change | 3.42 |
| FDR | False discovery rate | 0.001 |
| Direction | Up or down regulated | up |
| Adduct | Ion adduct type | [M+H]+ |
| Confidence | Annotation level | Level 2 |
| Database | Database ID | HMDB0000062 |
| Match % | Match score | 87% |
| Pathway | Biological pathway | Fatty acid metabolism |

### JSON Data Format

```json
{
  "study_id": "LCMS-2024-0142",
  "batch_name": "Batch A",
  "instrument": "Q-Exactive Plus",
  "analyst": "Dr. Sarah Chen",
  "matrix": "Plasma",
  "sample_count": 48,
  "company_name": "Your Company",
  "control_group": "Control",
  "treatment_group": "Treatment",
  "metabolites": [
    {
      "id": "FT-00184",
      "name": "L-Carnitine",
      "formula": "C7H15NO3",
      "mz": 162.1130,
      "rt": 5.42,
      "fc": 3.42,
      "fdr": 0.001,
      "direction": "up",
      "adduct": "[M+H]+",
      "confidence": "Level 2",
      "database": "HMDB0000062",
      "match_score": "87%",
      "pathway": "Fatty acid metabolism"
    }
  ]
}
```

## Available Themes

1. **Modern Light** - Clean executive dashboard style
2. **Clinical Clean** - Medical publication style
3. **Dark Analytics** - Dark mode analytics theme
4. **Biotech Premium** - Green biotech aesthetic
5. **Journal Figure** - Publication-ready figure style
6. **Minimal White** - Ultra-clean minimal design
7. **Data Dense** - Data-dense scientific layout
8. **Corporate Pro** - Business professional style
9. **Gradient SaaS** - Modern gradient SaaS style
10. **Academic** - Traditional academic style

## Report Structure

Each generated PDF includes:

1. **Summary Page**
   - Study metadata
   - Sample statistics
   - QC parameters

2. **Global Plots Page**
   - Volcano plot
   - Heatmap
   - PCA plot

3. **Metabolite Pages** (4 metabolites per page)
   - Relative abundance bar graph
   - Extracted ion chromatogram
   - MS2 fragmentation spectrum
   - MS2 mirror plot

## Customization

### Adding Custom Images

1. Click "Select Chromatogram" to add your chromatogram image
2. Click "Select MS2 Spectrum" to add your MS2 spectrum image
3. Images will be used as placeholders in the metabolite cards

### Adding Your Logo

1. Click "Select Logo" in the Company & Branding section
2. Choose a PNG, JPG, or SVG file
3. The logo will appear in the top-right corner of each page

## Troubleshooting

### "WeasyPrint not found" error

Install WeasyPrint:
```bash
pip install WeasyPrint
```

### Missing system libraries (Linux)

```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

### PDF generation fails

Check that:
1. All required fields are filled
2. Metabolite data is valid (numeric fields contain numbers)
3. Output directory is writable

## License

MIT License

## Support

For issues and feature requests, please open an issue on the project repository.

---

Created by NinjaTech AI