#data to be created --> how does imdb rating, box office collection, and oscars won look like for movies
#qualitative data --> document style chromaDB
#quantitative data --> SQL style
#complex query 1 --> combining written rules with numbers, combining both agents
#complex query 2 --> uses numbers then returns document answer, combining both agents

#data needs title, release year, imdb rating, budget, box office colleciton, director, oscar wins, runtime

import os
import sqlite3

def create_data(): 
    #create the document policies
    os.makedirs("data/docs", exist_ok=True)

    policy = """# Move Studio's FYC Campaign Policy

    #Rule 1: Rating Criteria
    To qualify for an official FYC awards campaign, a movie must have an IMDb rating of 8.5 or higher.

    #Rule 2: Runtime Criteria
    To qualify for any award submission, the movie runtime must be at least 120 minutes.

    #Rule 3: Budget Approval Threshold
    Any movie with a production budget greater than 100000000 requires special studio board sign-off for campaign spending.

"""

    with open("data/docs/awards_policy.md", "w") as f:
        f.write(policy)

    print("policy doc successfully written")

    #create the database
    connection = sqlite3.connect("enterprise.db")
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS movies")
    cursor.execute("""
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY,
            title TEXT,
            year INTEGER,
            imdb_rating REAL,
            runtime INTEGER,
            budget REAL,
            box_office REAL, 
            director TEXT, 
            oscars_won INTEGER
        )
        """)

    movie_data = [
        (1, "The Shawshank Redemption", 1994, 9.3, 142, 25000000, 28300000, "Frank Darabont", 0),
        (2, "The Godfather", 1972, 9.2, 175, 6000000, 270000000, "Francis Ford Coppola", 3),
        (3, "Good Will Hunting", 1997, 8.3, 126, 10000000, 225900000, "Gus Van Sant", 2), 
        (4, "Before Sunrise", 1995, 8.1, 101, 2500000, 22500000, "Richard Linklater", 0), 
        (5, "Rocky", 1976, 8.1, 120, 1000000, 225000000, "John G. Avildsen", 3), 
        (6, "The Dark Night", 2008, 9.0, 152, 185000000, 11000000000, "Christopher Nolan", 2), 
        (7, "Casablanca", 1942, 8.5, 102, 950000, 3700000, "Michael Curtiz", 3), 
        (8, "It Happend One Night", 1934, 8.1, 105, 325000, 2500000, "Frank Capra",5), 
        (9, "Titanic", 1997, 8.0, 195, 200000000, 2264000000, "James Cameron", 11),
        (10, "V for Vendetta", 2005, 8.2, 132, 50000000, 134700000, "James McTeigue", 0),      
    ]

    cursor.executemany("INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", movie_data)
    connection.commit()
    connection.close()

    print("success, database made")


if __name__ =="__main__":
    create_data()





