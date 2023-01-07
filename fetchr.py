# pull all data from shopvox and update the local files

import lookUpVox, datetime

prod = []
limbo = []
cal = []
all = []


def addCalDate(jobID, date, area, calData):
    if date in calData:  # if date exists just add trip
        t = next((calData[date][i] for i, a in enumerate(calData[date]) if
              [x for x in area if x in a['area']]), None)
        if t is not None:  # if trip exists add job to trip
            if jobID not in t['jobs']:
                ti = calData[date].index(t)
                calData[date][ti]['jobs'].append(jobID)
        else:
            trip = {'area': area,
                    'time': None,
                    'jobs': [jobID],
                    'crew': []}  # crew will be added later
            calData[date].append(trip)
    else:  # if date does not exits make a new date with trip
        insDate = {date: [{'area': area,
                           'time': None,
                           'jobs': [jobID],
                           'crew': []}]}
        calData.update(insDate)


def changeCalDate(jobID, oDate, date, area, calData):  # pass date=None to delete
    found = False
    xtrips = []
    if oDate is None:
        for day in calData:
            for trip in calData[day]:
                if jobID in trip['jobs']:
                    oDate = day
    for trip in calData[oDate]:
        if jobID in trip['jobs']:
            trip['jobs'].remove(jobID)
            found = True
        if len(trip['jobs']) == 0 and 'survey' not in trip:
            xtrips.append(trip)
    if found:
        for trip in xtrips:
            if trip in calData[oDate]:
                calData[oDate].remove(trip)
        if len(calData[oDate]) == 0:
            del calData[oDate]
        if date is not None:
            addCalDate(jobID, date, area, calData)
    else:
        addCalDate(jobID, date, area, calData)

def inCal(jobID, calData):
    inCalD = False
    for day in calData:
        for trip in calData[day]:
            if jobID in trip['jobs']:
                inCalD = True
                break
    return inCalD


def sortJob(job):
    if job['active'] is True and lookUpVox.getStep('Complete', job['steps'])['isCompleted'] is False:
        all.append(job)
        for step in job['steps']:
            if step['name'] == 'Print or Plot' and step['isCompleted'] is False:
                prod.append(job)
                break
            if step['name'] == 'Route Parts' and step['isCompleted'] is False:
                prod.append(job)
                break
            if step['name'] == 'Knife Cut' and step['isCompleted'] is False:
                prod.append(job)
                break
            if step['name'] == 'Paint Parts' and step['isCompleted'] is False:
                prod.append(job)
                break
            if step['name'] == 'Assemble' and step['isCompleted'] is False:
                prod.append(job)
                break
            if step['name'] == 'Schedule' and step['isCompleted'] is False:
                limbo.append(job)
                break
            if step['name'] == 'Complete' and step['isCompleted'] is False:
                cal.append(job)
                break

tday = datetime.datetime.today()
data = lookUpVox.getJobList()  # get an updated list of job data and sort it based on steps
for job in data:
    sortJob(job)
removes = []  # if a job has firm date skip schedule step by updating SV and re-sort lists
for job in limbo:
    if job['priority'] == 1 and tday < datetime.datetime.strptime(job['dueDate'], '%Y-%m-%d') + datetime.timedelta(days=1):
        try:
            lookUpVox.completeStep(job['id'], lookUpVox.getStep('Schedule', job['steps'])['id'])
            removes.append(job)
        except Exception as e:
            print(e)
if len(removes) > 0:
    for job in removes:
        cal.append(job)
        limbo.pop(job)
# save all updated SV data
with open('/var/www/html/prod/prodJobs.txt', 'w') as zSave:
    zSave.write(lookUpVox.json.dumps(prod))
with open('/var/www/html/cal/limboJobs.txt', 'w') as aSave:
    aSave.write(lookUpVox.json.dumps(limbo))
