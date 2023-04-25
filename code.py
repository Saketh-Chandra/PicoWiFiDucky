import socketpool
import wifi
import json
import os
from microcontroller import cpu
import mdns


from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.headers import HTTPHeaders
from adafruit_httpserver.methods import HTTPMethod
from adafruit_httpserver.status import HTTPStatus

from pico_ducky import PicoDucky

picoducky = PicoDucky()

ssid = os.getenv("WIFI_SSID")
password =  os.getenv("WIFI_PASSWORD")
port = os.getenv("PORT",80) 
hostname = os.getenv("HOSTNAME","picowifiducky")

wifi.radio.hostname = hostname
print("Connecting to", ssid)
wifi.radio.connect(ssid, password)
print("Connected to", ssid)


mdns_server = mdns.Server(wifi.radio)
mdns_server.hostname = hostname
mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=port)
print(f"Listening on http://{mdns_server.hostname}:{port}")

print(f"Listening on http://{wifi.radio.hostname}:{port}")

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool,root_path='/static')


@server.route("/")
def base(request):  
    """Default reponse is /index.html"""
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send_file("/static/index.html")
    
@server.route("/test")
def base(request):  
    """Default reponse is /index.html"""
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send_file("/static/index copy.html")

@server.route("/api/data")
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

@server.route("/api/cpu/temperature")
def info_cpu(request):
    """Route for the default."""
    details = {
        "Temperature":cpu.temperature,
        }
    with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
        response.send(json.dumps(details))



@server.route("/static/css/dark.min.css")
def css_file_gz(request):
    headers = HTTPHeaders({'Content-Encoding': 'gzip'})
    
    with HTTPResponse(request, content_type=MIMEType.TYPE_CSS ,headers=headers) as response:
        response.send_file("/static/css/dark.min.css")

# @server.route("/static/manifest.json")
# def static_manifest(request):
#     with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
#         response.send_file("manifest.json")    


# @server.route("/static/js/<file>")
# def static_js(request,file):
#     print(file)
#     with HTTPResponse(request, content_type=MIMEType.TYPE_JS) as response:
#         response.send_file(f"/static/js/{file}") 

# @server.route("/static/images/icons/<file>")
# def static_icon(request,file):
#     print(file)
#     with HTTPResponse(request, content_type=MIMEType.TYPE_PNG) as response:
#         response.send_file(f"/static/images/icons/{file}")

@server.route("/api/run",method = HTTPMethod.POST)
def run_payload(request):
    
    data = json.loads(request.body.decode('utf-8'))
    payload = data.get('payload')
    print(payload)
    if not payload:
        json_data = json.dumps({'message':'payload is missing'})

        with HTTPResponse(request, content_type=MIMEType.TYPE_JSON,status=HTTPStatus(400,"Bad Request")) as response:
            response.send(json_data)
    
    
    # picoducky
    data = {"message": "successfully Executed"}
    json_data = json.dumps(data)
   
    
    with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
        response.send(json_data)
# Never returns
server.serve_forever(str(wifi.radio.ipv4_address),port)