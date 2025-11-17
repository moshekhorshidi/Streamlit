import streamlit as st
import pandas as pd
from streamlit_navigation_bar import st_navbar


st.set_page_config(page_title="Moshe Khorshidi DE Test App", layout="wide", page_icon="📂")

def main():
    # Application title and header
    st.title("Data Engineering by Moshe Khorshidi")
    st.header("Scalable SQL Schema & Query System for Folder Events")

    section = st_navbar(
    menu_items=[
        "Overview",
        "Schema Design",
        "DDL Code",
        "Indexing",
        "Folder_Hierarchy",
        "Queries",
        "Bonus Data Flow Diagram"
    ],
    selected="Overview",
    nav_type="pills",      # "tabs" and "buttons" also available
    hide_nav=False
)

    if section == "Overview":
        st.markdown(""" 
            # Overview
            This solution is designed to efficiently track and query user events on a hierarchical folder system. 
            It includes:
            
            - **Schema Design** for folders, users, and events.
            - **DDL Code** to create the necessary tables.
            - **Indexing** to optimize queries on billions of records.
            - An additional **Folder_Hierarchy** table to precompute folder relationships.
            - **Queries** that leverage user-defined variables for a dynamic UI.
            - A **Bonus Data Flow Diagram** outlining a Lambda Architecture for scalable, real-time & batch processing.
        """)
        
    elif section == "Schema Design":
        st.markdown("## Schema Design")
        st.markdown("**Folder:** Stores folder information along with parent-child relationships.")
        st.code("""Folder(dirid BIGINT, parentId BIGINT, path NVARCHAR(2000))""", language="sql")
        st.markdown("**User:** Stores user details.")
        st.code("""User(userid INT, Name NVARCHAR(100))""", language="sql")
        st.markdown("**Event:** Stores actions/events on folders.")
        st.code("""Event(eventid BIGINT, date DATETIME, opcode VARCHAR(50), dirid BIGINT, userid INT)""", language="sql")
        
    elif section == "DDL Code":
        st.markdown("## Tables DDL Code")
        st.code("""CREATE TABLE Folder (
    dirid BIGINT PRIMARY KEY,
    parentId BIGINT NULL,
    path NVARCHAR(3000) NOT NULL,
    FOREIGN KEY (parentId) REFERENCES Folder(dirid) ON DELETE CASCADE
);

CREATE TABLE User (
    userid INT PRIMARY KEY,
    name NVARCHAR(100) NOT NULL
);

CREATE TABLE Event (
    eventid BIGINT PRIMARY KEY,
    event_date DATETIME NOT NULL,
    operation VARCHAR(50) NOT NULL,
    dirid BIGINT NOT NULL,
    userid INT NOT NULL,
    FOREIGN KEY (dirid) REFERENCES Folder(dirid) ON DELETE CASCADE,
    FOREIGN KEY (userid) REFERENCES User(userid) ON DELETE CASCADE
);""", language="sql")
        
    elif section == "Indexing":
        st.markdown("## Indexing for Schema Tables")
        st.markdown("The following indexes are created to optimize query performance on billions of records:")
        st.code("""-- Index on Event Table (For user event counts and filtering by folder ID)
CREATE INDEX idx_event_user ON Event(userid);
CREATE INDEX idx_event_folder_date ON Event(dirid, event_date);

-- Index on Folder Table (For faster lookup of parent-child folder relationships)
CREATE INDEX idx_folder_parent ON Folder(parentId);

-- Index on User Table (For faster lookup by ID)
CREATE INDEX idx_user_id ON User(userid);""", language="sql")
        
    elif section == "Folder_Hierarchy":
        st.markdown("## Additional Table: Folder_Hierarchy")
        st.markdown("This table precomputes folder relationships for efficient lookup of subfolders.")
        st.code("""CREATE TABLE Folder_Hierarchy (
    Parent BIGINT,  -- Parent folder
    Child BIGINT,   -- Child folder
    depth INT,      -- Distance from Parent
    PRIMARY KEY (Parent, Child)
);""", language="sql")
        st.markdown("### Populate Folder_Hierarchy Using a Recursive CTE")
        st.code("""WITH RECURSIVE folder_tree AS (
    SELECT dirid AS Parent, dirid AS Child, 0 AS depth FROM Folder
    UNION ALL
    SELECT f.parentId, f.dirid, ft.depth + 1
    FROM Folder f
    JOIN folder_tree ft ON f.parentId = ft.Child
)
INSERT INTO Folder_Hierarchy 
SELECT * FROM folder_tree;""", language="sql")
        
    elif section == "Queries":
        st.markdown("## Queries")
        st.markdown("### 0. Declare User-Defined Input Variables")
        st.code("""-- Declare user-defined input
DECLARE @UserID INT;
DECLARE @FolderPath NVARCHAR(3000);
DECLARE @EventDate DATE;

/*
Example UI usage:
SET @UserID = 1;
SET @FolderPath = 'C:\A';
SET @EventDate = '2025-02-26';
*/""", language="sql")
        st.markdown("### 1. Query: Number of Events per User")
        st.code("""SELECT u.name, COUNT(e.eventid) AS total_event_count
FROM Event e
JOIN User u ON e.userid = u.userid
GROUP BY u.name
ORDER BY total_event_count DESC;""", language="sql")
        st.markdown("### 2. Query: Events for a Specific User on a Folder (and its subfolders)")
        st.code("""SELECT e.eventid, e.event_date, e.operation, e.dirid, f.path
FROM Event e
JOIN Folder_Hierarchy fh ON e.dirid = fh.Child
JOIN Folder f ON e.dirid = f.dirid
WHERE e.userid = @UserID
  AND fh.Parent = (SELECT dirid FROM Folder WHERE path = @FolderPath)
  AND e.event_date = @EventDate;""", language="sql")
        st.markdown("Note: The Folder_Hierarchy table allows fast lookup of all subfolders, while indexes like idx_event_folder_date ensure quick filtering by date.")
        
        # --- 3. Queries & Interactive Execution ---
        query_options = ["Number of Events per User", "Filter Events by User, Folder, and Date"]
        selected_query = st.selectbox("Choose a query:", query_options)

        if selected_query == "Number of Events per User":
            st.write("This query calculates the number of events per user:")
            st.code("""
            SELECT u.name, COUNT(e.eventid) AS total_event_count
            FROM Event e
            JOIN User u ON e.userid = u.userid
            GROUP BY u.name
            ORDER BY total_event_count DESC;
            """, language="sql")

            # Execute Query (Dummy Data for UI)
            sample_data = pd.DataFrame({
                "User": ["Alice", "Bob", "Charlie"],
                "Total Events": [120, 95, 80]
            })
            st.bar_chart(sample_data.set_index("User"))

        elif selected_query == "Filter Events by User, Folder, and Date":
            st.write("Use the form below to filter events dynamically.")

            # User Inputs
            user_id = st.number_input("Enter User ID", min_value=1, step=1, value=1)
            folder_path = st.text_input("Enter Folder Path", "C:\\A")
            event_date = st.date_input("Select Event Date")

            st.code(f"""
            SELECT e.eventid, e.event_date, e.operation, e.dirid, f.path
            FROM Event e
            JOIN Folder_Hierarchy fh ON e.dirid = fh.Child
            JOIN Folder f ON e.dirid = f.dirid
            WHERE e.userid = {user_id}
            AND fh.Parent = (SELECT dirid FROM Folder WHERE path = '{folder_path}')
            AND e.event_date = '{event_date}';
            """, language="sql")

            st.success("🔍 This query efficiently retrieves user activities in a given folder.")
        
    elif section == "Bonus Data Flow Diagram":
        st.markdown("## Bonus: Optimal Data Flow Diagram - Lambda Architecture")
        st.markdown(""" 
            **Components:**
            - **Streaming Layer:** Ingests events in real-time using technologies such as Kafka, Memphis.dev, or Azure Service Bus.
            - **Batch Processing:** Aggregates and processes data daily using ETL tools like Spark, Alteryx, Airflow, Azure Synapse, or Databricks.
            - **SQL Database:** Stores the processed tables (User, Event, Folder, Folder_Hierarchy) using platforms like Azure SQL Database or Snowflake.
            
            This architecture ensures that data is handled in both real-time and batch modes, providing scalability and high performance for querying billions of events.
        """)

    # Add a footer note in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("MosheKhorshidi@Gmail.com")

if __name__ == "__main__":
    main()



