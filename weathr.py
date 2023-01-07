# scraps weather images off local news sites for display on the screen showing todays jobs

from bs4 import BeautifulSoup as BS
import requests

URL = 'https://www.wwltv.com/weather'
page = requests.get(URL)

soup = BS(page.content, 'html.parser')

div = soup.find('div', {'class': 'weather-10-day'})
#jsons = soup.find('script')
#print(jsons)

chilren = div.findChildren("div", recursive=False)
html = ''''''
for child in chilren:
    for img in child.find_all("img"):
        if '/assets/shared-images/weather-icons/' in img['src']:
            img['src'] = img['src'].replace('/assets/shared-images/weather-icons/', '/today/images/')
        if '/assets/shared-images/backgrounds/' in img['src']:
            img['src'] = img['src'].replace('/assets/shared-images/backgrounds/', '/today/images/')
        if '_8x8' in img['src']:
            img['src'] = img['src'].replace('_8x8', '_64x64')
    for temp in child.find_all("template"):
        temp.name = 'div'
    html += str(child)
with open('/var/www/html/today/wtest.html', 'w') as j:
    j.write(str(html))
