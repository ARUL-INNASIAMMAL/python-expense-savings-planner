from datetime import datetime, timedelta
import json
import os

DATA_FILE = "records.json"

CATEGORY_LIMITS = {
    "groceries": 300,
    "food": 400,
    "snacks": 300,
    "cloths": 850,
    "others": 0
}

def get_valid_date(prompt="Enter date (YYYY-MM-DD): "):
    while True:
        date_str = input(prompt).strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD (example: 2026-01-07).")

def load_records():
    if not os.path.exists(DATA_FILE):
        return [], 1, CATEGORY_LIMITS.copy()

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    records = data.get("records", [])
    next_id = data.get("next_income_id", 1)
    category_remaining = data.get("category_remaining", CATEGORY_LIMITS.copy())
    return records, next_id, category_remaining


def save_records():
    data = {
        "records": records,
        "next_income_id": next_income_id,
        "category_remaining": category_remaining
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


records, next_income_id, category_remaining = load_records()


def parse_date(date_str):   #this function gets i/p as string and changes into actual
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_income_period_start(d):
    # For any date d, its period starts at the 7th
    if d.day >= 7:
        return d.replace(day=7)
    else:
        # previous month 7th
        first_of_month = d.replace(day=1)
        prev_month_last = first_of_month - timedelta(days=1)
        return prev_month_last.replace(day=7)


def find_active_income(expense_date):
    d = parse_date(expense_date)
    period_start = get_income_period_start(d)

    # find income whose date == that period_start (the income for this cycle)
    candidates = [
        r for r in records
        if r["type"] == "income" and parse_date(r["date"]) == period_start
    ]
    if not candidates:
        return None
    return candidates[-1]  # last added if multiple


def add_income():
    global next_income_id
    amount = float(input("Enter income amount: "))
    category = input("Enter income category: ")
    date = get_valid_date("Enter date (YYYY-MM-DD): ")
    note = input("Enter a note: ")

    saving = amount * 0.20
    spending_limit = amount * 0.80

    income_record = {
        "id": next_income_id,
        "type": "income",
        "amount": amount,
        "category": category,
        "date": date,
        "note": note,  # <-- added
        "saving": saving,
        "spending_limit": spending_limit
    }


    records.append(income_record)
    next_income_id += 1
    save_records()



    print("Income added successfully!")
    print(f"Savings added: {saving} (20% of your income)")
    print(f"Available to spend this cycle: {spending_limit}")



def add_expense():
    print("---Add Expense---")
    amount = float(input("Enter Expense amount: "))

    print("Choose category:")
    print("1. groceries - 300")
    print("2. food      - 400")
    print("3. snacks    - 300")
    print("4. cloths    - 850")
    print("5. others    - no fixed limit")

    choice = input("Enter category number (1-5): ")

    if choice == "1":
        category = "groceries"
    elif choice == "2":
        category = "food"
    elif choice == "3":
        category = "snacks"
    elif choice == "4":
        category = "cloths"
    elif choice == "5":
        category = "others"
    else:
        print("Invalid category. Setting to 'others'.")
        category = "others"

    note = input("Enter a note: ")
    date = get_valid_date("Enter date (YYYY-MM-DD): ")


    income = find_active_income(date)
    if income is None:
        print("No income found for this period (7th to next 7th).")
        print("Please add the income for this month (date = 7th) first.")
        return

    expense_record = {
        "type": "expense",
        "amount": amount,
        "category": category,
        "note": note,
        "date": date,
        "parent_income_id": income["id"]
    }

    # --- category budget handling ---
    limit = CATEGORY_LIMITS.get(category)
    if limit is not None and limit > 0:
        left_before = category_remaining[category]
        left_after = left_before - amount

        if left_after < 0:
            print(f"Warning: {category} budget exceeded!")
            print(f"Limit: {limit}, remaining before: {left_before}, after this: {left_after}")
        else:
            print(f"{category} remaining after this: {left_after}/{limit}")

        category_remaining[category] = left_after
    # -------------------------------

    records.append(expense_record)
    save_records()

    print(f"Expense added successfully under income ID {income['id']}!")


def view_records():
    print("-----All Records-----")
    if not records:
        print("No records found yet")
        return

    for index, record in enumerate(records, start=1):
        extra = ""
        if record["type"] == "expense" and "parent_income_id" in record:
            extra = f" | income_id:{record['parent_income_id']}"
        print(
            f"{index}.[{record['type'].upper()}] "
            f"Amount:{record['amount']} | "
            f"category:{record['category']} | "
            f"date:{record['date']} | "
            f"note:{record.get('note', '')}{extra}"

        )


def show_summary():
    print("---Summary & Savings Suggestion---")

    incomes = [r for r in records if r["type"] == "income"]
    if not incomes:
        print("No incomes added yet.")
        return

    for income in incomes:
        income_id = income["id"]
        income_amount = income["amount"]
        saving = income.get("saving", income_amount * 0.20)
        spending_limit = income.get("spending_limit", income_amount * 0.80)

        linked_expenses = [
            r for r in records
            if r["type"] == "expense" and r.get("parent_income_id") == income_id
        ]
        total_expense = sum(e["amount"] for e in linked_expenses)

        remaining_spending = spending_limit - total_expense

        print(f"\nIncome ID: {income_id} | Date: {income['date']}")
        print(f"  Income amount          : {income_amount}")
        print(f"  Locked saving (20%)    : {saving}")
        print(f"  Spending limit (80%)   : {spending_limit}")
        print(f"  Total expenses (this 80%): {total_expense}")
        print(f"  Remaining spending money: {remaining_spending}")


def filter_expenses():
    print("--- Filter Expenses by Category and Date ---")

    # 1) Choose category
    print("Choose category:")
    print("1. groceries")
    print("2. food")
    print("3. snacks")
    print("4. cloths")
    print("5. others")
    choice = input("Enter category number (1-5): ")

    if choice == "1":
        category = "groceries"
    elif choice == "2":
        category = "food"
    elif choice == "3":
        category = "snacks"
    elif choice == "4":
        category = "cloths"
    elif choice == "5":
        category = "others"
    else:
        print("Invalid category choice.")
        return

    # 2) Optional date range
    use_dates = input("Filter by date range? (y/n): ").strip().lower()
    start_date = None
    end_date = None

    if use_dates == "y":
        start_date_str = get_valid_date("Enter start date (YYYY-MM-DD): ")
        end_date_str = get_valid_date("Enter end date (YYYY-MM-DD): ")

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        if end_date < start_date:
            print("End date cannot be before start date.")
            return

    # 3) Filter expenses
    filtered = []
    for r in records:
        if r["type"] != "expense":
            continue
        if r["category"] != category:
            continue

        expense_date = parse_date(r["date"])

        if start_date and end_date:
            if not (start_date <= expense_date <= end_date):
                continue

        filtered.append(r)

    # 4) Show result
    if not filtered:
        if start_date and end_date:
            print(f"No expenses found for '{category}' between {start_date} and {end_date}.")
        else:
            print(f"No expenses found for '{category}'.")
        return

    print(f"\nExpenses for category '{category}':")
    total = 0
    for idx, r in enumerate(filtered, start=1):
        print(
            f"{idx}. Amount: {r['amount']} | date: {r['date']} | "
            f"note: {r.get('note', '')} | income_id: {r.get('parent_income_id', '-')}"
        )
        total += r["amount"]

    print(f"\nTotal expenses in this filter: {total}")
        


def main():
    while True:
        print("===Personal Expense & Savings Planner===")
        print("1. Add income")
        print("2. Add Expense")
        print("3. View All Records")
        print("4. Show Summary & Savings Suggestion")
        print("5. Filter Expenses by Category/Date")
        print("6. Exit")

        choice = input("Enter your choice(1-6): ")
        if choice == "1":
            add_income()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            view_records()
        elif choice == "4":
            show_summary()
        elif choice == "5":
            filter_expenses()
        elif choice == "6":
            print("Exiting...Goodbye!")
            break
        else:
            print("Invalid Choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
