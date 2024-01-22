import pandas as pd

document_dataframe = pd.read_csv("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/resources/woo_documents.csv.gz").set_index('dc_identifier')
k = document_dataframe[document_dataframe['foi_pdfCreator'] == 'Microsoft® Word 2013'].dc_source.to_csv('output_file.txt', sep='\t', index=False)
print(k)