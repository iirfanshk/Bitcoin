
# ₿ Bitcoin Price Prediction & Analytics Platform

A web-based Bitcoin Price Prediction and Analytics Platform developed using Python and Flask. The application provides an interactive environment for exploring Bitcoin market trends, retrieving real-time cryptocurrency prices, analysing historical market data, and generating price predictions through multiple prediction approaches.

The platform also includes user authentication, an administrative dashboard, cryptocurrency news aggregation, and downloadable PDF reports.

## 📌 1. Project Overview

Bitcoin is one of the most actively traded cryptocurrencies, and its market price is influenced by several factors, including market demand, trading activity, investor sentiment, and global financial developments.

This project aims to build an interactive platform that brings cryptocurrency market information, historical price analysis, and prediction functionality together in one place.

Users can explore Bitcoin market information, view historical price trends, generate prediction outputs, and download reports to review the results.

The application is developed using Flask for backend functionality and integrates external cryptocurrency data sources to retrieve market information.

## 🎯 2. Project Objectives

The main objectives of this project are:

- Retrieve current Bitcoin market prices from external data providers.
- Collect and analyse historical Bitcoin price information.
- Explore different approaches to cryptocurrency price prediction.
- Present prediction outputs through an interactive web interface.
- Compare outputs from multiple prediction approaches.
- Generate downloadable PDF reports.
- Provide a dedicated administration interface for monitoring application activity.

## ✨ 3. Key Features

### 3.1 Real-Time Bitcoin Price Tracking

The application retrieves Bitcoin market prices using external data sources such as CoinGecko and Yahoo Finance.

Users can explore:

- Current Bitcoin price in USD.
- Historical market prices.
- Daily opening and closing prices.
- Highest and lowest recorded prices.
- Trading volume information.

This information helps users understand recent market movements and historical price behaviour.

### 3.2 Historical Market Data Analysis

Historical Bitcoin price information is used to explore market trends and price movements.

The application works with historical market data to provide a foundation for its prediction functionality.

Important data attributes include:

| Parameter | Description |
|---|---|
| Open | Opening price during a trading period |
| High | Highest price during a trading period |
| Low | Lowest price during a trading period |
| Close | Closing price during a trading period |
| Volume | Trading volume during a trading period |

### 3.3 Bitcoin Price Prediction

The application provides multiple prediction approaches to explore potential Bitcoin price movements.

The available approaches include:

1. LSTM
2. ARIMA
3. Gradient Boosting
4. Random Forest
5. Average-based Prediction

Each approach produces a numerical price output that can be displayed and compared within the application.

**Note:** The current implementations are prototype prediction functions rather than fully trained forecasting models. Their outputs are intended for demonstration and experimentation.

### 3.4 Ensemble Prediction

The application also provides an ensemble prediction approach that combines outputs from multiple prediction methods.

The purpose of this functionality is to demonstrate how predictions from different approaches can be brought together into a single result.

The ensemble output can be compared against individual prediction outputs.

### 3.5 Prediction Results and Numerical Analysis

The application presents prediction results in numerical form.

The output can include:

- Predicted Bitcoin price in USD.
- Individual prediction method outputs.
- Combined prediction output.
- Price difference.
- Percentage price change.

The percentage price change can be represented mathematically as:

Percentage Change = ((Predicted Price - Current Price) / Current Price) × 100

For example, consider the following illustrative values:

| Parameter | Example Value |
|---|---:|
| Current Bitcoin Price | $65,000 |
| Predicted Bitcoin Price | $66,000 |
| Price Difference | +$1,000 |
| Percentage Change | +1.54% |

These figures demonstrate the calculation format and are not actual application results or market forecasts.

### 3.6 PDF Report Generation

The application includes functionality to generate downloadable PDF reports.

The reports provide a convenient way to review prediction information outside the application.

Report content can include prediction summaries, numerical outputs, model comparisons, and graphical information.

### 3.7 Cryptocurrency News Aggregation

The application includes a news section that retrieves cryptocurrency-related news from external feeds.

This feature helps users explore recent Bitcoin and cryptocurrency developments alongside market information.

### 3.8 User Authentication

The platform provides user authentication functionality, including:

- User registration.
- User login.
- User logout.
- Separate user and administrator interfaces.

### 3.9 Admin Dashboard

The administrative dashboard provides functionality for monitoring application activity.

It includes features related to:

- User management.
- Prediction activity.
- Login activity monitoring.
- Application analytics.

## 🛠️ 4. Technology Stack

### Backend Development
- Python
- Flask

### Frontend Development
- HTML
- CSS
- JavaScript
- Jinja2 Templates

### Data Processing
- Pandas
- NumPy

### Machine Learning & Prediction
- Scikit-learn
- LSTM-related prediction interface
- ARIMA-related prediction interface
- Gradient Boosting
- Random Forest

### Financial Data Integration
- CoinGecko API
- Yahoo Finance (yFinance)

### Reporting & Additional Libraries
- ReportLab
- Feedparser
- Requests

## 🔄 5. Application Workflow

The overall application workflow follows these steps:

1. **User Access:** Users access the platform through the Flask web application.
2. **Authentication:** Users register or log in to access the application.
3. **Market Data Retrieval:** The application fetches Bitcoin price information from external data providers.
4. **Historical Data Processing:** Retrieved market information is prepared for analysis.
5. **Prediction Generation:** Users access the available prediction approaches.
6. **Result Comparison:** Individual prediction outputs and ensemble results are presented.
7. **Report Generation:** Users can generate downloadable PDF reports.
8. **Market Updates:** Users can explore cryptocurrency-related news.

## 📁 6. Project Structure

```text
Bitcoin/
│
├── templates/
│   ├── admin/
│   ├── auth/
│   └── user/
│
├── app.py
├── requirements.txt
├── package.json
├── vercel.json
└── .python-version
```

## ⚙️ 7. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/iirfanshk/Bitcoin.git
```

### Step 2: Navigate to the Project Directory

```bash
cd Bitcoin
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### Step 5: Install Required Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
python app.py
```

### Step 7: Access the Application

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

## 📸 8. Application Screenshots

Screenshots of the application, including the dashboard, Bitcoin market information, prediction results, and PDF reports, will be added here.

## 🔮 9. Future Improvements

Potential improvements for the project include:

- Implementing properly trained LSTM and ARIMA forecasting models.
- Integrating additional market indicators and technical analysis.
- Evaluating forecasting performance using MAE, RMSE, and R².
- Improving ensemble prediction techniques.
- Introducing persistent database storage.
- Enhancing application security and authentication.
- Adding interactive historical price visualisations.

## ⚠️ 10. Disclaimer

This project is developed for educational and demonstration purposes.

The current prediction functions are prototype implementations and should not be considered reliable financial forecasts.

Cryptocurrency markets are highly volatile. The application does not provide financial or investment advice.

---

## 👨‍💻 Developed By

**Irfan**

GitHub: https://github.com/iirfanshk
