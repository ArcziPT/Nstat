#parse data from https://www.nirsoft.net/countryip/
#to obtain ip address ranges for continents

import requests
from bs4 import BeautifulSoup

URL = 'https://www.nirsoft.net/countryip/'
#get html
page = requests.get(URL)

#parse html
soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find('table', cellspacing=12)
results = table.find_all('a')


#ip ranges for every country
country_ips = {}
for result in results:
    #get link
    #change html to csv
    link = result.get('href').replace("html", "csv")
    
    #get ip ranges page
    subpage = requests.get(URL + link)
    
    print(result.text)
    #parse csv
    ip_ranges = []
    temp = subpage.text.replace('\r', '').split('\n')
    lines = [i for i in temp if i]
    for line in lines:
        cols = line.split(',')
        #ip range from cols[0] to cols[1]
        ip_ranges.append([cols[0], cols[1]])

    country_ips[result.text] = ip_ranges


#save to file
file = open("ip_ranges.csv", "a")
for country, ranges in country_ips.items():
    for range in ranges:
        begin, end = range
        file.write(str(begin))
        file.write(',')
        file.write(str(end))
        file.write(';')
        file.write(str(country))
        file.write('\n')
file.close()