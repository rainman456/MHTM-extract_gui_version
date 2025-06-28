# MHTML File Extractor

## Overview

The MHTML File Extractor is a desktop application built with **PyQt5** that allows users to extract embedded resources from MHTML (MIME HTML) files. It provides a user-friendly GUI to browse MHTML files, preview their HTML content, and extract resources such as HTML, images (JPEG, PNG, WebP, GIF), CSS, JavaScript (embedded, inline, and external), fonts (TTF, OTF, WOFF, WOFF2), and other file types to a directory named after the MHTML file.

### Features
- **Browse and Load MHTML Files**: Select `.mhtml` or `.mht` files via a file dialog.
- **Preview HTML Content**: View HTML in a rendered format (using `QWebEngineView`) or raw source.
- **Resource Table**: Displays all extractable resources with details (type, filename, size, source: embedded/inline/external).
- **Selective Extraction**: Choose specific resources to extract using checkboxes.
- **Automatic Output Directory**: Extracts files to a folder named after the MHTML file in the same directory (e.g., `example.mhtml` → `example/` folder).
- **External Script Fetching**: Downloads external JavaScript files referenced in `<script src="...">` tags.
- **Inline JavaScript Extraction**: Extracts JavaScript code within `<script>` tags without `src` attributes.
- **CORS Handling**: Bypasses CORS restrictions for HTML preview in `QWebEngineView`.

## Installation

### Prerequisites
- Python 3.6+
- Required Python packages:
  ```bash
  pip install PyQt5 PyQtWebEngine requests beautifulsoup4
  ```
  - `PyQtWebEngine` is optional for HTML preview (falls back to text view if not installed).
  - `beautifulsoup4` is required for inline JavaScript extraction.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mhtml-extractor.git
   cd mhtml-extractor
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure the following files are in the project directory:
   - `mhtml_extractor_gui.py`: The main GUI application.
   - `mhtml_parser.py`: The MHTML parsing module.

## Usage
1. Run the application:
   ```bash
   python mhtml_extractor_gui.py
   ```
2. **Select an MHTML File**:
   - Click the "Browse" button to choose an `.mhtml` or `.mht` file.
   - The output directory is automatically set to a folder named after the MHTML file (e.g., `example.mhtml` → `./example/`).
3. **Preview Content**:
   - View the HTML content in the "HTML View" tab (rendered) or "Raw Source" tab (plain text).
4. **Select Resources**:
   - The resource table lists all extractable files (HTML, images, CSS, JavaScript, fonts) with their type, filename, size, and source (embedded, inline, or external).
   - Check/uncheck resources to select which to extract.
   - Use the "Select All" button to toggle selection.
5. **Extract Files**:
   - Click "Extract Selected" to save selected resources to the output directory.
   - The status bar displays the extraction status and output directory.

## Project Structure
- `mhtml_extractor_gui.py`: Implements the PyQt5 GUI with file selection, preview tabs, resource table, and extraction controls.
- `mhtml_parser.py`: Handles MHTML parsing, extracting embedded resources, inline JavaScript, and optionally downloading external scripts.
- `README.md`: This file, providing project documentation.
- `requirements.txt`: Lists required Python packages.

## Demonstration
Below is a GIF showcasing the MHTML File Extractor in action, demonstrating file selection, resource preview, and extraction.

![MHTML Extractor Demo](demo.gif)

*Note*: To create your own demo GIF, use a screen recording tool (e.g., OBS Studio, ScreenToGif) to capture the application workflow:
1. Record selecting an MHTML file.
2. Show the resource table populating with HTML, JavaScript, fonts, CSS, and images.
3. Demonstrate selecting resources and extracting them.
4. Save the recording as `demo.gif` in the repository root and update the path in this README.

## Contributing
Contributions are welcome! Please submit issues or pull requests to the GitHub repository. Ensure code follows PEP 8 and includes tests for new features.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.