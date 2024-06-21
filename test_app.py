import os
import unittest
from app import app, db, User, Transaction, Budget, calculate_spending, get_exchange_rate, convert_currency, calculate_spending_patterns
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from flask import session

# Set the Flask environment to testing
os.environ['FLASK_ENV'] = 'testing'

class ExpenseTrackerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_expenses.db'
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.create_test_user()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_user(self):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            if not user:
                user = User(username='testuser', password=generate_password_hash('testpassword'))
                db.session.add(user)
                db.session.commit()

    def test_signup(self):
        response = self.app.post('/signup', data=dict(
            username='newuser',
            password='newpassword'
        ), follow_redirects=True)
        with self.app as c:
            with c.session_transaction() as sess:
                flash_messages = sess.get('_flashes', [])
                self.assertIn(('message', 'User registered successfully!'), flash_messages)

    def test_login(self):
        response = self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)

    def test_invalid_login(self):
        response = self.app.post('/login', data=dict(
            username='testuser',
            password='wrongpassword'
        ), follow_redirects=True)
        with self.app as c:
            with c.session_transaction() as sess:
                flash_messages = sess.get('_flashes', [])
                self.assertIn(('message', 'Invalid username or password'), flash_messages)

    def test_calculate_spending(self):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            transaction = Transaction(
                user_id=user.id,
                type='expense',
                amount=100.0,
                category='Food',
                currency='CAD',
                date=datetime.now(timezone.utc)
            )
            db.session.add(transaction)
            db.session.commit()

            spending = calculate_spending(user.id)
            self.assertEqual(spending['Food'], 100.0)

    def test_get_exchange_rate(self):
        rate = get_exchange_rate('USD')
        self.assertIsInstance(rate, float)
        self.assertGreater(rate, 0)

    def test_convert_currency(self):
        converted_amount = convert_currency(100, 'USD')
        self.assertIsInstance(converted_amount, float)
        self.assertGreater(converted_amount, 0)

    def test_calculate_spending_patterns(self):
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            transaction1 = Transaction(
                user_id=user.id,
                type='expense',
                amount=100.0,
                category='Food',
                currency='CAD',
                date=datetime(2023, 1, 15, tzinfo=timezone.utc)
            )
            transaction2 = Transaction(
                user_id=user.id,
                type='expense',
                amount=150.0,
                category='Transport',
                currency='CAD',
                date=datetime(2023, 2, 15, tzinfo=timezone.utc)
            )
            db.session.add(transaction1)
            db.session.add(transaction2)
            db.session.commit()

            patterns = calculate_spending_patterns(user.id)
            self.assertEqual(patterns['2023-01'], 100.0)
            self.assertEqual(patterns['2023-02'], 150.0)

    def test_add_transaction(self):
        self.create_test_user()
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.app.post('/add_transaction', data=dict(
            type='expense',
            amount='50.0',
            category='Food',
            currency='CAD',
            date='2024-06-01'
        ), follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            transactions = Transaction.query.filter_by(user_id=user.id).all()
            self.assertEqual(len(transactions), 1)
            self.assertEqual(transactions[0].amount, 50.0)
            self.assertEqual(transactions[0].category, 'Food')

    def test_edit_transaction(self):
        self.create_test_user()
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            transaction = Transaction(
                user_id=user.id,
                type='expense',
                amount=100.0,
                category='Food',
                currency='CAD',
                date=datetime.now(timezone.utc)
            )
            db.session.add(transaction)
            db.session.commit()
            transaction_id = transaction.id
        
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.app.post(f'/edit_transaction/{transaction_id}', data=dict(
            type='expense',
            amount='150.0',
            category='Food',
            currency='CAD',
            date='2024-06-01'
        ), follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)
        with app.app_context():
            edited_transaction = db.session.get(Transaction, transaction_id)
            self.assertEqual(edited_transaction.amount, 150.0)

    def test_delete_transaction(self):
        self.create_test_user()
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            transaction = Transaction(
                user_id=user.id,
                type='expense',
                amount=100.0,
                category='Food',
                currency='CAD',
                date=datetime.now(timezone.utc)
            )
            db.session.add(transaction)
            db.session.commit()
            transaction_id = transaction.id
        
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.app.get(f'/delete_transaction/{transaction_id}', follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)
        with app.app_context():
            deleted_transaction = db.session.get(Transaction, transaction_id)
            self.assertIsNone(deleted_transaction)

    def test_set_budget(self):
        self.create_test_user()
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.app.post('/set_budget', data=dict(
            category='Food',
            amount='200.0',
            start_date='2024-06-01',
            end_date='2024-06-30'
        ), follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            budgets = Budget.query.filter_by(user_id=user.id).all()
            self.assertEqual(len(budgets), 1)
            self.assertEqual(budgets[0].amount, 200.0)
            self.assertEqual(budgets[0].category, 'Food')

    def test_edit_budget(self):
        self.create_test_user()
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            budget = Budget(
                user_id=user.id,
                category='Food',
                amount=200.0,
                start_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 6, 30, tzinfo=timezone.utc)
            )
            db.session.add(budget)
            db.session.commit()
            budget_id = budget.id
        
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.app.post(f'/edit_budget/{budget_id}', data=dict(
            category='Food',
            amount='250.0',
            start_date='2024-06-01',
            end_date='2024-06-30'
        ), follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)
        with app.app_context():
            edited_budget = db.session.get(Budget, budget_id)
            self.assertEqual(edited_budget.amount, 250.0)

    def test_delete_budget(self):
        self.create_test_user()
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            budget = Budget(
                user_id=user.id,
                category='Food',
                amount=200.0,
                start_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 6, 30, tzinfo=timezone.utc)
            )
            db.session.add(budget)
            db.session.commit()
            budget_id = budget.id
        
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.app.get(f'/delete_budget/{budget_id}', follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)
        with app.app_context():
            deleted_budget = db.session.get(Budget, budget_id)
            self.assertIsNone(deleted_budget)

    def test_exceed_budget_notification(self):
        self.create_test_user()
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            budget = Budget(
                user_id=user.id,
                category='Food',
                amount=50.0,
                start_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 6, 30, tzinfo=timezone.utc)
            )
            db.session.add(budget)
            db.session.commit()
            transaction = Transaction(
                user_id=user.id,
                type='expense',
                amount=100.0,
                category='Food',
                currency='CAD',
                date=datetime.now(timezone.utc)
            )
            db.session.add(transaction)
            db.session.commit()
        
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertIn(b'exceeded your budget', response.data)

    def test_dashboard_access_without_login(self):
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Log In', response.data)

    def test_logout(self):
        self.create_test_user()
        self.app.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Log In', response.data)

if __name__ == '__main__':
    unittest.main()
