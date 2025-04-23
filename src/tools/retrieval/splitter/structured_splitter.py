import os
import pandas as pd
from .base_splitter import Splitter
from tools.retrieval.document import Document
from typing import Any


class StructuredSplitter(Splitter):
    def __init__(self):
        pass

    def split_text(self, text: str) -> list[Document]:
        pass


    def split_file(self, file_path:str, **kwargs: Any) -> list[Document]:
        """At present, the functions of the parser and the splitter are temporarily combined. 
        They will be decoupled if necessary in the future. """
        # 这是结构化解析器，首先要获取哪几个字段是有结构化的
        structured_fields = kwargs.get("structured_fields", set())
        # 然后判断文件是tsv, csv, xlsx的某一种，如果是这几种意外事件就报不支持类型的错误
        try:
            file_name = os.path.splitext(file_path)[0]
            file_extension = os.path.splitext(file_path)[1]
            if file_extension == ".tsv":
                df = pd.read_csv(file_path, sep="\t")
            elif file_extension== ".csv":
                df = pd.read_csv(file_path)
            elif file_extension == ".xlsx":
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type {file_extension}")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
        
        result_list = []
        # 遍历df
        for index, row in df.iterrows():
            # get page_content
            page_content = ', '.join([f"{col}:{val}" for col, val in row.items()])
            # get fileds
            field_values = [str(row[col]) for col in row.index if col in structured_fields]
            field_str = ', '.join(field_values)

            # get document
            doc = Document(
                page_content=page_content,
                metadata={
                    "source": file_path,
                    "vector_text": field_str,
                }
            )
            result_list.append(doc)
        return result_list
    
    def split_documents(self, documents, **kwargs):
        pass