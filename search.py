import os

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriterConfig, IndexWriter, DirectoryReader
from org.apache.lucene.search import IndexSearcher, Query
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import NIOFSDirectory
from java.nio.file import Paths


# funkcia pre vypis a vyber moznosti
def options_picker(options_list, options_print, searcher):
    
    while(True):

        for option, obj in enumerate(options_list):
            if options_print == "1":
                print(f"Option: {option + 1}, Field: {obj}")
        
        try:
            option = input("\ntype number for field you want to search\pick: ")
            picked_option = options_list[int(option) - 1]
            print("\n")
            return picked_option
        
        except ValueError:
            print("Fatal error or document index is out of range. Please enter a valid number.\n")
            continue


def  count_regions(regions_list, region):

  
    if region is None or region == " ":
        return regions_list
    
    for obj in regions_list:
        if obj['region'] == region:
            obj['count'] =  obj['count'] + 1
            return regions_list

    regions_list.append({'region': region, 'count': 1})
    
    return regions_list
    
    

# Zatial funguje len na jeden doc. field nie viacero
def search_work(unit):

    # fieldy ktore viem vyhladat
    work_offer_fiels = ["title", "text", "start_tags", "profesions", "company"]

    index = NIOFSDirectory(Paths.get("index_html"))
    searcher = IndexSearcher(DirectoryReader.open(index))
    analyzer = StandardAnalyzer()
        
    while(True):
        
        if unit is None:
            # fieldy ktore chcem vybrat
            picked_field = options_picker(work_offer_fiels, "1", searcher )
          
            search_operator = input("type \"AND\" or \"OR\" or \"NO\" for query operator: ")

            # vytvorenie query
            if search_operator == "AND" or search_operator == "OR":
                first_phrase = input("Write first phrase for searching: ")
                second_phrase = input("Write second phrase for searching: ")
                search_query = f'"{first_phrase}" {search_operator} "{second_phrase}"'
            
            else:
                phrase =  input("Write one phrase for searching: ")
                search_query = f'"{phrase}"'

        # unit test exists
        else:
            picked_field = unit.field
            search_operator = unit.operator
            
            # vytvorenie query
            if search_operator == "AND" or search_operator == "OR":
                first_phrase = unit.first_phrase
                second_phrase = unit.second_phrase
                search_query = f'"{first_phrase}" {search_operator} "{second_phrase}"'
            
            else:
                phrase =  unit.first_phrase
                search_query = f'"{phrase}"' 
       
        query_parser = QueryParser(picked_field, analyzer)  

        
        if search_operator == "AND":
            query_parser.setDefaultOperator(QueryParser.Operator.AND)
        elif search_operator == "OR":
            query_parser.setDefaultOperator(QueryParser.Operator.OR)
        else:
            search_operator = "NONE"
            print("No Operator applicated")

        
        # spustenie query
        query = query_parser.parse(search_query)

        documents_offers = searcher.search(query, 50).scoreDocs
        
        grouped_regions = []
        
        for option, obj in enumerate(documents_offers):
          
            doc = searcher.doc(obj.doc)
            score = obj.score
            
            print(f"Number: {option + 1}, Score: {score}, Title: {doc.get('title')}, Location: {doc.get('location')}")
            
            region = search_settlement(doc.get('location'))
            grouped_regions = count_regions(grouped_regions, region)
        
        print("\n")
        for obj in grouped_regions:
            print(f"Region: {obj['region']}, Count: {obj['count']}")
        
        repeat = input("Repeat again?(y/n)")

        if repeat == "y": continue

        return 


def search_settlement(record):

    index = NIOFSDirectory(Paths.get("index_xml"))
    searcher = IndexSearcher(DirectoryReader.open(index))
    analyzer = StandardAnalyzer()

    
    query_parser = QueryParser("title", analyzer)

    query = query_parser.parse(record)
    
    settlements = searcher.search(query, 1).scoreDocs
    
    for docs in settlements:
        doc = searcher.doc(docs.doc)
        
        return  doc.get('region')
    
    return 