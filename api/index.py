"""
Vercel serverless function - Gym Platform Web Demo
Complete Flask API with in-memory demo data
"""
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from datetime import datetime, date, timedelta
import random

app = Flask(__name__)
CORS(app)

# ============ DEMO DATA ============
# In-memory storage for demo purposes

DEMO_MEMBERS = [
    {"id": 1, "full_name": "Ahmed Hassan", "phone": "+212612345678", "gym_plan": "Monthly", "start_date": "2026-05-01", "end_date": "2026-06-01", "gym_fee_paid": 300, "is_active": True, "date_of_birth": "1995-03-15"},
    {"id": 2, "full_name": "Sara Benali", "phone": "+212698765432", "gym_plan": "Quarterly", "start_date": "2026-04-15", "end_date": "2026-07-15", "gym_fee_paid": 800, "is_active": True, "date_of_birth": "1998-07-22"},
    {"id": 3, "full_name": "Youssef Amrani", "phone": "+212655443322", "gym_plan": "Yearly", "start_date": "2026-01-01", "end_date": "2027-01-01", "gym_fee_paid": 2500, "is_active": True, "date_of_birth": "1990-11-08"},
    {"id": 4, "full_name": "Fatima Zahra", "phone": "+212677889900", "gym_plan": "Monthly", "start_date": "2026-05-20", "end_date": "2026-06-20", "gym_fee_paid": 300, "is_active": True, "date_of_birth": "2000-02-14"},
    {"id": 5, "full_name": "Omar Tazi", "phone": "+212611223344", "gym_plan": "Weekly", "start_date": "2026-05-28", "end_date": "2026-06-04", "gym_fee_paid": 100, "is_active": False, "date_of_birth": "1988-09-30"},
    {"id": 6, "full_name": "Khadija Mourad", "phone": "+212633445566", "gym_plan": "Monthly", "start_date": "2026-05-10", "end_date": "2026-06-10", "gym_fee_paid": 300, "is_active": True, "date_of_birth": "1996-12-05"},
    {"id": 7, "full_name": "Mehdi Alaoui", "phone": "+212644556677", "gym_plan": "Half-Year", "start_date": "2026-03-01", "end_date": "2026-09-01", "gym_fee_paid": 1500, "is_active": True, "date_of_birth": "1992-04-18"},
    {"id": 8, "full_name": "Nadia Benjelloun", "phone": "+212666778899", "gym_plan": "Monthly", "start_date": "2026-04-25", "end_date": "2026-05-25", "gym_fee_paid": 300, "is_active": False, "date_of_birth": "1999-08-11"},
]

DEMO_PRODUCTS = [
    {"id": 1, "name": "Protein Shake", "category": "Supplements", "price": 45, "stock": 25, "is_available": True},
    {"id": 2, "name": "Energy Bar", "category": "Snacks", "price": 15, "stock": 50, "is_available": True},
    {"id": 3, "name": "Gym Gloves", "category": "Accessories", "price": 80, "stock": 15, "is_available": True},
    {"id": 4, "name": "Water Bottle", "category": "Accessories", "price": 35, "stock": 30, "is_available": True},
    {"id": 5, "name": "Pre-Workout", "category": "Supplements", "price": 120, "stock": 10, "is_available": True},
    {"id": 6, "name": "Gym Towel", "category": "Accessories", "price": 25, "stock": 40, "is_available": True},
    {"id": 7, "name": "BCAA Powder", "category": "Supplements", "price": 95, "stock": 8, "is_available": True},
    {"id": 8, "name": "Resistance Band", "category": "Equipment", "price": 50, "stock": 20, "is_available": True},
]

