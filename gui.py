import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QLineEdit, QTabWidget, QPlainTextEdit,
    QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView, QAbstractItemView, QStatusBar
)
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
from PyQt5.QtCore import Qt
from mhtm_parser3 import MHTMLParser

class MHTMLExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MHTML File Extractor")
        self.setGeometry(100, 100, 800, 600)
        self.selected_file = ""
        self.output_dir = ""  
        self.parser = None
        self.resources = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # File Selection Row
        file_layout = QHBoxLayout()
        self.browse_button = QPushButton("📂 Browse")
        self.browse_button.clicked.connect(self.browse_file)
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        file_layout.addWidget(QLabel("MHTML File:"))
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)

        # Tabs for Preview
        self.tabs = QTabWidget()
        if WEBENGINE_AVAILABLE:
            self.html_view = QWebEngineView()
            # Disable CORS restrictions
            settings = self.html_view.settings()
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            self.tabs.addTab(self.html_view, "🌐 HTML View")
        else:
            self.html_view = QPlainTextEdit("QWebEngineView not available")
            self.html_view.setReadOnly(True)
            self.tabs.addTab(self.html_view, "🌐 HTML View (Disabled)")
        self.raw_view = QPlainTextEdit()
        self.raw_view.setReadOnly(True)
        self.tabs.addTab(self.raw_view, "📄 Raw Source")
        layout.addWidget(self.tabs)

        # Resources Table
        layout.addWidget(QLabel("📦 Embedded and External Resources"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Select", "Type", "File Name", "Size", "Source"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.select_all_button = QPushButton("✓ Select All")
        self.select_all_button.clicked.connect(self.select_all_resources)
        self.extract_button = QPushButton("⬇️ Extract Selected")
        self.extract_button.clicked.connect(self.extract_selected)
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.extract_button)
        layout.addLayout(button_layout)

        # Status Bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open MHTML File", "", "MHTML Files (*.mhtml *.mht)")
        if file_name:
            self.selected_file = file_name
            self.file_path.setText(file_name)
            # Set output directory to a folder named after the MHTML file (without extension)
            base_name = os.path.splitext(os.path.basename(file_name))[0]
            self.output_dir = os.path.join(os.path.dirname(file_name), base_name)
            self.status_bar.showMessage(f"Loaded: {file_name} (Output directory: {self.output_dir})")
            try:
                self.load_mhtml(file_name)
            except Exception as e:
                self.status_bar.showMessage(f"Error loading file: {str(e)}")

    def load_mhtml(self, file_path):
        # Check if MHTMLParser supports fetch_external
        try:
            self.parser = MHTMLParser(file_path, fetch_external=True)
        except TypeError:
            self.parser = MHTMLParser(file_path)
            self.status_bar.showMessage("Warning: External script fetching not supported in this parser version")
        
        try:
            html_content, self.resources = self.parser.parse()
            self.table.setRowCount(0)

            if html_content:
                self.raw_view.setPlainText(html_content)
                if WEBENGINE_AVAILABLE:
                    self.html_view.setHtml(html_content)
                else:
                    self.html_view.setPlainText(html_content)

            # Populate table
            self.table.setRowCount(len(self.resources))
            for i, res in enumerate(self.resources):
                checkbox = QTableWidgetItem()
                checkbox.setCheckState(Qt.Checked)
                self.table.setItem(i, 0, checkbox)
                self.table.setItem(i, 1, QTableWidgetItem(res["type"]))
                self.table.setItem(i, 2, QTableWidgetItem(res["filename"]))
                self.table.setItem(i, 3, QTableWidgetItem(f"{res['size'] / 1024:.2f} KB"))
                source = res.get("source", "embedded")
                self.table.setItem(i, 4, QTableWidgetItem(source))

        except Exception as e:
            self.status_bar.showMessage(f"Error parsing MHTML: {str(e)}")
            raise

    def select_all_resources(self):
        if self.table.rowCount() == 0:
            return
        state = Qt.Checked if self.table.item(0, 0).checkState() == Qt.Unchecked else Qt.Unchecked
        for row in range(self.table.rowCount()):
            self.table.item(row, 0).setCheckState(state)
        self.status_bar.showMessage("All resources selected" if state == Qt.Checked else "All resources deselected")

    def extract_selected(self):
        if not self.selected_file:
            self.status_bar.showMessage("No MHTML file selected")
            return
        if not self.output_dir:
            self.status_bar.showMessage("No output directory set")
            return
        if not self.parser:
            self.status_bar.showMessage("No MHTML file loaded")
            return

        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        selected_indices = [row for row in range(self.table.rowCount()) if self.table.item(row, 0).checkState() == Qt.Checked]
        try:
            extracted_files = self.parser.extract_resources(self.output_dir, selected_indices)
            self.status_bar.showMessage(f"Extracted {len(extracted_files)} resource(s) to {self.output_dir}")
        except Exception as e:
            self.status_bar.showMessage(f"Extraction failed: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MHTMLExtractor()
    window.show()
    sys.exit(app.exec_())