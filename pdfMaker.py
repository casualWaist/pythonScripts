from fpdf import FPDF
from PIL import Image
import requests, os, lookUpVox, io

folder = 'C:/*/Desktop/shopVOX/'

def getCropImage(url, numOLines):
    response = requests.get(url + '/convert?format=jpg')
    img = Image.open(io.BytesIO(response.content))
    space = (16 * numOLines)
    left = 55
    right = 162
    top = space + 237
    botm = 380 + space
    img = img.crop((left, top, right, botm))
    img.save('%ssig.jpg' % folder)
    return '%ssig.jpg' % folder


def convP(string):
    string = string.replace('<p>', '')
    string = string.replace('</p>', '')
    string = string.replace('<b>', '')
    string = string.replace('</b>', '')
    string = string.replace('<i>', '')
    string = string.replace('</i>', '')
    string = string.replace('<br>', '\n')
    string = string.replace('<sup>', '')
    string = string.replace('</sup>', '')
    string = string.replace('&nbsp;', ' ')
    string = string.replace('\n\n', '\n')
    string = string.replace('\n \n', '\n')
    string = string.replace('\u2019', '\'')
    if len(string) > 100 and '\n' not in string:
        if '. ' in string:
            string = string.replace('. ', '.\n')
        else:
            string = '%s\n%s' % (string[:100], string[99:])
    print(string)
    parts = string.splitlines()
    return parts


