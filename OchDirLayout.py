import json, datetime, dash
import dash_core_components as dcc
import dash_html_components as html

d = {}
#home = '/home/pi/'
home = ''

try:
    with open('%slayout.json' % home) as f:
        d = json.load(f)
        widthInches = d['Screen Width']
        heightInches = d['Screen Height']
        pixelW = d['Screen Pixel Width']
        pixelH = d['Screen Pixel Height']
        minTextH = d['Min Text Height Inches']
        hasMap = d['Map']
        hasControls = d['Controls']
        hasDirections = d['Directions']
        layout = d['Layout']
        portrait = False
        if pixelH > pixelW:
            portrait = True
        if hasMap:
            with open('%smap.jpg' % home) as mapY:
                print('has map')
except Exception as e:
    with open("%slog.txt" % home, "a") as file:
        currentTime = datetime.datetime.now()
        file.write('%s  %s\n' % (currentTime, e))

