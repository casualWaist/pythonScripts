import requests, json, os

url = 'http://*/prod/prodJobs.txt'
response = requests.get(url)
data = json.loads(response.content.decode('utf-8'))
for piece in data:
    if piece['active'] is True:
        for step in piece['steps']:
            if step['name'] == 'Route Parts' and step['isCompleted'] == False:
                path = '//*/home/JOBS/'
                print(path + piece['name'])
                final = path + piece['name']
                try:
                    os.startfile(final.replace('/', '\\'))
                except:
                    print(piece['name'], 'file not found')
