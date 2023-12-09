from bs4 import BeautifulSoup
import requests
import time
import re

# zakladne url adresy
base_url = 'https://www.profesia.sk'
req_url = base_url + '/praca/?page_num='

offer_link_buffer = []


def get_work_page(link, firm_name):

    if not link in offer_link_buffer:
        
        res = requests.get(base_url + link)
        page = BeautifulSoup(res.content, "html.parser" )
        
        # odstran diakritiku
        name_offer = "raw_html/ponuky/" + re.sub("[^A-Za-z0-9šôáčďéíľĺňóôŕšťúýžŠČĎÉĽĹŇÓŔŤÚÝŽ]", '_', link) + ".html"
        
        f = open(name_offer, "w+", encoding="utf-8")
        f.write(str(page))
        f.close()

        offer_link_buffer.append(link)
        time.sleep(0.05)

    else:
        print("DUPLICATE")
        

def crawler():

    # i = int(input("Zadaj poziciu od 1: "))
    i = 1
    
    while True:

        # dostan celu stranku
        res = requests.get(req_url + str(i))
        page = BeautifulSoup(res.content, "html.parser" )

        # a zober si konkretny div
        page_list= page.find("div", class_="card no-padding-on-sides no-padding-on-bottom")
        
        if page_list is None : break

        # a najdi zlozku s linkami
        link_headers = page_list.find_all("li", class_="list-row")

       
        for header in link_headers:

            # link sa nachadza v <h2>
            link = header.find("h2").find("a")
            firm_name = header.find_all("span")[1].get_text()
            print(i, link['href'])
            print("\n")

            try:
                get_work_page(link['href'], firm_name)

            except:
                print("chyba")
    
        i = i + 1
        time.sleep(0.05)

crawler()