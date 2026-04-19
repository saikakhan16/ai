"""
Simple HTTP Server for FD Portfolio Optimizer Frontend
Serves static files from the current directory
"""

import http.server
import socketserver
import os
from pathlib import Path

# Configuration
PORT = 3000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def do_GET(self):
        # Serve index.html for root path
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS headers to allow API calls from different port
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def run_server():
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 70)
        print("  🎉 FD Portfolio Optimizer - Frontend Server")
        print("=" * 70)
        print(f"\n✅ Server running on: http://localhost:{PORT}")
        print(f"✅ Open in browser: http://localhost:{PORT}")
        print(f"\n📌 Backend API: http://localhost:8000")
        print(f"📌 Make sure backend is running: python api_new.py")
        print(f"\nPress CTRL+C to stop server\n")
        print("=" * 70 + "\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")

if __name__ == "__main__":
    run_server()
