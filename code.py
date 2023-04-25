import socketpool
import wifi
import json
import os
from microcontroller import cpu
import mdns


from adafruit_httpserver.server import HTTPServer
#from adafruit_httpserver.response import HTTPResponse
from _response import BuxFixHTTPResponse as HTTPResponse
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.headers import HTTPHeaders
from adafruit_httpserver.methods import HTTPMethod


ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password =  os.getenv("CIRCUITPY_WEB_API_PASSWORD")
port = os.getenv("PORT",80) 
hostname = os.getenv("HOSTNAME","picowifiducky")

wifi.radio.hostname = hostname
print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)


#mdns_server = mdns.Server(wifi.radio)
#mdns_server.hostname = hostname
#mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=port)

#print(f"Listening on http://{mdns_server.hostname}:{port}")

print(f"Listening on http://{wifi.radio.hostname}:{port}")

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)


@server.route("/")
def base(request):  
    """Default reponse is /index.html"""
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send_file("index.html")
    

@server.route("/data")
def info(request):
    """Route for the default."""
    details = {
        "Machine": os.uname().machine,
        "Release": f"CircuitPython {os.uname().release}",
        "Platform": os.uname().sysname,
        "MAC Address": ":".join([(hex(i)[2:]).upper() for i in wifi.radio.mac_address]),
        "Host Name": wifi.radio.hostname,
        "Temperature":cpu.temperature,
        }
    
    with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
        response.send(json.dumps(details))

@server.route("/cpu")
def info_cpu(request):
    """Route for the default."""
    details = {
        "Temperature":cpu.temperature,
        }
    
    with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
        response.send(json.dumps(details))

@server.route("/dark.min.css.gz")
def css_file_gz(request):
    
    headers = HTTPHeaders({'Content-Encoding': 'gzip'})
    with HTTPResponse(request, content_type=MIMEType.TYPE_CSS ,headers=headers) as response:
        response.send_file("/dark.min.css.gz")
    
@server.route("/dark.css")
def css_file(request):
    headers = HTTPHeaders({'Content-Encoding': 'gzip'})
    with HTTPResponse(request, content_type=MIMEType.TYPE_CSS ,headers=headers) as response:
        response.send_file("/dark.min.css.gz")

@server.route("/api/run",method = HTTPMethod.POST)
def run_payload(request):
    #data = json.loads(str(request.body))
    
    print(request.body, type(request.body))
    data = json.loads(request.body.decode('utf-8'))
    print(data.get('payload'), type(data))
    
    #json_data = json.dumps(data)
    json_data = json.dumps({'ok':'ok'})
    
    with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
        response.send(json_data)
# Never returns
server.serve_forever(str(wifi.radio.ipv4_address),port)