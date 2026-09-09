from agents.validate import validate_sql

def test_simple_select():
    query = "SELECT * FROM movies;"
    result = validate_sql(query)
    assert result["valid"] is True
    assert result["reason"]=="OK"

def test_aggregate_query():
    query = "SELECT AVG(imdb_rating) FROM movies WHERE year >=1990;"
    result = validate_sql(query)
    assert result["valid"] is True
    assert result["reason"]=="OK"

def test_block_drop_table():
    query = "DROP TABLE movies;"
    result = validate_sql(query)
    assert result["valid"] is False
    assert "DROP not permitted" in result["reason"]

def test_delete_records():
    query = "DELETE FROM movies WHERE id=1;"
    result = validate_sql(query)
    assert result["valid"] is False
    assert "DELETE not permitted" in result["reason"]

def test_block_update():
    query = "SELECT * FROM movies; UPDATE movies SET imdb_rating=10.0;"
    result = validate_sql(query)
    assert result["valid"] is False
    assert "UPDATE not permitted" in result["reason"]

def test_non_select_start():
    query = "EXPLAIN QUERY PLAN SELECT * FROM movies"
    result = validate_sql(query)
    assert result["valid"] is False
    assert result["reason"]=="Only SELECT queries are permitted"
