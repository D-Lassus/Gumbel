# Gumbel Wind Speed Estimator

A desktop application built with PySide6 to estimate wind speeds for various return periods using a Gumbel distribution. Designed for use in structural engineering applications to generate interactive graphs and export PDF reports.

---

## Features
- **Data Input**: Dynamically add/remove rows to enter multiple pairs of known wind speeds (m/s) and their associated return periods (years).
- **Gumbel Distribution Fitting**: Automatically fits a Gumbel distribution to the provided data using least squares on the reduced variate.
- **Interactive Plotting**:
    - Displays the Gumbel curve on an interactive Matplotlib graph.
    - Includes standard Matplotlib navigation toolbar (pan, zoom, save).
    - Click on the graph to read the corresponding wind speed and return period in the status bar.
- **Dual Query Mode**:
    - Input specific return periods to calculate and plot corresponding wind speeds.
    - Input specific wind speeds to calculate and plot corresponding return periods.
    - Queried points are clearly marked on the graph with values and guide lines.
- **Customisable Views**: Toggle between linear and logarithmic scales for the return period axis on the graph.
- **PDF Report Generation**: Export a comprehensive PDF report including inputs, fitted Gumbel parameters, a detailed theoretical derivation, an annotated plot matching the GUI, and a summary of plotted points.
- **Borderless Dark Theme UI**: Modern, dark themed interface built with PySide6 featuring a borderless main window with integrated window controls (minimise, maximise, close).
- **Project Save/Load**: Save input data, calculated parameters, queried points, and plot settings to a project file (`.gblproj`) and load them back into the application.

---

## User Interface Overview
The application features a customised borderless user interface with:
- A main toolbar containing file operations (Open, Save, Export PDF) and custom window controls (Minimise, Maximise/Restore, Close).
- A menu bar for standard application actions.
- A left panel with:
    - A table for dynamic input of return period and wind speed data points.
    - Controls for adding/removing data rows.
    - Sections for inputting specific return periods or wind speeds for querying.
    - A button to trigger Gumbel fit calculation and plotting.
    - A display area for the calculated Gumbel parameters.
- A right panel displaying:
    - An embedded Matplotlib canvas with the interactive Gumbel plot.
    - The standard Matplotlib navigation toolbar.
    - A checkbox to toggle the plot's x-axis scale (log/linear).
- A status bar at the bottom for user feedback and clicked plot coordinates.

---

## Typical Workflow
1. **Enter Data**: Input known wind speed and return period data points using the table. Add/remove rows as needed. Alternatively, load data from a previously saved `.gblproj` file.
2. **Calculate Fit & Plot**: Click the "Calculate Gumbel Fit & Plot" button. The Gumbel parameters (\(\mu\) and \(1/\alpha\)) are calculated and displayed, and the plot is updated.
3. **Explore Interactively**: View the plotted Gumbel curve. Use the Matplotlib toolbar to zoom/pan. Click on the graph to explore wind speed/return period relationships shown in the status bar. Toggle the x-axis scale.
4. **Query Specific Points**:
   - Enter a desired return period (> 1 year) and click "Find Wind Speed".
   - Enter a desired wind speed (> 0 m/s) and click "Find Return Period".
   - Queried points are marked on the graph with annotations and guide lines.
5. **Generate Report**: Click the "Export to PDF" button (or use the File menu) to create a PDF document summarising all inputs, calculations, theoretical background, the annotated plot, and a summary of plotted points.
6. **Save Project**: Use the "Save Project" button (or File menu) to save the current input data, results, and settings for later use.

---

## Setup Instructions

### 1. Create a Virtual Environment (Recommended)
```bash
python -m venv venv

### 2. Activate the Virtual Environment
   - **Windows:** Use `venv\Scripts\activate`
   - **macOS/Linux:** Use `source venv/bin/activate`

### 3. Install Required Packages
   Run `pip install PySide6 matplotlib numpy pandas reportlab`

---

## How to Run

In your terminal, ensure your virtual environment is activated and run:

`python gumbel.py`

(Assuming your script is named `gumbel.py`)

---

## Notes
- The interactive graph supports both **linear and logarithmic** return period views.
- All calculations follow the **Gumbel extreme value distribution (Type I EVD)**:
  $$ V_T = \mu + \frac{1}{\alpha} \cdot y_T \quad \text{where} \quad y_T = -\ln(-\ln(1 - 1/T)) $$
  - \( V_T \): Wind speed for return period T
  - \( T \): Return period in years (must be > 1 for the formula)
  - \( \mu \): Location parameter of the Gumbel distribution
  - \( 1/\alpha \): Scale parameter of the Gumbel distribution
  - \( y_T \): Reduced Gumbel variate for return period T

---

## PDF Report Includes:
- **Input Data Summary**: Table of user-provided wind speeds and return periods used for the fit.
- **Gumbel Parameters**: Calculated \(\mu\) (location) and \(1/\alpha\) (scale) parameters.
- **Queried Points**: Table summarising specific user-queried return periods/wind speeds and their calculated counterparts.
- **Theoretical Background & Derivation**: Detailed explanation of EVT, GEV, the Gumbel distribution, return period definition, and step-by-step derivation of the \(V_T\) formula.
- **Plot**: An embedded image of the Wind Speed vs. Return Period graph, matching the current GUI view (log/linear scale) and including annotations for input data and queried points, plus guide lines for queries.
- **Plot Summary**: A textual summary of the points annotated on the included graph.

---

## Future Enhancements
- **Advanced UI Polish**: Further refinements to widget spacing, styling, and visual feedback.
- **Advanced Plot Customisation**: User options for changing colours, line styles, labels, etc.
- **Error Handling**: More specific feedback for calculation edge cases or invalid data combinations.
- **Internationalisation**: Support for multiple languages in the UI and reports.
- **Data Import/Export**: Options to import data from CSV/Excel and export results beyond the project file format.
- **Alternative Fitting Methods**: Option to use Maximum Likelihood Estimation (MLE) for parameter fitting.

---

## Licence
This tool is released under the MIT Licence. Modify and use freely.