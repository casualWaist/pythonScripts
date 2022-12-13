import lookUpVox, datetime, traceback

with open('/var/www/html/jobs/byID.txt', 'r') as idFile:
    idD = lookUpVox.json.loads(idFile.read())

initials = {"AJJ": "Alan", "CMT": "Chad", "LB": "Luke", "MH": "Matt", "MM": "Marel"}

def addLineHtmlProd(job, altLine):
    imageURL = job['currentProofUrl']
    rush = ''
    if job['priority'] != 0:
        rnum = job['priority']
        if lookUpVox.jobFinType(job) == 'Shipping':
            rnum += 10
        rush = ' class=rush%d' % rnum
    elif lookUpVox.jobFinType(job) == 'Shipping':
        rush = ' class=rush10'
    if imageURL is None:
        imageURL = '''blank.jpg'''
    else:
        imageURL = imageURL + '''/convert?fit=scale&format=jpg&h=100&rotate=exif&w=100'''
    url = 'href=\"https://app.shopvox.com/app/#/jobs/%s\"' % job['id']
    names = '''<i>%s</i><a%s %s>%s</a>''' % (lookUpVox.folderName(job['name']), rush, url, lookUpVox.formatedName(job['name']))
    line = '''<tr><td class=pic><a href=\"%s\"><img src=%s></a></td><td%s>%s</td><td class=arrows>''' % \
           (job['currentProofUrl'], imageURL, rush, names)
    if altLine:
        line = '''<tr class=altLine><td class=pic><a href=\"%s\"><img src=%s></a></td><td%s>%s</td><td class=arrows>''' % \
               (job['currentProofUrl'], imageURL, rush, names)
    titles = ['Print or Plot', 'FlatBed' 'Print Insert', 'Route Parts',
              'Knife Cut', 'Paint Parts', 'Assemble']
    for title in titles:
        if lookUpVox.hasStep(title, job['steps']):
            statement = lookUpVox.getStepState(job, title)
            line = line + statement
        else:
            line = line + '''<p class=noStep>></p>'''
    pjM = 'Unknown'
    if 'projectManager' in job and 'name' in job['projectManager']:
        pjM = job['projectManager']['name'][:5]
    line = line + '''</td><td class=so><i>%s</i>%s</td><td class=due><i>%s</i><span%s>%s</span></td></tr>''' % (
    pjM, job['orderNumber'], job['createdAt'][5:10], rush, job['dueDate'][5:])
    return line


def htmlSetupProd(list):
    html = '''<!doctype html><html><head><link rel="stylesheet" href="style.css?v=1.1" type="text/css"/>
    <meta http-equiv="refresh" content="120"></head><body><div id=paint>Paint<ul>
    <li id=header><h1>NAME</h1><h2>P/P | FtB | PIn | CNC | CIn |Paint| Asm</h2><h3>Due</h3></li></ul><table>
    '''
    altLine = False
    assList = []
    for job in list:
        if lookUpVox.hasStep('Paint Parts', job['steps']) and lookUpVox.getStep('Paint Parts', job['steps'])['isCompleted'] is False:
            html = html + addLineHtmlProd(job, altLine)
            if altLine:
                altLine = False
            else:
                altLine = True
        else:
            assList.append(job)
    html = html + '''</table></div><div id=ass>Assemble<ul>
    <li id=header><h1>NAME</h1><h2>P/P | FtB | PIn | CNC | CIn |Paint| Asm</h2><h3>Due</h3></li></ul><table>'''
    altLine = False
    for job in assList:
        html = html + addLineHtmlProd(job, altLine)
        if altLine:
            altLine = False
        else:
            altLine = True
    html = html + '''</table></body></html>'''
    return html


