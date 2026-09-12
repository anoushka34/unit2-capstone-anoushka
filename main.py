import sys
from agents.manager import run_manager
from tokens import display_output
import time

BENCHMARK_QUERIES = [
    # 1-3: Qualitative Queries
    "What are the official runtime requirements for an award submission?",
    "What IMDb rating threshold must a movie achieve to qualify for an FYC campaign?",
    "When does campaign spending require special studio board sign-off according to policy?",
   
    # 4-6: Quantitative Queries
    "Which director has won the most Oscars in our database, and how many did they win?",
    "What is the average box office collection for films directed by Christopher Nolan?",
    "How many films in our database were released before the year 1980?",
   
    # 7-10: Complex Hybrid Queries
    "Based on our FYC campaign policy, do our 1990s films meet our minimum IMDb rating criteria?",
    "Which movies in our database satisfy both the policy runtime criteria and the 8.5 IMDb rating threshold?",
    "Do any films with a budget over $100M meet our FYC campaign rating criteria?",
    "Are there any movies directed by Francis Ford Coppola that qualify for an FYC campaign based on runtime and rating?"
]

def run_benchmark():
    print("\n" + "=" * 60)
    print("      RUNNING 10-QUERY CAPSTONE BENCHMARK EVALUATION")
    print("=" * 60 + "\n")

    for idx, query in enumerate(BENCHMARK_QUERIES, start=1):
        print(f"[{idx}/10] Query: {query}")
        result = run_manager(query)
        print(f"Route: {result.get('route')}")
        print(f"Answer Summary: {result.get('answer')[:120]}...\n" + "-" * 40)

        if idx < len(BENCHMARK_QUERIES):
            print("sleeping for 45s for rate limits")
            time.sleep(45)

    # Print the aggregate tokenomics summary required by the rubric
    display_output()

def interactive_cli():
    print("\n=======================================================")
    print("  Enterprise FYC Movie Intelligence System (CLI)")
    print("  Type your question or 'exit' to quit.")
    print("=======================================================\n")

    while True:
        try:
            user_input = input("Enter Query > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("\nSession ended.")
                display_output()
                break

            response = run_manager(user_input)
            print(f"\n[Route Used: {response.get('route')}]")
            print(f"\n{response.get('answer')}\n")
            print("-" * 55)

        except KeyboardInterrupt:
            print("\nSession interrupted.")
            display_output()
            break

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--benchmark":
        run_benchmark()
    else:
        interactive_cli()