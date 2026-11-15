import argparse
import os
from faultline.api import App,make_server

p=argparse.ArgumentParser()
p.add_argument('--port',type=int,default=int(os.environ.get('PORT','8765')))
p.add_argument('--experiment',default='demo-web')
a=p.parse_args()
public_origin=os.environ.get('FAULTLINE_PUBLIC_ORIGIN') or None
bind_host=os.environ.get('FAULTLINE_BIND_HOST','127.0.0.1')
server=make_server(App(a.experiment),a.port,public_origin=public_origin,bind_host=bind_host)
print(f'FAULTLINE demo listening on {bind_host}:{server.server_port}; public origin configured: {bool(public_origin)}',flush=True)
try: server.serve_forever()
finally: server.server_close()
