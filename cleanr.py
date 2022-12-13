import os, json
from datetime import datetime, timedelta

for qr in os.listdir('/var/www/html/front/QRs'):
    os.remove('/var/www/html/front/QRs/%s' % qr)

for qr in os.listdir('/var/www/html/today/QRs'):
    os.remove('/var/www/html/today/QRs/%s' % qr)

with open('/var/www/html/cal/dates.txt', 'r+') as clFile:
    calData = json.loads(clFile.read())
    rdate = []
    for date in calData:
        removes = []
        for trip in calData[date]:
            if len(trip['jobs']) == 0:
                if 'survey' not in trip:
                    removes.append(trip)
                elif datetime.strptime(date, '%Y-%m-%d') < datetime.today() + timedelta(days=1):
                    removes.append(trip)
        for trip in removes:
            calData[date].remove(trip)
        if len(calData[date]) == 0 and date not in rdate:
            rdate.append(date)
        if datetime.strptime(date, '%Y-%m-%d') < datetime.today() + timedelta(days=1) and date not in rdate:
            rdate.append(date)
    for date in rdate:
        calData.pop(date)

with open('/var/www/html/cal/dates.txt', 'w+') as cFile:
    cFile.write(json.dumps(calData))
