import os
import glob
import json
import lucene

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriterConfig, IndexWriter, DirectoryReader
from org.apache.lucene.document import Document, Field, TextField, StringField, IntPoint
from org.apache.lucene.store import NIOFSDirectory

from org.apache.lucene.search import IndexSearcher, Query
from org.apache.lucene.queryparser.classic import QueryParser

from java.nio.file import Paths

def index_xml_columns(record):
    record
    return
    document = Document()
    document.add(Field("title", record["title"], TextField.TYPE_STORED))
    document.add(Field("text", record["_VALUE"], TextField.TYPE_STORED))
    
    
    return document


def index_html_columns(record, num):
    split_end_tag = record["end_tags"].split('.', 1)
    loc =  split_end_tag[0].split(":",1)[1].strip()
  
    document = Document()
    document.add(Field("title", record["title"], TextField.TYPE_STORED))
    document.add(Field("text", record["text"], TextField.TYPE_STORED))
    document.add(Field("start_tags", record["tags"] if record["tags"] else "", TextField.TYPE_STORED))
    document.add(Field("location", loc, StringField.TYPE_STORED))
    document.add(Field("end_tags", split_end_tag[1], TextField.TYPE_NOT_STORED))
    
    return document


def xml_indexer():
   
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    store = NIOFSDirectory(Paths.get("index"))
    writer = IndexWriter(store, config)
    
    os.chdir("wikiset")
    for file in glob.glob("*.json"):
        
        f_in = open(file,"r")

        for line in f_in:
            js = json.loads(line)
            print(js["title"])
            return
        # doc = index_file(record, num)
        # writer.addDocument(doc)
    
    print("done") 
    writer.commit()
    writer.close()     


def html_indexer():
    data = open('Dataset.json', 'r').read() 
    dataset = json.loads(data)
   
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    store = NIOFSDirectory(Paths.get("index"))
    writer = IndexWriter(store, config)
    
    for num, record in enumerate(dataset):
        doc = index_html_columns(record, num)
        writer.addDocument(doc)
    
    print("done") 
    writer.commit()
    writer.close() 


def search():
    print("ddd")
    operator = "and"

    index = NIOFSDirectory(Paths.get("index_html"))
    searcher = IndexSearcher(DirectoryReader.open(index))

    analyzer = StandardAnalyzer()
    query_parser = QueryParser("title", analyzer)
    query_parser.setDefaultOperator(QueryParser.Operator.AND)
    query = query_parser.parse("Junior AND Java")
    
    top_docs = searcher.search(query, 10).scoreDocs

    for docs in top_docs:
        doc = searcher.doc(docs.doc)
        print(f"Score: {docs.score}, Content: {doc.get('title')}")
    return


def pylucene():

    print("i - index files s - search q - quit program")
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    while(True):
        command = input("type a character: ")
        if command == "i":
            print("read html or xml json files h - html x - xml")
            fileRead = input("type a character: ")
            if fileRead == "h":
                html_indexer()
            else:
                xml_indexer()
        elif command == "s":
            search()
        elif command == "q":
            print("Quitting..")

            return
        else:
            print("Try again")


pylucene()

