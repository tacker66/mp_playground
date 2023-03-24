
# https://github.com/pfalcon/picoweb

from machine import Pin
import gc
import utime
import network
import camera
import picoweb

config = dict()
def read_config(file):
    fd = open(file)
    for line in fd:
        line = line.strip()
        if len(line) > 0 and line[0] != "#":
            tok = line.split("=")
            config[tok[0].strip()] = tok[1].strip()
read_config("webcam.conf")

ssid = config["ssid"]
pwd  = config["pwd"]

led = Pin(2, Pin.OUT)
led_val = 0
led.value(led_val)
def toggle_led():
    global led_val
    if led_val == 0:
        led_val = 1
    else:
        led_val = 0
    led.value(led_val)
        
acp_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)
acp_if.active(False)
sta_if.active(True)

def wlan_connect(ssid, pwd):
    try:
        if sta_if.isconnected():
            print('disconnecting')
            sta_if.disconnect()
            while sta_if.isconnected():
                print(wlan_status(sta_if.status()))
                utime.sleep_ms(1000)
        if not sta_if.isconnected():
            print('connecting to', ssid)
            sta_if.connect(ssid, pwd)
            while not sta_if.isconnected():
                toggle_led()
                print(wlan_status(sta_if.status()))
                utime.sleep_ms(1000)
    except:
        pass
    print(wlan_status(sta_if.status()), sta_if.ifconfig())

def wlan_stations():
    print("=== available stations ===")
    try:
        for sta in sta_if.scan():
            print(sta)
    except:
        pass
    print("======")

def wlan_status(status):
    if status == network.STAT_IDLE:
        return 'STAT_IDLE'
    elif status == network.STAT_CONNECTING:
        return 'STAT_CONNECTING'
    elif status == network.STAT_WRONG_PASSWORD:
        return 'STAT_WRONG_PASSWORD'
    elif status == network.STAT_NO_AP_FOUND:
        return 'STAT_NO_AP_FOUND'
    elif status == network.STAT_GOT_IP:
        return 'STAT_GOT_IP'
    else:
        return "unknown WLAN status: {}".format(status) 

def camera_init():
    print('init camera')
    camera.deinit()
    camera.init(0, d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
                format=camera.JPEG, framesize=camera.FRAME_CIF, 
                xclk_freq=camera.XCLK_10MHz,
                href=23, vsync=25, reset=-1, pwdn=-1,
                sioc=27, siod=26, xclk=21, pclk=22, fb_location=camera.PSRAM)

    # FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
    # FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
    # FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA
    
    camera.flip(1)                       # Flip up and down window: 0-1
    camera.mirror(1)                     # Flip window left and right: 0-1
    camera.saturation(0)                 # saturation: -2,2 (default 0). -2 grayscale 
    camera.brightness(0)                 # brightness: -2,2 (default 0). 2 brightness
    camera.contrast(0)                   # contrast: -2,2 (default 0). 2 highcontrast
    camera.quality(15)                   # quality: # 10-63 lower number means higher quality
    
    camera.speffect(camera.EFFECT_NONE)  # special effects:
    # EFFECT_NONE (default) EFFECT_NEG EFFECT_BW EFFECT_RED EFFECT_GREEN EFFECT_BLUE EFFECT_RETRO

    camera.whitebalance(camera.WB_NONE)  # white balance
    # WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME

index_web="""
HTTP/1.0 200 OK\r\n
<html>
  <head>
    <title>WebCam</title>
  </head>
  <body>
    <h1>WebCam</h1>
    <img src="/video" margin-top:100px; style="transform:rotate(180deg)"; />
  </body>
</html>
"""

def index(req, resp):
    yield from resp.awrite(index_web)

def send_frame():
    buf = camera.capture()
    yield (b'--frame \r\n Content-Type: image/jpeg \r\n\r\n' + buf + b'\r\n')
    del buf
    gc.collect()
        
def video(req, resp):
    yield from picoweb.start_response(resp, content_type="multipart/x-mixed-replace; boundary=frame")
    while True:
        yield from resp.awrite(next(send_frame()))
        gc.collect()

ROUTES = [
    ("/", index),
    ("/video", video),
]

wlan_stations()
wlan_connect(ssid, pwd)
camera_init()

print('starting webserver ...')
app = picoweb.WebApp(__name__, ROUTES)
led.value(1)
app.run(debug=0, port=80, host="0.0.0.0")
