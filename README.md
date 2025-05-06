# Gumbel Wind Speed Estimator

A desktop application built with PySide6 to estimate wind speeds for various return periods using a Gumbel distribution. Designed for use in structural engineering applications to generate interactive graphs and export PDF reports.

---

## Features
- **Data Input**: Enter multiple pairs of known wind speeds (m/s) and their associated return periods (years).
- **Gumbel Distribution Fitting**: Automatically fits a Gumbel distribution to the provided data.
- **Interactive Plotting**: 
    - Displays the Gumbel curve on an interactive Matplotlib graph.
    - Click on the graph to read the corresponding wind speed and return period.
    - Automatically draws horizontal lines for user-specified wind speeds or vertical lines for user-specified return periods, showing their calculated counterparts.
- **Dual Query Mode**:
    - Input specific return periods to calculate and plot corresponding wind speeds.
    - Input specific wind speeds to calculate and plot corresponding return periods.
- **Customizable Views**: Supports both linear and logarithmic scales for the return period axis on the graph.
- **PDF Report Generation**: Export a comprehensive PDF report including inputs, Gumbel parameters, theoretical derivations, live calculations, and plots.
- **Dark Theme UI**: Built with PySide6 featuring a dark theme for comfortable viewing.

---

## User Interface Overview
The application will feature a user-friendly interface with:
- Input fields for wind speed and return period data.
- Sections to input specific return periods or wind speeds for querying.
- An embedded Matplotlib canvas for interactive graph display.
- Buttons to trigger calculations, plot updates, and PDF report generation.
- Display areas for Gumbel parameters and calculation results.

---

## Typical Workflow
1. **Enter Data**: Input known wind speed and return period data points.
2. **Fit Distribution**: The application automatically calculates Gumbel parameters \( \mu \) and \( \alpha \).
3. **Explore Interactively**: View the plotted Gumbel curve. Click on the graph to explore wind speed/return period relationships.
4. **Query Specific Points**:
   - Enter desired return periods to find corresponding wind speeds.
   - Enter desired wind speeds to find corresponding return periods.
   - These points will be marked on the graph.
5. **Generate Report**: Create a PDF document summarizing all inputs, calculations, theoretical background, and plots.

---

## Setup Instructions (Windows + VS Code)

### 1. Create a Virtual Environment
```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
```bash
venv\Scripts\activate
```

### 3. Install Required Packages
```bash
pip install PySide6 matplotlib numpy pandas reportlab
```

---

## How to Run
In your VS Code terminal, ensure your virtual environment is activated and run:
```bash
python gumbel_wind_app.py
```

---

## Notes
- Graph supports both **linear and logarithmic** return period views.
- All calculations follow the **Gumbel extreme value distribution**:
  \[ V_T = \mu + \frac{1}{\alpha} \cdot y_T \quad \text{where} \quad y_T = -\ln(-\ln(1 - 1/T)) \]
  - \( V_T \): Wind speed for return period T
  - \( T \): Return period in years
  - \( \mu \): Location parameter of the Gumbel distribution
  - \( \alpha \): Scale parameter of the Gumbel distribution
  - \( y_T \): Reduced variate for return period T

---

## PDF Report Includes:
- **Input Data Summary**: Table of user-provided wind speeds and return periods.
- **Gumbel Parameters**: Calculated \( \mu \) (location) and \( \alpha \) (scale) parameters.
- **Queried Points**: Table of user-specified return periods/wind speeds and their calculated counterparts.
- **Theoretical Background**: Explanation of the Gumbel distribution and relevant equations.
- **Live Calculations**: Step-by-step calculations for queried points.
- **Graphs**:
    - Plot of wind speed vs. return period (linear scale).
    - Plot of wind speed vs. return period (logarithmic scale).
    - Plots will include markings for user-queried points.
- (Planned) Embedding of plot images directly in the PDF.

---

## Future Enhancements
- **UI Polish**: Further refinements to the user interface for a more professional look and feel.
- **Advanced Plot Customization**: Options for changing colors, line styles, labels, etc.
- **Project Files**: Ability to save and load input data and session settings.
- **Error Handling**: More robust error checking and user feedback.
- **Internationalization**: Support for multiple languages.
- **Data Import/Export**: Options to import data from CSV/Excel and export results.

---

## License
This tool is released under the MIT License. Modify and use freely.