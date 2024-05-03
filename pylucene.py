import os
import glob
import json
import re
import shutil
import lucene

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriterConfig, IndexWriter, DirectoryReader
from org.apache.lucene.document import Document, Field, TextField, StringField, IntPoint
from org.apache.lucene.store import NIOFSDirectory

from java.nio.file import Paths

from search import search_work


def text_cleaner(text):

    cleaned_text = re.sub(r"(\[\[|\]\])","", text)
    cleaned_text = re.sub(r"<ref>[\s\S]*?<\/ref>","", cleaned_text)
    cleaned_text = re.sub(r"<gallery>[\s\S]*?<\/gallery>","", cleaned_text)

    pattern = r'{{([^{}]*)}}'
    
    # odstran vsetko v {{}}
    while re.search(pattern, cleaned_text):
        cleaned_text = re.sub(pattern, "", cleaned_text)
    
    return cleaned_text


def title_cleaner(text):
    return re.sub(r"\(.*?\)", "", text)


def get_settlement_type(text):
    match = re.search(r"settlement_type(.*?)\n", text)
    if match:
        match = match.group(1).split('=')[1]
        return re.sub(r"(\[\[|\]\])","", match).lower()
    else:
        return " "


def get_settlement_region(text):
    match1 = re.search(r"subdivision_name1(.*?)\n", text)
    match2 = re.search(r"subdivision_name2(.*?)\n", text)

    if match1 and re.search(r"Region\|", match1.group(1)):
        match = match1.group(1)
    elif match2 and re.search(r"Region\|", match2.group(1)):
        match = match2.group(1)
    elif match2 is not None:
        match = match2.group(1)
    else:
        match = None
    
    if match:
        match = match.split('=')[1]
        match = re.sub(r"\[\[File:Coat of Arms of Bratislava Region.svg\|20px\]\]", "", match)
        match = re.sub(r"(\|)",", ", match)
        return re.sub(r"(\[\[|\]\])","", match).lower()
    else:
        return " "

def add_xml_columns(record):
    
    # vycisti text 
    title = title_cleaner( record["title"])
    settlement =  get_settlement_type(record["_VALUE"])
    settlement_region = get_settlement_region(record["_VALUE"])
    text = text_cleaner(record["_VALUE"])
    
    document = Document()
    
    document.add(Field("title", title, TextField.TYPE_STORED))
    document.add(Field("settlement", settlement, TextField.TYPE_STORED))
    document.add(Field("region", settlement_region, TextField.TYPE_STORED))
    document.add(Field("text", text, TextField.TYPE_STORED))
    
    return document


def xml_indexer():

    # ak existuje priecinok s indexom vymaz a znova ho vytvor
    dir = 'index_xml/*'
    files = glob.glob(dir)

    for f in files:
        os.remove(f)
   
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    store = NIOFSDirectory(Paths.get("index_xml"))
    writer = IndexWriter(store, config)
    
    # vyhladavanie vsetkych sparsovanych wiki dumpov
    os.chdir("wikiset")
    for file in glob.glob("*.json"):
        
        f_in = open(file,"r")

        for line in f_in:
            js = json.loads(line)
            doc = add_xml_columns(js)
            writer.addDocument(doc)
      
    print("done") 
   
    writer.commit()
    writer.close()     


def html_indexer():

    # ak existuje priecinok s indexom vymaz subory
    dir = 'index_html/*'
    files = glob.glob(dir)

    for f in files:
        os.remove(f)

    data = open('Dataset.json', 'r').read() 
    dataset = json.loads(data)
   
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    store = NIOFSDirectory(Paths.get("index_html"))
    writer = IndexWriter(store, config)
    
    for record in dataset:

        split_end_tag = record["end_tags"].split('.', 2)

        if  "Position:" in record["end_tags"]:

            location =  split_end_tag[0].split(":",1)[1].strip()
            profesions =  split_end_tag[1].split(":",1)[1].strip()
            company =  split_end_tag[2].split(":",1)[1].strip()
        else:

            location =  split_end_tag[0].split(":",1)[1].strip()
            profesions =  "  "
            company =  split_end_tag[1].split(":",1)[1].strip()
      
        document = Document()
        document.add(Field("title", record["title"], TextField.TYPE_STORED))
        document.add(Field("text", record["text"], TextField.TYPE_STORED))
        document.add(Field("start_tags", record["tags"] if record["tags"] else "", TextField.TYPE_STORED))
        document.add(Field("location", location, TextField.TYPE_STORED))
        document.add(Field("profesions", profesions.lower(), TextField.TYPE_STORED))
        document.add(Field("company", company[0:-1], TextField.TYPE_STORED))
       
        
        writer.addDocument(document)
    
    print("done")
    writer.commit()
    writer.close() 


class Unit1:
    def __init__(self, field, operator, first_phrase, second_phrase):
        self.field = field
        self.operator = operator
        self.first_phrase = first_phrase
        self.second_phrase = second_phrase


# Menu na inicializaciu programu - a to ndexaciu alebo vyhladavanie
def main():

    print("\ni -> index files, s -> search, q -> quit program\n")
    
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    
    while(True):
        command = input("type a character: ")
        
        if command == "i":

            print("\nread parsed html or xml files: h -> html, x -> xml: ")
            fileRead = input("type a character: ")
            
            if fileRead == "h":
                html_indexer()
            
            elif fileRead == "x" :
                xml_indexer()
        
        elif command == "s":

            u1 = Unit1('company', 'NONE', 'VOLKSWAGEN SLOVAKIA, a.s.', None)

            u2 = Unit1('profesions', 'AND', 'breeder', "agronomist")

            u3 = Unit1('title', 'AND', 'Junior', "Java")

            u4 = Unit1('company', 'NONE', 'ESET', None)

            search_work(u2)
            
        elif command == "q":
            print("Quitting..")
            return
        
        else:
            print("Try again or first create index with -i")


main()
