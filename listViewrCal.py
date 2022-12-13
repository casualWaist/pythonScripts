import requests, json, datetime, os, time

def shouldInclude(job):
    answer = False
    if job['active'] is True:
        for step in job['steps']:
            if step['name'] == 'Complete' and (step['workflowState'] == 'started' or step['workflowState'] == 'idling'):
                answer = True
        if job['priority'] == 1 and job['workflowState'] != 'completed':
            answer = True
        if job['daysLeft'] < 0 and job['workflowState'] != 'completed':
            answer = True
    return answer

def hasStep(title, steps):
    has = False
    for step in steps:
        if step['name'] == title:
            has = True
    return has

def getStepState(job, name):
    statement = '''<p>></p>'''
    for step in job['steps']:
        if step['name'] == name:
            if step['isStarted'] is True:
                statement = '''<p class=started>></p>'''
            if step['isCompleted'] is True:
                statement = '''<p class=completed>></p>'''
            break
    return statement

def getStep(title, steps):
    x = {}
    for step in steps:
        if step['name'] == title:
            x = step
    return x

def formatedName(name):
    slash = name.rfind('/') + 1
    dot = name.rfind('.')
    if dot is 0:
        dot = -1
    return name[slash:dot]

def formatToday(day):
    days = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday'
    }
    return days.get(day)

def htmlListJob(job, clas):
    imageURL = job['currentProofUrl']
    if imageURL is None:
        imageURL = '''/home/pi/blank.jpg'''
    else:
        imageURL = imageURL + '''/convert?fit=scale&format=jpg&h=200&rotate=exif&w=200'''
    line = '''<li%s><img src=%s><p>%s</p></li>''' % (clas, imageURL, formatedName(job['name']))
    return line

def htmlListLead(job, clas):
    imageURL = '''/home/pi/blank.jpg'''
    line = '''<li%s><img src=%s><p>%s</p></li>''' % (clas, imageURL, formatedName(job['title']))
    return line

def htmlSetup(list, leads):
    html = '''<!doctype html><html><head><link rel="stylesheet" href="style.css" type="text/css"/>
        <meta http-equiv="refresh" content="300"></head><body><div id=past>Past Due<ul>
        '''
    calList = []
    for job in list:
        if job['daysLeft'] < 0:
            html = html + htmlListJob(job, '')
        else:
            calList.append(job)
    html = html + '''</ul></div>This Week<div id=cal><div id=thisWeek>'''
    today = datetime.datetime.now()
    x = today.weekday()
    rmList = []
    rmLdList = []
    dont = []
    while x < 5:
        html = html + '''<div class=day>%s<ul>''' % formatToday(x)
        if len(leads) > 0:
            for lead in leads:
                if lead['nextContactDate'] == datetime.datetime.strftime(today, '%Y-%m-%d'):
                    html = html + htmlListLead(lead, ' class=callis')
                    dont.append(lead)
                elif lead not in rmLdList:
                    rmLdList.append(lead)
        for job in calList:
            if job['dueDate'] == datetime.datetime.strftime(today, '%Y-%m-%d'):
                html = html + htmlListJob(job, ' class=callis')
                dont.append(job)
            elif job not in rmList:
                rmList.append(job)
        html = html + '''</ul></div>'''
        today += datetime.timedelta(days=1)
        x += 1
    html = html + '''</div><div id=later>Coming Soon...'''
    for job in rmList:
        if job not in dont:
            html += '''<div class=dayB>%s<ul>%s</ul></div>''' % (job['dueDate'], htmlListJob(job, ' class=callis'))
    for lead in rmLdList:
        if lead not in dont:
            html += '''<div class=dayB>%s<ul>%s</ul></div>''' % (lead['nextContactDate'], htmlListLead(lead, ' class=callis'))
    html = html + '''</div></body></html>'''
    return html

aID = '*'
token = '*'
creds = '*' % (aID, token)
url = '*' % creds

while True:
    try:
        jobList = []
        response = requests.get(url)
        data = json.loads(response.content.decode('utf-8'))
        for job in data:
            if shouldInclude(job):
                jobList.append(job)
        jobList.sort(key=lambda x: datetime.datetime.strptime(x['dueDate'], '%Y-%m-%d'))
        response = requests.get('https://api.shopvox.com/v1/sales_leads/?%s' % creds)
        leads = json.loads(response.content.decode('utf-8'))
        with open('/home/pi/index.html', 'w') as file:
            file.write(htmlSetup(jobList, leads))


    except Exception as error:
        with open("/home/pi/log.txt", "a") as file:
            currentTime = datetime.datetime.now()
            file.write('%s  %s\n' % (currentTime, error))
    time.sleep(300)