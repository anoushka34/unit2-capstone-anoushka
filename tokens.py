COST_PER_1K_INPUT = 0.00001875  # check current Gemini pricing — free tier may not report usage the same way
COST_PER_1K_OUTPUT = 0.000075

#track all the logs for the 10 queries
usage = []

def log_usage(agent_name: str, input_tokens: int, output_tokens: int):
    input_tokens = input_tokens or 0
    output_tokens = output_tokens or 0
    cost = (input_tokens / 1000 * COST_PER_1K_INPUT) + (output_tokens / 1000 * COST_PER_1K_OUTPUT)
    print(f"[{agent_name}] tokens: in={input_tokens} out={output_tokens} cost=${cost:.6f}")

    usage.append({
        "agent": agent_name,
        "input": input_tokens, 
        "output": output_tokens,
        "cost": cost
    })


def display_output():
    #if usage is empty, then return nothing
    if not usage:
        print("usage empty, no queries")
        return

    #dictionary to keep track of each agent and their usage
    total = {}
    c = 0

    for i in usage:
        a = i["agent"]
        #if no agent, no tokens, no cost
        if a not in total:
            total[a] = {"tokens": 0, "cost": 0}

        #otherwise, sum up input & output tokens and cost
        total[a]["tokens"] += i["input"] + i["output"]
        total[a]["cost"] += i["cost"]

        #keep summing up total cost
        c += i["cost"]


    print("\n---TOKENOMICS SUMMARY---")
    for i, j in total.items():
        print(f"Agent: {i} | Total tokens: {j['tokens']} | Cost: ${j['cost']:.6f}")

    highest_agent = max(total.items(), key=lambda x: x[1]["tokens"])

    print(f"/nTtoal system cost: ${c:.6f}")
    print(f"Most tokens used by: {highest_agent[0]} ({highest_agent[1]['tokens']} tokents)")
    