try:
    with open('/var/www/html/prod/prodJobs.txt', 'r') as dataFile:
        data = lookUpVox.json.loads(dataFile.read())
    removes = []
    for job in data:
        if not lookUpVox.hasStep('Assemble', job['steps']):
            removes.append(job)
    for job in removes:
        data.remove(job)
    data.sort(key=lambda x: datetime.datetime.strptime(x['dueDate'], '%Y-%m-%d'))
    with open('/var/www/html/prod/index.html', 'w') as file:
        file.write(htmlSetupProd(data))

except Exception as error:
    with open("/var/www/html/prod/log.txt", "a") as file:
        currentTime = datetime.datetime.now()
        file.write('%s  %s\n%s\n' % (currentTime, error, traceback.format_exc()))

def orderDay(day):
    nones = []
    order = []
    times = []
    for trip in day:
        if trip['time'] is None:
            nones.append(trip)
        elif trip['time'] == 'AM':
            order.insert(0, trip)
        elif trip['time'] == 'PM':
            order.append(trip)
        else:
            times.append(trip)
    times.sort(key=lambda x: datetime.datetime.strptime(x['time'], '%I:%M %p'))
    if len(times) > 0:
        time = datetime.datetime.strptime(times[0]['time'], '%I:%M %p')
        while time < datetime.datetime.strptime('12:01 PM', '%I:%M %p'):
            nones.append(times[0])
            del times[0]
            if len(times) > 0:
                time = datetime.datetime.strptime(times[0]['time'], '%I:%M %p')
            else:
                break
    for i in order:
        if i['time'] == 'AM':
            nones.append(i)
    nones = nones + times
    for i in order:
        if i['time'] == 'PM':
            nones.append(i)
    return nones

def todayHTML(day, d):
    htmll = '''<!doctype html><html><head><title>%s</title><link rel="stylesheet" href="style.css?v=1.1" type="text/css"/>
            <meta http-equiv="refresh" content="120"></head><body><table>''' % d
    nones = orderDay(day)
    with open('/var/www/html/jobs/all.txt', 'r') as sv:
        voxJs = lookUpVox.json.loads(sv.read())
    for trip in nones:
        tt = ''
        if trip['time'] is not None:
            tt = trip['time']
        c = '''<td class=colC></td>'''
        if len(trip['crew']) > 0:
            cr = ''
            for p in trip['crew']:
                cr += '%s ' % initials[p]
            c = '''<td class=colN>%s</td>''' % cr
        area = trip['area'][0]
        if len(trip['area']) > 1:
            area = trip['area'][0] + '/' + trip['area'][1]
        line = '''<tr class="hrow"><td class=colA>%s%s<td class=colB>%s</td></td></tr>''' % (area, c, tt)
        for jId in trip['jobs']:
            href = 'href=\"https://app.shopvox.com/app/#/jobs/%s\"' % jId
            rush = ' class=rush%d' % idD[jId]['priority']
            a = '<a %s%s>%s</a>' % (href, rush, idD[jId]['name'])
            qr = lookUpVox.servertudeQR(jId, '/var/www/html/today/')
            img = [x for x in voxJs if x['id'] == jId][0]['currentProofThumbnailUrl']
            h = '''<td class=qr><img src=%s><img src=%s></td>''' % (qr, img)
            indLine = '''<tr><td class=colC><p>%s</p>%s</td>%s</tr>''' % (idD[jId]['folder'], a, h)
            line += indLine
        if 'survey' in trip:
            line += '''<tr><td class=colC><p>%s</p>%s</td></tr>''' % (trip['survey']['time'], trip['survey']['name'])
        htmll += line
    htmll += '''</table><div id="weath">'''
    with open('/var/www/html/today/wtest.html', 'r') as wet:
        htmll += wet.read()
    htmll = htmll + '''</div></body></html>'''
    return htmll

