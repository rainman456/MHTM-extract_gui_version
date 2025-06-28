import os
import re
import requests
from email import policy
from email.parser import BytesParser
import uuid
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

class MHTMLParser:
    def __init__(self, input_file, fetch_external=False):
        self.input_file = input_file
        self.resources = []
        self.html_content = None
        self.fetch_external = fetch_external  # Option to fetch external resources

    def parse(self):
        """Parse the MHTML file and extract embedded, inline, and external resources."""
        if not os.path.isfile(self.input_file):
            raise FileNotFoundError(f"Input file {self.input_file} does not exist.")

        try:
            with open(self.input_file, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)

            self.resources = []
            self.html_content = None

            for part in msg.walk():
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                filename = part.get_filename()
                if not filename:
                    extension = self._get_extension(content_type)
                    filename = f"resource_{uuid.uuid4().hex[:8]}{extension}"

                try:
                    size = len(payload)
                    if content_type.startswith("text/html"):
                        self.html_content = payload.decode('utf-8', errors='ignore')
                        # Add HTML as an extractable resource
                        self.resources.append({
                            "type": content_type,
                            "filename": f"page_{uuid.uuid4().hex[:8]}.html",
                            "data": payload,
                            "size": size,
                            "source": "embedded"
                        })
                    else:
                        self.resources.append({
                            "type": content_type,
                            "filename": filename,
                            "data": payload,
                            "size": size,
                            "source": "embedded"
                        })
                except Exception as e:
                    print(f"Error processing part {filename}: {str(e)}")

            # Extract inline JavaScript and external scripts
            if self.html_content:
                if BS4_AVAILABLE:
                    inline_scripts = self._parse_inline_scripts(self.html_content)
                    self.resources.extend(inline_scripts)
                else:
                    print("Warning: BeautifulSoup not installed, skipping inline JavaScript extraction")
                if self.fetch_external:
                    external_scripts = self._parse_external_scripts(self.html_content)
                    self.resources.extend(external_scripts)

            return self.html_content, self.resources

        except Exception as e:
            raise ValueError(f"Failed to parse MHTML file: {str(e)}")

    def _get_extension(self, content_type):
        """Map content types to file extensions."""
        extension_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif",
            "text/css": ".css",
            "text/javascript": ".js",
            "application/javascript": ".js",
            "application/json": ".json",
            "font/ttf": ".ttf",
            "font/otf": ".otf",
            "font/woff": ".woff",
            "font/woff2": ".woff2",
            "text/plain": ".txt",
            "text/html": ".html"
        }
        return extension_map.get(content_type, ".bin")

    def _parse_inline_scripts(self, html_content):
        """Extract inline JavaScript from <script> tags without src attribute."""
        resources = []
        if not BS4_AVAILABLE:
            return resources

        soup = BeautifulSoup(html_content, 'html.parser')
        scripts = soup.find_all('script')
        for i, script in enumerate(scripts):
            if not script.get('src'):  # Inline script (no src attribute)
                content = script.string
                if content and content.strip():
                    content_bytes = content.encode('utf-8', errors='ignore')
                    filename = f"inline_script_{uuid.uuid4().hex[:8]}.js"
                    resources.append({
                        "type": "text/javascript",
                        "filename": filename,
                        "data": content_bytes,
                        "size": len(content_bytes),
                        "source": "inline"
                    })
        return resources

    def _parse_external_scripts(self, html_content):
        """Parse HTML for external <script src='...'> tags and download them."""
        resources = []
        script_pattern = re.compile(r'<script\s+[^>]*src=["\'](.*?)["\'][^>]*>', re.IGNORECASE)
        matches = script_pattern.findall(html_content)

        for url in matches:
            if url.startswith('http://') or url.startswith('https://'):
                try:
                    response = requests.get(url, timeout=5)
                    response.raise_for_status()
                    content = response.content
                    filename = os.path.basename(url.split('?')[0]) or f"script_{uuid.uuid4().hex[:8]}.js"
                    resources.append({
                        "type": "text/javascript",
                        "filename": filename,
                        "data": content,
                        "size": len(content),
                        "source": "external"
                    })
                    print(f"Downloaded external script: {url}")
                except Exception as e:
                    print(f"Failed to download {url}: {str(e)}")
        return resources

    def extract_resources(self, output_dir, selected_indices=None):
        """Extract selected or all resources to the output directory."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        extracted = []
        try:
            for i, res in enumerate(self.resources):
                if selected_indices is None or i in selected_indices:
                    output_path = os.path.join(output_dir, res["filename"])
                    base, ext = os.path.splitext(output_path)
                    counter = 1
                    while os.path.exists(output_path):
                        output_path = f"{base}_{counter}{ext}"
                        counter += 1

                    with open(output_path, 'wb') as f:
                        f.write(res["data"])
                    extracted.append(output_path)
            return extracted
        except Exception as e:
            raise ValueError(f"Extraction failed: {str(e)}")

    def get_html_content(self):
        """Return the HTML content of the MHTML file."""
        return self.html_content