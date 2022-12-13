#!/usr/bin/python3
import cgi, lookUpVox, datetime, traceback, sys

r = cgi.FieldStorage()
html = 'Content-type: text/html\r\n\r\n'

def openIds():
    with open('/var/www/html/jobs/byID.txt', 'r') as idFile:
        return lookUpVox.json.loads(idFile.read())
def openCal():
    with open('/var/www/html/cal/dates.txt', 'r') as clFile:
        return lookUpVox.json.loads(clFile.read())
def openArea():
    with open('/var/www/html/zips/areaData.txt', 'r') as arFile:
        return lookUpVox.json.loads(arFile.read())
def openZip():
    with open('/var/www/html/zips/zipCodeData.txt', 'r') as zpFile:
        return lookUpVox.json.loads(zpFile.read())
def openQuer():
    with open('/var/www/html/crew/queryList.txt', 'r') as quFile:
        return lookUpVox.json.loads(quFile.read())
def openInv():
    with open('/var/www/html/front/invList.txt', 'r') as inFile:
        return lookUpVox.json.loads(inFile.read())
def openSVJs():
    with open('/var/www/html/jobs/all.txt', 'r') as allFile:
        return lookUpVox.json.loads(allFile.read())

def saveIds(data):
    with open('/var/www/html/jobs/byID.txt', 'w') as idsFile:
        idsFile.write(lookUpVox.json.dumps(data))
def saveCal(data):
    with open('/var/www/html/cal/dates.txt', 'w') as clsFile:
        clsFile.write(lookUpVox.json.dumps(data))
def saveQuer(data):
    with open('/var/www/html/crew/queryList.txt', 'w') as qusFile:
        qusFile.write(lookUpVox.json.dumps(data))

def makeButts(butts, div):
    htmlButts = ''''''
    oclk = '''onclick="sRpy(this, '%s')"''' % div
    for butt in butts:
        htmlButts += '''<button name="%s" %s data-jId="%s">%s''' % (butt, oclk, div, butt)
    return htmlButts

def makeForm(butts, div, this):
    names = [b['name'] for b in butts if b['type'] != 'button']
    form = ''''''
    for butt in butts:
        if butt['type'] == 'radio':
            label = '''<label for="%s">%s</label>''' % (butt['name'], butt['name'])
            form += '''<input name="%s" type="%s" class="%s" id="%s">%s'''\
                    % (butt['group'], butt['type'], butt['class'], butt['name'], label)
        elif butt['type'] == 'button':
            form += '''<button name="%s" id="%s" onclick="sDpy(this, %s, '%s')">%s'''\
                    % (butt['name'], this, names, div, butt['name'])
        else:
            form += '''<input id="%s" type="%s" class="%s">''' % (butt['name'], butt['type'], butt['class'])
    return form

def finSVStep(jId, aajob, step):
    jobs = openSVJs()
    svJob = next(j for j in jobs if j['id'] == jId)
    sch = lookUpVox.getStep(step, svJob['steps'])
    if sch['isCompleted'] is not True:
        try:
            lookUpVox.completeStep(svJob['id'], sch['id'])
            return '''%s %s step has been completed in ShopVox''' % (aajob['name'], step)
        except Exception as err:
            return '''<h1>ShopVox complete failed because</h1><p>%s</p>''' % err
    else:
        return '''%s %s step is already complete in ShopVox''' % (aajob['name'], step)

