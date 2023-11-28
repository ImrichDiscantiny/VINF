
import json
import re
import os
from googletrans import Translator

def get_header(input_string):
    return re.sub(r'<[\s\S]*?>', '', input_string)


# Zober cisty text z html, vsetko v <> bude vymazane a zaroven headery <li> budu nahradene pre lepsiu semantiku
def get_clean_text(main_content):
    main_content = re.sub(r"<h[2-6]>",'\n* ',main_content)
    main_content = re.sub(r"<\/h[2-6]>",' *\n',main_content)
    main_content = re.sub(r"<li>",'\n\t',main_content)
    main_content = re.sub(r"<\/li>",'\n',main_content)
    main_content = re.sub(r"<button[\s\S]*?<\/button>",'',main_content)
    main_content = re.sub(r"<img[\s\S]*?<\/img>",'',main_content)
    main_content = re.sub(r"<br>",'\n',main_content)
    main_content = re.sub(r"<.*?>",'',main_content)
    main_content = re.sub(r"<!--([\s\S]*?)-->",'',main_content)
    main_content = re.sub(r'\n{4,}','',main_content)

    
    return main_content

# Zober cisty text z html, vsetko v <> bude vymazane
def get_tags_info(main_tag):
    
    main_tag = re.search(r"<div class=\"padding-on-bottom overall-info\">([\s\S]*?)<\/div>", main_tag).group()
   
    tags = re.sub(r"<\/span>",';',main_tag)
    tags = re.sub(r"<strong>",'. ',tags)
    tags =re.sub(r'<\/a>', ', ', tags)
    tags = re.sub(r"<.*?>",'',tags)
    tags =re.sub(r'\n+', ' ', tags).strip()
    tags = re.search(r"lokalita: (.*?) ;", tags).group().strip()
    tags =re.sub(r', ,', ', ', tags).strip()
    tags = re.sub(r",    .",'. ',tags)
   
    return tags


def create_header(main_tag):
    panel_body_tags = re.search(r"<div class=\".*panel.*\">([\s\S]*?)<h[2-4]", main_tag)
    
    if panel_body_tags:
        tags = re.sub(r"<.*?>",'',panel_body_tags.group())
        tags =re.sub(r'\n+', ', ', tags).strip()
        tags =re.sub(r'\s+', ' ', tags).strip()
        tags =re.sub(r', ,', ', ', tags).strip()
        length = len(tags)
        return tags[1:(length - 4)]
    else: return None


def offer_parser():

    ponuky_path = "raw_html/ponuky/"
    json_obj = []
    translator= Translator()
    
    for num, raw_file in enumerate(os.listdir(ponuky_path)):
        print(num, raw_file)
        html = open(ponuky_path + raw_file, "r", encoding="utf-8").read()
        
        main_tag = re.search(r"<main[\s\S]*?<\/main>", html).group()

        # main header
        try:
            main_h1 = get_header(re.search(r"<h1.*?>([\s\S]*?)<\/h1>", main_tag).group())
        except:
            continue # skip ak h1 neexistuje

        start_tags = create_header(main_tag)
        
        end_tags = get_tags_info(main_tag)

        # dostan cast webstranky kde zacinaju informacie o pracovnej ponuke
        main_content = re.search(r"<h[2-6]>([\s\S]*?)<div class=\"padding-on-bottom overall-info\">", main_tag)

        # Ak nema standartnu strukturu zober vsetko od <h1> 
        if not main_content:
            main_content = re.search(r"<h1.*?>([\s\S]*?)<div class=\"padding-on-bottom overall-info\">", main_tag)
            main_content = get_clean_text(main_content.group())
            start_tags = None

        else:
            main_content = get_clean_text(main_content.group())

        # output = main_h1 + "\n" + main_content + "\n" + main_tags if main_tags else main_location
       
      

        chunks = len(main_content)

        # Rozdel prilis velky text na chunky a potom ich naraz posli na preklad v jednom http
        
        main_content_list = [main_content[i:i+2000] for i in range(0, chunks, 2000) ]
        main_content_list = translator.translate(main_content_list, src='sk', dest='en')
        main_text_content = ''.join([o.text for o in main_content_list])

        # tiez naraz posli tagy a nadpis ponuky na preklad v jednom http volani
        header_content = translator.translate([main_h1, end_tags], src='sk', dest='en')

        js = {
            "id": num,
            "title": header_content[0].text ,
            "tags": translator.translate(start_tags, src='sk', dest='en').text  if start_tags else None,
            "text": main_text_content,
            "end_tags":  header_content[1].text
        }
       
        json_obj.append(js)
    
    with open("Dataset.json", "w",encoding='utf-8') as f:
        json.dump(json_obj, f, indent=4, ensure_ascii=False)
        

   
 

    return



offer_parser()