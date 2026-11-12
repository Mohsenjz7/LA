#!/usr/bin/env python3
"""Run the local course. No dependencies outside Python's standard library."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse, webbrowser, threading

def main():
    p=argparse.ArgumentParser(description='Local linear algebra course')
    p.add_argument('--port',type=int,default=8000)
    p.add_argument('--no-browser',action='store_true')
    args=p.parse_args()
    root=Path(__file__).resolve().parent
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*a,**kw):super().__init__(*a,directory=str(root),**kw)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    url=f'http://localhost:{args.port}/'
    print(f'Open {url} — Ctrl+C to stop.',flush=True)
    if not args.no_browser:threading.Timer(.5,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:print('\nStopped.')
    finally:server.server_close()
if __name__=='__main__':main()