def makeQuotePdf(invD):
    company = lookUpVox.getCompanyInfo(invD['company']['id'])
    pdf = FPDF(orientation='P', unit='pt', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=10)
    pdf.set_font('Helvetica', size=12)
    pdf.set_text_color(3, 43, 62)
    pdf.set_xy(40, 35)
    pdf.multi_cell(443, 12, 'A&A Quick Quality Signs, Inc.\n718 Labarre Rd, Jefferson, LA, 70121\nhttp://www.imageisit.com\n(504) 836-2998', align='L')
    pdf.image('%sA&A Web.jpg' % folder, 440, 5, 100, 100)
    pdf.set_fill_color(227, 221, 216)
    pdf.set_draw_color(3, 43, 62)
    pdf.set_xy(0, 110)
    pdf.cell(595, 100, border='T B', fill=True)
    pdf.set_font('Helvetica', size=18)
    if invD['customerPoNumber'] is None:
        raise Exception('invoice has no p.o. number')
    deets = 'INVOICE #: %s\nP.O. #: %s\n%s' % (invD['txnNumber'], invD['customerPoNumber'], lookUpVox.formatedName(invD['name']))
    pdf.set_xy(40, 121)
    pdf.multi_cell(395, 26, deets, border='R', align='J')
    pdf.set_xy(395, 121)
    pdf.set_font('Helvetica', size=10)
    terms = 'Net 30 Days'
    if company['termCodeName'] is not None:
        terms = company['termCodeName']
    deets = 'TERMS\n%s\nINVOICE DATE\n%s\nDUE DATE\n%s' % (terms, invD['txnDate'], invD['dueDate'])
    pdf.multi_cell(200, 13, deets, align='C')
    pdf.set_xy(0, 210)
    pdf.cell(50, 15, '# ', border='R', align='R')
    pdf.cell(300, 15, ' ITEM', border="R", align='L')
    pdf.cell(45, 15, 'QTY', border='R', align='C')
    pdf.cell(100, 15, 'U.PRICE', border='R', align='C')
    pdf.cell(100, 15, ' TOTAL', align='L')
    place = 225
    items = invD['lineItems']
    for item in items:
        pdf.set_xy(0, place)
        height = 15
        pdf.set_font('Helvetica', size=10)
        pdf.cell(50, 15, '%s ' % item['position'], border='T R', align='R')
        pdf.cell(300, 15, ' %s' % item['name'], border="T R", align='L')
        pdf.cell(45, 15, '%s' % int(float(item['quantity'])), border='T R', align='C')
        pdf.cell(100, 15, '%s' % item['priceInDollars'], border='T R', align='C')
        pdf.cell(100, 15, ' %s' % item['totalPriceInDollars'], border='T', align='L')
        pdf.set_font('Helvetica', size=6)
        if item['description'] is not None:
            for part in convP(item['description']):
                pdf.set_xy(50, place + height)
                pdf.cell(300, 10, '\t\t\t %s' % part, border='L R')
                pdf.cell(45, 10, border='R')
                pdf.cell(100, 10, border='R')
                height += 10
            place += height
        else:
            place += height
    pdf.set_font('Helvetica', size=10)
    pdf.set_xy(0, place)
    place += 5
    pdf.cell(595, 5, border='T')
    if place < 692:
        place = 692
    size = 842 - place - 25
    pdf.set_xy(0, place)
    pdf.cell(595, size, fill=True, border='T B')
    pdf.set_xy(0, place)
    pdf.cell(99, size, 'ORDERED BY ', align='R')
    pdf.set_xy(99, place)
    pdf.set_fill_color(255, 255, 255)
    pdf.cell(296, size, fill=True, border=True)
    pdf.set_xy(99, place + (size/4))
    c = ''
    v = ''
    s = ''
    if len(company['addresses']) > 0:
        a = company['addresses'][0]
        v = a['street']
        s = a['city'] + ', ' + a['state'] + ', ' + a['zip']
    if invD['primaryContact']['name'] is not None:
        contact = lookUpVox.getContactInfo(invD['primaryContact']['id'])
        c = contact['name']
        if contact['email'] != '' and contact['phone'] != '':
            v = contact['email']
            s = contact['phone']
    pdf.multi_cell(145, 15, ' %s\n %s\n %s\n %s' % (company['name'], c, v, s), align='L')
    pdf.set_xy(244, place)
    if len(invD['signatures']) == 0:
        raise Exception('no signature was found on invoice')
    else:
        pdf.image(getCropImage(invD['signatures'][0]['signatureUrl'], len(invD['lineItems'])), 270, place + 10, 98, 98)
        pdf.cell(151, 15, '%s' % invD['signatures'][0]['name'], align='C')
        pdf.set_xy(244, place + 105)
        pdf.set_font('Helvetica', size=8)
        pdf.cell(151, 15, '%s' % invD['signatures'][0]['createdAt'][:10], align='C')
    pdf.set_xy(395, place)
    pdf.set_font('Helvetica', size=24)
    pdf.cell(160, 30, ' Total:', align='L')
    pdf.set_xy(395, place + 30)
    pdf.cell(160, size - 30, '$%6.2f' % float(invD['totalPriceWithTaxInDollars']), align='R')
    pdf.output('%sPO# %s.pdf' % (folder, invD['customerPoNumber']))


