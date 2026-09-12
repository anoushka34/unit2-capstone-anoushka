import os
import re
import sqlite3
from dotenv import load_dotenv
from google import genai
from agents.validate import validate_sql
from tokens import log_usage

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#include the schema so the model knows what's included
SCHEMA_PROMPT = """
You have access to an SQLite table named 'movies' with the following schema:
- id INTEGER PRIMARY KEY
- title TEXT
- year INTEGER
- imdb_rating REAL
- runtime INTEGER (in minutes)
- budget REAL
- box_office REAL
- director TEXT
- oscars_won INTEGER

Return ONLY a valid, raw SQL query. Do not wrap in markdown quotes, no explanation, no backticks.
Only read-only SELECT queries are allowed.
"""

#this will clear the back ticks and stuff it is clean
def clean_sql_output(raw_text: str) -> str:
    """Removes backticks and 'sql' language tags if the model includes them."""
    cleaned = re.sub(r"^```(sql)?", "", raw_text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"```$", "", cleaned.strip())
    return cleaned.strip()

def run_quantitative_agent(query: str) -> dict:
    """
    Converts a natural language query into SQL, validates safety,
    executes against SQLite, and summarizes the result.
    """
   #convert what the user entered into the sql query
    sql_prompt = f"{SCHEMA_PROMPT}\nUser Request: {query}\nSQL Query:"
   
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=sql_prompt
    )

    #keep track of the tokens to do the calculations later
    in_tokens = response.usage_metadata.prompt_token_count
    out_tokens = response.usage_metadata.candidates_token_count
    log_usage("Quantitative", in_tokens, out_tokens)

    #makes sure the string was made into SQL
    generated_sql = clean_sql_output(response.text)

    #this is meant to ensure the query doesn't have any of the blocked words 
    validation = validate_sql(generated_sql)
    if not validation["valid"]:
        return {
            "error": f"SQL Rejected by Validator: {validation['reason']}",
            "sql": generated_sql,
            "answer": None
        }

    #executing the query
    conn = sqlite3.connect("enterprise.db")
    cursor = conn.cursor()
    try:
        cursor.execute(generated_sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
    except Exception as e:
        conn.close()
        return {
            "error": f"SQL Execution Error: {str(e)}",
            "sql": generated_sql,
            "answer": None
        }
    finally:
        conn.close()

    #after execution, translate the database rows into a sentence
    summary_prompt = (
        f"User question: {query}\n"
        f"Executed SQL: {generated_sql}\n"
        f"Data retrieved (columns: {columns}): {rows}\n"
        "Provide a concise, direct answer based purely on this data."
    )

    summary_response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=summary_prompt
    )

    #calculate the tokens that were used
    in_tokens_sum = summary_response.usage_metadata.prompt_token_count
    out_tokens_sum = summary_response.usage_metadata.candidates_token_count
    log_usage("Quantitative", in_tokens_sum, out_tokens_sum)

    return {
        "sql": generated_sql,
        "raw_data": rows,
        "answer": summary_response.text
    }