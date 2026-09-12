#will handle unstructured data retrieval
#embeds policy text and indexes it to chromadb

import os
from dotenv import load_dotenv
from google import genai
import chromadb
from chromadb.utils import embedding_functions
from tokens import log_usage

load_dotenv()

#retrieve the API key from the env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#meant to transform the english text into a vector with numbers
#no API cost, the model will do the conversion
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

#chromadb as an in-memory vector database that stores the text and numbers for easy lookup
#collection is like a table in SQL
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name="studio_policies",
    embedding_function=embed_fn
)


def index_documents():
    """Reads all markdown files in data/docs/ and indexes them into ChromaDB."""
    #checking to see if the path exists
    docs_dir = "data/docs"
    if not os.path.exists(docs_dir):
        return

    #documents: holds the raw text, metadatas: holds the file name, ids: unique identifier for each chunk in chromadb
    documents = []
    metadatas = []
    ids = []

    #loop through each file in the data/docs, which is the award criteria.md
    for filename in os.listdir(docs_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(docs_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            #splitting the document by separting at the ##, creates 3 separate rules now
            sections = content.split("## ")
            for i, section in enumerate(sections):
                cleaned_chunk = section.strip()
                if cleaned_chunk:
                    chunk_text = f"## {cleaned_chunk}" if i > 0 else cleaned_chunk
                    documents.append(chunk_text)
                    metadatas.append({"source": filename, "chunk_id": i})
                    ids.append(f"{filename}_chunk_{i}")
    #upsert --> update if the ID exists, or add if it's new
    if documents:
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)


index_documents()

def run_qualitative_agent(query: str) -> dict:
    """
    Retrieves the top-k document chunks from ChromaDB and
    prompts Gemini to answer with citations.
    """
    #checking vector simlarity
    #chrombadb changes the text query to numbers and compares it to the what is already stored
    #n_results=2 means give the top 2 chunks that are closest in meaning
    results = collection.query(query_texts=[query], n_results=2)
    #retrieving the matched text chunks with their metadata too
    retrieved_docs = results["documents"][0] if results["documents"] else []
    retrieved_meta = results["metadatas"][0] if results["metadatas"] else []

    #combine the matched chunks together into one string
    context = "\n\n".join(retrieved_docs)
    sources = list(set(meta["source"] for meta in retrieved_meta))

    #prompt so the output is seen from that lens
    system_instruction = (
        "You are an enterprise movie studio policy expert. "
        "Answer the user's question using ONLY the provided document context. "
        "Always cite the exact rule, document name, and criteria mentioned."
    )

    #bundle the retrieved text chunks and the user's question together
    prompt = f"Context:\n{context}\n\nUser Question:\n{query}"

    #return the response by calling the gemini model
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={"system_instruction": system_instruction}
    )

    #collect the token usage and use the log_usage from tokens.py to see how much was used and the cost
    in_tokens = response.usage_metadata.prompt_token_count
    out_tokens = response.usage_metadata.candidates_token_count
    log_usage("Qualitative", in_tokens, out_tokens)

    return {
        "answer": response.text,
        "sources": sources,
        "raw_context": context
    }