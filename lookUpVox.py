import requests, json, qrcode, pyqrcode

aID = '*'
token = '*'
creds = '&account_id=%s&authToken=%s' % (aID, token)


def getJobList():
    url = 'https://api.shopvox.com/v1/jobs/?%s' % creds
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    return data


def getSOList():
    url = 'https://api.shopvox.com/v1/sales_orders/?%s' % creds
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    return data


def getSOwNum(num):
    url = 'https://api.shopvox.com/v1/sales_orders/show.json?txn_number=%s%s' % (num, creds)
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    return data


def getInvNum(num):
    url = 'https://api.shopvox.com/v1/invoices/show.json?txn_number=%s%s' % (num, creds)
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    print(data)
    return data


def getCompanyInfo(num):
    url = 'https://api.shopvox.com/v1/companies/%s?%s' % (num, creds)
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    return data


def getCompanies(page):
    url = 'https://api.shopvox.com/v1/companies/?page=%s?%s' % (page, creds)
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    return data


def getContactInfo(num):
    url = 'https://api.shopvox.com/v1/contacts/%s?%s' % (num, creds)
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    return data


def getContacts():
    url = 'https://api.shopvox.com/v1/contacts/?%s' % creds
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    return data


def getLeads():
    url = 'https://api.shopvox.com/v1/sales_leads?%s' % creds
    print(url)
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    return data


def formatedName(name):
    slash = name.rfind('/') + 1
    dot = name.rfind('.')
    return name[slash:dot]


def folderName(name):
    slash = name.rfind('/')
    firstS = name.rfind('/', 0, name.rfind('/')) + 1
    return name[firstS:slash]


def jobFinType(job):
    type = 'TBD'
    if 'lineItems' in job:
        for item in job['lineItems']:
            if item['name'] == 'Shipping':
                type = 'Shipping'
            elif item['name'] == 'Pick-Up':
                type = 'Pick-Up'
            elif item['name'] == 'Installation':
                type = 'Installation'
            elif item['name'] == 'Delivery':
                type = 'Delivery'
    return type


def hasStep(title, steps):
    has = False
    for step in steps:
        if step['name'] == title:
            has = True
    return has


def getStep(title, steps):
    x = {}
    for step in steps:
        if step['name'] == title:
            x = step
    return x

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

def completeStep(jobId, stepId):
    url = 'https://api.shopvox.com/v1/jobs/%s/steps/%s/complete?%s' % (jobId, stepId, creds)
    requests.post(url)

def genQRCode(name):
    data = getJobList()
    for job in data:
        if job['name'] == name:
            img = qrcode.make(job['id'].replace('-', ''))
            img.save('QRs/%s.png' % formatedName(job['name']))

def servertudeQR(id, folder):
    noDash = id.replace('-', '')
    img = pyqrcode.create(noDash)
    img.png('%sQRs/%s.png' % (folder, noDash), scale=4)
    return 'QRs/%s.png' % noDash

def setDueDates(num, date):
    so = getSOwNum(num)
    d = json.dumps({'dueDate': date})
    url = 'https://api.shopvox.com/v1/sales_orders/%s?%s' % (so['id'], creds)
    response = requests.put(url, d, headers={'Content-Type': 'application/json'})
    data = json.loads(response.content.decode('utf-8'))
    return data

# test stuff
#setDueDates(1640, '2020-07-15')
#data = getSOwNum(1640)
#    if job['active'] is True and hasStep('Schedule', job['steps']):
#        print(job['name'], ':', jobFinType(job))
#    if len(job['lineItems']) > 0:
#for job in data:
#    if job['active'] is True and getStepState(job, 'Complete') != 'isCompleted':
#        if 'projectManager' in job:
#            print(job['projectManager']['initials'])
#genQRCode('Ochsner/Main Campus/4-5 Donna Boyd.fs')