with open('/var/www/html/cal/schedJobs.txt', 'w') as bSave:
    bSave.write(lookUpVox.json.dumps(cal))
with open('/var/www/html/jobs/all.txt', 'w') as cSave:
    cSave.write(lookUpVox.json.dumps(all))
# open AA data files for updating
with open('/var/www/html/jobs/byID.txt', 'r') as idFile:
    idData = lookUpVox.json.loads(idFile.read())
with open('/var/www/html/cal/dates.txt', 'r') as clFile:
    calData = lookUpVox.json.loads(clFile.read())
with open('/var/www/html/zips/areaData.txt', 'r') as arFile:
    areaData = lookUpVox.json.loads(arFile.read())
with open('/var/www/html/zips/zipCodeData.txt', 'r') as zpFile:
    zipData = lookUpVox.json.loads(zpFile.read())
with open('/var/www/html/crew/queryList.txt', 'r') as quFile:
    queryData = lookUpVox.json.loads(quFile.read())
with open('/var/www/html/front/invList.txt', 'r') as inFile:
    invList = lookUpVox.json.loads(inFile.read())
with open('/var/www/html/crew/alan/data.txt', 'r') as alF:
    alData = lookUpVox.json.loads(alF.read())
with open('/var/www/html/crew/chad/data.txt', 'r') as chF:
    chData = lookUpVox.json.loads(chF.read())
with open('/var/www/html/crew/marel/data.txt', 'r') as mlF:
    mlData = lookUpVox.json.loads(mlF.read())
with open('/var/www/html/crew/matt/data.txt', 'r') as mtF:
    mtData = lookUpVox.json.loads(mtF.read())
with open('/var/www/html/crew/luke/data.txt', 'r') as luF:
    luData = lookUpVox.json.loads(luF.read())
# update the AA jobs data only overwriting certain things
for job in cal:  # add SV scheduled jobs to the cal if they aren't there already
    if job['id'] in idData and job['priority'] != 1:
        if idData[job['id']]['type'] == 'Delivery' or idData[job['id']]['type'] == 'Installation':
            dday = datetime.datetime.strptime(job['dueDate'], '%Y-%m-%d')
            if tday < dday + datetime.timedelta(days=1):
                if not inCal(job['id'], calData):
                    idData[job['id']]['install'] = job['dueDate']
                    addCalDate(job['id'], job['dueDate'], idData[job['id']]['area'], calData)
                elif idData[job['id']]['install'] is not None and idData[job['id']]['install'] != job['dueDate']:
                    if idData[job['id']]['install'] not in calData:
                        addCalDate(job['id'], idData[job['id']]['install'], idData[job['id']]['area'], calData)
                else:
                    if job['dueDate'] in calData:
                        changeCalDate(job['id'], None, job['dueDate'], idData[job['id']]['area'], calData)
                        idData[job['id']]['install'] = job['dueDate']
                    else:
                        addCalDate(job['id'], job['dueDate'], idData[job['id']]['area'], calData)
                        idData[job['id']]['install'] = job['dueDate']
            else:
                limbo.append(job)
                cal.remove(job)
