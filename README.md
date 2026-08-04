# Delivery Pattern Analytics Platform

## Project Overview

The Delivery Pattern Analytics Platform is a Python-based analytics dashboard developed to help food delivery operations teams identify delivery patterns that lead to SLA (Service Level Agreement) violations during peak hours.

The platform centralizes delivery logs, rider assignments, customer complaints, and refund records into a single dashboard, enabling data-driven operational decisions.

---

## Tech Stack

- Python
- Flask
- SQLite
- HTML5
- CSS3
- Bootstrap 5
- Chart.js

---

## Project Structure

```
SW2627-Python-DeliveryPatternAnalytics/

├── app/
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   └── utils/
│
├── run.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Setup Instructions

### Clone Repository

```bash
git clone https://github.com/<your-username>/SW2627-Python-DeliveryPatternAnalytics.git
```

### Navigate into Project

```bash
cd SW2627-Python-DeliveryPatternAnalytics
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Git Bash

```bash
source venv/Scripts/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python run.py
```

---

## Features

- Delivery Dashboard
- Rider Performance
- SLA Analysis
- Complaint Analysis
- Refund Analysis
- Reports

---

# GitHub Workflow

## Branch Strategy

The project follows a feature branch workflow.

```
main
│
├── feature/github-workflow-setup
├── feature/dashboard-ui
├── feature/database-models
```

Only reviewed code is merged into the main branch.

---

## Commit Convention

We use Conventional Commits.

Examples

```
feat: add dashboard page
fix: correct database query
docs: update project documentation
refactor: improve application structure
chore: update project dependencies
```

---

## Pull Request Process

Every feature is developed in its own branch.

Each Pull Request includes:

- Summary
- Related GitHub Issue
- Testing information

---

## Issue Tracking

All development tasks are tracked using GitHub Issues.

Each issue contains:

- Title
- Description
- Label
- Assignee

## Team

SW2627 Project