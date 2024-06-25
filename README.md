**Expense Tracker**

**Project Description**

The Expense Tracker is a Python Flask application that allows users to manage their expenses and income. The application provides the following features:

**User Authentication**

-Simple user authentication system using database-based storage.

-Users can sign up, log in, and log out.

**Expense and Income Management**

-Users can add, edit, and delete their expenses and income.

-Includes categories for expenses and income (e.g., food, rent, salary, etc.).

**Transaction History**

-Displays a transaction history for each user, showing a list of past expenses and income, along with relevant details (amount, category, date).

**Budgeting**

-Allows users to set monthly budgets for different expense

**Categories**

-Notifies users if they exceed their budget in a specific category.

**Data Storage**

-Uses database-based storage to persist user data between sessions.

-Each user has a separate file to store their data securely.

**Data Visualization**

-Implements a simple textual and visual representation of the user's spending patterns over time.

**Currency Converter**

-Includes a basic currency converter to allow users to input expenses in different currencies.

**Testing**

-Unit tests are written for critical parts of the code using the unittest library.


**Installation and Setup**

1. Clone the repository:

git clone https://github.com/MahdiMubarrat/expense_tracker_flask

cd EXPENSE_TRACKER_FLASK

2. Create a virtual environment and activate it:

python -m venv venv

source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install the required packages:

Make sure you have the following dependencies installed. If you haven't created a requirements.txt file, you can do so by running:

pip install flask flask_sqlalchemy werkzeug requests

pip freeze > requirements.txt

4. Install the dependencies:

pip install -r requirements.txt

5. Set the environment to development and initialize the database:

For Unix-based systems:

export FLASK_ENV=development

python init_db.py

For Windows:

set FLASK_ENV=development

python init_db.py

6. Run the application:

For Unix-based systems:

export FLASK_ENV=development

flask run

For Windows:

set FLASK_ENV=development

flask run


**Usage**

Sign Up:
Navigate to /signup to create a new user account.

Log In:
Navigate to /login to log into your account.

Dashboard:
View your transaction history, budgets, and spending patterns.

Add Transaction:
Navigate to /add_transaction to add a new expense or income.

Set Budget:
Navigate to /set_budget to set a monthly budget for a specific category.

**File Descriptions**

app.py: Contains the main application code, including routes, models, and utility functions.

init_db.py: Initializes the database by creating necessary tables.

test_app.py: Contains unit tests for the application.

templates/: Contains HTML templates for different pages (e.g., login, signup, dashboard).

static/: Contains static files such as CSS.

instance/: Contains the SQLite database files.
