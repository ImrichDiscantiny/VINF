from bs4 import BeautifulSoup
import requests
import time
import re

base_url = 'https://www.profesia.sk'
url = base_url + '/praca/?page_num='

offer_link_buffer = []
company_link_buffer = []


def get_AboutUs(link, firm_name):

    if not link in company_link_buffer:

        global company_i

        res = requests.get(base_url + link)
        page = BeautifulSoup(res.content, "html.parser" )
        name_firm = "firmy/" + re.sub("[^A-Za-z0-9šôáčďéíľĺňóôŕšťúýžŠČĎÉĽĹŇÓŔŤÚÝŽ]", '_', firm_name) + ".html"

         
        f = open(name_firm, "w+", encoding="utf-8")
        f.write(str(page))
        f.close()

        company_link_buffer.append(link)

        time.sleep(0.1)



def get_work_page(link, firm_name):

    if not link in offer_link_buffer:
        
        res = requests.get(base_url + link)
        page = BeautifulSoup(res.content, "html.parser" )
        
        name_offer = "ponuky/" + re.sub("[^A-Za-z0-9šôáčďéíľĺňóôŕšťúýžŠČĎÉĽĹŇÓŔŤÚÝŽ]", '_', link) + ".html"
        
        f = open(name_offer, "w+", encoding="utf-8")
        f.write(str(page))
        f.close()

        offer_link_buffer.append(link)
        time.sleep(0.05)


        offer_page = page.find("div", class_="card card-content")

        nav_link = offer_page.find('nav')
        div_link = offer_page.find("ul")

        try:
            if nav_link: 
                
                a_list = nav_link.find_all('a')

                for a in a_list:
                    
                    if a.string and a.string.lower() in "o\xa0nás":
                        print(firm_name)
                        print("\n")
                        get_AboutUs(a['href'], firm_name)
                

            elif div_link:
                
                a_list = div_link.find_all('a')

                for a in a_list:
                    
                    if a.string and a.string.lower() in "o\xa0nás":
                        get_AboutUs(a['href'], firm_name)
        
        except:
            print("chyba")
            
    else:
        print("DUPLICATE")
        

def main():

    i = int(input("Zadaj poziciu: "))

    while True:

        res = requests.get(url + str(i))
        page = BeautifulSoup(res.content, "html.parser" )
        page_list= page.find("div", class_="card no-padding-on-sides no-padding-on-bottom")
       
       
        link_headers = page_list.find_all("li", class_="list-row")

        if len( link_headers) == 0 : break
       
        for header in link_headers:

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

main()