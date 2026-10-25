from fastmcp import FastMCP
import sqlite3
from pydantic import Field
import os

# 1. FastMCP server instance banayein
mcp = FastMCP("AI Engineer Utility Server")

DB_FILE = "test.db"


# Testing ke liye ek chota sa SQLite database aur sample table initialize karte hain
def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            status TEXT
        )
    """)
  # Sample data insert karte hain
  cursor.execute(
      "INSERT OR IGNORE INTO projects (id, name, status) VALUES (1, 'SidekickAI',"
      " 'Active')"
  )
  cursor.execute(
      "INSERT OR IGNORE INTO projects (id, name, status) VALUES (2,"
      " 'WorldMonitor', 'In Progress')"
  )
  conn.commit()
  conn.close()


init_db()


# 2. Tool 1: Database Query Tool (Pydantic validation ke sath)
@mcp.tool()
def query_database(
    query: str = Field(
        ...,
        description=(
            "A valid SQLite SELECT query to run against the projects database."
        ),
    )
) -> str:
  """Executes a read-only SQLite query and returns the rows safely."""
  try:
    # Security check: Sirf SELECT queries allow karenge taaki koi data delete/drop na kar sake
    clean_query = query.strip().lower()
    if not clean_query.startswith("select"):
      return (
          "Security Error: Only SELECT queries are allowed on this database."
      )

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return str(rows)
  except Exception as e:
    return f"Database Error: {str(e)}"


# 3. Tool 2: System Log Reader Tool
@mcp.tool()
def read_system_logs(
    log_path: str = Field(
        ..., description="The absolute or relative path to the log file to read."
    )
) -> str:
  """Reads the last 10 lines of a local system log file safely."""
  try:
    if not os.path.exists(log_path):
      return f"Error: Log file not found at path '{log_path}'."

    with open(log_path, "r", encoding="utf-8") as f:
      lines = f.readlines()

    # Sirf last 10 lines return karenge taaki context window overload na ho
    recent_logs = "".join(lines[-10:])
    return recent_logs if recent_logs else "Log file is empty."
  except Exception as e:
    return f"Log Read Error: {str(e)}"


if __name__ == "__main__":
  mcp.run()