# when accessed through a private server url, returned a page for each crew member to see installs assigned to them

#!/usr/bin/python3
import cgi, lookUpVox, datetime, traceback, sys

user = cgi.FieldStorage()['crew'].value  # crew value comes in from the url call and will be used to fetch data
html = '''Content-type: text/html\r\n\r\n<html><head><title>%s</title></head><body>''' % user
crew = {"alan": "AJJ",
           "chad": "CMT",
           "luke": "LB",
           "matt": "MH",
           "marel": "MM"}
initials = {"AJJ": "alan", "CMT": "chad", "LB": "luke", "MH": "matt", "MM": "marel"}
userIni = crew[user]
script = '''<script>
        function sRpy(ele, parent){ //for processing a single button click
            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "../cgi-bin/formr.py", true);
            xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhttp.send("answer=" + ele.name + "&jId=" + ele.getAttribute('data-jId') + "&user=" + "%s");
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    actYN(this.responseText, parent)
                }
            }
        }
        function sDpy(ele, eles, parent){ //single button is clicked but has other attached elements
            var i = 0;
            var answer = "bId=" + ele.id + "&butt=" + ele.name;
            for (x of eles) {
                answer = answer + "&a" + i + "=" + document.getElementById(x).value;
                i += 1;
            }
            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "../cgi-bin/formr.py", true);
            xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhttp.send(answer + "&jId=" + parent + "&user=" + "%s");
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    actYN(this.responseText, parent)
                }
            }
        }
        function actYN(r, par){
            var div = document.getElementById(par);
            while(div.firstChild){div.removeChild(div.firstChild);}
            div.insertAdjacentHTML("beforeend", r);
        }</script>''' % (user, user)
style = '''<style>@font-face{
          font-family: Futura;
          src: url("../futuramc.TTF");
        }
        body{
          background-color: #032B3E;
        }
        h1, p{
          color: red;
        }
        div{
          font-family: Futura;
          padding-bottom: 3vw;
          color: #E2CAB5;
          background-color: #032B3E;
          font-size: 5vw;
        }
        button{
          color: #E2CAB5;
          font-family:Futura;
          font-size: 4vw;
          margin: 2vw;
          background-color: #032B3E;
          border-color: #E2CEB5;
        }
        button:hover{
          background-color: #C0A893;
        }
        input[type=text]{
          width: 50%;
          height: 4vw;
        }
        </style>'''
html += style + script
today = str(datetime.date.today())

with open('/var/www/html/crew/queryList.txt', 'r') as quFile:
    queryData = lookUpVox.json.loads(quFile.read())
with open('/var/www/html/crew/%s/data.txt' % user, 'r') as alF:
    userData = lookUpVox.json.loads(alF.read())
with open('/var/www/html/jobs/byID.txt', 'r') as idFile:
    idData = lookUpVox.json.loads(idFile.read())
with open('/var/www/html/cal/dates.txt', 'r') as clFile:
    calData = lookUpVox.json.loads(clFile.read())
with open('/var/www/html/jobs/all.txt', 'r') as allFile:
    allJobs = lookUpVox.json.loads(allFile.read())
with open('/var/www/html/zips/areaData.txt') as areaFile:
    areas = lookUpVox.json.loads(areaFile.read())

def aaid():
    now = datetime.datetime.now()
    aid = 'AA%s' % now.strftime('%Y%m%d%H%M%S%f')
    return aid

def makeButts(butts, div):
    htmlButts = ''''''
    oclk = '''onclick="sRpy(this, '%s')"''' % div
    for butt in butts:
        htmlButts += '''<button name="%s" %s data-jId="%s">%s''' % (butt, oclk, div, butt)
    return htmlButts

