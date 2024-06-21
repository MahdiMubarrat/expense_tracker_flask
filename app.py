from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from collections import defaultdict
from datetime import datetime, timezone
import os

# Configuration class
class Config:
    SECRET_KEY = 'my_random_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///expenses.db'

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_expenses.db'
    TESTING = True

# Set the environment variable for Flask
env = os.getenv('FLASK_ENV', 'development')

# Initialize the Flask app
app = Flask(__name__)

if env == 'testing':
    app.config.from_object(TestingConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Initialize the database
db = SQLAlchemy(app)

# Constants for exchange rate calculation
API_KEY = '335f3eddeb932c5278dd4a75'
BASE_CURRENCY = 'CAD'

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    end_date = db.Column(db.DateTime, nullable=False)

# Calculate user spending within an optional date range
def calculate_spending(user_id, start_date=None, end_date=None):
    spending = {}
    query = Transaction.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    transactions = query.all()
    for transaction in transactions:
        if transaction.category not in spending:
            spending[transaction.category] = 0
        spending[transaction.category] += transaction.amount if transaction.type == 'expense' else -transaction.amount
    return spending

# Get exchange rate from the base currency to the target currency
def get_exchange_rate(target_currency):
    if target_currency == BASE_CURRENCY:
        return 1
    url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{target_currency}/{BASE_CURRENCY}'
    response = requests.get(url)
    data = response.json()
    rate = data['conversion_rate']
    print(f"Exchange rate from {target_currency} to {BASE_CURRENCY}: {rate}")
    return rate

# Convert amount to the base currency
def convert_currency(amount, target_currency):
    rate = get_exchange_rate(target_currency)
    return amount * rate

# Calculate spending patterns over time for a user
def calculate_spending_patterns(user_id):
    spending_patterns = defaultdict(float)
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    for transaction in transactions:
        date_str = transaction.date.strftime('%Y-%m')
        spending_patterns[date_str] += transaction.amount if transaction.type == 'expense' else -transaction.amount
    return spending_patterns

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        user = User(username=username, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('User registered successfully!')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash('Error creating user. Please try again.')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    budgets = Budget.query.filter_by(user_id=user_id).all()
    spending_patterns = calculate_spending_patterns(user_id)

    notifications = []
    current_date = datetime.now(timezone.utc)
    for budget in budgets:
        # Ensure budget dates are aware datetime objects
        if budget.start_date.tzinfo is None:
            budget.start_date = budget.start_date.replace(tzinfo=timezone.utc)
        if budget.end_date.tzinfo is None:
            budget.end_date = budget.end_date.replace(tzinfo=timezone.utc)
        if budget.start_date <= current_date <= budget.end_date:
            spending = calculate_spending(user_id, budget.start_date, budget.end_date)
            total_spent = spending.get(budget.category, 0)
            if total_spent > budget.amount:
                notifications.append(f"You have exceeded your budget for {budget.category} by {total_spent - budget.amount:.2f}")

    return render_template('dashboard.html', transactions=transactions, budgets=budgets, notifications=notifications, spending_patterns=spending_patterns)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        type = request.form['type']
        amount = float(request.form['amount'])
        category = request.form['category']
        currency = request.form['currency']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        user_id = session['user_id']
        
        converted_amount = convert_currency(amount, currency)
        
        transaction = Transaction(type=type, amount=converted_amount, category=category, currency=currency, date=date, user_id=user_id)
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    today = datetime.now(timezone.utc).date()
    return render_template('add_transaction.html', today=today)

@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        user_id = session['user_id']
        budget = Budget(category=category, amount=amount, start_date=start_date, end_date=end_date, user_id=user_id)
        db.session.add(budget)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('set_budget.html')

@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    transaction = db.session.get(Transaction, transaction_id)
    if request.method == 'POST':
        transaction.type = request.form['type']
        transaction.amount = float(request.form['amount'])
        transaction.category = request.form['category']
        transaction.currency = request.form['currency']
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_transaction.html', transaction=transaction)

@app.route('/delete_transaction/<int:transaction_id>')
def delete_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    transaction = db.session.get(Transaction, transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit_budget/<int:budget_id>', methods=['GET', 'POST'])
def edit_budget(budget_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    budget = db.session.get(Budget, budget_id)
    if request.method == 'POST':
        budget.category = request.form['category']
        budget.amount = float(request.form['amount'])
        budget.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        budget.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_budget.html', budget=budget)


@app.route('/delete_budget/<int:budget_id>')
def delete_budget(budget_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    budget = db.session.get(Budget, budget_id)
    db.session.delete(budget)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/api/spending_patterns')
def api_spending_patterns():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 403
    user_id = session['user_id']
    spending_patterns = calculate_spending_patterns(user_id)
    
    dates = sorted(spending_patterns.keys())
    amounts = [spending_patterns[date] for date in dates]
    
    return jsonify({'dates': dates, 'amounts': amounts})

@app.route('/api/spending_by_category')
def api_spending_by_category():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 403
    user_id = session['user_id']
    spending = calculate_spending(user_id)
    
    categories = list(spending.keys())
    amounts = [spending[category] for category in categories]
    
    return jsonify({'categories': categories, 'amounts': amounts})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