DEMO_EXPENSES = [
    {"id": 1, "title": "Electricity Bill", "category": "Utilities", "amount": 850, "created_at": "2026-05-01", "created_by": "admin"},
    {"id": 2, "title": "Water Bill", "category": "Utilities", "amount": 200, "created_at": "2026-05-01", "created_by": "admin"},
    {"id": 3, "title": "Equipment Maintenance", "category": "Maintenance", "amount": 500, "created_at": "2026-05-15", "created_by": "admin"},
    {"id": 4, "title": "Cleaning Supplies", "category": "Supplies", "amount": 150, "created_at": "2026-05-20", "created_by": "admin"},
    {"id": 5, "title": "Internet Service", "category": "Utilities", "amount": 300, "created_at": "2026-05-01", "created_by": "admin"},
]

DEMO_PAYMENTS = [
    {"id": 1, "member_id": 1, "member_name": "Ahmed Hassan", "amount": 300, "payment_type": "gym_fee", "paid_at": "2026-05-01"},
    {"id": 2, "member_id": 2, "member_name": "Sara Benali", "amount": 800, "payment_type": "gym_fee", "paid_at": "2026-04-15"},
    {"id": 3, "member_id": 3, "member_name": "Youssef Amrani", "amount": 2500, "payment_type": "gym_fee", "paid_at": "2026-01-01"},
    {"id": 4, "member_id": 1, "member_name": "Ahmed Hassan", "amount": 45, "payment_type": "product", "paid_at": "2026-05-10"},
    {"id": 5, "member_id": 4, "member_name": "Fatima Zahra", "amount": 300, "payment_type": "gym_fee", "paid_at": "2026-05-20"},
]


