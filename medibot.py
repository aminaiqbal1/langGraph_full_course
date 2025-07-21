import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict, Annotated
import os
from dotenv import load_dotenv
# Create and connect to SQLite database
conn = sqlite3.connect('PatientData.db')
cursor = conn.cursor()

# Create tablesyes
cursor.execute('''CREATE TABLE IF NOT EXISTS Patient (
                    patient_id INTEGER PRIMARY KEY, 
                    name TEXT, 
                    age INTEGER, 
                    gender TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Diagnosis (
                    diagnosis_id INTEGER PRIMARY KEY, 
                    patient_id INTEGER, 
                    diagnosis_date TEXT, 
                    diagnosis TEXT, 
                    FOREIGN KEY(patient_id) REFERENCES Patient(patient_id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Medication (
                    medication_id INTEGER PRIMARY KEY, 
                    diagnosis_id INTEGER, 
                    medication TEXT, 
                    dosage TEXT, 
                    FOREIGN KEY(diagnosis_id) REFERENCES Diagnosis(diagnosis_id))''')

import sqlite3

# Create and connect to SQLite database
conn = sqlite3.connect('PatientData.db')
cursor = conn.cursor()


# Commit and close the connection
conn.commit()
conn.close()


# Initialize the database
db = SQLDatabase.from_uri("sqlite:///PatientData.db")


load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=GEMINI_API_KEY,
    temperature=0
)

# Define system prompt to generate SQL queries
system_message = """
Given an input question, create a correct {dialect} query to
run to help find the answer. Unless the user specifies in his question a
specific number of examples they wish to obtain, always limit your query to
at most {top_k} results. You can order the results by a relevant column to
return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the
few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema
description. Be careful to not query for columns that do not exist. Also,
pay attention to which column is in which table.

Only use the following tables:
{table_info}
"""

user_prompt = "Question: {input}"

query_prompt_template = ChatPromptTemplate(
    [("system", system_message), ("user", user_prompt)]
)


class QueryOutput(TypedDict):
    query: Annotated[str, ..., "valid SQL query."]


# Function to write SQL query
def write_query(state):
    """Generate SQL query to fetch patient diagnosis"""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 5,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result}
# Function to get the patient's last diagnosis
def get_previous_diagnosis(patient_id):
    query = f"SELECT diagnosis FROM Diagnosis patient_id = {patient_id} "
    result = db.run(query)
    if result:
        return result
    return "No previous diagnosis found."

def record_new_diagnosis(patient_id, diagnosis, medication, dosage):
    query = f"INSERT INTO Diagnosis VALUES ({patient_id}, '{diagnosis}')"
    db.run(query)

    diagnosis_id = db.run(f"patient_id = {patient_id} ")

    query = f"INSERT INTO Medication VALUES ({diagnosis_id}, '{medication}', '{dosage}')"
    db.run(query)

    return "Diagnosis and medication recorded successfully."


class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str
def execute_query(state: State):
    """Execute SQL query."""
    result = db.run(state["query"])
    return {"result": result}
def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        f"Given the following user question, corresponding SQL query, and SQL result, answer the user question.\n\n"
        f"Question: {state['question']}\n"
        f"SQL Query: {state['query']}\n"
        f"SQL Result: {state['result']}"
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}
graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)
# ...rest of your code...
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

# Stream the result
for step in graph.stream("What was the last diagnosis for Patient ?"):
    print(step)
# Confirm with user before executing query
config = {"configurable": {"thread_id": "1"}}
user_approval = input("Do you want to proceed with executing the query? (yes/no): ")
if user_approval.lower() == "yes":
    for step in graph.stream(
        {"question": "What was the last diagnosis for Patient?"}, config, stream_mode="updates"
    ):
        print(step)
else:
    print("Operation cancelled by user.")