try:
    with open('/var/www/html/cal/dates.txt', 'r') as c:
        cal = lookUpVox.json.loads(c.read())
    html = ''''''
    today = str(datetime.date.today())
    if today in cal:
        html = todayHTML(cal[today], today)
    else:
        html = '''<!doctype html><html><head><link rel="stylesheet" href="style.css" type="text/css"/>
        <meta http-equiv="refresh" content="120"></head><body><table><tr>
        <td class=colA>There's Nothing Scheduled Today</td></tr></table><div id="weath">'''
        with open('/var/www/html/today/wtest.html', 'r') as wet:
            html += wet.read()
        html += '''</div></body></html>'''
    with open('/var/www/html/today/index.html', 'w') as t:
        t.write(html)

except Exception as error:
    with open("/var/www/html/today/log.txt", "a") as file:
        currentTime = datetime.datetime.now()
        file.write('%s  %s\n%s\n' % (currentTime, error, traceback.format_exc()))

def makeDay(nones, d):
    add = ''''''
    for trip in nones:
        tt = ''
        if trip['time'] is not None:
            tt = trip['time']
        v = 0
        if trip['area'] is not None:
            f = d + trip['area'][0]
        else:
            f = d + str(v)
            v += 1
        tr = '''<tr class=show>'''
        c = '''<td class=colC></td>'''
        if len(trip['crew']) > 0:
            cr = ''
            for p in trip['crew']:
                cr += '%s ' % initials[p]
            c = '''<td class=colN>%s</td>''' % cr
        area = trip['area'][0]
        if len(trip['area']) > 1:
            area = trip['area'][0] + '/' + trip['area'][1]
        add += '''%s<td class=colA>%s</td>%s<td class=colD>%s</td></tr>''' % (tr, area, c, tt)
        for jId in trip['jobs']:
            i = '<tr id=%s>' % f
            href = 'href=\"https://app.shopvox.com/app/#/jobs/%s\"' % jId
            rush = ' class=rush%d' % idD[jId]['priority']
            a = '<a %s%s>%s</a>' % (href, rush, idD[jId]['name'])
            indLine = '''%s<td class=colJ><i>%s</i>%s</td></tr>''' % (i, idD[jId]['folder'], a)
            add += indLine
        if 'survey' in trip:
            add += '''<tr><td class=colJ><i>%s</i><a>%s</a></td></tr>''' % (trip['survey']['time'], trip['survey']['name'])
    return add

def calHTML(week, calD, limb):
    htmll = '''<!doctype html><html><head><title>Calendar</title><link rel="stylesheet" href="style.css?v=1.1" type="text/css"/>
                <meta http-equiv="refresh" content="120"></head><body><div id=week>'''
    for day in week:
        d = day.strftime('%Y-%m-%d')
        o = 'd' + str(week.index(day))
        line = '''<div id=%s><table>''' % o
        line += '''<th>%s - %s</th>''' % (day.strftime('%A'), d[5:])
        if d in calD:
            nones = orderDay(calD[d])
            line += makeDay(nones, d)
            htmll += line
        else:
            line += '''<tr><td class=colA>Nothing Scheduled</td></tr>'''
            htmll += line
        htmll += '''</table></div>'''
    htmll += '''</div><div id=upcoming><table id=uDays><tr class=dayRow>'''
    fives = 0
    alt = False
    upcoming = []
    for day in calD:
        if day > week[4].strftime('%Y-%m-%d'):
            upcoming.append(day)
    upcoming.sort()
    for day in upcoming:
        if fives > 4:
            htmll += '''</tr><tr class=dayRow>'''
            fives = 0
        if alt:
            line = '''<td class=upAlt>%s<table>''' % day[5:]
            alt = False
        else:
            line = '''<td class=upDay>%s<table>''' % day[5:]
            alt = True
        nones = orderDay(calD[day])
        line += makeDay(nones, day)
        htmll += line + '''</table></td>'''
        fives += 1
    htmll += '''</tr></table></div><div id=limbo><table>'''
    yestDay = week[0] - datetime.timedelta(days=1)
    limbos = []
    for job in limb:
        if job['id'] in idD:
            limbos.append(job['id'])
    for job in limbos:
        i = '''<i>%s</i>''' % idD[job]['folder']
        href = 'href=\"https://app.shopvox.com/app/#/jobs/%s\"' % job
        a = '<a %s>%s</a>' % (href, idD[job]['name'])
        line = '''<tr><td class=colL>%s%s</td></tr>''' % (i, a)
        htmll += line
    htmll += '''</table></div></body></html>'''
    return htmll

