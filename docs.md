# Documentation for Tkinter SQL Server Application

## 1. Overview
This is a Python-based desktop application built using **Tkinter** as the GUI framework and **SQL Server** as the database. The application provides:

- User authentication  
- Table data viewing with pagination and column selection  
- CRUD operations (Create, Read, Update, Delete)  
- Raw SQL query execution  

It also supports dynamic login credentials for different databases.

---

## 2. Features

### 2.1 User Authentication
- **Login Window**:
  - Users can connect to any SQL Server database by entering:
    - **Host**  
    - **Port**  
    - **Username**  
    - **Password**  
    - **Database Name**  
  - Credentials are validated, and user details are saved in the **home directory**.

- **Logout and Re-Login**:
  - Users can log out and log in again with the same or different database credentials.

---

### 2.2 Dashboard
The dashboard provides the following features:

#### 2.2.1 Select Table
- **Table Selection**:
  - View all tables in the connected database.
- **Pagination**:
  - Display the first **20 rows** of the table.
  - Use **Next** and **Previous** buttons to navigate.
  - Fetch a **specific page** of data.
- **Column Selection**:
  - Choose specific columns to display.

---

#### 2.2.2 Insert New Entry
- **Dynamic Form Generation**:
  - Fields are created based on the table schema.
  - Required fields include their **data types**.
  - For **foreign key columns**, dropdowns display entries from the referenced table.

- **Buttons**:
  - **Save**: Saves the entry after validating fields.  
  - **Cancel**: Resets fields to default or empty values.

---

#### 2.2.3 Update Existing Entry
- **Prefill Form**:
  - Selected row data is prefilled into the form.
- **Update**:
  - Edit values and save them back to the database after validation.

---

#### 2.2.4 Delete Rows
- **Multiple Row Deletion**:
  - Select multiple rows and delete them.
- **Foreign Key Constraints**:
  - Prevents deletion if foreign key relationships exist.

---

#### 2.2.5 Non-Primary Key Support
- For tables without a primary key:
  - Users must select **unique columns** to identify rows.
  - Updates and deletions are performed based on these unique columns.

---

### 2.3 Execute Raw SQL Queries
- **Query Box**:
  - Write and execute raw SQL queries.
  - Supports common queries like `SELECT`, `UPDATE`, `DELETE`, and `INSERT`.
- **Execute Button**:
  - Runs the query and displays results in a table.

---

### 2.4 Logout and Re-Login
- Log out from the current session and return to the login page.
- Allows connecting to a different database or reusing credentials.

---

## 3. Application Workflow

1. **Launch Application**: Opens the login window.  
2. **Login**: Enter **host, port, username, password, and database name**.  
3. **Dashboard**:
   - **View Table Data**: Paginate and filter columns.  
   - **Insert New Entry**: Add new rows with validation.  
   - **Update Rows**: Edit existing rows.  
   - **Delete Rows**: Delete selected rows.  
   - **Execute Raw Queries**: Write and execute custom SQL queries.  
4. **Logout**: Log out and return to the login screen.

---

## 4. Technologies Used
- **Python**: Core programming language.  
- **Tkinter**: GUI framework for the desktop interface.  
- **SQL Server**: Database management system.  
- **pyodbc**: Python library for SQL Server connectivity.

---

## 5. Installation

### 5.1 Prerequisites
- **Python 3.10+**  
- SQL Server database with valid credentials.  
- Required Python libraries:
  - `tkinter` (bundled with Python)  
  - `pyodbc`  

### 5.2 Steps
1. Clone the repository:
   ```bash
   git clone git@github.com:apltechno/python-admin.git python_admin
   cd python_admin
   pip install -r requirements.txt
   python main.py

## 6. User Guide

### 6.1 Login Page
- Enter the **host, port, username, password, and database name**.
- Click **Login** to connect.

### 6.2 Dashboard

#### Select Table:
- Choose a table and view data with pagination.
- Use column filters to display specific columns.

#### Insert New Entry:
- Fill in the form fields and click **Save**.

#### Update Existing Entry:
- Select a row, update its values, and save.

#### Delete Rows:
- Select rows and click **Delete**.

#### Execute Raw Query:
- Write a query in the query box and click **Execute**.

---

## 7. Validation and Error Handling
- **Login**: Displays an error for invalid credentials.  
- **Insert/Update**: Validates each field before saving.  
- **Raw Query**: Handles invalid queries without crashing the application.  
- **Delete**: Prevents deletion if foreign key constraints exist.

---

## 8. Troubleshooting

| **Issue**                            | **Solution**                                      |
|--------------------------------------|---------------------------------------------------|
| Cannot connect to SQL Server         | Verify database credentials and connection string.|
| Application crashes on startup       | Check for missing Python dependencies.            |
| Invalid query error in Raw Query Box | Validate SQL syntax.                              |
| Foreign key error during delete      | Ensure no dependent rows exist in related tables. |

---

## 9. Future Enhancements
- Role-based access control.  
- Export data to CSV/Excel.  
- Advanced query validation and suggestions.  
- Improved UI design with modern frameworks.

---

## 10. Conclusion
This Tkinter-based application provides a comprehensive and user-friendly interface for managing SQL Server databases. It simplifies data viewing, CRUD operations, and raw query execution while ensuring data integrity and usability.
