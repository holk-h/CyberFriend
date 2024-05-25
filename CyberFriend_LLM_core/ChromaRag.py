# -*- coding: utf-8 -*-
import hashlib
import importlib
import os
import sys
import uuid
from typing import Literal, List, Dict, Tuple

import chardet
import chromadb
import langchain
import numpy as np
from chromadb import QueryResult
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from nonebot import logger

sys.path.append(os.path.join(os.path.dirname(__file__), '../CyberFriend_bot_plugin'))
from CyberFriend_bot_plugin.GetPathUtil import getPath

import threading

EMBEDDING_MODEL = "bge-large-zh"

TEXT_SPLITTER_NAME = "ChineseRecursiveTextSplitter"

# 知识库中单段文本长度(不适用MarkdownHeaderTextSplitter)
CHUNK_SIZE = 250
# 知识库中相邻文本重合长度(不适用MarkdownHeaderTextSplitter)
OVERLAP_SIZE = 50
# 知识库匹配向量数量
VECTOR_SEARCH_TOP_K = 3
# 知识库匹配的距离阈值，一般取值范围在0-1之间，SCORE越小，距离越小从而相关度越高。
# 但有用户报告遇到过匹配分值超过1的情况，为了兼容性默认设为1，在WEBUI中调整范围为0-2
SCORE_THRESHOLD = 1.0

# TextSplitter配置项，如果你不明白其中的含义，就不要修改。
text_splitter_dict = {
    "ChineseRecursiveTextSplitter": {
        "source": "huggingface",  # 选择tiktoken则使用openai的方法
        "tokenizer_name_or_path": "",
    },
    "SpacyTextSplitter": {
        "source": "huggingface",
        "tokenizer_name_or_path": "gpt2",
    },
    "RecursiveCharacterTextSplitter": {
        "source": "tiktoken",
        "tokenizer_name_or_path": "cl100k_base",
    },
    "MarkdownHeaderTextSplitter": {
        "headers_to_split_on":
            [
                ("#", "head1"),
                ("##", "head2"),
                ("###", "head3"),
                ("####", "head4"),
            ]
    },
}


def detect_device() -> Literal["cuda", "mps", "cpu"]:
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
    except:
        pass
    return "cpu"


def normalize(embeddings: List[List[float]]) -> np.ndarray:
    '''
    sklearn.preprocessing.normalize 的替代（使用 L2），避免安装 scipy, scikit-learn
    '''
    norm = np.linalg.norm(embeddings, axis=1)
    norm = np.reshape(norm, (norm.shape[0], 1))
    norm = np.tile(norm, (1, len(embeddings[0])))
    return np.divide(embeddings, norm)


def encrypt(fpath: str, algorithm: str = "md5") -> str:
    hash_algorithm = None
    if algorithm is not None and isinstance(algorithm, str):
        algorithm = algorithm.lower()

    if algorithm == 'md5':
        hash_algorithm = hashlib.md5()
    elif algorithm == 'sha1':
        hash_algorithm = hashlib.sha1()
    elif algorithm == 'sha256':
        hash_algorithm = hashlib.sha256()
    else:
        raise ValueError("unsupported hash algorithm")
    # 以二进制模式打开文件
    with open(fpath, 'rb') as f:
        # 分块读取文件内容
        for chunk in iter(lambda: f.read(2 ** 12), b''):
            # 更新散列值
            hash_algorithm.update(chunk)
    # 返回十六进制字符串
    return hash_algorithm.hexdigest()


def encryptText(texts: List[str], algorithm: str = "md5") -> List[str]:
    hash_algorithm = None
    if algorithm is not None and isinstance(algorithm, str):
        algorithm = algorithm.lower()
    ans = []
    for text in texts:
        if algorithm == 'md5':
            hash_algorithm = hashlib.md5()
        elif algorithm == 'sha1':
            hash_algorithm = hashlib.sha1()
        elif algorithm == 'sha256':
            hash_algorithm = hashlib.sha256()
        else:
            raise ValueError("unsupported hash algorithm")
        hash_algorithm.update(text.encode())
        ans.append(hash_algorithm.hexdigest())
    return ans


class WordEmbeddingModel:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, embed_model=EMBEDDING_MODEL, device=detect_device()):
        if not hasattr(self, 'initialized'):
            self.model = HuggingFaceEmbeddings(model_name=embed_model,
                                               model_kwargs={'device': device})
            self.initialized = True


