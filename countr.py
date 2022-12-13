'''import json

with open('testData.txt', 'r') as file:
    data = json.loads(file.read())
    print(json.dumps(data))
    total = 0
    nones = 0
    alan = 0
    marel = 0
    chad = 0
    noPjm = 0
    for id in data:
        if data[id]['zip'] is None:
            if data[id]['crew'] is None:
                noPjm += 1
            else:
                if data[id]['crew'][0] == 'AJJ':
                    alan += 1
                if data[id]['crew'][0] == 'MM':
                    marel += 1
                if data[id]['crew'][0] == 'CMT':
                    chad += 1
            nones += 1
        total += 1
    print(nones, 'out of', total)
    print('alan %d' % alan, 'marel %d' % marel, 'chad %d' % chad, 'none %d' % noPjm)'''

#!/usr/bin/python3
import datetime, cgi
print('Content-type:text/html\r\n\r\n')
print('<html><body><div>Hello</div>')
d = cgi.FieldStorage()
print('<h1>%s</h1>' % d['answer'].value)
print('</body></html>')
with open("/var/www/html/crew/log.txt", "a") as file:
    currentTime = datetime.datetime.now()
    file.write('%s\n %s' % (currentTime, d['answer'].value))




