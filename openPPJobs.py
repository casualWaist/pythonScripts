# file from local server and opens all relavent jobs on client system

import lookUpVox, os

data = lookUpVox.getJobList()
for piece in data:
    if piece['active'] is True:
        print(piece)
        for step in piece['steps']:
            if step['name'] == 'Print or Plot' and step['isCompleted'] == False:
                path = '//*/Public/JOBS'
                print(path + piece['name'])
                final = path + piece['name']
                try:
                    os.startfile(final.replace('/', '\\'))
                except:
                    print(piece['name'], 'file not found')
