"""
Seed the Gym Platform database with realistic demo data.

`seed_data()` runs automatically on first launch (from init_db) and only when
the database is empty. It fills every tab with believable data: members in
all membership states, employees, products, payments, expenses, purchases,
today's check-ins and a rich activity/audit log.

To wipe an existing database and regenerate this data, run:
    python seed_fake_data.py
"""
import random
from datetime import date, datetime, timedelta

from backend.database import get_db_session
from backend.models import (
    SystemUser, Member, MemberActivity, Product, Purchase,
    Payment, Expense, EmployeeLog,
)
from backend.utils.auth import get_password_hash

DIAL = "+212"

FIRST_NAMES = [
    "Alice", "Bilal", "Carlos", "Diana", "Emir", "Fatima", "George", "Hana",
    "Imane", "Jamal", "Karim", "Lina", "Mohammed", "Nadia", "Omar", "Priya",
    "Rania", "Samir", "Tariq", "Umar", "Vera", "Walid", "Yasmine", "Zaid",
    "Adam", "Carla", "Driss", "Sofia", "Nabil", "Leila",
]
LAST_NAMES = [
    "Strong", "Power", "Iron", "Steel", "Swift", "Bolt", "Flex", "Stone",
    "Hawk", "Titan", "Vital", "Forge", "Peak", "Rush", "Core", "Pulse",
    "Lift", "Hammer", "Blaze", "Storm",
]
PLANS = {
    "Daily": (1, 8), "Weekly": (7, 25), "Monthly": (30, 300),
    "Quarterly": (90, 800), "Half-Year": (180, 1400), "Yearly": (365, 2500),
    "Student": (30, 200), "VIP": (30, 600),
}
EXPENSE_PRESETS = [
    ("Electricity", "Monthly electricity bill", (800, 1800)),
    ("Water", "Monthly water bill", (200, 600)),
    ("Internet", "Internet service fee", (300, 500)),
    ("Rent", "Monthly rent payment", (5000, 9000)),
    ("Maintenance", "Equipment maintenance", (400, 2000)),
    ("Cleaning", "Cleaning services", (300, 900)),
    ("Equipment", "New equipment purchase", (1500, 6000)),
    ("Marketing", "Social media campaign", (500, 2500)),
    ("Supplies", "Front-desk supplies", (150, 700)),
    ("Security", "Security service", (600, 1200)),
    ("Software", "Management software", (200, 800)),
    ("Insurance", "Facility insurance", (900, 2200)),
]
PRODUCTS = [
    ("Water Bottle", "drinks", 2.00, 100), ("Protein Bar", "nutrition", 5.00, 60),
    ("Greek Yogurt", "nutrition", 4.00, 30), ("Gym Towel", "accessories", 8.00, 40),
    ("Whey Protein Shake", "nutrition", 7.00, 25), ("Energy Drink", "drinks", 3.50, 80),
    ("Resistance Band", "accessories", 12.00, 20), ("Gym Gloves", "accessories", 15.00, 18),
    ("Shaker Bottle", "accessories", 6.00, 35), ("Pre-Workout", "nutrition", 25.00, 12),
    ("Headband", "accessories", 5.00, 50), ("Protein Chips", "nutrition", 3.00, 45),
    ("BCAA Drink", "nutrition", 6.50, 22), ("Lifting Straps", "accessories", 10.00, 16),
]
ACTIVITIES = ["Personal Training", "Yoga Class", "CrossFit", "Boxing", "Spin Class", "Pilates"]


