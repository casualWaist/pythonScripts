# calls a file hosted on local server and opens relevant jobs on the client system

import requests, json, os

url = 'http://192.168.0.12/prod/prodJobs.txt'
response = requests.get(url)
data = json.loads(response.content.decode('utf-8'))
for piece in data:
    if piece['active'] is True:
        for step in piece['steps']:
            if step['name'] == 'Knife Cut' and step['isCompleted'] == False:
                path = '//*/Public/JOBS/'
                print(path + piece['name'])
                final = path + piece['name']
                try:
                    os.startfile(final.replace('/', '\\'))
                except:
                    print(piece['name'], 'file not found')