total = 0
a = 0
for job in all:
    total += 1
    if job['id'] not in idData:  # add new job
        a += 1
        so = {}
        if 'orderNumber' in job:
            so = lookUpVox.getSOwNum(job['orderNumber'])
        zipCode = None
        if 'shippingAddress' in so:
            zipCode = so['shippingAddress']['zip']
            if len(zipCode) > 5:
                zipCode = zipCode[:5]
        date = job['dueDate']
        install = None
        crew = None
        if 'projectManager' in job:
            crew = [job['projectManager']['initials']]
        finType = lookUpVox.jobFinType(job)
        area = None
        if finType == 'Delivery' or finType == 'Installation':
            if zipCode is not None:
                if zipCode in zipData:
                    area = zipData[zipCode]
                else:
                    area = ['New']  # add matt query to add zip code to data*****
            else:  # if no zip make query to salesman to define location*****
                area = ['Neverland']
        if job['priority'] == 1 and tday < datetime.datetime.strptime(job['dueDate'], '%Y-%m-%d') + datetime.timedelta(days=1):
            install = date
            if finType == 'Delivery' or finType == 'Installation':
                addCalDate(job['id'], date, area, calData)
        inv = False
        if 'invoiced' in so:
            inv = so['invoiced']
        new = {job['id']: {
            'name': lookUpVox.formatedName(job['name']),
            'folder': lookUpVox.folderName(job['name']),
            'date': date,
            'install': install,
            'priority': job['priority'],
            'zip': zipCode,
            'area': area,
            'crew': crew,
            'stored': '',
            'ask': None,
            'soNum': job['orderNumber'],
            'soId': job['orderId'],
            'invoiced': inv,
            'type': finType}}
        idData.update(new)
    else:  # update AA data
        idData[job['id']]['date'] = job['dueDate']
        # add handlers for priority 2 and 3*****
        idData[job['id']]['priority'] = job['priority']
        finType = lookUpVox.jobFinType(job)
        idData[job['id']]['type'] = finType
        if job['priority'] == 1:
            j = idData[job['id']]
            if finType == 'Delivery' or finType == 'Installation':
                inDay = False
                if job['dueDate'] in calData:
                    for trip in calData[job['dueDate']]:
                        if job['id'] in trip['jobs']:
                            inDay = True
                if not inDay and tday < datetime.datetime.strptime(job['dueDate'], '%Y-%m-%d') + datetime.timedelta(days=1):
                    if j['install'] is None:  # priority changed to 1
                        addCalDate(job['id'], job['dueDate'], j['area'], calData)
                    else:
                        changeCalDate(job['id'], j['install'], job['dueDate'], j['area'], calData)
                    j['install'] = job['dueDate']
for job in limbo:  # check limbo jobs against AA data for newness
    ask = idData[job['id']]['ask']
    if ask is None:
        idData[job['id']]['ask'] = datetime.datetime.strftime(tday, '%Y-%m-%d')
    elif datetime.datetime.strptime(ask, '%Y-%m-%d') < tday + datetime.timedelta(days=1):
        idData[job['id']]['ask'] = datetime.datetime.strftime(tday, '%Y-%m-%d')
    if idData[job['id']]['invoiced'] is False and [job['id'], job['orderNumber']] not in invList:
        invList.append([job['id'], job['orderNumber']])  # add new limbo jobs to list of ready to invoice jobs in front
removes = []
for jobId in invList:  # update invoice list with SV
    soD = lookUpVox.getSOwNum(jobId[1])
    invoiced = True
    if 'invoiced' in soD:
        invoiced = soD['invoiced']
    if invoiced or soD['active'] is False:
        removes.append(jobId)
for jobId in removes:
    invList.remove(jobId)
removes = []  # remove old jobs that have been completed from the data
r = 0
for jId in idData:
    inData = False
    for job in all:
        if job['id'] == jId:
            inData = True
            break
    if not inData:
        r += 1
        removes.append(jId)
        if inCal(jId, calData):
            changeCalDate(jId, idData[jId]['install'], None, idData[jId]['area'], calData)
for jId in removes:
    idData.pop(jId)
    if jId in queryData:
        queryData.pop(jId)
print(total, '+', a, '-', r)  # counts the jobs added and removed
with open('/var/www/html/front/invList.txt', 'w') as i:
    i.write(lookUpVox.json.dumps(invList))
with open('/var/www/html/jobs/byID.txt', 'w') as w:
    w.write(lookUpVox.json.dumps(idData))
with open('/var/www/html/crew/queryList.txt', 'w') as q:
    q.write(lookUpVox.json.dumps(queryData))
with open('/var/www/html/cal/dates.txt', 'w') as c:
    c.write(lookUpVox.json.dumps(calData))

