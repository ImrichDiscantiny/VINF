
import json
import re
import os


# class Offer:
#     set(): 
#         return

def get_header(input_string):
    return re.sub(r'<[\s\S]*?>', '', input_string)


def get_text(main_content):
    main_content = re.sub(r"<h[2-6]>",'\n* ',main_content)
    main_content = re.sub(r"<\/h[2-6]>",' *\n',main_content)
    main_content = re.sub(r"<li>",'\n\t',main_content)
    main_content = re.sub(r"<\/li>",'\n',main_content)
    main_content = re.sub(r"<button[\s\S]*?<\/button>",'',main_content)
    main_content = re.sub(r"<img[\s\S]*?<\/img>",'',main_content)
    main_content = re.sub(r"<br>",'\n',main_content)
    main_content = re.sub(r"<.*?>",'',main_content)
    main_content = re.sub(r"<!--([\s\S]*?)-->",'',main_content)
    
    return main_content

def create_tags2(main_tag):
    
    main_tag = re.search(r"<div class=\"padding-on-bottom overall-info\">([\s\S]*?)<\/div>", main_tag).group()
   
    tags = re.sub(r"<\/span>",';',main_tag)
    tags =re.sub(r'<\/a>', ', ', tags)
    tags = re.sub(r"<.*?>",'',tags)
    tags =re.sub(r'\n+', ' ', tags).strip()
    tags = re.search(r"lokalita: (.*?) ;", tags).group().strip()
    tags =re.sub(r', ,', ', ', tags).strip()
   
    return tags



def create_tags(main_tag):
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

    for num, raw_file in enumerate(os.listdir(ponuky_path)):
        print(num, raw_file)
        html = open(ponuky_path + raw_file, "r", encoding="utf-8").read()
        
        main_tag = re.search(r"<main[\s\S]*?<\/main>", html).group()

        # header
        try:
            main_h1 = get_header(re.search(r"<h1.*?>([\s\S]*?)<\/h1>", main_tag).group())
        except:
            continue

        main_tags = create_tags(main_tag)
        
        main_tags2 = create_tags2(main_tag)


      
        main_content = re.search(r"<h[2-6]>([\s\S]*?)<div class=\"padding-on-bottom overall-info\">", main_tag)

        if not main_content:
            main_content = re.search(r"<h1.*?>([\s\S]*?)<div class=\"padding-on-bottom overall-info\">", main_tag)
            main_content = get_text(main_content.group())
            main_tags = None

        else:
            main_content = get_text(main_content.group())

        js = {
            "title":main_h1,
            "tags": main_tags,
            "text": main_content,
            "end_tags": main_tags2
        }
       
        json_obj.append(js)
        #print(json_obj)
        # print(main_content)

    with open("Dataset.json", "w",encoding='utf-8') as f:
        json.dump(json_obj, f, indent=4, ensure_ascii=False)

       
        

        
        

    return



offer_parser()