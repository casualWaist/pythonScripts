import requests, json, datetime, os, time

def shouldInclude(job):
    answer = False
    if job['active'] is True:
        for step in job['steps']:
            if step['name'] == 'Assemble' and step['isCompleted'] == False:
                answer = True
            if step['name'] == 'Paint Parts' and step['isCompleted'] == False:
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

def addLineHtml(job, altLine):
    imageURL = job['currentProofUrl']
    rush = ''
    if job['priority'] != 0:
        rush = ' class=rush%d' % job['priority']
    if imageURL is None:
        imageURL = '''/home/pi/blank.jpg'''
    else:
        imageURL = imageURL + '''/convert?fit=scale&format=jpg&h=100&rotate=exif&w=100'''
    line = '''<li><img src=%s><div%s>%s</div><div class=arrows>''' % (imageURL, rush, formatedName(job['name']))
    if altLine:
        line = '''<li class=altLine><img src=%s><div%s>%s</div><div class=arrows>''' % (imageURL, rush, formatedName(job['name']))
    titles = ['Print or Plot', 'Print Insert', 'Route Parts',
              'Knife Cut', 'Paint Parts', 'Laminate', 'Plot', 'Assemble']
    for title in titles:
        if hasStep(title, job['steps']):
            statement = getStepState(job, title)
            line = line + statement
        else:
            line = line + '''<p class=noStep>></p>'''
    line = line + '''</div><div class=dates><span>%s</span><span>%s</span><span%s>%s</span></div></li>''' % (
    job['orderNumber'], job['createdAt'][5:10], rush, job['dueDate'][5:])
    return line

def htmlSetup(list):
    html = '''<!doctype html><html><head><link rel="stylesheet" href="style.css" type="text/css"/>
    <meta http-equiv="refresh" content="300"></head><body><div id=paint>Paint<ul>
    <li id=header><h1>NAME</h1><h2>P/P | PIn | CNC | CIn |Paint| Lam | DiC | Asm |</h2><h3>Due</h3></li>
    '''
    altLine = False
    assList = []
    for job in list:
        if hasStep('Paint Parts', job['steps']) and getStep('Paint Parts', job['steps'])['isCompleted'] is False:
            html = html + addLineHtml(job, altLine)
            if altLine:
                altLine = False
            else:
                altLine = True
        else:
            assList.append(job)
    html = html + '''</ul></div><div id=ass>Assemble<ul>
    <li id=header><h1>NAME</h1><h2>Prt/Pl | P Ins | Route | CutIn | Paint | Lamnt | PlotL | Asmble |</h2><h3>Due</h3></li>'''
    altLine = False
    for job in assList:
        html = html + addLineHtml(job, altLine)
        if altLine:
            altLine = False
        else:
            altLine = True
    html = html + '''</ul></body></html>'''
    return html

aID = '*'
token = '*'
creds = '*' % (aID, token)
url = '*' % creds

try:
    jobList = []
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    for job in data:
        if shouldInclude(job):
            jobList.append(job)
    jobList.sort(key=lambda x: datetime.datetime.strptime(x['dueDate'], '%Y-%m-%d'))
    with open('/home/pi/index.html', 'w') as file:
        file.write(htmlSetup(jobList))
except Exception as error:
    with open("/home/pi/log.txt", "a") as file:
        currentTime = datetime.datetime.now()
        file.write('%s  %s\n' % (currentTime, error))