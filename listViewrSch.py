import requests, json, datetime, os, time

def shouldInclude(job):
    answer = False
    if job['active'] is True:
        for step in job['steps']:
            if step['name'] == 'Schedule' and (step['workflowState'] == 'started' or step['workflowState'] == 'idling'):
                answer = True
    return answer

def formatedName(name):
    slash = name.rfind('/') + 1
    dot = name.rfind('.')
    if dot is 0:
        dot = -1
    return name[slash:dot]

def formatJob(job):
    imageURL = job['currentProofUrl']
    rush = ''
    if job['priority'] == 1:
        rush = ' class=rush'
    if imageURL is None:
        imageURL = '''/home/pi/blank.jpg'''
    else:
        imageURL = imageURL + '''/convert?fit=scale&format=jpg&h=200&rotate=exif&w=200'''
    line = '''<li><img src=%s><p%s>%s %s</p></li>''' % (imageURL, rush, job['dueDate'][5:], formatedName(job['name']))
    return line

def htmlSetup(list):
    html = '''<!doctype html><html><head><link rel="stylesheet" href="style.css" type="text/css"/>
    <meta http-equiv="refresh" content="300"></head><body><div id=deliver>Deliveries<ul>
    '''
    for job in list:
        if job['description'] is not None and job['description'].find('Delivery') > 0:
            line = formatJob(job)
            html = html + line
    html = html + '''</ul></div><div id=install>Installs<ul>'''
    for job in list:
        if job['description'] is not None and job['description'].find('Installation') > 0:
            line = formatJob(job)
            html = html + line
    html = html + '''</ul></div><div id=pu>Pick Ups<ul>'''
    for job in list:
        if job['description'] is not None and job['description'].find('Pick-Up') > 0:
            line = formatJob(job)
            html = html + line
    html = html + '''</ul></div id=ship><div>To Ship<ul>'''
    for job in list:
        if job['description'] is not None and job['description'].find('Shipping') > 0:
            line = formatJob(job)
            html = html + line
    html = html + '''</ul></div><div id=other>Other<ul>'''
    for job in list:
        if job['description'] is None or job['description'] == '<p>null</p>':
            line = formatJob(job)
            html = html + line
    html = html + '''</ul></div></body></html>'''
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
        with open('/home/pi/index.html', 'w') as file:
            file.write(htmlSetup(jobList))


    except Exception as error:
        with open("/home/pi/log.txt", "a") as file:
            currentTime = datetime.datetime.now()
            file.write('%s  %s\n' % (currentTime, error))
    time.sleep(300)