# Personal Expense & Savings Planner (Python)

A command-line app to track monthly income, enforce a 20% savings rule, 
and monitor expenses by category between two salary dates (7th to next 7th).

## Features

- Add income with automatic 20% savings and 80% spending limit.
- Add expenses linked to an income cycle (7th of month to next 7th).
- Category-wise budgets (groceries, food, snacks, cloths, others).
- View all incomes and expenses with notes and linked income ID.
- Summary per income: savings, spending limit, total expenses, remaining money.
- Filter expenses by category and optional date range.

## Tech stack

- Python 3.9+
- JSON file storage for persistence
- `datetime` for custom monthly cycle and date handling

## How to run

```bash
python expense_planner.py
