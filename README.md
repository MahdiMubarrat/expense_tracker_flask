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

cd expense_tracker_flask

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

**For Unix-based systems:**

export FLASK_ENV=development

python init_db.py

**For Windows:**

set FLASK_ENV=development

python init_db.py

6. Run the application:

**For Unix-based systems:**

export FLASK_ENV=development

flask run

**For Windows:**

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

**Running Tests**

**Setting Up for Tests**

Before running the tests, ensure your Flask environment is set to testing and initialize the test database:

Set the Flask environment to testing and initialize the test database:

**For Unix-based systems:**

export FLASK_ENV=testing

python init_db.py

**For Windows:**

set FLASK_ENV=testing

python init_db.py

**Run the tests:**

python -m unittest test_app.py

**Detailed Test Instructions**

The test_app.py file includes various tests to ensure the functionality of the Expense Tracker application. Here are the tests included:

test_signup: Tests user registration.

test_login: Tests user login.

test_invalid_login: Tests login with invalid credentials.

test_calculate_spending: Tests the calculation of user spending.

test_get_exchange_rate: Tests fetching the exchange rate.

test_convert_currency: Tests currency conversion.

test_calculate_spending_patterns: Tests the calculation of spending patterns over time.

test_add_transaction: Tests adding a transaction.

test_edit_transaction: Tests editing a transaction.

test_delete_transaction: Tests deleting a transaction.

test_set_budget: Tests setting a budget.

test_edit_budget: Tests editing a budget.

test_delete_budget: Tests deleting a budget.

test_exceed_budget_notification: Tests budget exceed notifications.

test_dashboard_access_without_login: Tests dashboard access without login.

test_logout: Tests user logout.

**Example Usage of Tests**

Here's a step-by-step example of how to run a specific test:

Ensure the virtual environment is activated:

source venv/bin/activate  # On Windows use 'venv\Scripts\activate'

Set the Flask environment to testing and run a specific test function:

**For Unix-based systems:**

export FLASK_ENV=testing

python init_db.py  # Initialize the test database

python -m unittest test_app.ExpenseTrackerTestCase.test_signup

**For Windows:**

set FLASK_ENV=testing

python init_db.py  # Initialize the test database

python -m unittest test_app.ExpenseTrackerTestCase.test_signup

**File Descriptions**

app.py: Contains the main application code, including routes, models, and utility functions.

init_db.py: Initializes the database by creating necessary tables.

test_app.py: Contains unit tests for the application.

templates/: Contains HTML templates for different pages (e.g., login, signup, dashboard).

static/: Contains static files such as CSS.

instance/: Contains the SQLite database files.
