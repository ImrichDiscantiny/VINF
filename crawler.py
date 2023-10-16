from bs4 import BeautifulSoup
import requests
import time
import re


base_url = 'https://www.profesia.sk'
url = base_url + '/praca/?page_num='
work_link_buffer = []
about_link_buffer = []

def get_AboutUs(link):
    if not about_link_buffer in work_link_buffer:
        res = requests.get(base_url + link)
        page = BeautifulSoup(res.content)
        name_firm = "ponuky/" + re.sub("[^A-Za-z0-9šôáčďéíľĺňóôŕšťúýžŠČĎÉĽĹŇÓŔŤÚÝŽ]", '_', page.find("h1").get_text()) + ".html"

def get_work_page(link):

    if not link in work_link_buffer:
        res = requests.get(base_url + link)
        page = BeautifulSoup(res.content)
        
        name_offer = "firmy/" + re.sub("[^A-Za-z0-9šôáčďéíľĺňóôŕšťúýžŠČĎÉĽĹŇÓŔŤÚÝŽ]", '_', page.find("h1").get_text()) + ".html"
        
        f = open(name_offer, "w+", encoding="utf-8")
        f.write(str(page))
        f.close()
        work_link_buffer.append(link)
        time.sleep(0.05)

        card_offer = page.find("div", class_="card no-padding-on-sides no-padding-on-bottom")

        card_links = card_offer.find('nav').find('a', text="O nás")

        get_AboutUs(card_links['href'])



   

def main():

    i = 1
    while True:

        res = requests.get(url + str(i))
        page = BeautifulSoup(res.content)
        page_list= page.find("div", class_="card no-padding-on-sides no-padding-on-bottom")
       
       
        link_headers = page_list.find_all("h2")

        if len( link_headers) == 0 : break
       
        
        for header in link_headers:
            link = header.find("a")
            print(link['href'])
            
          
            get_work_page(link['href'])
           
       
    
        i = i + 1
        time.sleep(0.1)

       
        break





main()