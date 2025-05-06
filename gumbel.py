import sys
import json
import numpy as np
import pandas as pd
from io import BytesIO

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QGroupBox, QLineEdit, QStatusBar, QToolBar, QSizePolicy, QCheckBox,
    QMessageBox, QSpacerItem
)
from PySide6.QtGui import QAction, QIcon, QPalette, QColor, QPainter
from PySide6.QtCore import Qt, QSize

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table as RLTable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

class GumbelWindApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gumbel Wind Speed Estimator")
        self.setGeometry(100, 100, 1200, 800)

        self.u = None
        self.alpha_inv = None
        self.input_data_points = []
        self.queried_points = []

        self.initialise_ui()


    def initialise_ui(self):
        self.setup_styling()
        self.create_actions()
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.create_central_widget()
        self.update_button_states()

    def setup_styling(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2E2E2E;
                color: #E0E0E0;
                font-size: 10pt;
            }
            QTableWidget {
                background-color: #3C3C3C;
                alternate-background-color: #454545;
                gridline-color: #505050;
            }
            QHeaderView::section {
                background-color: #505050;
                color: #E0E0E0;
                padding: 4px;
                border: 1px solid #3C3C3C;
            }
            QPushButton {
                background-color: #505050;
                color: #E0E0E0;
                border: 1px solid #606060;
                padding: 8px 12px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
            QPushButton:disabled {
                background-color: #3A3A3A;
                color: #707070;
            }
            QLineEdit {
                background-color: #3C3C3C;
                border: 1px solid #505050;
                padding: 5px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #505050;
                margin-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLabel {
                padding: 2px;
            }
            QToolTip {
                background-color: #3C3C3C;
                color: #E0E0E0;
                border: 1px solid #505050;
            }
            QStatusBar {
                font-size: 9pt;
            }
        """)

        try:
            self.add_icon = QIcon.fromTheme("list-add", QIcon(":/qt-project.org/styles/commonstyle/images/standardbutton-add-16.png"))
            self.remove_icon = QIcon.fromTheme("list-remove", QIcon(":/qt-project.org/styles/commonstyle/images/standardbutton-remove-16.png"))
            self.calc_icon = QIcon.fromTheme("system-run", QIcon(":/qt-project.org/styles/commonstyle/images/media-playback-start-32.png"))
            self.pdf_icon = QIcon.fromTheme("document-export", QIcon(":/qt-project.org/styles/commonstyle/images/fileprint-32.png"))
            self.open_icon = QIcon.fromTheme("document-open", QIcon(":/qt-project.org/styles/commonstyle/images/fileopen-32.png"))
            self.save_icon = QIcon.fromTheme("document-save", QIcon(":/qt-project.org/styles/commonstyle/images/filesave-32.png"))
            self.exit_icon = QIcon.fromTheme("application-exit", QIcon(":/qt-project.org/styles/commonstyle/images/standardbutton-cancel-32.png"))
        except: # Fallback if theme icons are not available
            self.add_icon = QIcon()
            self.remove_icon = QIcon()
            self.calc_icon = QIcon()
            self.pdf_icon = QIcon()
            self.open_icon = QIcon()
            self.save_icon = QIcon()
            self.exit_icon = QIcon()


    def create_actions(self):
        self.open_action = QAction(self.open_icon, "&Open Project...", self)
        self.open_action.setStatusTip("Open a project file")
        self.open_action.triggered.connect(self.load_project)

        self.save_action = QAction(self.save_icon, "&Save Project...", self)
        self.save_action.setStatusTip("Save the current project data")
        self.save_action.triggered.connect(self.save_project)
        self.save_action.setEnabled(False)

        self.exit_action = QAction(self.exit_icon, "E&xit", self)
        self.exit_action.setStatusTip("Exit application")
        self.exit_action.triggered.connect(self.close)

        self.export_pdf_action = QAction(self.pdf_icon, "Export to &PDF...", self)
        self.export_pdf_action.setStatusTip("Export report to PDF file")
        self.export_pdf_action.triggered.connect(self.export_pdf)
        self.export_pdf_action.setEnabled(False)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_pdf_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

    def create_tool_bar(self):
        tool_bar = QToolBar("Main Toolbar")
        tool_bar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.TopToolBarArea, tool_bar)
        tool_bar.addAction(self.open_action)
        tool_bar.addAction(self.save_action)
        tool_bar.addAction(self.export_pdf_action)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Please input data or open a project.", 5000)

    def create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel_layout = QVBoxLayout()
        left_panel_layout.setSpacing(10)

        input_data_group = QGroupBox("Input Data Points (Return Period & Wind Speed)")
        input_data_layout = QVBoxLayout(input_data_group)

        self.table = QTableWidget(2, 2)
        self.table.setHorizontalHeaderLabels(["Return Period (years)", "Wind Speed (m/s)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                item = QTableWidgetItem()
                self.table.setItem(r, c, item)
                if c == 0: item.setToolTip("Enter return period in years (e.g., 50)")
                else: item.setToolTip("Enter wind speed in m/s (e.g., 30.5)")
        input_data_layout.addWidget(self.table)

        table_buttons_layout = QHBoxLayout()
        self.add_row_button = QPushButton(self.add_icon, "Add Row")
        self.add_row_button.clicked.connect(self.add_table_row)
        self.add_row_button.setToolTip("Add a new row for data input")
        table_buttons_layout.addWidget(self.add_row_button)

        self.remove_row_button = QPushButton(self.remove_icon, "Remove Row")
        self.remove_row_button.clicked.connect(self.remove_table_row)
        self.remove_row_button.setToolTip("Remove the selected row")
        table_buttons_layout.addWidget(self.remove_row_button)
        input_data_layout.addLayout(table_buttons_layout)
        left_panel_layout.addWidget(input_data_group)

        query_group = QGroupBox("Specific Value Queries")
        query_layout = QVBoxLayout(query_group)

        rp_query_layout = QHBoxLayout()
        rp_query_layout.addWidget(QLabel("Return Period (years):"))
        self.rp_query_input = QLineEdit()
        self.rp_query_input.setPlaceholderText("e.g., 100")
        self.rp_query_input.setToolTip("Enter a specific return period to find its wind speed")
        rp_query_layout.addWidget(self.rp_query_input)
        self.rp_query_button = QPushButton("Find Wind Speed")
        self.rp_query_button.clicked.connect(lambda: self.query_value('rp'))
        self.rp_query_button.setToolTip("Calculate wind speed for the given return period")
        rp_query_layout.addWidget(self.rp_query_button)
        query_layout.addLayout(rp_query_layout)

        ws_query_layout = QHBoxLayout()
        ws_query_layout.addWidget(QLabel("Wind Speed (m/s):        "))
        self.ws_query_input = QLineEdit()
        self.ws_query_input.setPlaceholderText("e.g., 40.0")
        self.ws_query_input.setToolTip("Enter a specific wind speed to find its return period")
        ws_query_layout.addWidget(self.ws_query_input)
        self.ws_query_button = QPushButton("Find Return Period")
        self.ws_query_button.clicked.connect(lambda: self.query_value('ws'))
        self.ws_query_button.setToolTip("Calculate return period for the given wind speed")
        ws_query_layout.addWidget(self.ws_query_button)
        query_layout.addLayout(ws_query_layout)
        left_panel_layout.addWidget(query_group)

        self.calc_button = QPushButton(self.calc_icon, "Calculate Gumbel Fit & Plot")
        self.calc_button.clicked.connect(self.calculate_and_plot)
        self.calc_button.setToolTip("Perform Gumbel distribution fitting and update the plot")
        left_panel_layout.addWidget(self.calc_button)

        self.result_label = QLabel("Gumbel Parameters: Not yet calculated.")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-style: italic; padding: 5px; border: 1px solid #404040; background-color: #353535;")
        left_panel_layout.addWidget(self.result_label)

        left_panel_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        left_widget = QWidget()
        left_widget.setLayout(left_panel_layout)
        left_widget.setFixedWidth(450)
        main_layout.addWidget(left_widget)

        right_panel_layout = QVBoxLayout()
        plot_group = QGroupBox("Wind Speed vs. Return Period Plot")
        plot_layout = QVBoxLayout(plot_group)

        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#2E2E2E')
        self.fig.patch.set_facecolor('#2E2E2E')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color: #3C3C3C; border: 1px solid #505050;") 
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        plot_options_layout = QHBoxLayout()
        self.log_scale_checkbox = QCheckBox("Logarithmic Scale (Return Period)")
        self.log_scale_checkbox.setChecked(True)
        self.log_scale_checkbox.toggled.connect(self.update_plot_scale)
        self.log_scale_checkbox.setToolTip("Toggle between logarithmic and linear scale for the return period axis")
        plot_options_layout.addWidget(self.log_scale_checkbox)
        plot_layout.addLayout(plot_options_layout)
        right_panel_layout.addWidget(plot_group)
        
        main_layout.addLayout(right_panel_layout)
        self.canvas.mpl_connect("button_press_event", self.on_plot_click)

    def add_table_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        for c in range(self.table.columnCount()):
            item = QTableWidgetItem()
            self.table.setItem(row_count, c, item)
            if c == 0: item.setToolTip("Enter return period in years (e.g., 50)")
            else: item.setToolTip("Enter wind speed in m/s (e.g., 30.5)")
        self.status_bar.showMessage("Added new row to input table.", 3000)

    def remove_table_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0 and self.table.rowCount() > 1 :
            self.table.removeRow(current_row)
            self.status_bar.showMessage(f"Removed row {current_row + 1}.", 3000)
        elif self.table.rowCount() <=1:
            QMessageBox.warning(self, "Cannot Remove Row", "At least one row must remain.")
        else:
            QMessageBox.information(self, "Remove Row", "Please select a row to remove.")

    def reduced_variate(self, T):
        T_array = np.array(T, dtype=float)
        y = np.full_like(T_array, np.nan) # Initialise with NaNs

        # Perform calculation only on valid T_array values (T > 1)
        # Suppress warnings for log(0) or log(negative) as these cases are handled
        with np.errstate(divide='ignore', invalid='ignore'):
            valid_mask = T_array > 1
            if np.any(valid_mask):
                T_valid = T_array[valid_mask]
                # term1 = 1.0 - 1.0 / T_valid -> (0, 1) for T_valid > 1
                # term2 = -np.log(term1) -> positive for T_valid > 1
                # y_valid = -np.log(term2)
                y[valid_mask] = -np.log(-np.log(1.0 - (1.0 / T_valid)))
        
        if isinstance(T, (list, np.ndarray)):
            return y
        else: # Input was scalar
            return y.item() if y.size == 1 else np.nan


    def wind_speed_from_params(self, T):
        if self.u is None or self.alpha_inv is None:
            if isinstance(T, (list, np.ndarray)):
                return np.full(np.shape(T), np.nan)
            return np.nan
        
        y = self.reduced_variate(T) # y can be scalar NaN or array with NaNs
        
        # NumPy's arithmetic operations propagate NaNs automatically
        return self.u + self.alpha_inv * y


    def return_period_from_params(self, V):
        if self.u is None or self.alpha_inv is None or self.alpha_inv == 0:
            return np.nan
        y = (V - self.u) / self.alpha_inv
        
        with np.errstate(over='ignore', under='ignore'): # Ignore exp under/overflow temporarily
            exp_neg_y = np.exp(-y)
            # Probability p = exp(-exp(-y))
            # T = 1 / (1 - p)
            # Need 1 - p > 0, so p < 1. exp(-exp(-y)) < 1
            # This is true if -exp(-y) < 0, which means exp(-y) > 0. Always true for real y.
            # Also need 1 - p != 0, so p != 1.
            # Denominator 1.0 - np.exp(-exp_neg_y) must not be zero or cause issues.
            # If exp_neg_y is very large (y is very negative), exp(-exp_neg_y) -> 0, T -> 1.
            # If exp_neg_y is very small (y is very positive), exp(-exp_neg_y) -> 1, T -> inf.
            
            probability_non_exceedance = np.exp(-exp_neg_y)
            
            # Check for probability close to 1, which makes T very large or infinite
            if isinstance(probability_non_exceedance, np.ndarray):
                if np.any(probability_non_exceedance >= 1.0 - 1e-9): # Check if p is too close to 1
                     # Assign NaN or a very large number for these cases if appropriate
                     return np.where(probability_non_exceedance < 1.0 - 1e-9, 1.0 / (1.0 - probability_non_exceedance), np.inf)

            elif probability_non_exceedance >= 1.0 - 1e-9: # Scalar case
                return np.inf # Or np.nan if preferred for out of bounds

            return 1.0 / (1.0 - probability_non_exceedance)


    def get_table_data(self):
        T_vals, V_vals = [], []
        valid_points = []
        for row in range(self.table.rowCount()):
            try:
                T_item = self.table.item(row, 0)
                V_item = self.table.item(row, 1)
                if T_item and V_item and T_item.text() and V_item.text():
                    T_str = T_item.text().strip()
                    V_str = V_item.text().strip()
                    if not T_str or not V_str: 
                        continue
                    T = float(T_str)
                    V = float(V_str)
                    if T <= 1 or V <= 0: 
                        QMessageBox.warning(self, "Invalid Input", f"Data in row {row + 1} is out of typical range: Return period must be > 1 and wind speed > 0.")
                        return None, None, None 
                    T_vals.append(T)
                    V_vals.append(V)
                    valid_points.append({'T': T, 'V': V})
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", f"Invalid numeric data in row {row + 1}. Please enter valid numbers.")
                return None, None, None
            except Exception as e: 
                 QMessageBox.warning(self, "Input Error", f"Error reading data in row {row + 1}: {str(e)}")
                 return None, None, None
        self.input_data_points = valid_points
        return T_vals, V_vals, valid_points
        
    def calculate_and_plot(self):
        self.queried_points = [] 
        T_vals, V_vals, _ = self.get_table_data()

        if T_vals is None or len(T_vals) < 2:
            if T_vals is not None and len(T_vals) < 2 : 
                QMessageBox.warning(self, "Insufficient Data", "Please enter at least two valid data points to fit the Gumbel distribution.")
            self.u = None
            self.alpha_inv = None
            self.update_button_states()
            self.result_label.setText("Gumbel Parameters: Calculation failed. Insufficient or invalid data.")
            self.update_plot() # Call update_plot to clear or show "no data"
            return

        try:
            y_vals_arr = self.reduced_variate(np.array(T_vals, dtype=float))
            if np.isnan(y_vals_arr).any():
                QMessageBox.critical(self, "Calculation Error", "Invalid return period encountered leading to error in reduced variate calculation (e.g., T <= 1).")
                self.u = None; self.alpha_inv = None
                self.update_button_states()
                self.update_plot()
                return

            A = np.vstack([y_vals_arr, np.ones(len(y_vals_arr))]).T
            self.alpha_inv, self.u = np.linalg.lstsq(A, V_vals, rcond=None)[0]
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"An error occurred during Gumbel parameter calculation: {str(e)}")
            self.u = None
            self.alpha_inv = None
            self.update_button_states()
            self.result_label.setText("Gumbel Parameters: Calculation failed.")
            self.update_plot()
            return

        self.result_label.setText(f"Gumbel Parameters: Location (\u03BC) = {self.u:.3f} m/s, Scale (1/\u03B1) = {self.alpha_inv:.3f} m/s")
        self.status_bar.showMessage("Gumbel parameters calculated successfully.", 5000)
        self.update_plot()
        self.update_button_states()


    def update_plot_scale(self):
        if self.u is not None or self.ax.lines or self.ax.collections: # Check if there's something to plot/plotted or params exist
            self.update_plot()

    def update_plot(self):
        self.ax.clear() # Clear previous plot elements

        if self.u is None or self.alpha_inv is None:
            self.ax.text(0.5, 0.5, 'No Gumbel fit available.\nPlease input data and calculate.', 
                         horizontalalignment='center', verticalalignment='center', 
                         transform=self.ax.transAxes, color='gray', fontsize=10)
        else:
            # Plot Gumbel Fit Line
            T_plot_min_val = 1.01 # Start slightly above 1 to avoid issues with log(0) from 1-1/T
            max_T_plot_val = 10000 
            
            if self.log_scale_checkbox.isChecked():
                T_plot_values = np.logspace(np.log10(T_plot_min_val), np.log10(max_T_plot_val), 400)
            else:
                T_plot_values = np.linspace(T_plot_min_val, max_T_plot_val, 400)
            
            V_plot_values = self.wind_speed_from_params(T_plot_values)
            
            valid_plot_indices = ~np.isnan(V_plot_values) & ~np.isinf(V_plot_values)
            if np.any(valid_plot_indices):
                self.ax.plot(T_plot_values[valid_plot_indices], V_plot_values[valid_plot_indices], label="Gumbel Fit", color='cyan', linewidth=2)

            # Plot Input Data Points (re-fetch clean data if necessary, or use self.input_data_points)
            if self.input_data_points: # Assumes self.input_data_points is up-to-date
                input_T = [p['T'] for p in self.input_data_points]
                input_V = [p['V'] for p in self.input_data_points]
                self.ax.scatter(input_T, input_V, color='red', zorder=5, label="Input Data")
                for T_val, V_val in zip(input_T, input_V):
                     self.ax.text(T_val * 1.02, V_val * 1.02, f'({T_val:.0f}y, {V_val:.1f}m/s)', fontsize=8, color='pink', va='bottom', ha='left')

            # Plot Queried Points
            for point in self.queried_points:
                try:
                    if point['type'] == 'V_from_T' and not (np.isnan(point['T_in']) or np.isnan(point['V_out'])):
                        self.ax.plot([point['T_in'], point['T_in']], [self.ax.get_ylim()[0], point['V_out']], linestyle='--', color='lime', alpha=0.7)
                        self.ax.plot([self.ax.get_xlim()[0], point['T_in']], [point['V_out'], point['V_out']], linestyle='--', color='lime', alpha=0.7)
                        self.ax.scatter([point['T_in']], [point['V_out']], color='lime', marker='o', s=50, zorder=6, label=f"Query: T={point['T_in']:.0f}y \u2192 V={point['V_out']:.1f}m/s")
                    elif point['type'] == 'T_from_V' and not (np.isnan(point['V_in']) or np.isnan(point['T_out'])):
                        self.ax.plot([point['T_out'], point['T_out']], [self.ax.get_ylim()[0], point['V_in']], linestyle='--', color='orange', alpha=0.7)
                        self.ax.plot([self.ax.get_xlim()[0], point['T_out']], [point['V_in'], point['V_in']], linestyle='--', color='orange', alpha=0.7)
                        self.ax.scatter([point['T_out']], [point['V_in']], color='orange', marker='s', s=50, zorder=6, label=f"Query: V={point['V_in']:.1f}m/s \u2192 T={point['T_out']:.0f}y")
                except Exception: 
                    pass 

        # Setup Plot Appearance (always do this)
        self.ax.set_xlabel("Return Period (years)")
        self.ax.set_ylabel("Wind Speed (m/s)")
        self.ax.set_title("Gumbel Distribution of Wind Speeds")

        if self.log_scale_checkbox.isChecked():
            self.ax.set_xscale("log")
            if self.u is None: self.ax.set_xlim(1, 10000) # Default if no fit
        else:
            self.ax.set_xscale("linear")
            if self.u is None: self.ax.set_xlim(0, 100) # Default if no fit
        
        if self.u is None: self.ax.set_ylim(0,50) # Default if no fit

        self.ax.grid(True, which="both", linestyle="--", linewidth=0.5, color='#BBBBBB', alpha=0.5)
        handles, labels = self.ax.get_legend_handles_labels()
        if handles: 
            by_label = dict(zip(labels, handles)) 
            self.ax.legend(by_label.values(), by_label.keys(), facecolor='#3C3C3C', edgecolor='#505050', labelcolor='white', fontsize='small')
        
        try:
            self.fig.tight_layout(pad=2.0, rect=[0, 0, 1, 0.95]) 
        except ValueError: # Can happen if plot is empty or too constrained
            pass
        self.canvas.draw()
        if self.u is not None:
            self.status_bar.showMessage("Plot updated.", 3000)

    def on_plot_click(self, event):
        if event.inaxes != self.ax:
            return
        if event.xdata is None or event.ydata is None: 
            self.status_bar.clearMessage()
            return

        clicked_T = event.xdata
        clicked_V_on_curve = self.wind_speed_from_params(clicked_T) if self.u is not None else None

        if clicked_V_on_curve is not None and not np.isnan(clicked_V_on_curve):
             message = f"Clicked: Return Period \u2248 {clicked_T:.1f} years. " \
                       f"On Curve: Wind Speed \u2248 {clicked_V_on_curve:.2f} m/s. " \
                       f"Cursor Y: {event.ydata:.2f} m/s."
        else:
            message = f"Clicked: Return Period \u2248 {clicked_T:.1f} years, Wind Speed \u2248 {event.ydata:.2f} m/s. (No Gumbel fit to show value)"
        
        self.status_bar.showMessage(message)

    def query_value(self, query_type):
        if self.u is None or self.alpha_inv is None:
            QMessageBox.warning(self, "Parameters Needed", "Please calculate Gumbel parameters first before querying.")
            return

        new_query_point = None
        if query_type == 'rp':
            try:
                T_in_str = self.rp_query_input.text().strip()
                if not T_in_str: QMessageBox.warning(self, "Input Missing", "Please enter a return period."); return
                T_in = float(T_in_str)
                if T_in <= 1: # Gumbel strictly for T > 1 for this formulation
                    QMessageBox.warning(self, "Invalid Input", "Return period must be greater than 1 year.")
                    return
                V_out = self.wind_speed_from_params(T_in)
                if np.isnan(V_out) or np.isinf(V_out):
                    QMessageBox.information(self, "Query Result", f"Could not calculate wind speed for T = {T_in:.1f} years (possibly outside valid range or unstable fit).")
                    return
                self.status_bar.showMessage(f"For T = {T_in:.1f} years, estimated Wind Speed = {V_out:.2f} m/s.", 10000)
                new_query_point = {'type': 'V_from_T', 'T_in': T_in, 'V_out': V_out}
                self.rp_query_input.clear()
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for return period.")
                return
        elif query_type == 'ws':
            try:
                V_in_str = self.ws_query_input.text().strip()
                if not V_in_str: QMessageBox.warning(self, "Input Missing", "Please enter a wind speed."); return
                V_in = float(V_in_str)
                if V_in <=0:
                     QMessageBox.warning(self, "Invalid Input", "Wind speed must be greater than 0 m/s.")
                     return
                T_out = self.return_period_from_params(V_in)
                if np.isnan(T_out) or np.isinf(T_out) or T_out <=1 : # Check if T_out is valid (T>1)
                    QMessageBox.information(self, "Query Result", f"Could not calculate a valid return period (T > 1) for V = {V_in:.1f} m/s (possibly outside valid range, unstable fit, or T \u2264 1).")
                    return
                self.status_bar.showMessage(f"For V = {V_in:.1f} m/s, estimated Return Period = {T_out:.1f} years.", 10000)
                new_query_point = {'type': 'T_from_V', 'V_in': V_in, 'T_out': T_out}
                self.ws_query_input.clear()
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for wind speed.")
                return
        
        if new_query_point:
            self.queried_points.append(new_query_point)
            self.update_plot()


    def update_button_states(self):
        has_params = self.u is not None and self.alpha_inv is not None
        self.export_pdf_action.setEnabled(has_params)
        self.save_action.setEnabled(True) 
        self.rp_query_button.setEnabled(has_params)
        self.ws_query_button.setEnabled(has_params)


    def export_pdf(self):
        if self.u is None or self.alpha_inv is None:
            QMessageBox.warning(self, "Cannot Export", "Please perform Gumbel calculation before exporting to PDF.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "", "PDF Files (*.pdf)")
        if not path:
            return

        try:
            doc = SimpleDocTemplate(path, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
            styles = getSampleStyleSheet()
            # Increase font size for normal text and code slightly for better readability
            styles['Normal'].fontSize = 10
            styles['Code'].fontSize = 9 # If you use a 'Code' style

            story = []

            story.append(Paragraph("<b>Gumbel Wind Speed Estimation Report</b>", styles['h1']))
            story.append(Spacer(1, 0.2 * inch))

            story.append(Paragraph("<b>1. Fitted Gumbel Parameters</b>", styles['h2']))
            story.append(Paragraph(f"Location parameter (\u03BC): {self.u:.4f} m/s", styles['Normal']))
            story.append(Paragraph(f"Scale parameter (1/\u03B1): {self.alpha_inv:.4f} m/s", styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))

            story.append(Paragraph("<b>2. Input Data Points</b>", styles['h2']))
            if self.input_data_points:
                data_for_table = [["Return Period (years)", "Wind Speed (m/s)"]]
                for item in self.input_data_points:
                    data_for_table.append([f"{item['T']:.1f}", f"{item['V']:.2f}"])
                
                pdf_table_style = [
                    ('BACKGROUND', (0,0), (-1,0), '#CCCCCC'), ('TEXTCOLOR', (0,0), (-1,0), '#000000'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTRE'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 12), ('BACKGROUND', (0,1), (-1,-1), '#EEEEEE'),
                    ('GRID', (0,0), (-1,-1), 1, '#666666')
                ]
                pdf_table = RLTable(data_for_table, style=pdf_table_style, colWidths=[2*inch, 2*inch])
                story.append(pdf_table)
            else:
                story.append(Paragraph("No valid input data provided for this report.", styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))

            if self.queried_points:
                story.append(Paragraph("<b>3. Specific Queried Values</b>", styles['h2']))
                query_data_for_table = [["Query Type", "Input Value", "Calculated Value"]]
                for q_point in self.queried_points:
                    if q_point['type'] == 'V_from_T':
                        query_data_for_table.append([f"T={q_point['T_in']:.1f}y \u2192 V", f"{q_point['T_in']:.1f} years", f"{q_point['V_out']:.2f} m/s"])
                    elif q_point['type'] == 'T_from_V':
                        query_data_for_table.append([f"V={q_point['V_in']:.1f}m/s \u2192 T", f"{q_point['V_in']:.1f} m/s", f"{q_point['T_out']:.1f} years"])
                
                query_pdf_table = RLTable(query_data_for_table, style=pdf_table_style, colWidths=[2*inch, 2*inch, 2*inch])
                story.append(query_pdf_table)
                story.append(Spacer(1, 0.2 * inch))

            story.append(Paragraph("<b>4. Theoretical Background and Derivation</b>", styles['h2']))
            
            theory_text = f"""
            Extreme Value Theory (EVT) provides a framework for modelling the stochastic behaviour of the extreme tails of probability distributions.
            For phenomena like maximum annual wind speeds, EVT suggests that the distribution of these extremes (block maxima) can often be approximated by the Generalized Extreme Value (GEV) distribution.
            <br/><br/>
            <b>Generalized Extreme Value (GEV) Distribution:</b><br/>
            The Cumulative Distribution Function (CDF) of the GEV distribution is given by:<br/>
            <i>F(x; \u03BC, \u03C3, \u03BE) = exp{'{'}-[1 + \u03BE * ( (x-\u03BC) / \u03C3 ) ]<sup>-1/\u03BE</sup>{'}'}</i>
            <br/>
            This is valid for <i>1 + \u03BE * ( (x-\u03BC) / \u03C3 ) > 0</i>.
            The parameters are:
            <ul>
                <li>\u03BC: location parameter</li>
                <li>\u03C3: scale parameter (\u03C3 > 0)</li>
                <li>\u03BE: shape parameter</li>
            </ul>
            The GEV encompasses three types of extreme value distributions: Type I (Gumbel), Type II (Fréchet), and Type III (Weibull), depending on the value of the shape parameter \u03BE.
            <br/><br/>
            <b>The Gumbel Distribution (Type I Extreme Value Distribution):</b><br/>
            The Gumbel distribution is a special case of the GEV distribution that arises when the shape parameter \u03BE approaches 0 (\u03BE &rarr; 0). It is commonly used for modelling phenomena such as maximum wind speeds, flood levels, and other maximal events.
            The CDF of the Gumbel distribution is:
            <br/>
            <i>F(x; \u03BC, \u03C3) = exp{'{'}-exp{'{'}-( (x-\u03BC) / \u03C3 ){'}'}{'}'}</i>
            <br/>
            In this application, we denote the scale parameter \u03C3 as <i>1/\u03B1</i>. Thus, \u03C3 = 1/\u03B1.
            <br/>
            <i>F(V; \u03BC, \u03B1) = exp{'{'}-exp{'{'}-\u03B1 (V-\u03BC){'}'}{'}'}</i> (using V for wind speed instead of x)
            <br/><br/>
            <b>Return Period:</b><br/>
            The return period, <i>T</i>, of an event (e.g., a wind speed V<sub>T</sub>) is the average time interval between occurrences of an event of magnitude V<sub>T</sub> or greater.
            It is defined as the reciprocal of the probability of exceedance in a given time unit (typically one year for annual maxima):
            <br/>
            <i>T = 1 / P(V > V<sub>T</sub>)</i>
            <br/>
            Since <i>P(V > V<sub>T</sub>) = 1 - P(V &le; V<sub>T</sub>) = 1 - F(V<sub>T</sub>)</i>, where F(V<sub>T</sub>) is the CDF evaluated at V<sub>T</sub>, we have:
            <br/>
            <i>T = 1 / (1 - F(V<sub>T</sub>))</i>
            <br/><br/>
            <b>Derivation of Wind Speed (V<sub>T</sub>) for a given Return Period (T):</b>
            <br/>
            1. From the definition of return period: <i>F(V<sub>T</sub>) = 1 - (1/T)</i>
            <br/>
            2. Substitute the Gumbel CDF for F(V<sub>T</sub>):
            <br/>&nbsp;&nbsp;&nbsp;<i>exp{'{'}-exp{'{'}-( (V<sub>T</sub>-\u03BC) / \u03C3 ){'}'}{'}'} = 1 - (1/T)</i>
            <br/>
            3. Take the natural logarithm (ln) of both sides:
            <br/>&nbsp;&nbsp;&nbsp;<i>-exp{'{'}-( (V<sub>T</sub>-\u03BC) / \u03C3 ){'}'} = ln(1 - (1/T))</i>
            <br/>
            4. Multiply by -1:
            <br/>&nbsp;&nbsp;&nbsp;<i>exp{'{'}-( (V<sub>T</sub>-\u03BC) / \u03C3 ){'}'} = -ln(1 - (1/T))</i>
            <br/>
            5. Take the natural logarithm again:
            <br/>&nbsp;&nbsp;&nbsp;<i>-( (V<sub>T</sub>-\u03BC) / \u03C3 ) = ln{'{'}-ln(1 - (1/T)){'}'}</i>
            <br/>
            6. Let the "reduced variate" y<sub>T</sub> be defined as:
            <br/>&nbsp;&nbsp;&nbsp;<i>y<sub>T</sub> = -ln{'{'}-ln(1 - (1/T)){'}'}</i>
            <br/>
            7. Substituting y<sub>T</sub> into the equation from step 5 (after multiplying by -1):
            <br/>&nbsp;&nbsp;&nbsp;<i>(V<sub>T</sub>-\u03BC) / \u03C3 = y<sub>T</sub></i>
            <br/>
            8. Rearranging to solve for V<sub>T</sub>:
            <br/>&nbsp;&nbsp;&nbsp;<i>V<sub>T</sub> = \u03BC + \u03C3 * y<sub>T</sub></i>
            <br/>
            9. Using the application's notation where the scale parameter \u03C3 = 1/\u03B1:
            <br/>&nbsp;&nbsp;&nbsp;<b><i>V<sub>T</sub> = \u03BC + (1/\u03B1) * y<sub>T</sub></i></b>
            <br/>
            This is the formula used in the application to estimate the wind speed V<sub>T</sub> for a given return period T, where \u03BC is the location parameter (current fit: {self.u:.4f} m/s) and 1/\u03B1 is the scale parameter (current fit: {self.alpha_inv:.4f} m/s).
            <br/><br/>
            <b>Parameter Estimation:</b><br/>
            The parameters \u03BC (location) and \u03B1 (or \u03C3, scale) are typically estimated from historical wind speed data. Common methods include the Method of Moments, Maximum Likelihood Estimation (MLE), or graphical methods using probability paper. This application uses a least-squares linear regression approach on the transformed data points (V vs. y<sub>T</sub>). The equation V<sub>T</sub> = (1/\u03B1) * y<sub>T</sub> + \u03BC is a linear equation of the form Y = mX + c, where V corresponds to Y, y<sub>T</sub> corresponds to X, the scale parameter (1/\u03B1) is the slope (m), and the location parameter (\u03BC) is the y-intercept (c).
            """
            story.append(Paragraph(theory_text, styles['Normal']))
            story.append(Spacer(1, 0.1 * inch)) 
            
            # Page break might be needed before the plot if theory is long
            # story.append(PageBreak()) # Uncomment if theory section pushes plot too far

            story.append(Paragraph("<b>5. Plot: Wind Speed vs. Return Period</b>", styles['h2']))
            story.append(Spacer(1, 0.1 * inch))
            
            img_data = BytesIO()
            temp_fig_pdf = Figure(figsize=(7.5, 5.5))
            temp_ax_pdf = temp_fig_pdf.add_subplot(111)

            # Plot Gumbel Fit Line
            T_plot_min_val = 1.01
            max_T_plot_val = 10000

            if self.log_scale_checkbox.isChecked():
                T_plot_values_pdf = np.logspace(np.log10(T_plot_min_val), np.log10(max_T_plot_val), 400)
            else:
                T_plot_values_pdf = np.linspace(T_plot_min_val, max_T_plot_val, 400)

            V_plot_values_pdf = self.wind_speed_from_params(T_plot_values_pdf)
            valid_plot_indices_pdf = ~np.isnan(V_plot_values_pdf) & ~np.isinf(V_plot_values_pdf)

            if np.any(valid_plot_indices_pdf):
                temp_ax_pdf.plot(T_plot_values_pdf[valid_plot_indices_pdf], V_plot_values_pdf[valid_plot_indices_pdf], label="Gumbel Fit", color='blue', linewidth=1.5)

            # Plot Input Data Points
            if self.input_data_points:
                input_T_pdf = [p['T'] for p in self.input_data_points]
                input_V_pdf = [p['V'] for p in self.input_data_points]
                temp_ax_pdf.scatter(input_T_pdf, input_V_pdf, color='red', zorder=5, label="Input Data", s=35)
                for T_val, V_val in zip(input_T_pdf, input_V_pdf):
                     temp_ax_pdf.text(T_val * 1.02, V_val * 1.02, f' ({T_val:.0f}y, {V_val:.1f}m/s)', fontsize=7, color='black', va='bottom', ha='left')

            # Apply x and y scales BEFORE trying to get limits for dashed lines
            if self.log_scale_checkbox.isChecked():
                temp_ax_pdf.set_xscale("log")
            else:
                temp_ax_pdf.set_xscale("linear")

            # Let Matplotlib auto-scale based on the Gumbel fit and input data first
            temp_ax_pdf.autoscale_view() # This adjusts limits based on plotted data

            # Now get the calculated limits to draw dashed lines appropriately
            plot_ymin, plot_ymax = temp_ax_pdf.get_ylim()
            plot_xmin, plot_xmax = temp_ax_pdf.get_xlim()
            
            # Ensure xmin is positive for log scale if it was auto-scaled too low
            if self.log_scale_checkbox.isChecked() and plot_xmin <= 0:
                plot_xmin = T_plot_min_val # Reset to a safe minimum

            for point in self.queried_points:
                label_text = ""
                point_color = 'gray'

                if point['type'] == 'V_from_T' and not (np.isnan(point['T_in']) or np.isnan(point['V_out'])):
                    T_q, V_q = point['T_in'], point['V_out']
                    label_text = f"Query: T={T_q:.0f}y \u2192 V={V_q:.1f}m/s"
                    point_color = 'green'
                    temp_ax_pdf.plot([T_q, T_q], [plot_ymin, V_q], linestyle='--', color=point_color, alpha=0.7)
                    temp_ax_pdf.plot([plot_xmin, T_q], [V_q, V_q], linestyle='--', color=point_color, alpha=0.7)
                    temp_ax_pdf.scatter([T_q], [V_q], color=point_color, marker='o', s=50, zorder=6, label=label_text)
                    temp_ax_pdf.text(T_q, V_q * 1.02, f' ({T_q:.0f}y, {V_q:.1f}m/s)', fontsize=7, color='black', va='bottom')

                elif point['type'] == 'T_from_V' and not (np.isnan(point['V_in']) or np.isnan(point['T_out'])):
                    V_q, T_q = point['V_in'], point['T_out']
                    label_text = f"Query: V={V_q:.1f}m/s \u2192 T={T_q:.0f}y"
                    point_color = 'purple'
                    temp_ax_pdf.plot([T_q, T_q], [plot_ymin, V_q], linestyle='--', color=point_color, alpha=0.7)
                    temp_ax_pdf.plot([plot_xmin, T_q], [V_q, V_q], linestyle='--', color=point_color, alpha=0.7)
                    temp_ax_pdf.scatter([T_q], [V_q], color=point_color, marker='s', s=50, zorder=6, label=label_text)
                    temp_ax_pdf.text(T_q, V_q * 1.02, f' ({T_q:.0f}y, {V_q:.1f}m/s)', fontsize=7, color='black', va='bottom')

            # Finalize plot appearance (labels, title, grid, legend)
            temp_ax_pdf.set_xlabel("Return Period (years)")
            temp_ax_pdf.set_ylabel("Wind Speed (m/s)")
            temp_ax_pdf.set_title("Gumbel Distribution of Wind Speeds")
            
            # Re-apply x and y scales if needed, though autoscale should handle the type
            if self.log_scale_checkbox.isChecked():
                temp_ax_pdf.set_xscale("log")
            else:
                temp_ax_pdf.set_xscale("linear")
            
            # Set explicit limits again after drawing dashed lines, if needed, or fine-tune padding
            # For log scale, ensure xmin is positive.
            final_xmin, final_xmax = temp_ax_pdf.get_xlim()
            final_ymin, final_ymax = temp_ax_pdf.get_ylim()

            if self.log_scale_checkbox.isChecked():
                if final_xmin <= 0: final_xmin = T_plot_min_val # Ensure positive xmin for log
                # Add some padding for log scale if max is very large
                if final_xmax > 1000: # Example condition
                     temp_ax_pdf.set_xlim(final_xmin, final_xmax * 1.5)
                else:
                     temp_ax_pdf.set_xlim(final_xmin, final_xmax)
            else: # Linear scale padding
                x_range = final_xmax - final_xmin
                if x_range > 0 : temp_ax_pdf.set_xlim(final_xmin - 0.05 * x_range, final_xmax + 0.05 * x_range)


            y_range = final_ymax - final_ymin
            if y_range > 0: temp_ax_pdf.set_ylim(final_ymin - 0.05 * y_range, final_ymax + 0.05 * y_range)
            
            temp_ax_pdf.grid(True, which="both", linestyle="--", linewidth=0.5, color='#AAAAAA')
            
            handles_pdf, labels_pdf = temp_ax_pdf.get_legend_handles_labels()
            if handles_pdf:
                by_label_pdf = dict(zip(labels_pdf, handles_pdf))
                temp_ax_pdf.legend(by_label_pdf.values(), by_label_pdf.keys(), fontsize='x-small', loc='best')

            temp_fig_pdf.tight_layout(pad=1.5)
            temp_fig_pdf.savefig(img_data, format='png', dpi=300)
            img_data.seek(0)
            
            story.append(Image(img_data, width=7*inch, height=5*inch)) 
            story.append(Spacer(1, 0.2 * inch))

            story.append(Paragraph("<b>6. Summary of Points Annotated on Graph</b>", styles['h2']))
            
            summary_text_lines = []
            if self.input_data_points:
                summary_text_lines.append("<b>Input Data Points:</b>")
                for i, point in enumerate(self.input_data_points):
                    summary_text_lines.append(f"- Point {i+1}: Return Period = {point['T']:.1f} years, Wind Speed = {point['V']:.2f} m/s")
            
            if self.queried_points:
                if summary_text_lines: summary_text_lines.append("") # Add a small gap
                summary_text_lines.append("<b>Queried Points:</b>")
                for point in self.queried_points:
                    if point['type'] == 'V_from_T':
                        summary_text_lines.append(f"- Query (T \u2192 V): Input T = {point['T_in']:.1f} years \u2192 Calculated V = {point['V_out']:.2f} m/s")
                    elif point['type'] == 'T_from_V':
                        summary_text_lines.append(f"- Query (V \u2192 T): Input V = {point['V_in']:.1f} m/s \u2192 Calculated T = {point['T_out']:.1f} years")
            
            if not summary_text_lines:
                 summary_text_lines.append("No specific data points or queries were annotated on this graph.")
            
            for line in summary_text_lines:
                story.append(Paragraph(line, styles['Normal']))
                if line.startswith("<b>") and ":" in line : story.append(Spacer(1, 0.05 * inch)) # Small space after subheadings

            doc.build(story)
            self.status_bar.showMessage(f"PDF report saved successfully to {path}", 7000)
        except Exception as e:
            QMessageBox.critical(self, "PDF Export Error", f"Could not generate PDF: {str(e)}")
            self.status_bar.showMessage(f"PDF export failed: {str(e)}", 7000)


    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Project As", "", "Gumbel Project Files (*.gblproj)")
        if not path:
            return

        project_data = {
            "u": self.u,
            "alpha_inv": self.alpha_inv,
            "table_data": [],
            "queried_points": self.queried_points, 
            "log_scale": self.log_scale_checkbox.isChecked()
        }
        for row in range(self.table.rowCount()):
            try:
                T_item = self.table.item(row, 0)
                V_item = self.table.item(row, 1)
                t_val = T_item.text() if T_item else ""
                v_val = V_item.text() if V_item else ""
                project_data["table_data"].append((t_val, v_val))
            except AttributeError: 
                 project_data["table_data"].append(("", ""))


        try:
            with open(path, 'w') as f:
                json.dump(project_data, f, indent=4)
            self.status_bar.showMessage(f"Project saved to {path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save project: {str(e)}")

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "Gumbel Project Files (*.gblproj)")
        if not path:
            return

        try:
            with open(path, 'r') as f:
                project_data = json.load(f)

            self.u = project_data.get("u")
            self.alpha_inv = project_data.get("alpha_inv")
            self.queried_points = project_data.get("queried_points", []) 
            self.log_scale_checkbox.setChecked(project_data.get("log_scale", True))

            table_data = project_data.get("table_data", [])
            self.table.setRowCount(0) 
            if not table_data and (self.u is None): 
                self.table.setRowCount(1)
                self.table.setItem(0,0, QTableWidgetItem(""))
                self.table.setItem(0,1, QTableWidgetItem(""))
            else:
                for r, row_tuple in enumerate(table_data):
                    self.table.insertRow(r)
                    t_val_str = str(row_tuple[0]) if len(row_tuple) > 0 else ""
                    v_val_str = str(row_tuple[1]) if len(row_tuple) > 1 else ""
                    self.table.setItem(r, 0, QTableWidgetItem(t_val_str))
                    self.table.setItem(r, 1, QTableWidgetItem(v_val_str))
            
            # Crucially, after loading table data, re-validate it to populate self.input_data_points
            _, _, self.input_data_points = self.get_table_data()

            if self.u is not None and self.alpha_inv is not None:
                 self.result_label.setText(f"Gumbel Parameters: Location (\u03BC) = {self.u:.3f} m/s, Scale (1/\u03B1) = {self.alpha_inv:.3f} m/s")
            else: # If no u/alpha from project, try to calculate if table data exists
                if self.input_data_points and len(self.input_data_points) >=2:
                    self.calculate_and_plot() # This will set u, alpha_inv and update plot
                else:
                    self.result_label.setText("Gumbel Parameters: Not calculated or not found in project.")
            
            self.update_plot() # Always update plot after loading
            self.update_button_states()
            self.status_bar.showMessage(f"Project loaded from {path}", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Could not load project: {str(e)}")
            self.status_bar.showMessage(f"Failed to load project: {str(e)}", 5000)


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit Application',
                                     "Are you sure you want to exit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GumbelWindApp()
    window.show()
    sys.exit(app.exec())