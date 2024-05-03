import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *


def xmlParser():

    xmlFile = "xml/enwiki-latest-pages-articles.xml.bz2"
    spark = SparkSession.builder \
    .appName("vinfXml") \
    .master("local[*]") \
    .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.17.0") \
    .getOrCreate()

    # schema df
    xml_schema = StructType([
        StructField("title", StringType(), True),
        StructField("revision", StructType([
            StructField("text", StructType([
                StructField("_VALUE", StringType(), True)
            ]), True)
        ]), True)
    ])

    df = spark.read.format('xml').options(rowTag='page').schema(xml_schema).load(xmlFile, format="xml")
    
    selected_df = df.select("title", "revision.text._VALUE")

    # filtrovanie na zaklade infoboxov
    selected_df_settlements = selected_df.filter(
        col("revision.text._VALUE").rlike(r"\{\{Infobox settlement[\s\S]*?(Slovakia|Slovak Republic)[\s\S]*?\r?\n\}\}\r?\n")
    )
   
    selected_df_settlements.coalesce(1).write.json("wikiset")
    
    spark.stop()

xmlParser()