def qFormr(job, jId, action):  #generates an html form for each job with buttons that allow user to update job data
    global html
    if action is None:
        tmi = {}
        if job['type'] == 'TBD':
            div = 'TBD:' + jId
            butts = ['Install On...', 'Make Pick Up', 'Ship Out']
            tmi = {'quest': job['name'] + ' has no Finish Type',
                   'acts': makeButts(butts, div),
                   'div': div}
        elif job['type'] == 'Shipping':
            div = 'Ship:' + jId
            butts = ['Job Complete', 'Remind Me Later']
            tmi = {'quest': job['name'] + ' is ready to Ship',
                   'acts': makeButts(butts, div),
                   'div': div}
        elif job['type'] == 'Delivery' or job['type'] == 'Installation':
            butts = []
            for date in calData:
                for trip in calData[date]:
                    if any([i in job['area'] for i in trip['area']]):
                        guy = 'Someone'
                        if len(trip['crew']) > 0:
                            guy = initials[trip['crew'][0]]
                        butts.append('%s is going to %s on %s' % (guy, trip['area'][0], date[5:]))
            div = 'Inst:' + jId
            butts += ['Install On...', 'Remind Me Later']
            strip = ' is ready to be installed. Going to '
            if job['type'] == 'Delivery':
                strip = ' is ready to be delivered. Going to '
            tmi = {'quest': job['name'] + strip + job['area'][0],
                   'acts': makeButts(butts, div),
                   'div': div}
        else:
            tmi = {'quest': job['name'] + ' is ready to be picked up',
                   'acts': [],
                   'div': 'PickUp:' + jId}
        return tmi
    elif action == 'area':
        tmi = {'quest': 'Where is %s?' % job['name'],
               'acts': makeButts(areas.keys(), 'Area:' + jId),
               'div': 'Area:' + jId}
        return tmi

try:
    installs = []
    unknowns = []
    if today in calData:  # look up installs and serveys
        for trip in calData[today]:
            if userIni in trip['crew']:
                installs.append(trip)
            elif len(trip['crew']) == 0:
                unknowns.append(trip)
    if len(installs) > 0:
        t = 'trip'
        if len(installs) > 1:
            t = 'trips'
        html += '''<div id=installs>You've got %s %s today''' % (str(len(installs)), t)
        for trip in installs:
            t = trip['time']
            if t is None:
                t = ''
            html += '''<h2>%s</h2><i>%s</i><br>''' % (trip['area'][0], t)
        html += '''</div>'''
    if len(unknowns) > 0:
        for trip in unknowns:
            csId = 'CrewSet:' + trip['jobs'][0]
            jobs = ''
            for job in trip['jobs']:
                if job in idData:
                    if len(jobs) is not 0:
                        jobs += ' and then '
                    jobs += '%s' % idData[job]['name']
            html += '''<div id=%s>Someone has to go to %s to do %s<br>''' % (csId, trip['area'][0], jobs)
            for butt in makeButts(['alan', 'marel', 'luke', 'matt', 'chad'], csId):
                html += butt
            html += '''</div>'''
    for job in idData:  # shows jobs that are completed but not installed and need to be sorted
        if idData[job]['crew'] is not None and idData[job]['crew'][0] == userIni:
            if idData[job]['area'] is not None and idData[job]['area'][0] == 'Neverland':
                tmi = qFormr(idData[job], job, 'area')
                html += '''<div id=%s>%s<br>''' % (tmi['div'], tmi['quest'])
                for butt in tmi['acts']:
                    html += butt
                html += '''</div>'''
            elif idData[job]['ask'] is not None and idData[job]['ask'] == today:
                tmi = qFormr(idData[job], job, None)
                html += '''<div id=%s>%s<br>''' % (tmi['div'], tmi['quest'])
                for butt in tmi['acts']:
                    html += butt
                html += '''</div>'''
    addSId = 'Surv:%s' % aaid()
    html += '''<div id=%s>Schedule Surveys<br>''' % addSId
    for butt in makeButts(['Add', 'Remove'], addSId):
        html += butt
    html += '''</div><div><u>Change Install Dates</u><br>'''
    for date in calData:
        for trip in calData[date]:
            for job in trip['jobs']:
                if idData[job]['priority'] != 1:
                    chDatId = 'DateCh:%s' % job
                    html += '''<div id=%s>%s is on %s<br>''' % (chDatId, idData[job]['name'], date)
                    for butt in makeButts(['Install On...', 'Use Shop Vox', 'Assign'], chDatId):
                        html += butt
                    html += '''</div>'''
    html += '''</div></body></html>'''
    print(html)
except Exception as e:  # logs error and returns a message to the user
    with open("log.txt", "a") as file:
        currentTime = datetime.datetime.now()
        file.write('%s  %s\n' % (currentTime, e))
    html += '''<h1>Error! Show Matt this</h1><p>'''
    print(html)
    traceback.print_exc(file=sys.stdout)