def make_text_splitter(
        splitter_name: str = TEXT_SPLITTER_NAME,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = OVERLAP_SIZE,
):
    """
    根据参数获取特定的分词器
    """
    splitter_name = splitter_name or "SpacyTextSplitter"
    try:
        if splitter_name == "MarkdownHeaderTextSplitter":  # MarkdownHeaderTextSplitter特殊判定
            headers_to_split_on = text_splitter_dict[splitter_name]['headers_to_split_on']
            text_splitter = langchain.text_splitter.MarkdownHeaderTextSplitter(
                headers_to_split_on=headers_to_split_on)
        else:

            try:  ## 优先使用用户自定义的text_splitter
                text_splitter_module = importlib.import_module('text_splitter')
                TextSplitter = getattr(text_splitter_module, splitter_name)
            except:  ## 否则使用langchain的text_splitter
                text_splitter_module = importlib.import_module('langchain.text_splitter')
                TextSplitter = getattr(text_splitter_module, splitter_name)

            if text_splitter_dict[splitter_name]["source"] == "tiktoken":  ## 从tiktoken加载
                try:
                    text_splitter = TextSplitter.from_tiktoken_encoder(
                        encoding_name=text_splitter_dict[splitter_name]["tokenizer_name_or_path"],
                        pipeline="zh_core_web_sm",
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                except:
                    text_splitter = TextSplitter.from_tiktoken_encoder(
                        encoding_name=text_splitter_dict[splitter_name]["tokenizer_name_or_path"],
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
            elif text_splitter_dict[splitter_name]["source"] == "huggingface":  ## 从huggingface加载
                if text_splitter_dict[splitter_name]["tokenizer_name_or_path"] == "":
                    text_splitter_dict[splitter_name]["tokenizer_name_or_path"] = EMBEDDING_MODEL

                if text_splitter_dict[splitter_name]["tokenizer_name_or_path"] == "gpt2":
                    from transformers import GPT2TokenizerFast
                    from langchain.text_splitter import CharacterTextSplitter
                    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
                else:  ## 字符长度加载
                    from transformers import AutoTokenizer
                    tokenizer = AutoTokenizer.from_pretrained(
                        text_splitter_dict[splitter_name]["tokenizer_name_or_path"],
                        trust_remote_code=True)
                text_splitter = TextSplitter.from_huggingface_tokenizer(
                    tokenizer=tokenizer,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            else:
                try:
                    text_splitter = TextSplitter(
                        pipeline="zh_core_web_sm",
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                except:
                    text_splitter = TextSplitter(
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
    except Exception as e:
        print(e)
        text_splitter_module = importlib.import_module('langchain.text_splitter')
        TextSplitter = getattr(text_splitter_module, "RecursiveCharacterTextSplitter")
        text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # If you use SpacyTextSplitter you can use GPU to do split likes Issue #1287
    # text_splitter._tokenizer.max_length = 37016792
    # text_splitter._tokenizer.prefer_gpu()
    return text_splitter


LOADER_DICT = {"UnstructuredHTMLLoader": ['.html', '.htm'],
               "MHTMLLoader": ['.mhtml'],
               "UnstructuredMarkdownLoader": ['.md'],
               "JSONLoader": [".json"],
               "JSONLinesLoader": [".jsonl"],
               "CSVLoader": [".csv"],
               # "FilteredCSVLoader": [".csv"], 如果使用自定义分割csv
               "RapidOCRPDFLoader": [".pdf"],
               "RapidOCRDocLoader": ['.docx', '.doc'],
               "RapidOCRPPTLoader": ['.ppt', '.pptx', ],
               "RapidOCRLoader": ['.png', '.jpg', '.jpeg', '.bmp'],
               "UnstructuredFileLoader": ['.eml', '.msg', '.rst',
                                          '.rtf', '.txt', '.xml',
                                          '.epub', '.odt', '.tsv'],
               "UnstructuredEmailLoader": ['.eml', '.msg'],
               "UnstructuredEPubLoader": ['.epub'],
               "UnstructuredExcelLoader": ['.xlsx', '.xls', '.xlsd'],
               "NotebookLoader": ['.ipynb'],
               "UnstructuredODTLoader": ['.odt'],
               "PythonLoader": ['.py'],
               "UnstructuredRSTLoader": ['.rst'],
               "UnstructuredRTFLoader": ['.rtf'],
               "SRTLoader": ['.srt'],
               "TomlLoader": ['.toml'],
               "UnstructuredTSVLoader": ['.tsv'],
               "UnstructuredWordDocumentLoader": ['.docx', '.doc'],
               "UnstructuredXMLLoader": ['.xml'],
               "UnstructuredPowerPointLoader": ['.ppt', '.pptx'],
               "EverNoteLoader": ['.enex'],
               }


def get_LoaderClass(file_extension):
    for LoaderClass, extensions in LOADER_DICT.items():
        if file_extension in extensions:
            return LoaderClass


SUPPORTED_EXTS = [ext for sublist in LOADER_DICT.values() for ext in sublist]


def get_loader(loader_name: str, file_path: str, loader_kwargs: Dict = None):
    '''
    根据loader_name和文件路径或内容返回文档加载器。
    '''
    loader_kwargs = loader_kwargs or {}
    try:
        if loader_name in ["RapidOCRPDFLoader", "RapidOCRLoader", "FilteredCSVLoader",
                           "RapidOCRDocLoader", "RapidOCRPPTLoader"]:
            document_loaders_module = importlib.import_module('document_loaders')
        else:
            document_loaders_module = importlib.import_module('langchain_community.document_loaders')
        DocumentLoader = getattr(document_loaders_module, loader_name)
    except Exception as e:
        msg = f"为文件{file_path}查找加载器{loader_name}时出错：{e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e)
        document_loaders_module = importlib.import_module('langchain_community.document_loaders')
        DocumentLoader = getattr(document_loaders_module, "UnstructuredFileLoader")

    if loader_name == "UnstructuredFileLoader":
        loader_kwargs.setdefault("autodetect_encoding", True)
    elif loader_name == "CSVLoader":
        if not loader_kwargs.get("encoding"):
            # 如果未指定 encoding，自动识别文件编码类型，避免langchain loader 加载文件报编码错误
            with open(file_path, 'rb') as struct_file:
                encode_detect = chardet.detect(struct_file.read())
            if encode_detect is None:
                encode_detect = {"encoding": "utf-8"}
            loader_kwargs["encoding"] = encode_detect["encoding"]

    elif loader_name == "JSONLoader":
        loader_kwargs.setdefault("jq_schema", ".")
        loader_kwargs.setdefault("text_content", False)
    elif loader_name == "JSONLinesLoader":
        loader_kwargs.setdefault("jq_schema", ".")
        loader_kwargs.setdefault("text_content", False)

    loader = DocumentLoader(file_path, **loader_kwargs)
    return loader


class ChromaRag:

    def __init__(self, dbpath=getPath("knowledge_db", "default"), llm=None, embed_model=EMBEDDING_MODEL):
        self.client = chromadb.PersistentClient(path=dbpath)
        self.defaultCollection = self.client.get_or_create_collection("default")
        self.collection = {"default": self.defaultCollection}
        self.embed_model = embed_model
        self.word_embedding_model = None

    def loadWordEmbeddingModel(self):
        self.word_embedding_model = WordEmbeddingModel(embed_model=self.embed_model)

    def embedding(self, texts: List[str]) -> List[List[float]]:
        if self.word_embedding_model is None:
            self.loadWordEmbeddingModel()
        return self.word_embedding_model.model.embed_documents(texts=texts)

    def embeddingDocs(self, docs):
        texts = [x.page_content for x in docs]
        metadatas = [x.metadata for x in docs]
        if self.word_embedding_model is None:
            self.loadWordEmbeddingModel()
        embeddings = normalize(self.word_embedding_model.model.embed_documents(texts)).tolist()
        # embeddings = embed_texts(texts=texts, embed_model=embed_model, to_query=to_query).data
        if embeddings is not None:
            return {
                "texts": texts,
                "embeddings": embeddings,
                "metadatas": metadatas,
            }

    def search(self, msg, top_k: int = VECTOR_SEARCH_TOP_K, collectionName="default", score_threshold: float = SCORE_THRESHOLD) -> List[
        Tuple[Document, float]]:
        embeddings = self.embedding([msg])[0]
        collection = self.collection.get(collectionName, self.defaultCollection)
        query_result: QueryResult = collection.query(query_embeddings=embeddings, n_results=top_k)
        return [
            # TODO: Chroma can do batch querying,
            (Document(page_content=result[0], metadata=result[1] or {}), result[2])
            for result in zip(
                query_result["documents"][0],
                query_result["metadatas"][0],
                query_result["distances"][0],
            )
        ]

    def add_doc(self, filePath, collectionName="default", loader_kwargs: Dict = {}, text_splitter=TEXT_SPLITTER_NAME, chunk_size=CHUNK_SIZE,
                chunk_overlap=OVERLAP_SIZE):
        if not os.path.exists(filePath):
            raise RuntimeError(f"{filePath} not exists")

        md5 = encrypt(filePath)
        res = self.queryByMd5Bool(md5, collectionName)
        if res:
            logger.warning(f"{filePath} is exists")
            return []

        fileName = os.path.basename(filePath)
        ext = os.path.splitext(filePath)[-1].lower()
        document_loader_name = get_LoaderClass(ext)
        loader = get_loader(loader_name=document_loader_name,
                            file_path=filePath,
                            loader_kwargs=loader_kwargs)
        docs = loader.load()
        text_splitter = make_text_splitter(splitter_name=text_splitter, chunk_size=chunk_size,
                                           chunk_overlap=chunk_overlap)
        if text_splitter == "MarkdownHeaderTextSplitter":
            docs = text_splitter.split_text(docs[0].page_content)
        else:
            docs = text_splitter.split_documents(docs)

        if not docs:
            raise RuntimeError("分割文档失败")

        for doc in docs:
            source = doc.metadata.get("source", "")
            if not source or os.path.isabs(source):
                doc.metadata["source"] = fileName
                doc.metadata["md5"] = md5

        doc_infos = []
        data = self.embeddingDocs(docs)
        ids = [str(uuid.uuid1()) for _ in range(len(data["texts"]))]
        collection = self.collection.get(collectionName, self.defaultCollection)

        for _id, text, embedding, metadata in zip(ids, data["texts"], data["embeddings"], data["metadatas"]):
            collection.add(ids=_id, embeddings=embedding, metadatas=metadata, documents=text)
            doc_infos.append({"id": _id, "metadata": metadata})
        return doc_infos

    def add_docs(self, filePaths, collectionName="default"):
        for i in filePaths:
            self.add_doc(i, collectionName)

    def add_text(self, text, collectionName="default", metadata=None):
        if metadata is None:
            return self.add_texts([text], collectionName, None)
        else:
            return self.add_texts([text], collectionName, [metadata])

    def add_texts(self, texts, collectionName="default", metadata=None):
        if metadata is None:
            metadata = [{"source": "default"} for _ in range(len(texts))]

        md5s = encryptText(texts)
        addText = []
        for md5, metaD in zip(md5s, metadata):
            metaD["md5"] = md5
            addText.append(not self.queryByMd5Bool(md5, collectionName))
        doc_infos = []
        embed = self.embedding(texts)
        ids = [str(uuid.uuid1()) for _ in range(len(texts))]
        collection = self.collection.get(collectionName, self.defaultCollection)

        for _id, text, embedding, metadata, needAdd in zip(ids, texts, embed, metadata, addText):
            if needAdd:
                collection.add(ids=_id, embeddings=embedding, metadatas=metadata, documents=text)
                doc_infos.append({"id": _id, "metadata": metadata, "result": True})
            else:
                doc_infos.append({"id": _id, "metadata": metadata, "result": False})
        return doc_infos

    def deleteByFile(self, fileName, collectionName="default"):
        collection = self.collection.get(collectionName, self.defaultCollection)
        return collection.delete(where={"source": fileName})

    def queryBySource(self, source, collectionName="default"):
        collection = self.collection.get(collectionName, self.defaultCollection)
        return collection.get(where={"source": source})

    def queryByMd5(self, md5, collectionName="default"):
        collection = self.collection.get(collectionName, self.defaultCollection)
        return collection.get(where={"md5": md5})

    def queryByMd5Bool(self, md5, collectionName="default"):
        res = self.queryByMd5(md5, collectionName)
        if res:
            if len(res["ids"]) > 0:
                return True
        return False



if __name__ == '__main__':
    rc = ChromaRag()
    # print(rc.add_doc(r"test.txt"))
    # print(rc.add_text("test"))
    print(rc.add_text("test"))
    print(rc.queryBySource("default"))
    print(rc.queryByMd5("098f6bcd4621d373cade4e832627b4f6"))
    print(rc.queryByMd5Bool("098f6bcd4621d373cade4e832627b4f6"))
    print(rc.search("test"))
