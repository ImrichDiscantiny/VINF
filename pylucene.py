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

from org.apache.lucene.search import IndexSearcher, Query
from org.apache.lucene.queryparser.classic import QueryParser

from java.nio.file import Paths


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


def get_settlement(text):
    match = re.search(r"settlement_type(.*?)\n", text)
    if match:
        match = match.group(1).split('=')[1]
        return re.sub(r"(\[\[|\]\])","", match)
    else:
        return " "


def add_xml_columns(record):
    
    title = title_cleaner( record["title"])
    settlement =  get_settlement(record["_VALUE"])
    text = text_cleaner(record["_VALUE"])
    
    print(title)
    print(text)
    document = Document()
    
    document.add(Field("title", title, StringField.TYPE_STORED))
    document.add(Field("settlement", settlement, StringField.TYPE_STORED))
    document.add(Field("text", text, TextField.TYPE_STORED))
    
    return document


def xml_indexer():

    # ak existuje priecinok s indexom vymaz a znova ho vytvor
    dir = 'index_xml'
    
    if os.path.exists(dir):
        shutil.rmtree(dir)
      
    os.makedirs(dir)
   
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
    exit()
    writer.commit()
    writer.close()     


def html_indexer():

    # ak existuje priecinok s indexom vymaz a znova ho vytvor
    dir = 'index_html'

    if os.path.exists(dir):
        shutil.rmtree(dir)
        
    os.makedirs(dir)

    data = open('Dataset.json', 'r').read() 
    dataset = json.loads(data)
   
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    store = NIOFSDirectory(Paths.get("index_html"))
    writer = IndexWriter(store, config)
    
    for record in dataset:
        split_end_tag = record["end_tags"].split('.', 1)
        loc =  split_end_tag[0].split(":",1)[1].strip()

        document = Document()
        document.add(Field("title", record["title"], TextField.TYPE_STORED))
        document.add(Field("text", record["text"], TextField.TYPE_STORED))
        document.add(Field("start_tags", record["tags"] if record["tags"] else "", TextField.TYPE_STORED))
        document.add(Field("location", loc, StringField.TYPE_STORED))
        document.add(Field("end_tags", split_end_tag[1], TextField.TYPE_NOT_STORED))
        
        writer.addDocument(document)
    
    print("done") 
    writer.commit()
    writer.close() 


def search_settlement(offer_doc):

    index = NIOFSDirectory(Paths.get("index_xml"))
    searcher = IndexSearcher(DirectoryReader.open(index))
    analyzer = StandardAnalyzer()

    query_parser = QueryParser("text", analyzer)

    query = query_parser.parse(offer_doc.get("location"))
    
    settlements = searcher.search(query, 10).scoreDocs
   
    
    for docs in settlements:
        doc = searcher.doc(docs.doc)
        print(f"Score: {docs.score}, Content: {doc.get('title')}")
    return  



def options_picker(options_list, options_print, searcher):
    
    while(True):

        for option, obj in enumerate(options_list):
            if options_print == "1":
                print(f"Option: {option + 1}, Field: {obj}")
            else:
                doc = searcher.doc(obj.doc)
                score = obj.score
                print(f"Option: {option + 1}, Score: {score}, Content: {doc.get('title')}")
        
        try:
            option = input("type number for field you want to search\pick: ")
            picked_option = options_list[int(option) - 1]
            return picked_option
        
        except ValueError:
            print("Fatal error or document index is out of range. Please enter a valid number.")
            continue


# Zatial funguje len na jeden doc. field nie viacero
def search_work():

    # fieldy ktore viem vyhladat
    work_offer_fiels = ["title", "text", "start_tags", "end_tags"]

    index = NIOFSDirectory(Paths.get("index_html"))
    searcher = IndexSearcher(DirectoryReader.open(index))
    analyzer = StandardAnalyzer()

    while(True):
        
         # fieldy ktore chcem vybrat
        picked_field = options_picker(work_offer_fiels, "1", searcher )
        print("\n")
        
        search_operator = input("type \"AND\" or \"OR\" or \"NO\" for query operator: ")
        query_parser = QueryParser(picked_field, analyzer)  

        if search_operator == "AND":
            query_parser.setDefaultOperator(QueryParser.Operator.AND)
        elif search_operator == "OR":
            query_parser.setDefaultOperator(QueryParser.Operator.OR)
        else:
            print("No Operator applicated")

        # vytvorenie query
        if search_operator ==  "AND" or search_operator ==  "OR":
            first_phrase = input("Write first phrase for searching: ")
            second_phrase = input("Write second phrase for searching: ")
            search_query = f'"{first_phrase}" {search_operator} "{second_phrase}"'
        
        else:
            phrase =  input("Write one phrase for searching: ")
            search_query = f'"{phrase}"'

        # spustenie query
        query = query_parser.parse(search_query)

        documents_offers = searcher.search(query, 4).scoreDocs
        
        doc_number=  options_picker(documents_offers, "2", searcher ).doc
        
        picked_doc = searcher.doc(doc_number)
        
        print(picked_doc.get("location") + "\n")
        search_settlement(picked_doc)
        return 

# Menu na inicializaciu programu - a to ndexaciu alebo vyhladavanie
def main():

    print("i - index files s - search q - quit program")
    
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    
    while(True):
        command = input("type a character: ")
        
        if command == "i":
            print("read html or xml json files -> h - html x - xml")
            fileRead = input("type a character: ")
            
            if fileRead == "h":
                html_indexer()
            
            elif fileRead == "x" :
                xml_indexer()
        
        elif command == "s" and os.path.isdir('index_html') and os.path.isdir("index_xml"):
            search_work()
            
        elif command == "q":
            print("Quitting..")
            return
        
        else:
            print("Try again or first create index with -i")


main()