def seed_data():
    """Populate the database with demo data, but only if it is empty."""
    db = get_db_session()
    try:
        if db.query(SystemUser).count() > 0:
            return  # already has data — don't duplicate

        random.seed(42)
        today = date.today()
        now = datetime.now()

        def _dt(days_ago=0, hour=None):
            d = now - timedelta(days=days_ago)
            if hour is not None:
                d = d.replace(hour=hour, minute=random.randint(0, 59), second=0, microsecond=0)
            return d

        # ---------------- Employees / users ----------------
        users = [
            SystemUser(username="admin", hashed_password=get_password_hash("admin123"),
                       full_name="Main Administrator", role="admin", salary=0,
                       working_days=6, phone=f"{DIAL}600112233",
                       hire_date=today - timedelta(days=900), is_active=True, created_at=_dt(900)),
            SystemUser(username="sara", hashed_password=get_password_hash("sara123"),
                       full_name="Sara Bennani", role="employee", salary=4200,
                       working_days=6, phone=f"{DIAL}611223344",
                       hire_date=today - timedelta(days=400), is_active=True, created_at=_dt(400)),
            SystemUser(username="youssef", hashed_password=get_password_hash("youssef123"),
                       full_name="Youssef El Amrani", role="employee", salary=3800,
                       working_days=5, phone=f"{DIAL}622334455",
                       hire_date=today - timedelta(days=250), is_active=True, created_at=_dt(250)),
            SystemUser(username="khalid", hashed_password=get_password_hash("khalid123"),
                       full_name="Khalid Tazi", role="employee", salary=3500,
                       working_days=6, phone=f"{DIAL}633445566",
                       hire_date=today - timedelta(days=120), is_active=True, created_at=_dt(120)),
        ]
        db.add_all(users)
        db.flush()
        employees = users

        # ---------------- Products ----------------
        products = [Product(name=n, category=c, price=p, stock=s, is_available=True)
                    for (n, c, p, s) in PRODUCTS]
        db.add_all(products)
        db.flush()

        # ---------------- Members (all membership states) ----------------
        buckets = (["active"] * 16) + (["expiring"] * 4) + (["expired"] * 5) + (["inactive"] * 3)
        random.shuffle(buckets)
        members = []
        used_names = set()
        for i, status in enumerate(buckets):
            while True:
                name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
                if name not in used_names:
                    used_names.add(name)
                    break
            plan = random.choice(list(PLANS.keys()))
            duration, fee = PLANS[plan]

            if status == "active":
                end = today + timedelta(days=random.randint(12, 320)); is_active = True
            elif status == "expiring":
                end = today + timedelta(days=random.randint(1, 7)); is_active = True
            elif status == "expired":
                end = today - timedelta(days=random.randint(1, 60)); is_active = True
            else:
                end = today - timedelta(days=random.randint(20, 120)); is_active = False
            start = end - timedelta(days=duration)

            if i < 2:
                dob = date(random.randint(1985, 2003), today.month, today.day)
            elif i < 5:
                fut = today + timedelta(days=random.randint(1, 14))
                dob = date(random.randint(1985, 2003), fut.month, fut.day)
            else:
                dob = date(random.randint(1980, 2004), random.randint(1, 12), random.randint(1, 28))

            members.append(Member(
                full_name=name, date_of_birth=dob,
                phone_number=f"{DIAL}6{random.randint(10000000, 99999999)}",
                start_date=start, end_date=end, gym_plan=plan, gym_fee_paid=float(fee),
                is_active=is_active, renewal_notified=False,
                created_at=datetime.combine(start, datetime.min.time()) + timedelta(hours=10),
            ))
        db.add_all(members)
        db.flush()

        # ---------------- Payments ----------------
        rcp = 1
        payments = []
        for m in members:
            payments.append(Payment(
                member_id=m.id, amount=m.gym_fee_paid, payment_type="Membership",
                description=f"{m.gym_plan} membership", receipt_number=f"RCP-{rcp:04d}",
                paid_at=datetime.combine(m.start_date, datetime.min.time()) + timedelta(hours=11)))
            rcp += 1
            if random.random() < 0.5:
                payments.append(Payment(
                    member_id=m.id, amount=round(m.gym_fee_paid * random.uniform(0.8, 1.0), 2),
                    payment_type="Renewal", description="Membership renewal",
                    receipt_number=f"RCP-{rcp:04d}", paid_at=_dt(random.randint(1, 75), hour=12)))
                rcp += 1
        for _ in range(40):
            m = random.choice(members)
            kind, amt = random.choice([("Product Sale", round(random.uniform(2, 30), 2)),
                                       ("Day Pass", round(random.uniform(5, 15), 2))])
            payments.append(Payment(
                member_id=m.id, amount=amt, payment_type=kind, description=kind,
                receipt_number=f"RCP-{rcp:04d}", paid_at=_dt(random.randint(0, 300), hour=15)))
            rcp += 1
        db.add_all(payments)

        # ---------------- Expenses ----------------
        exp_no = 1
        expenses = []
        for month_back in range(0, 11):
            for cat, desc, (lo, hi) in random.sample(EXPENSE_PRESETS, k=random.randint(3, 6)):
                expenses.append(Expense(
                    title=desc, description=desc, amount=float(random.randint(lo, hi)),
                    category=cat, receipt_number=f"EXP-{exp_no:04d}",
                    created_by=random.choice(employees).username,
                    created_at=_dt(month_back * 30 + random.randint(0, 27), hour=9)))
                exp_no += 1
        db.add_all(expenses)

        # ---------------- Purchases ----------------
        for _ in range(18):
            m = random.choice(members); p = random.choice(products); qty = random.randint(1, 3)
            db.add(Purchase(member_id=m.id, product_id=p.id, quantity=qty,
                            total_price=round(p.price * qty, 2),
                            purchased_by=random.choice(employees).username,
                            purchased_at=_dt(random.randint(0, 90), hour=16)))

        # ---------------- Member activities ----------------
        for _ in range(12):
            m = random.choice(members)
            db.add(MemberActivity(member_id=m.id, activity_type=random.choice(ACTIVITIES),
                                  fee=float(random.randint(50, 300)), is_paid=random.random() < 0.7,
                                  enrolled_at=_dt(random.randint(0, 120), hour=17)))

        # ---------------- Employee logs (activity / check-ins / audit) ----------------
        logs = []
        for e in employees:
            for _ in range(random.randint(4, 9)):
                logs.append(EmployeeLog(employee_id=e.id, employee_username=e.username,
                                        action="Logged in",
                                        created_at=_dt(random.randint(0, 30), hour=random.randint(7, 20))))
        for m in random.sample(members, k=8):  # today's check-ins
            e = random.choice(employees)
            logs.append(EmployeeLog(employee_id=e.id, employee_username=e.username,
                                    action=f"Check-in: {m.full_name}",
                                    created_at=_dt(0, hour=random.randint(7, 19))))
        for _ in range(35):  # past two weeks
            m = random.choice(members); e = random.choice(employees)
            logs.append(EmployeeLog(employee_id=e.id, employee_username=e.username,
                                    action=f"Check-in: {m.full_name}",
                                    created_at=_dt(random.randint(1, 14), hour=random.randint(7, 20))))
        for _ in range(4):  # leave requests
            e = random.choice(employees[1:])
            lt = random.choice(["Vacation", "Sick Leave", "Personal"])
            s = today + timedelta(days=random.randint(3, 30))
            logs.append(EmployeeLog(employee_id=e.id, employee_username=e.username,
                                    action=f"Leave Request: {lt} from {s} to {s + timedelta(days=random.randint(1, 5))}",
                                    created_at=_dt(random.randint(0, 20), hour=10)))
        for m in random.sample(members, k=6):  # audit-style
            e = random.choice(employees)
            logs.append(EmployeeLog(employee_id=e.id, employee_username=e.username,
                                    action=f"Added member: {m.full_name}",
                                    created_at=datetime.combine(m.start_date, datetime.min.time()) + timedelta(hours=11)))
        db.add_all(logs)

        db.commit()
        print(f"[seed] Demo data ready: {len(members)} members, {len(payments)} payments, "
              f"{len(expenses)} expenses, {len(logs)} logs. Login: admin / admin123")
    except Exception as e:
        db.rollback()
        print(f"[seed] Seed error: {e}")
    finally:
        db.close()
