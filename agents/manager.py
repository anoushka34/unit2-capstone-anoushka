import json
import os
import re
from dotenv import load_dotenv
from google import genai
from agents.qualitative_agent import run_qualitative_agent
from agents.quant_agent import run_quantitative_agent
from tokens import log_usage

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#the prompt is meant to ensure that the request is routed correctly
#either goes to qualitiative, quantitative, or hybrid (the advanced queries)
ROUTER_PROMPT = """
You are the routing supervisor for an enterprise movie studio AI system.
Analyze the user request and determine the proper routing strategy:
- "QUALITATIVE": Pure studio rules, eligibility criteria, or policy documentation queries.
- "QUANTITATIVE": Pure numeric data, averages, counts, or SQL queries on the movie database.
- "HYBRID": Involves checking a policy standard/threshold against real movie data to see if criteria are met or counting films that exceed a policy rule.

Respond with ONLY a raw JSON object formatted as:
{
  "route": "QUALITATIVE" | "QUANTITATIVE" | "HYBRID",
  "qual_subquery": "subquery for documents if needed, else null",
  "quant_subquery": "subquery for SQL database if needed, else null"
}
"""

def clean_json_output(raw_text: str) -> str:
    cleaned = re.sub(r"^```(json)?", "", raw_text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"```$", "", cleaned.strip())
    return cleaned.strip()

def run_manager(user_query: str) -> dict:
    """
    Classifies user intent, delegates work to specialized agents,
    and synthesizes results for complex hybrid questions.
    """
    #this is teling gemini which route to choose based on the user query
    routing_prompt = f"{ROUTER_PROMPT}\nUser Request: {user_query}\nJSON Response:"
    route_response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=routing_prompt
    )

    in_tokens = route_response.usage_metadata.prompt_token_count
    out_tokens = route_response.usage_metadata.candidates_token_count
    log_usage("Manager", in_tokens, out_tokens)

    #this is mean to convert the text into a dictoinary
    try:
        plan = json.loads(clean_json_output(route_response.text))
    except Exception:
        #if json parsing fails, default to the hybrid route
        plan = {"route": "HYBRID", "qual_subquery": user_query, "quant_subquery": user_query}

    route = plan.get("route", "HYBRID")

    #the qualitative way
    if route == "QUALITATIVE":
        result = run_qualitative_agent(user_query)
        return {"route": "QUALITATIVE", "answer": result["answer"], "sources": result.get("sources")}

    #the quantitative way
    if route == "QUANTITATIVE":
        result = run_quantitative_agent(user_query)
        return {"route": "QUANTITATIVE", "answer": result["answer"], "sql": result.get("sql")}

    #the hybrid way
    qual_query = plan.get("qual_subquery") or user_query
    quant_query = plan.get("quant_subquery") or user_query

    #get the qualitative info by running the qualitiative agen
    qual_result = run_qualitative_agent(qual_query)

    #do the same but for quantiative
    context_enhanced_quant = f"{quant_query} (Context from studio policy: {qual_result['answer']})"
    quant_result = run_quantitative_agent(context_enhanced_quant)

    #combine both responses into one output
    synthesis_prompt = (
        f"Original User Request: {user_query}\n\n"
        f"Studio Policy Findings: {qual_result['answer']}\n\n"
        f"Database Findings (SQL executed: {quant_result.get('sql')}): {quant_result.get('answer')}\n\n"
        "Provide a unified, comprehensive final answer that directly addresses the user request, "
        "explicitly stating how the policy standards align with or compare to the database figures."
    )

    synthesis_response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=synthesis_prompt
    )

    in_tokens_syn = synthesis_response.usage_metadata.prompt_token_count
    out_tokens_syn = synthesis_response.usage_metadata.candidates_token_count
    log_usage("Manager", in_tokens_syn, out_tokens_syn)

    return {
        "route": "HYBRID",
        "answer": synthesis_response.text,
        "policy_context": qual_result["answer"],
        "sql_context": quant_result.get("sql"),
        "sql_answer": quant_result.get("answer")
    }