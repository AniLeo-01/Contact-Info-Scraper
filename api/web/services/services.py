from codecs import ignore_errors
from typing import List, Dict
from ..dto.request_model import CreateDocumentURL, CreateQuery, CreateDocument, CreateURL, CreateLeads
from supabase.client import Client, create_client
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import AsyncChromiumLoader
from langchain.vectorstores import SupabaseVectorStore
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import BeautifulSoupTransformer
import requests
import json
from ...prompts.prompt import prompt
from ..repositories import repositories
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from sqlalchemy.ext.asyncio import AsyncSession
from langchain.chains import RetrievalQA
from fastapi import HTTPException
from ...config.config import get_settings
from ..dao.db_model import URL
import asyncio
import ast
import random
from time import sleep

async def initialize_supabase_db():
    supabase: Client = create_client(get_settings().SUPABASE_URL, get_settings().SUPABASE_KEY)
    return supabase

async def scraper_with_playwright(url):
    # loader = AsyncChromiumLoader(url)
    loader = AsyncHtmlLoader(url, default_parser="html5lib", ignore_load_errors=True)
    docs = loader.load()
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=["header", "p", "li", "div", "a", "footer"]
    )
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    docs = splitter.split_documents(docs_transformed)
    return docs

async def create_supabase_vectorstore(embeddings: OpenAIEmbeddings, docs):
    vector_store = SupabaseVectorStore.from_documents(
        docs,
        embedding = embeddings,
        client=await initialize_supabase_db(),
        table_name="documents",
        query_name="match_documents",
    )
    return vector_store

async def contact_info_scraper_using_llm(prompt: str, docs):
    llm = ChatOpenAI(temperature=0, openai_api_key = get_settings().OPENAI_API_KEY)
    embeddings = OpenAIEmbeddings(openai_api_key=get_settings().OPENAI_API_KEY)
    vector_retriever = await create_supabase_vectorstore(embeddings, docs)

    prompt_template = PromptTemplate(template=prompt,
                                     input_variables=["question", "context"])
    question = "Extract the contact number and email address"
    qa = RetrievalQA.from_chain_type(
        llm = llm,
        chain_type = 'stuff',
        retriever = vector_retriever.as_retriever(),
        chain_type_kwargs = {'prompt': prompt_template}
    )
    #fetch the query instruction from the prompts file
    res = qa({'query': question})
    return res

async def get_google_search_results(query, filters, num_results):
    # Make a GET request to the Google Custom JSON Search API
    for filter in filters:
        query = query + " -inurl:" + filter
    url = "https://google.serper.dev/search"
    payload = json.dumps({
    "q": query,
    "num": num_results
    })
    headers = {
    'X-API-KEY': get_settings().SERPER_API_KEY,
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # Parse the JSON response
    data = ast.literal_eval(response.content.decode())

    # Extract the URLs of the search results
    urls = []
    for item in data["organic"]:
        url = item["link"]
        urls.append(url)

    return urls

async def scrape_data_to_json(query: CreateQuery, session: AsyncSession):
    #store to query db
    print("Query:",query)
    created_query = await repositories.create_query(session, query)
    urls = await get_google_search_results(query.query, query.exceptionFilters, query.query_num)
    print("URL: ", urls)
    data = []
    for url in urls:
        #check for url redundancy
        get_url_data = await repositories.get_URL_data_by_column(session = session, column = URL.url, value = url) # type: ignore
        if get_url_data == None:
            #store to URL db
            url_query_entry = CreateURL(
                url = url,
                query_id = created_query.id
            ) # type: ignore
            url_response = await repositories.create_url(url = url_query_entry, session = session)
            url_id = url_response.id
        else:
            url_id = get_url_data.id
        docs = await scraper_with_playwright([url])
        results = await contact_info_scraper_using_llm(prompt, docs)
        # #store the document table entries into documents_url table with the url_id
        # document_data = await repositories.get_all_documents(session = session)
        # for document in document_data:
        #     create_entry_document_url = CreateDocumentURL(
        #         url_id = url_id,
        #         content = document.content,
        #         document_metadata = document.metadata,
        #         embedding = ast.literal_eval(document.embedding)
        #     ) # type: ignore
        #     await repositories.store_documents_url(session = session, document_data = create_entry_document_url)
        #delete the entries of documents table
        await repositories.delete_all_documents(session = session)
        res = json.loads(results['result'])
        res['url'] = url
        #store to Leads table
        contact_info_query = CreateLeads(
            email = str(res['email']) if res['email'] != 'None' or res['email'] != 'Null' else None,
            phone = str(res['phone_number']) if res['phone_number'] != 'None' or res['phone_number'] != 'Null' else None,
            url = url
        ) # type: ignore
        await repositories.create_contact_info(contact_info = contact_info_query, session = session)
        data.append(res)
    return data

async def get_all_user_queries(session: AsyncSession):
    queries = await repositories.get_all_queries(session = session)
    if queries:
        return queries
    else:
        raise HTTPException(
            status_code=400,
            detail="No queries found!"
        )