def processResponce(act, div, user):
    crew = {"alan": "AJJ", "Alan": "AJJ",
            "chad": "CMT", "Chad": "CMT",
            "luke": "LB", "Luke": "LB",
            "matt": "MH", "Matt": "MH",
            "marel": "MM", "Marel": "MM",
            "shelby": "SE", "Shelby": "SE"}
    jId = div[div.index(':') + 1:]
    task = div[:div.index(':')]
    if task == 'Area':
        jobs = openIds()
        jobs[jId]['area'] = [act]
        saveIds(jobs)
        return '''%s is now in %s''' % (jobs[jId]['name'], act)
    elif task == 'CrewSet':
        cal = openCal()
        jobs = openIds()
        for date in cal:
            for trip in cal[date]:
                if jId in trip['jobs']:
                    trip['crew'].append(crew[act])
                    break
        saveCal(cal)
        return '''%s is scheduled to handle %s''' % (act, jobs[jId]['name'])
    elif task == 'Inst':
        if isinstance(act, list):
            if act[0] == 'instDate':
                cal = openCal()
                jobs = openIds()
                time = None
                if len(act) is 4:
                    time = datetime.datetime.strftime(datetime.datetime.strptime(act[3], '%H:%M'), '%I:%M %p')
                if act[2] in cal:
                    t = None
                    for trip in cal[act[2]]:
                        for a in jobs[jId]['area']:
                            if a in trip['area']:
                                t = trip
                    if t is not None:
                        ti = cal[act[2]].index(t)
                        cal[act[2]][ti]['jobs'].append(jId)
                        if cal[act[2]][ti]['time'] is None:
                            cal[act[2]][ti]['time'] = time
                    else:
                        cal[act[2]].append({'area': jobs[jId]['area'], 'time': time, 'jobs': [jId],
                                              'crew': [crew[user]]})
                else:
                    cal.update({act[2]: [{'area': jobs[jId]['area'], 'time': time, 'jobs': [jId],
                                          'crew': [crew[user]]}]})
                jobs[jId]['install'] = act[2]
                jobs[jId]['ask'] = None
                saveCal(cal)
                saveIds(jobs)
                svR = finSVStep(jId, jobs[jId], 'Schedule')
                ttr = ''
                if time is not None:
                    ttr = 'at %s' % time
                return '''%s\n%s is scheduled on %s%s''' % (svR, jobs[jId]['name'], act[2], ttr)
        elif act == 'Install On...':
            return makeForm([{'name': 'date', 'type': 'date', 'class': 'dateIn'},
                             {'name': 'time', 'type': 'time', 'class': 'timeIn'},
                             {'name': 'done', 'type': 'button', 'class': 'buttIn'}], div, 'instDate')
        else:
            cal = openCal()
            jobs = openIds()
            date = act.split()[-1]
            area = act.split()[-3]
            for d in cal:
                if date in d:
                    for trip in cal[d]:
                        if area in trip['area'] and jId not in trip['jobs']:
                            trip['jobs'].append(jId)
                            jobs[jId]['install'] = d
                            jobs[jId]['ask'] = None
            saveCal(cal)
            saveIds(jobs)
            return '''%s added to %s trip on %s''' % (jobs[jId]['name'], area, date)
    elif task == 'PickUp':
        return '''No Functionality Yet'''
    elif task == 'Ship':
        if act == 'Job Complete':
            js = openIds()
            aajob = js.pop(jId)
            saveIds(js)
            return finSVStep(jId, aajob, 'Complete')
        elif act == 'Remind Me Later':
            jobs = openIds()
            jobs[jId]['ask'] = datetime.datetime.today() + datetime.timedelta(days=2)
    elif task == 'Surv':
        if isinstance(act, list):
            if act[0] == 'goDate':
                cal = openCal()
                time = None
                if len(act) is 5:
                    time = datetime.datetime.strftime(datetime.datetime.strptime(act[4], '%H:%M'), '%I:%M %p')
                if act[3] in cal and any([trip for trip in cal[act[3]] if act[1] in trip['area']]):
                    for trip in cal[act[3]]:
                        if act[1] in trip['area']:
                            trip['survey'] = {'time': time, 'name': act[2]}
                            break
                elif act[3] in cal:
                    cal[act[3]].append({'area': [act[1]], 'time': None, 'jobs': [], 'crew': [],
                                        'survey': {'time': time, 'name': act[2]}})
                else:
                    cal[act[3]] = [{'area': [act[1]], 'time': None, 'jobs': [], 'crew': [],
                                    'survey': {'time': time, 'name': act[2]}}]
                saveCal(cal)
                ttl = ''
                if time is not None:
                    ttl = 'at %s' % time
                return '''Added %s to %s %s going to %s''' % (act[2], act[3], ttl, act[1])
        elif act == 'Add':
            form = [{'name': 'title', 'type': 'text', 'class': 'titleIn'},
                    {'name': 'date', 'type': 'date', 'class': 'dateIn'},
                    {'name': 'time', 'type': 'time', 'class': 'timeIn'}]
            for area in openArea().keys():
                form.append({'name': area, 'type': 'button', 'class': 'buttIn'})
            return makeForm(form, div, 'goDate')
        elif act == 'Remove':
            cal = openCal()
            butts = []
            for date in cal:
                for trip in cal[date]:
                    if 'survey' in trip:
                        butts.append(trip['survey']['name'])
            return makeButts(butts, div)
        else:
            cal = openCal()
            for date in cal:
                for trip in cal[date]:
                    if 'survey' in trip and trip['survey']['name'] == act:
                        trip.pop('survey')
            saveCal(cal)
            return '''%s is removed''' % act
    elif task == 'TBD':
        return '''No Functionality Yet'''
    elif task == 'DateCh':
        if isinstance(act, list):
                cal = openCal()
                jobs = openIds()
                if jobs[jId]['install'] in cal:
                    for trip in cal[jobs[jId]['install']]:
                        if jId in trip['jobs']:
                            trip['jobs'].remove(jId)
                time = None
                if len(act) is 4:
                    time = datetime.datetime.strftime(datetime.datetime.strptime(act[3], '%H:%M'), '%I:%M %p')
                if act[2] in cal:
                    t = None
                    for trip in cal[act[2]]:
                        for a in jobs[jId]['area']:
                            if a in trip['area']:
                                t = trip
                    if t is not None:
                        ti = cal[act[2]].index(t)
                        cal[act[2]][ti]['jobs'].append(jId)
                        if cal[act[2]][ti]['time'] is None:
                            cal[act[2]][ti]['time'] = time
                    else:
                        cal[act[2]].append({'area': jobs[jId]['area'], 'time': time, 'jobs': [jId],
                                              'crew': [crew[user]]})
                else:
                    cal.update({act[2]: [{'area': jobs[jId]['area'], 'time': time, 'jobs': [jId],
                                          'crew': [crew[user]]}]})
                jobs[jId]['install'] = act[2]
                jobs[jId]['ask'] = None
                saveCal(cal)
                saveIds(jobs)
                svR = finSVStep(jId, jobs[jId], 'Schedule')
                ttr = ''
                if time is not None:
                    ttr = 'at %s' % time
                return '''%s\n%s is scheduled on %s%s''' % (svR, jobs[jId]['name'], act[2], ttr)
        elif act == 'Use Shop Vox':
            jobs = openIds()
            cal = openCal()
            if jobs[jId]['install'] in cal:
                for trip in cal[jobs[jId]['install']]:
                    if jId in trip['jobs']:
                        trip['jobs'].remove(jId)
            jobs[jId]['install'] = None
            saveIds(jobs)
            saveCal(cal)
            return '''%s date changed to ShopVox date''' % jobs[jId]['name']
        elif act == 'Install On...':
            return makeForm([{'name': 'date', 'type': 'date', 'class': 'dateIn'},
                             {'name': 'time', 'type': 'time', 'class': 'timeIn'},
                             {'name': 'done', 'type': 'button', 'class': 'buttIn'}], div, 'instDate')
        elif act == 'Assign':
            return makeButts(['Chad', 'Matt', 'Shelby', 'Marel', 'Alan', 'Luke'], div)
        elif act in crew:
            cal = openCal()
            jobs = openIds()
            for date in cal:
                for trip in cal[date]:
                    if jId in trip['jobs']:
                        trip['crew'].append(crew[act])
                        break
            saveCal(cal)
            return '''%s is scheduled to handle %s''' % (act, jobs[jId]['name'])

try:
    if 'answer' in r:
        answer = r['answer'].value
    else:
        i = 0
        answer = [r['bId'].value, r['butt'].value]
        while 'a%d' % i in r:
            answer.append(r['a%d' % i].value)
            i += 1
    html += processResponce(answer, r['jId'].value, r['user'].value)
    print(html)
except Exception as e:
    with open("log.txt", "a") as file:
        file.write('%s\n' % e)
    html += '''<h1>Error! Show Matt this</h1><p>'''
    print(html)
    traceback.print_exc(file=sys.stdout)
    print('''</p>''')
