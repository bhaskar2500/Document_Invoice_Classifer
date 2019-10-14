from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy import insert
from sqlalchemy.sql import text

def getExtractedData(predicted_text):
    engine = create_engine('postgres://postgres:Admin@localhost:5432/postgres',echo=False)
    conn = engine.connect()
    sqlInsertExtractedData = text('INSERT INTO public.tbl_invoice_data(extracted_data) VALUES (:extracted_data)')
    conn.execute(sqlInsertExtractedData,extracted_data=predicted_text)
    # detail = pd.read_sql("select * from  public.tbl_invoice_data",engine)
getExtractedData('invoice data')