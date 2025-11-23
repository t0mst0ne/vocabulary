from flask import Flask, request, send_from_directory, Response
import requests
import os

app = Flask(__name__, static_folder=None)

@app.route('/')
def root():
    return send_from_directory('.', 'index.html')

@app.route('/data/<path:path>')
def serve_data(path):
    return send_from_directory('data', path)

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Missing url", 400
    
    try:
        # Add User-Agent to avoid being blocked
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(url, headers=headers)
        
        # Exclude some headers that might cause issues
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        response = Response(resp.content, resp.status_code, headers)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"Proxy error: {e}")
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