def makeOchQuotePdf(invD):
    pdf = FPDF(orientation='P', unit='pt', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=10)
    pdf.set_font('Helvetica', size=12)
    pdf.set_text_color(3, 43, 62)
    pdf.set_xy(40, 35)
    pdf.multi_cell(443, 12, 'A&A Quick Quality Signs, Inc.\n718 Labarre Rd, Jefferson, LA, 70121\nhttp://www.imageisit.com\n(504) 836-2998', align='L')
    pdf.image('%sA&A Web.jpg' % folder, 440, 5, 100, 100)
    pdf.set_fill_color(227, 221, 216)
    pdf.set_draw_color(3, 43, 62)
    pdf.set_xy(0, 110)
    pdf.cell(595, 100, border='T B', fill=True)
    pdf.set_font('Helvetica', size=18)
    if invD['customerPoNumber'] is None:
        raise Exception('invoice has no p.o. number')
    deets = 'INVOICE #: %s\nP.O. #: %s\n%s' % (invD['txnNumber'], invD['customerPoNumber'], lookUpVox.formatedName(invD['name']))
    pdf.set_xy(40, 121)
    pdf.multi_cell(395, 26, deets, border='R', align='J')
    pdf.set_xy(395, 121)
    pdf.set_font('Helvetica', size=10)
    deets = 'TERMS\nNet 30 Days\nINVOICE DATE\n%s\nDUE DATE\n%s' % (invD['txnDate'], invD['dueDate'])
    pdf.multi_cell(200, 13, deets, align='C')
    pdf.set_xy(0, 210)
    pdf.cell(50, 15, '# ', border='R', align='R')
    pdf.cell(300, 15, ' ITEM', border="R", align='L')
    pdf.cell(45, 15, 'QTY', border='R', align='C')
    pdf.cell(100, 15, 'U.PRICE', border='R', align='C')
    pdf.cell(100, 15, ' TOTAL', align='L')
    place = 225
    items = invD['lineItems']
    for item in items:
        pdf.set_xy(0, place)
        height = 15
        pdf.set_font('Helvetica', size=10)
        pdf.cell(50, 15, '%s ' % item['position'], border='T R', align='R')
        pdf.cell(300, 15, ' %s' % item['name'], border="T R", align='L')
        pdf.cell(45, 15, '%s' % int(float(item['quantity'])), border='T R', align='C')
        pdf.cell(100, 15, '%s' % item['priceInDollars'], border='T R', align='C')
        pdf.cell(100, 15, ' %s' % item['totalPriceInDollars'], border='T', align='L')
        pdf.set_font('Helvetica', size=6)
        if item['description'] is not None:
            for part in convP(item['description']):
                pdf.set_xy(50, place + height)
                pdf.cell(300, 10, '\t\t\t %s' % part, border='L R')
                pdf.cell(45, 10, border='R')
                pdf.cell(100, 10, border='R')
                height += 10
            place += height
        else:
            place += height
    pdf.set_font('Helvetica', size=10)
    pdf.set_xy(0, place)
    place += 5
    pdf.cell(595, 5, border='T')
    if place < 692:
        place = 692
    size = 842 - place - 25
    pdf.set_xy(0, place)
    pdf.cell(595, size, fill=True, border='T B')
    pdf.set_xy(0, place)
    pdf.cell(99, size, 'ORDERED BY ', align='R')
    pdf.set_xy(99, place)
    pdf.set_fill_color(255, 255, 255)
    pdf.cell(296, size, fill=True, border=True)
    pdf.set_xy(99, place + (size/4))
    pdf.multi_cell(145, 15, ' Ochsner Medical Foundation\n Accounts Payable\n 1201 Dickory Ave\n Harahan, LA, 70123', align='L')
    pdf.set_xy(244, place)
    if len(invD['signatures']) == 0:
        raise Exception('no signature was found on invoice')
    else:
        pdf.image(getCropImage(invD['signatures'][0]['signatureUrl'], len(invD['lineItems'])), 270, place + 10, 98, 98)
        pdf.cell(151, 15, '%s' % invD['signatures'][0]['name'], align='C')
        pdf.set_xy(244, place + 105)
        pdf.set_font('Helvetica', size=8)
        pdf.cell(151, 15, '%s' % invD['signatures'][0]['createdAt'][:10], align='C')
    pdf.set_xy(395, place)
    pdf.set_font('Helvetica', size=24)
    pdf.cell(160, 30, ' Total:', align='L')
    pdf.set_xy(395, place + 30)
    pdf.cell(160, size - 30, '$%6.2f' % float(invD['totalPriceWithTaxInDollars']), align='R')
    pdf.output('%sPO# %s.pdf' % (folder, invD['customerPoNumber']))


x = True
while x:
    orderNum = input('Enter the Invoice Number\n')
    try:
        orderNum = int(orderNum)
        data = lookUpVox.getInvNum(orderNum)
#        for item in data:
#            print(item, ':', data[item])
        if data['company']['id'] == '*':
            makeOchQuotePdf(data)
        else:
            makeQuotePdf(data)
        x = False
        os.startfile(folder)
    except Exception as error:
        print( error, '\ntry again')