# ============ HTML TEMPLATE ============
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gym Platform - Demo</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0a0506;
            --bg-card: #160d0e;
            --bg-elevated: #211314;
            --bg-hover: #2e1a1b;
            --primary: #e11d2e;
            --primary-dark: #991b1b;
            --primary-light: #f87171;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #f8fafc;
            --text-secondary: #cbb6b8;
            --text-muted: #8b7173;
            --border: #2c1819;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            min-height: 100vh;
        }
        
        .demo-banner {
            background: linear-gradient(90deg, var(--primary), var(--primary-dark));
            padding: 12px 20px;
            text-align: center;
            font-size: 14px;
            font-weight: 500;
        }
        
        .demo-banner a {
            color: white;
            text-decoration: underline;
            margin-left: 10px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo-icon {
            width: 50px;
            height: 50px;
            background: var(--primary);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }
        
        .logo h1 {
            font-size: 24px;
            font-weight: 700;
        }
        
        .logo span {
            font-size: 12px;
            color: var(--text-muted);
            display: block;
        }
        
        nav {
            display: flex;
            gap: 8px;
        }
        
        nav button {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
            background: var(--bg-elevated);
            color: var(--text);
        }
        
        nav button:hover, nav button.active {
            background: var(--primary);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border);
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            border-color: var(--primary);
            transform: translateY(-2px);
        }
        
        .stat-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        
        .stat-label {
            color: var(--text-muted);
            font-size: 14px;
        }
        
        .stat-trend {
            font-size: 12px;
            margin-top: 8px;
        }
        
        .stat-trend.up { color: var(--success); }
        .stat-trend.down { color: var(--danger); }
        
        .content-card {
            background: var(--bg-card);
            border-radius: 16px;
            border: 1px solid var(--border);
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .card-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .card-header h2 {
            font-size: 18px;
            font-weight: 600;
        }
        
        .search-box {
            display: flex;
            gap: 10px;
        }
        
        .search-box input {
            padding: 10px 16px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--bg-dark);
            color: var(--text);
            width: 250px;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 16px 24px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        th {
            color: var(--text-muted);
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        tr:hover td {
            background: var(--bg-elevated);
        }
        
        .badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .badge-success {
            background: rgba(34, 197, 94, 0.2);
            color: var(--success);
        }
        
        .badge-danger {
            background: rgba(239, 68, 68, 0.2);
            color: var(--danger);
        }
        
        .badge-warning {
            background: rgba(245, 158, 11, 0.2);
            color: var(--warning);
        }
        
        .section {
            display: none;
        }
        
        .section.active {
            display: block;
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        @media (max-width: 768px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
            nav {
                flex-wrap: wrap;
            }
            .search-box {
                flex-direction: column;
            }
            .search-box input {
                width: 100%;
            }
        }
        
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
            padding: 20px;
        }
        
        .product-card {
            background: var(--bg-elevated);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.2s;
        }
        
        .product-card:hover {
            transform: scale(1.02);
            border: 1px solid var(--primary);
        }
        
        .product-icon {
            font-size: 40px;
            margin-bottom: 12px;
        }
        
        .product-name {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .product-category {
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }
        
        .product-price {
            font-size: 20px;
            font-weight: 700;
            color: var(--primary-light);
        }
        
        .product-stock {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 8px;
        }
        
        .chart-placeholder {
            height: 200px;
            background: var(--bg-elevated);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            margin: 20px;
        }
        
        .expense-list {
            padding: 0;
        }
        
        .expense-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 24px;
            border-bottom: 1px solid var(--border);
        }
        
        .expense-item:hover {
            background: var(--bg-elevated);
        }
        
        .expense-info {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .expense-icon {
            width: 44px;
            height: 44px;
            background: var(--bg-elevated);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        .expense-title {
            font-weight: 500;
        }
        
        .expense-category {
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .expense-amount {
            font-weight: 600;
            color: var(--danger);
        }
        
        footer {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
            border-top: 1px solid var(--border);
            margin-top: 40px;
        }
        
        footer a {
            color: var(--primary-light);
        }
    </style>
</head>
<body>
    <div class="demo-banner">
        🎯 This is a DEMO version with sample data. <a href="#">Contact us for the full version</a>
    </div>
    
    <div class="container">
        <header>
            <div class="logo">
                <div class="logo-icon">🏋️</div>
                <div>
                    <h1>GYM PLATFORM</h1>
                    <span>Train · Track · Transform</span>
                </div>
            </div>
            <nav>
                <button class="active" onclick="showSection('dashboard')">📊 Dashboard</button>
                <button onclick="showSection('members')">👥 Members</button>
                <button onclick="showSection('products')">📦 Products</button>
                <button onclick="showSection('expenses')">💸 Expenses</button>
                <button onclick="showSection('payments')">💳 Payments</button>
            </nav>
        </header>
        
        <!-- Dashboard Section -->
        <section id="dashboard" class="section active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">👥</div>
                    <div class="stat-value" id="totalMembers">8</div>
                    <div class="stat-label">Total Members</div>
                    <div class="stat-trend up">↑ 12% this month</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-value" id="activeMembers">6</div>
                    <div class="stat-label">Active Members</div>
                    <div class="stat-trend up">↑ 8% this month</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💰</div>
                    <div class="stat-value" id="monthlyRevenue">5,245 DH</div>
                    <div class="stat-label">Monthly Revenue</div>
                    <div class="stat-trend up">↑ 15% vs last month</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📦</div>
                    <div class="stat-value" id="totalProducts">8</div>
                    <div class="stat-label">Products in Stock</div>
                    <div class="stat-trend">198 total items</div>
                </div>
            </div>
            
            <div class="grid-2">
                <div class="content-card">
                    <div class="card-header">
                        <h2>📅 Recent Members</h2>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Plan</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="recentMembers">
                        </tbody>
                    </table>
                </div>
                
                <div class="content-card">
                    <div class="card-header">
                        <h2>💸 Recent Expenses</h2>
                    </div>
                    <div class="expense-list" id="recentExpenses">
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Members Section -->
        <section id="members" class="section">
            <div class="content-card">
                <div class="card-header">
                    <h2>👥 Members Management</h2>
                    <div class="search-box">
                        <input type="text" placeholder="🔍 Search members..." id="memberSearch" onkeyup="filterMembers()">
                        <button class="btn btn-primary" onclick="alert('Demo: Add member form would open here')">+ Add Member</button>
                    </div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Phone</th>
                            <th>Plan</th>
                            <th>End Date</th>
                            <th>Fee Paid</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="membersTable">
                    </tbody>
                </table>
            </div>
        </section>
        
        <!-- Products Section -->
        <section id="products" class="section">
            <div class="content-card">
                <div class="card-header">
                    <h2>📦 Products & Inventory</h2>
                    <button class="btn btn-primary" onclick="alert('Demo: Add product form would open here')">+ Add Product</button>
                </div>
                <div class="product-grid" id="productsGrid">
                </div>
            </div>
        </section>
        
        <!-- Expenses Section -->
        <section id="expenses" class="section">
            <div class="content-card">
                <div class="card-header">
                    <h2>💸 Expenses Tracking</h2>
                    <button class="btn btn-primary" onclick="alert('Demo: Add expense form would open here')">+ Add Expense</button>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Category</th>
                            <th>Amount</th>
                            <th>Date</th>
                            <th>Created By</th>
                        </tr>
                    </thead>
                    <tbody id="expensesTable">
                    </tbody>
                </table>
            </div>
        </section>
        
        <!-- Payments Section -->
        <section id="payments" class="section">
            <div class="content-card">
                <div class="card-header">
                    <h2>💳 Payment History</h2>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Member</th>
                            <th>Amount</th>
                            <th>Type</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody id="paymentsTable">
                    </tbody>
                </table>
            </div>
        </section>
        
        <footer>
            <p>🏋️ <strong>Gym Platform</strong> - Professional Gym Management Software</p>
            <p style="margin-top: 10px;">This is a demo version. <a href="#">Contact us</a> to get the full desktop application.</p>
            <p style="margin-top: 20px; font-size: 12px;">© 2026 Gym Platform. All rights reserved.</p>
        </footer>
    </div>
    
    <script>
        // Demo Data
        const members = {{ members | tojson }};
        const products = {{ products | tojson }};
        const expenses = {{ expenses | tojson }};
        const payments = {{ payments | tojson }};
        
        // Product icons by category
        const productIcons = {
            'Supplements': '💊',
            'Snacks': '🍫',
            'Accessories': '🧤',
            'Equipment': '🏋️'
        };
        
        // Expense icons by category
        const expenseIcons = {
            'Utilities': '💡',
            'Maintenance': '🔧',
            'Supplies': '📦'
        };
        
        // Show section
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(sectionId).classList.add('active');
            document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        // Render members table
        function renderMembers(data = members) {
            const tbody = document.getElementById('membersTable');
            tbody.innerHTML = data.map(m => `
                <tr>
                    <td>#${m.id}</td>
                    <td><strong>${m.full_name}</strong></td>
                    <td>${m.phone}</td>
                    <td>${m.gym_plan}</td>
                    <td>${m.end_date}</td>
                    <td>${m.gym_fee_paid} DH</td>
                    <td><span class="badge ${m.is_active ? 'badge-success' : 'badge-danger'}">${m.is_active ? 'Active' : 'Inactive'}</span></td>
                </tr>
            `).join('');
        }
        
        // Filter members
        function filterMembers() {
            const query = document.getElementById('memberSearch').value.toLowerCase();
            const filtered = members.filter(m => 
                m.full_name.toLowerCase().includes(query) || 
                m.phone.includes(query) ||
                m.gym_plan.toLowerCase().includes(query)
            );
            renderMembers(filtered);
        }
        
        // Render recent members
        function renderRecentMembers() {
            const tbody = document.getElementById('recentMembers');
            tbody.innerHTML = members.slice(0, 5).map(m => `
                <tr>
                    <td><strong>${m.full_name}</strong></td>
                    <td>${m.gym_plan}</td>
                    <td><span class="badge ${m.is_active ? 'badge-success' : 'badge-danger'}">${m.is_active ? 'Active' : 'Inactive'}</span></td>
                </tr>
            `).join('');
        }
        
        // Render products grid
        function renderProducts() {
            const grid = document.getElementById('productsGrid');
            grid.innerHTML = products.map(p => `
                <div class="product-card">
                    <div class="product-icon">${productIcons[p.category] || '📦'}</div>
                    <div class="product-name">${p.name}</div>
                    <div class="product-category">${p.category}</div>
                    <div class="product-price">${p.price} DH</div>
                    <div class="product-stock">Stock: ${p.stock} units</div>
                </div>
            `).join('');
        }
        
        // Render expenses table
        function renderExpenses() {
            const tbody = document.getElementById('expensesTable');
            tbody.innerHTML = expenses.map(e => `
                <tr>
                    <td><strong>${e.title}</strong></td>
                    <td>${e.category}</td>
                    <td class="expense-amount">-${e.amount} DH</td>
                    <td>${e.created_at}</td>
                    <td>${e.created_by}</td>
                </tr>
            `).join('');
        }
        
        // Render recent expenses
        function renderRecentExpenses() {
            const list = document.getElementById('recentExpenses');
            list.innerHTML = expenses.slice(0, 4).map(e => `
                <div class="expense-item">
                    <div class="expense-info">
                        <div class="expense-icon">${expenseIcons[e.category] || '💰'}</div>
                        <div>
                            <div class="expense-title">${e.title}</div>
                            <div class="expense-category">${e.category}</div>
                        </div>
                    </div>
                    <div class="expense-amount">-${e.amount} DH</div>
                </div>
            `).join('');
        }
        
        // Render payments table
        function renderPayments() {
            const tbody = document.getElementById('paymentsTable');
            tbody.innerHTML = payments.map(p => `
                <tr>
                    <td>#${p.id}</td>
                    <td><strong>${p.member_name}</strong></td>
                    <td style="color: var(--success); font-weight: 600;">+${p.amount} DH</td>
                    <td><span class="badge ${p.payment_type === 'gym_fee' ? 'badge-success' : 'badge-warning'}">${p.payment_type}</span></td>
                    <td>${p.paid_at}</td>
                </tr>
            `).join('');
        }
        
        // Update stats
        function updateStats() {
            document.getElementById('totalMembers').textContent = members.length;
            document.getElementById('activeMembers').textContent = members.filter(m => m.is_active).length;
            document.getElementById('totalProducts').textContent = products.length;
            
            const totalRevenue = payments.reduce((sum, p) => sum + p.amount, 0);
            document.getElementById('monthlyRevenue').textContent = totalRevenue.toLocaleString() + ' DH';
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            renderMembers();
            renderRecentMembers();
            renderProducts();
            renderExpenses();
            renderRecentExpenses();
            renderPayments();
            updateStats();
        });
    </script>
</body>
</html>
'''


# ============ ROUTES ============

@app.route('/')
def index():
    """Render the main web app"""
    return render_template_string(
        HTML_TEMPLATE,
        members=DEMO_MEMBERS,
        products=DEMO_PRODUCTS,
        expenses=DEMO_EXPENSES,
        payments=DEMO_PAYMENTS
    )


@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "version": "2.0", "mode": "demo"})


@app.route('/api/members', methods=['GET'])
def get_members():
    return jsonify(DEMO_MEMBERS)


@app.route('/api/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = next((m for m in DEMO_MEMBERS if m['id'] == member_id), None)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(member)


@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(DEMO_PRODUCTS)


@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    return jsonify(DEMO_EXPENSES)


@app.route('/api/payments', methods=['GET'])
def get_payments():
    return jsonify(DEMO_PAYMENTS)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_members = len(DEMO_MEMBERS)
    active_members = len([m for m in DEMO_MEMBERS if m['is_active']])
    total_products = len(DEMO_PRODUCTS)
    total_revenue = sum(p['amount'] for p in DEMO_PAYMENTS)
    total_expenses = sum(e['amount'] for e in DEMO_EXPENSES)
    
    return jsonify({
        "total_members": total_members,
        "active_members": active_members,
        "total_products": total_products,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": total_revenue - total_expenses
    })


# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)