try:
    with open('/var/www/html/cal/dates.txt', 'r') as c:
        cal = lookUpVox.json.loads(c.read())
    html = ''''''
    w = 1
    week = []
    x = 0
    while w <= 5:
        day = datetime.datetime.today() + datetime.timedelta(days=w + x)
        if day.strftime('%A') == 'Saturday':
            x = 2
            day = datetime.datetime.today() + datetime.timedelta(days=w + x)
        elif day.strftime('%A') == 'Sunday':
            x = 1
            day = datetime.datetime.today() + datetime.timedelta(days=w + x)
        week.append(day)
        w += 1
    with open('/var/www/html/cal/limboJobs.txt', 'r') as lFile:
        limb = lookUpVox.json.loads(lFile.read())
    html = calHTML(week, cal, limb)
    with open('/var/www/html/cal/index.html', 'w') as t:
        t.write(html)

except Exception as error:
    with open("/var/www/html/cal/log.txt", "a") as file:
        currentTime = datetime.datetime.now()
        file.write('%s  %s\n%s\n' % (currentTime, error, traceback.format_exc()))

def qFormr(job, jId, action):
    if action is None:
        tmi = ''
        if job['type'] == 'TBD':
            tmi = job['name'] + 'is in limbo and has no Finish Type'
        elif job['type'] == 'Shipping':
            tmi = job['name'] + ' is ready to Ship'
        elif job['type'] == 'Delivery' or job['type'] == 'Installation':
            strip = ' is ready to be installed. Going to '
            if job['type'] == 'Delivery':
                strip = ' is ready to be delivered. Going to '
            tmi = job['name'] + strip + job['area'][0]
        else:
            tmi = job['name'] + ' is ready to be picked up'
        return tmi

