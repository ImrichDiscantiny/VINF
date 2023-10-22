
import json
import re
import os


def get_text(input_string):
    return re.sub(r'<[\s\S]*?>', '', input_string)



def offer_parser():

    ponuky_path = "raw_html/ponuky/"

    for raw_file in os.listdir(ponuky_path):
        print(raw_file)
        html = open(ponuky_path + raw_file, "r", encoding="utf-8").read()
        
        main_tag = re.search(r"<main[\s\S]*?<\/main>", html).group()
        
        main_tag = re.sub("<nav[\s\S]*?nav>", "", main_tag)

        # header
        main_h1 = get_text(re.search(r"<h1 class=\".*?\">([\s\S]*?)<\/h1>", main_tag).group())
        
        panel_body_tags = re.search(r"<div class=\"panel-body\">([\s\S]*?)<h[2-4]", main_tag)

        if panel_body_tags:
        
            tag_keys = re.findall( r"<div class=\"upper-info-box-title.*?\">([\s\S]*?)<\/div>" ,panel_body_tags.group())

            if not tag_keys:
                tag_keys = re.findall( r"<strong>([\s\S]*?)<\/strong>" ,panel_body_tags.group())
        
          
            
            tag_values = re.findall( r"<span class=\".*?\">([\s\S]*?)<\/span>" ,panel_body_tags.group())

        
        main_content = re.search(r"<h[2-6]>([\s\S]*?)<div class=\"padding-on-bottom overall-info\">", main_tag).group()
        main_content = re.sub(r"<h2>",'\n* ',main_content)
        main_content = re.sub(r"<\/h2>",' *\n',main_content)
        main_content = re.sub(r"<h3>",'\n* ',main_content)
        main_content = re.sub(r"<\/h3>",' *\n',main_content)
        main_content = re.sub(r"<h4>",'\n* ',main_content)
        main_content = re.sub(r"<\/h4>",' *\n',main_content)
        main_content = re.sub(r"<h5>",'\n* ',main_content)
        main_content = re.sub(r"<\/h5>",' *\n',main_content)
        main_content = re.sub(r"<li>",'\n\t',main_content)
        main_content = re.sub(r"<\/li>",'\n',main_content)
        main_content = re.sub(r"<button[\s\S]*?<\/button>",'',main_content)
        main_content = re.sub(r"<img[\s\S]*?<\/img>",'',main_content)
        main_content = re.sub(r"<.*?>",'',main_content)

        print(main_content)


       
        break

        
        

    return



offer_parser()