import lookUpVox

def qQuery(person, ):

with open('/var/www/html/jobs/byID.txt', 'r') as idFile:
    idData = lookUpVox.json.loads(idFile.read())
with open('/var/www/html/crew/cal/data.txt', 'r') as clFile:
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

# check AA cal data and look for zip matches from cal -> limbo
for day in calData:
    for trip in day:



# add any matches as alerts to AA crew data
# look for zip matches from cal -> prod
# if found create a cew query based on steps and add it to crew and query data
# go through queries and update cal and query based on crew answers
# if crew answers no, do nothing, if yes ask next crew in chain or add to cal