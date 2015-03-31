import psutil, datetime, json, logging
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer


def get_cpu_info():
    return {'percent': psutil.cpu_percent(1)}


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def get_memory_info():
    mem = psutil.virtual_memory()
    available = mem.available
    total = mem.total
    return {'total': bytes2human(total), 'available': bytes2human(available)}


def get_disk_info():
    partitions = psutil.disk_partitions(True)
    devices = {}
    for part in partitions:
        usage = psutil.disk_usage(part.mountpoint)
        devices[part.device] = {
            'total': bytes2human(usage.total),
            'used': bytes2human(usage.used),
            'free': bytes2human(usage.free),
            'percent': usage.percent,
            'type': part.fstype,
            'mountpoint': part.mountpoint
        }
    return devices


def get_boot_time():
    boot = psutil.boot_time()
    return {'boottime': datetime.datetime.fromtimestamp(boot).strftime("%Y-%m-%d %H:%M:%S")}



class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        logging.info(self.command + ' ' + self.path)
        self.send_response(200)
        self.send_header("Content-type", 'text/json')
        #self.send_header("Content-Length", )
        self.end_headers()
        result = {}
        if self.path[1:] == 'CPU':
            result = get_cpu_info()
        elif self.path[1:] == 'MEMORY':
            result = get_memory_info()
        elif self.path[1:] == 'DISK':
            result = get_disk_info()
        elif self.path[1:] == 'BOOT':
            result = get_boot_time()
        logging.info(result)
        result = json.dumps(result)
        self.wfile.write(bytes(result, 'utf-8'))
    def log_message(self, format, *args):
        return

logging.basicConfig(filename='srvmonitor.log', level=logging.DEBUG)

httpd = http.server.HTTPServer(('', 8090), MyHttpRequestHandler)
logging.info('Listening at port 8090')
httpd.serve_forever()
