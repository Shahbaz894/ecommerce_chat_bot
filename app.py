import pandas as pd
import numpy as np
from langchain_core.documents import Document

def load_data_file(file_path):
    data = pd.read_csv(file_path)
    product_list = []
    for index, row in data.iterrows():
        obj = {
            'product_name': row['product_title'],
            'review': row['review'],
            'rating': row['rating']
        }
        product_list.append(obj)
    
    docs = []
    for entry in product_list:
        metadata = {
            'product_name': entry['product_name'],
            'rating': entry['rating']
        }
        doc = Document(page_content=entry['review'], metadata=metadata)
        docs.append(doc)
    
    return docs