def frontHTLM(invs, ableJobs, limboJobs, allJobs):
    html = '''<!doctype html><html><head><title>Front</title><link rel="stylesheet" href="style.css?v=1.1" type="text/css"/>
                <meta http-equiv="refresh" content="120"><script>
                function startTime() {
                  var today = new Date();
                  var h = today.getHours();
                  if (h > 12) {h = h - 12;}
                  var m = today.getMinutes();
                  m = checkTime(m);
                  document.getElementById('txt').innerHTML =
                  h + ":" + m;
                  var t = setTimeout(startTime, 60000);
                }
                function checkTime(i) {
                  if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
                  return i;
                }</script></head><body onload="startTime()"><div id=rti><table>'''
    for inv in invs:
        if inv[0] in idD:
            job = idD[inv[0]]
            a = '''<i>%s</i><a href=\"https://app.shopvox.com/app/#/jobs/%s\">%s</a>''' % (job['folder'], inv[0], job['name'])
            s = '''<a href=\"https://app.shopvox.com/app/#/pos/work_orders/%s\">%s</a>''' % (job['soinv'], job['soNum'])
        else:
            job = None
            for opt in allJobs:
                if opt['id'] == inv[0]:
                    job = opt
                    break
            if job is None:
                job = lookUpVox.getSOwNum(inv[1])
            fold = lookUpVox.folderName(job['title'])
            name = lookUpVox.formatedName(job['title'])
            a = '''<i>%s</i><a href=\"https://app.shopvox.com/app/#/jobs/%s\">%s</a>''' % (fold, inv[0], name)
            s = '''<a href=\"https://app.shopvox.com/app/#/pos/work_orders/%s\">%s</a>''' % (job['id'], job['txnNumber'])
        line = '''<tr><td class=colI>%s</td><td class=colS>%s</td></tr>''' % (a, s)
        html += line
    html += '''</table></div><div id=pickup><table><tr>'''
    count = 0
    for job in ableJobs:
        if count > 6:
            html += '''</tr><tr>'''
            count = 0
        if lookUpVox.jobFinType(job) == 'Pick-Up':
            a = '''<a href=\"https://app.shopvox.com/app/#/jobs/%s\">%s</a>''' % (job['id'], idD[job['id']]['name'])
            qr = lookUpVox.servertudeQR(job['id'], '/var/www/html/front/')
            line = '''<td><img src=%s>%s</td>''' % (qr, a)
            count += 1
            html += line
    html += '''</tr></table></div><div id=note><table>'''
    # add notifications *******
    td = datetime.datetime.today()
    altLine = False
    b = [0, 0, 0, 0, 0]
    for job in idD:
        b[0] += 1
        if idD[job]['crew'] is not None:
            if idD[job]['crew'][0] == 'AJJ':
                b[1] += 1
            if idD[job]['crew'][0] == 'MM':
                b[2] += 1
            if idD[job]['crew'][0] == 'CMT':
                b[3] += 1
    for job in allJobs:
        if job['id'] in idD:
            if job['companyId'] == '9dfa229f-d7b8-44cf-aad9-407a894f1b99':
                b[4] += 1
    b[4] = str((b[4]/b[0]) * 100)[:4]
    d = ['Number of jobs in house', 'Number of jobs from Alan', 'Number of jobs from Marel',
         'Number of jobs from Chad', 'Percent of jobs ordered by Ochsner']
    f = 0
    while f < 5:
        cl = 'class=noteR'
        if altLine:
            cl = 'class=note'
            altLine = False
        else:
            altLine = True
        html += '''<tr><td %s>%s <p>%s</p></td></tr>''' % (cl, d[f], b[f])
        f += 1
    for job in limboJobs:
        if idD[job['id']]['ask'] == datetime.datetime.strftime(td, '%Y-%m-%d'):
            m = qFormr(idD[job['id']], job['id'], None)
            cl = 'class=noteR'
            if altLine:
                cl = 'class=note'
                altLine = False
            else:
                altLine = True
            html += '''<tr><td %s>%s</td></tr>''' % (cl, m)
    for job in allJobs:
        date = datetime.datetime.strptime(job['createdAt'][:10], '%Y-%m-%d')
        if td > date + datetime.timedelta(days=30):
            cl = 'class=noteR'
            if altLine:
                cl = 'class=note'
                altLine = False
            else:
                altLine = True
            delta = td - date
            html += '''<tr><td %s>%s has been in house for <p>%s</p> days</td></tr>''' % (cl, idD[job['id']]['name'], delta.days )
    x = int(td.strftime('%d'))
    if 4 <= x <= 20 or 24 <= x <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][x % 10 - 1]
    d = '''<h1>%s</h1><h2>%s%s</h2>''' % (td.strftime('%A'), td.strftime('%B %d'), suffix)
    html += '''</tr></table></div><div id="infoB"><div id="txt"></div>%s</div></body></html>''' % d
    return html

try:
    with open('/var/www/html/front/invList.txt', 'r') as iv:
        invs = lookUpVox.json.loads(iv.read())
    with open('/var/www/html/cal/schedJobs.txt', 'r') as sc:
        ableJobs = lookUpVox.json.loads(sc.read())
    with open('/var/www/html/cal/limboJobs.txt', 'r') as lb:
        limboJobs = lookUpVox.json.loads(lb.read())
    with open('/var/www/html/jobs/all.txt', 'r') as aj:
        allJobs = lookUpVox.json.loads(aj.read())
    with open('/var/www/html/front/index.html', 'w') as fr:
        fr.write(frontHTLM(invs, ableJobs, limboJobs, allJobs))


except Exception as error:
    with open("/var/www/html/front/log.txt", "a") as file:
        currentTime = datetime.datetime.now()
        file.write('%s  %s\n%s\n' % (currentTime, error, traceback.format_exc()))
