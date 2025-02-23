# text2sql

LLM Application that converts text to SQL and execute it

## Problem and Approach

### Problem

The main problem this application aims to solve is the complexity and difficulty of writing SQL queries for users who may not be familiar with SQL syntax. Users often need to extract specific information from databases but lack the expertise to write the necessary SQL queries.

### Approach

The approach taken to solve this problem involves leveraging a Language Model (LLM) to convert natural language text into SQL queries. This allows users to input their queries in plain English, and the application translates these queries into SQL, executes them, and returns the results.

## Key Implementation Decisions

### Database Choice

DuckDB is used as the database engine due to its efficiency and ease of integration with Python. It supports SQL and is optimized for analytical queries. Since the data was in csv, it support out of the box csv to sql support.

### LLM Integration

The application integrates with the Gemini LLM to generate SQL queries from user prompts. This involves sending the user prompt to the LLM and receiving the generated SQL query.

## Demo

### Running the Application

To run the application, use the following command:

- use your gemini api key as shown in .env.example
- install poetry and run the command `poetry install`
- finally run the application via the command

```sh
python src/api.py
```
