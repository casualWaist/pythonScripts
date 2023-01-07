# looks up invoice data and returns some HTML that gets injected into a page

#!/usr/bin/python3
import cgi, lookUpVox, traceback, sys

r = cgi.FieldStorage()
html = 'Content-type: text/html\r\n\r\n'

def formHtml(l, d, tagL, tagD):
    return '''<%s>%s : </%s><%s>%s</%s><br>''' % (tagL, l, tagL, tagD, d, tagD)

try:
    if 'soID' in r and r['soID'].value.isnumeric():
        so = lookUpVox.getSOwNum(r['soID'].value)
        with open('/var/www/html/jobs/byID.txt', 'r') as idFile:
            idData = lookUpVox.json.loads(idFile.read())
        with open('/var/www/html/cal/dates.txt', 'r') as clFile:
            calData = lookUpVox.json.loads(clFile.read())
        for x in so:
            if x in ['dueDate', 'fullyInvoiced', 'projectManager']:
                html += formHtml(x, so[x], 'h2', 'h3')
        invoiced = False
        if so['id'] in [idData[j]['soId'] for j in idData]:
            aajob = idData[next(a for a in idData if idData[a]['soId'] == so['id'])]
            for x in aajob:
                if x == 'name' or x == 'crew' or x == 'type':
                    html += formHtml(x, aajob[x], 'h2', 'h3')
                elif x == 'date' or x == 'install':
                    html += formHtml(x, aajob[x], 'h2', 'h3')
                    if aajob[x] in calData:
                        html += formHtml('%s in Cal' % x, calData[aajob[x]], 'h2', 'h3')
                    else:
                        html += '''<h1>%s not in Calendar</h1>''' % x
                elif x == 'priority':
                    html += formHtml(x, aajob[x], 'h2', 'h3')
                elif x == 'zip':
                    html += '''<h2>Zip/Area AAData: </h2>%s''' % formHtml(aajob[x], aajob['area'], 'h3', 'h3')
                elif x == 'invoiced':
                    invoiced = aajob[x]
            for date in calData:
                for trip in calData[date]:
                    if aajob in trip['jobs']:
                        html += formHtml('Job found in', date, 'h2', 'h3')
        else:
            html += '''<h1>Job not in AAData</h1>'''
        with open('/var/www/html/front/invList.txt', 'r') as inFile:
            invList = lookUpVox.json.loads(inFile.read())
        if so['id'] in [l[1] for l in invList]:
            html += '''<h2>AAData invoiced:</h2>%s''' % formHtml(str(invoiced), 'is in invoice list', 'h3', 'h3')
        else:
            html += '''<h1>Not found in invoice list</h1>'''
    else:
        html += '''<h1>NOOOOOOO...</h1>'''
    print(html)
except Exception as e:
    with open("log.txt", "a") as file:
        file.write('%s\n' % e)
    html += '''<h1>Error! Show Matt this</h1><p>'''
    print(html)
    traceback.print_exc(file=sys.stdout)
    print('''</p>''')
