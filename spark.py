import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

def xmlParser():

    xmlFile = "xml/enwiki-latest-pages-articles1.xml-p1p41242"
    spark = SparkSession.builder \
    .appName("vinfXml") \
    .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.17.0") \
    .getOrCreate()


    df = spark.read.format('xml').options(rowTag='page').load(xmlFile)
    
    df = df.filter(col("redirect").isNull())
    df_filtered = df.filter(col("revision").isNotNull())
    
    selected_df = df_filtered.select("title", "revision.text._VALUE")
    
    selected_df_settlements = selected_df.where(
    col("title").isNotNull() &
    col("revision.text._VALUE").rlike("\\{\\{Infobox settlement[\\s\\S]*?\\}\\}")
)
    
    selected_df_settlements.coalesce(1).write.json("wikiset")
    # \{\{pp-semi-indef[\s\S][SVK|SK|Slovakia][\s\S]*?}}
    # df_filtered.select("revision.text._VALUE").filter(col("revision.text").isNotNull()).show(1, truncate=False)
    # df_filtered.select("title", "text._VALUE").filter(col("revision.text").isNotNull()).printSchema()
    # \{\{Infobox settlement[\s\S]*?(\bSVK\b|\bSvk\b|Slovakia)[\s\S]*?}}
    spark.stop()

xmlParser()