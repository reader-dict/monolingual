#!/usr/bin/env python3
import http.server
import socketserver
import mimetypes
import os

PORT = 8000

class GzipStaticHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # If the requested file ends with .gz, add Content-Encoding
        if self.path.endswith(".gz"):
            self.send_header("Content-Encoding", "gzip")

            # Try to infer the original MIME type (e.g., .js.gz -> .js)
            base, _ = os.path.splitext(self.path)
            mime, _ = mimetypes.guess_type(base)
            if mime:
                self.send_header("Content-Type", mime)

        super().end_headers()


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), GzipStaticHandler) as httpd:
        print(f"Serving HTTP on port {PORT} (http://localhost:{PORT}/)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.server_close()
