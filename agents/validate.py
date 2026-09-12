#copy the code given to validate sql operations

#Basically are blocking the SQL verbs that exist to alter data

BLOCKED_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]

def validate_sql(query: str) -> dict:
    #puts everything to upperase and takes away the whitespace
    query_upper = query.upper().strip()
    #this is to search for verbs, 
    for keyword in BLOCKED_KEYWORDS:
        if f" {keyword} " in f" {query_upper} " or query_upper.startswith(keyword):
            return {"valid": False, "reason": f"Blocked: {keyword} not permitted"}
        #makes sure that only read queries are allowed, anything that isn't is rejected
    if not query_upper.startswith("SELECT"):
        return {"valid": False, "reason": "Only SELECT queries are permitted"}
    return {"valid": True, "reason": "OK"}