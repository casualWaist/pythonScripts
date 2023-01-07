# keeps a directory of current qr image files as well as a PDF containing the qr and job data

import qrcode, lookUpVox, os, datetime
from fpdf import FPDF


def shouldInclude(job):
    b = False
    day = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    if job['active'] is True and day in job['createdAt']:
        b = True
    return b


def genQRCode(job):
    img = qrcode.make(job['id'].replace('-', ''))
    img.save('QRs/%s.png' % lookUpVox.formatedName(job['name']))


def makeJobPDF(job):
    pdf = FPDF(orientation='P', unit='pt', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(False)
    pdf.set_font('Helvetica', size=30)
    pdf.set_fill_color(240, 20, 20)
    name = lookUpVox.formatedName(job['name'])
    pdf.set_xy(40, 40)
    pdf.cell(515, 35, name, align='C')
    pdf.set_xy(40, 75)
    pdf.cell(257, 35, 'WO #: %s'% job['orderNumber'])
    rush = False
    if job['priority'] == 1:
        rush = True
    pdf.cell(257, 35, 'Due: %s' % job['dueDate'], fill=rush)
    ridof = 'TBD'
    if job['description'].find('Shipping') > 0:
        ridof = 'Ship'
    elif job['description'].find('Pick-Up') > 0:
        ridof = 'Pick-Up'
    elif job['description'].find('Installation') > 0:
        ridof = 'Install'
    elif job['description'].find('Delivery') > 0:
        ridof = 'Deliver'
    pdf.set_xy(40, 110)
    pdf.cell(171, 35, ridof)
    pdf.image('QRs/%s' % name + '.png', w=100, h=100)
    pdf.set_font('Helvetica', size=12)
    pdf.cell(100, 15, name, align='C')
    pdf.output('jobPDFs/%s.pdf' % name)


data = lookUpVox.getJobList()
print('got jobs')
for file in os.listdir('QRs'):
    os.remove('QRs/%s' % file)
print('removed files')
for job in data:
    if shouldInclude(job):
        genQRCode(job)
        print('qr for %s' % job['name'])
        makeJobPDF(job)
        print('made job pdf')
