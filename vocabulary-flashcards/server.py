import http.server
import socketserver
import urllib.request
import urllib.parse
import sys
import os

PORT = int(os.environ.get('PORT', 8000))

class ProxyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/proxy'):
            self.handle_proxy()
        else:
            super().do_GET()

    def handle_proxy(self):
        try:
            # Parse query parameters
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            target_url = params.get('url', [None])[0]

            if not target_url:
                self.send_error(400, "Missing 'url' parameter")
                return

            # Fetch the external URL
            # Add User-Agent to avoid being blocked by some sites
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            req = urllib.request.Request(target_url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                content = response.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*') # Allow CORS
                self.end_headers()
                self.wfile.write(content)

        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_error(500, f"Proxy error: {str(e)}")

print(f"Serving at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), ProxyRequestHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
