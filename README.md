# 🌐 Sentiment Sphere

> A Facebook comments sentiment analysis and triage dashboard built with Flask.

Sentiment Sphere fetches comments from a Facebook Page via the Meta Graph API, automatically classifies them as **positive**, **negative**, or **neutral** using NLP, and provides a rich internal dashboard for support engineers to review, log cases, reply, and track resolution metrics.

---

## ✨ Features

- **Automated Sentiment Analysis** — NLTK-powered sentiment scoring on every fetched comment
- **Facebook Graph API Integration** — Live comment sync with automatic reply posting
- **Interactive Dashboard** — Filter by sentiment, date range, and status; switch between card and table views
- **Case Management** — Log Salesforce cases, assign associates, and track acknowledgements
- **Analytics & Charts** — Monthly trends, sentiment distribution, word cloud, user activity, associate performance, and repeated issue categorisation
- **CSV Export** — Download the full comment log as a spreadsheet
- **Docker Support** — Dockerfile included for containerised deployment

---

## 🖥️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | SQLite via SQLAlchemy |
| NLP | NLTK (VADER) |
| API | Meta Graph API |
| Frontend | Jinja2 templates, Chart.js, WordCloud2.js |
| Container | Docker |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A Facebook Page Access Token with `pages_read_engagement` and `pages_manage_posts` permissions

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Jeevan-b-03/sentiment-sphere.git
cd sentiment-sphere

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Facebook Access Token
#    Open app.py and replace the ACCESS_TOKEN value (or move it to an .env file)

# 5. Run the app
python app.py
```

The app will be available at `http://127.0.0.1:5000`.

### Default Login Credentials

| Username | Password |
|----------|----------|
| admin | admin |
| manager | manager |

> ⚠️ Change these credentials before deploying to production.

---

## 🐳 Docker

```bash
docker build -t sentiment-sphere .
docker run -p 5000:5000 sentiment-sphere
```

---

## 📁 Project Structure

```
sentiment-sphere/
├── app.py                  # Flask routes and core logic
├── models.py               # SQLAlchemy Comment model
├── sentiment_engine.py     # FB API fetch + NLTK sentiment analysis
├── requirements.txt        # Python dependencies
├── Dockerfile
├── README.md
├── .gitignore
├── templates/
│   ├── base.html           # Base layout
│   ├── dashboard.html      # Main triage dashboard
│   ├── graphs.html         # Analytics graphs page
│   └── login.html          # Login page
└── static/
    └── img/                # UI icons and assets
```

---

## ⚙️ Configuration

| Setting | Location | Description |
|---------|----------|-------------|
| `ACCESS_TOKEN` | `app.py` line 21 | Facebook Page Access Token |
| `SECRET_KEY` | `app.py` line 11 | Flask session secret |
| `DATABASE_URI` | `app.py` line 12 | SQLite path (default: `instance/comments.db`) |

> **Recommended:** Move `ACCESS_TOKEN` and `SECRET_KEY` to environment variables or a `.env` file before production use.

---

## 📊 Dashboard Overview

| Section | Description |
|---------|-------------|
| Metric Cards | Total, positive, negative, neutral comment counts |
| Monthly Chart | Comment volume by month |
| Sentiment Trend | Line chart of sentiment over time |
| Word Cloud | Most frequent words colour-coded by sentiment |
| Repeated Issues | Top issue categories from negative comments |
| Comment Cards | Individual comments with action controls |

---

## 📄 License

Internal tool — not licensed for public distribution.
