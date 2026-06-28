
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
from datetime import datetime, timedelta
import requests
import yfinance as yf
import pickle
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import feedparser
from urllib.parse import quote

# ========================
# ML Model Placeholder Functions
# ========================
def simple_lstm_prediction(prices, days):
    # Dummy LSTM: predict next price as last price + small random walk
    import random
    return float(prices[-1]) * (1 + 0.01 * random.uniform(-1, 1))

def simple_arima_prediction(prices, days):
    # Dummy ARIMA: predict next price as mean of last 7 days
    return float(sum(prices[-7:]) / 7)

def simple_gb_prediction(prices, days):
    # Dummy Gradient Boosting: predict next price as last price + 0.5%
    return float(prices[-1]) * 1.005

def simple_rf_prediction(prices, days):
    # Dummy Random Forest: predict next price as last price - 0.5%
    return float(prices[-1]) * 0.995

def simple_average_prediction(prices, days):
    # Dummy Average: predict next price as average of all prices
    return float(sum(prices) / len(prices))

def advanced_ensemble_prediction(prices, days):
    # Dummy ensemble: average of all above models for each day
    preds = []
    for i in range(days):
        vals = [
            simple_lstm_prediction(prices, i+1),
            simple_arima_prediction(prices, i+1),
            simple_gb_prediction(prices, i+1),
            simple_rf_prediction(prices, i+1),
            simple_average_prediction(prices, i+1)
        ]
        preds.append(sum(vals) / len(vals))
    return preds


# Flask app initialization and global variables
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key in production

# In-memory user database (replace with persistent DB in production)
USERS_DB = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'role': 'admin',
        'created_at': datetime.now().isoformat()
    }
}
SUSPICIOUS_ACTIVITIES = []
LOGIN_LOGS = []
PREDICTIONS_LIST = []

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = USERS_DB.get(username)
        # Validate credentials
        if not user or not check_password_hash(user['password'], password):
            LOGIN_LOGS.append({
                'username': username or 'unknown',
                'status': 'failed',
                'ip': request.remote_addr,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user_agent': request.headers.get('User-Agent', '')
            })
            return render_template(
                'auth/login.html',
                error='Invalid username or password',
                login_username=username,
                login_password=''
            )

        # Successful login
        session['username'] = username
        session['role'] = user['role']

        LOGIN_LOGS.append({
            'username': username,
            'status': 'success',
            'ip': request.remote_addr,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user_agent': request.headers.get('User-Agent', '')
        })

        # Clear any pre-filled credentials from signup
        session.pop('login_password', None)

        # Redirect based on role
        if user['role'] == 'admin':
            return redirect(url_for('admin_home'))
        return redirect(url_for('user_home'))

    # GET: show login page, possibly pre-filled from signup
    login_username = session.pop('login_username', '')
    login_password = session.pop('login_password', '')
    return render_template(
        'auth/login.html',
        login_username=login_username,
        login_password=login_password
    )

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # Validation
        if not username or not password or not confirm_password:
            return render_template('auth/signup.html', error='All fields are required')
        if len(username) < 3:
            return render_template('auth/signup.html', error='Username must be at least 3 characters')
        if len(password) < 6:
            return render_template('auth/signup.html', error='Password must be at least 6 characters')
        if password != confirm_password:
            return render_template('auth/signup.html', error='Passwords do not match')
        if username in USERS_DB:
            return render_template('auth/signup.html', error='Username already exists')
        # Create new user
        USERS_DB[username] = {
            'password': generate_password_hash(password),
            'role': 'user',
            'created_at': datetime.now().isoformat()
        }
        # Store credentials in session for pre-filling login
        session['login_username'] = username
        session['login_password'] = password
        return redirect(url_for('login'))
    return render_template('auth/signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'user':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ========================
# Admin Routes
# ========================

@app.route('/admin')
@admin_required
def admin_home():
    active_users_this_month = len(USERS_DB) - 1  # Exclude admin
    total_predictions = len(PREDICTIONS_LIST)
    
    return render_template('admin/home.html', 
                         username=session['username'],
                         active_users=active_users_this_month,
                         total_predictions=total_predictions,
                         ml_models_count=5)

@app.route('/admin/security')
@admin_required
def admin_security():
    return render_template('admin/security.html', 
                          login_logs=LOGIN_LOGS[-50:],
                          suspicious_activities=SUSPICIOUS_ACTIVITIES[-30:])

@app.route('/admin/delete-user', methods=['POST'])
@admin_required
def admin_delete_user():
    username = request.form.get('username')
    if username and username in USERS_DB and username != 'admin':
        del USERS_DB[username]
        # Optionally, remove login logs for deleted user
        global LOGIN_LOGS
        LOGIN_LOGS = [log for log in LOGIN_LOGS if log['username'] != username]
    return redirect(url_for('admin_security'))

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    return render_template('admin/analytics.html', username=session['username'])

@app.route('/admin/realtime-price')
@admin_required
def admin_realtime_price():
    return render_template('admin/realtime_price.html', username=session['username'])

# ========================
# User Routes
# ========================

@app.route('/')
@app.route('/user')
@user_required
def user_home():
    return render_template('user/home.html', username=session['username'])

@app.route('/user/about')
@user_required
def user_about():
    return render_template('user/about.html', username=session['username'])

@app.route('/user/predict')
@user_required
def user_predict():
    return render_template('user/predict.html', username=session['username'])

@app.route('/user/ai-predict')
@user_required
def user_ai_predict():
    return render_template('user/ai_predict.html', username=session['username'])

@app.route('/user/contact')
@user_required
def user_contact():
    return render_template('user/content.html', username=session['username'])

@app.route('/user/news')
@user_required
def user_news():
    """Display Bitcoin news page"""
    return render_template('user/news.html')

# ========================
# API Routes - Real-Time Price
# ========================

@app.route('/api/btc-price')
def get_btc_price():
    """
    Fetch real-time Bitcoin price from CoinGecko and yFinance.
    Returns a combined payload used by the admin realtime dashboard.
    """
    result = {
        'coingecko_available': False,
        'yfinance_available': False
    }

    # CoinGecko current price
    try:
        cg_response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin', 'vs_currencies': 'usd', 'include_last_updated_at': 'true'},
            timeout=5
        )
        cg_response.raise_for_status()
        cg_data = cg_response.json().get('bitcoin', {})
        if 'usd' in cg_data:
            result['coingecko_available'] = True
            result['coingecko_price'] = float(cg_data['usd'])
            ts = cg_data.get('last_updated_at')
            if ts:
                result['coingecko_timestamp'] = datetime.fromtimestamp(ts).isoformat()
            else:
                result['coingecko_timestamp'] = datetime.utcnow().isoformat()
    except Exception as e:
        print(f"[v0] CoinGecko price error: {str(e)}")

    # yFinance current price
    try:
        ticker = yf.Ticker('BTC-USD')
        hist = ticker.history(period='1d', interval='1m')
        if not hist.empty:
            last_row = hist.iloc[-1]
            result['yfinance_available'] = True
            result['yfinance_price'] = float(last_row['Close'])
            # index is a Timestamp
            result['yfinance_timestamp'] = last_row.name.to_pydatetime().isoformat()
    except Exception as e:
        print(f"[v0] yFinance price error: {str(e)}")

    return jsonify(result)


@app.route('/api/btc-historical/<int:days>')
def get_btc_historical(days):
    """
    Fetch historical Bitcoin price data from CoinGecko and yFinance.
    Returns:
        {
          "coingecko": [["YYYY-MM-DD", price], ...],
          "yfinance": [["YYYY-MM-DD", price], ...]
        }
    """
    data = {'coingecko': [], 'yfinance': []}

    # Clamp days to a reasonable range
    days = max(1, min(days, 365))

    # CoinGecko historical
    try:
        cg_response = requests.get(
            'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart',
            params={'vs_currency': 'usd', 'days': str(days)},
            timeout=5
        )
        cg_response.raise_for_status()
        cg_json = cg_response.json()
        for ts, price in cg_json.get('prices', []):
            date = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d')
            data['coingecko'].append([date, float(price)])
    except Exception as e:
        print(f"[v0] CoinGecko historical error: {str(e)}")

    # yFinance historical
    try:
        ticker = yf.Ticker('BTC-USD')
        hist = ticker.history(period=f'{days}d')
        for idx, row in hist.iterrows():
            date = idx.strftime('%Y-%m-%d')
            data['yfinance'].append([date, float(row['Close'])])
    except Exception as e:
        print(f"[v0] yFinance historical error: {str(e)}")

    return jsonify(data)

# ========================
# API Routes - ML Predictions
# ========================

@app.route('/api/predict', methods=['POST'])
@user_required
def predict_price():
    """Generate Bitcoin price prediction using ML models"""
    try:
        # Handle form-data (file upload)
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            days = int(request.form.get('days', 30))
            model = request.form.get('model', 'lstm')
            file = request.files.get('dataFile')
            prices = None
            if file:
                import csv
                import io
                stream = io.StringIO(file.stream.read().decode('utf-8'))
                reader = csv.reader(stream)
                prices = []
                for row in reader:
                    try:
                        prices.append(float(row[0]))
                    except Exception:
                        continue
                prices = np.array(prices)
        else:
            data = request.json
            days = int(data.get('days', 30))
            model = data.get('model', 'lstm')
            prices = None

        # If no file uploaded, use CoinGecko or yfinance data
        if prices is None or len(prices) < 2:
            try:
                response = requests.get(
                    'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart',
                    params={'vs_currency': 'usd', 'days': '365'},
                    timeout=5
                )
                response.raise_for_status()
                historical_data = response.json()
                prices = [price for ts, price in historical_data['prices']]
                prices = np.array(prices)
            except Exception:
                btc = yf.Ticker('BTC-USD')
                hist = btc.history(period='365d')
                prices = [float(row['Close']) for idx, row in hist.iterrows()]
                prices = np.array(prices)

        # Map model names to functions (updated to return time series)
        def model_predict_series(model_func, prices, days):
            # Predict next N days as a time series
            preds = []
            for i in range(1, days+1):
                preds.append(model_func(prices, i))
            return preds

        model_funcs = {
            'lstm': simple_lstm_prediction,
            'arima': simple_arima_prediction,
            'gradient_boosting': simple_gb_prediction,
            'random_forest': simple_rf_prediction,
            'average': simple_average_prediction
        }

        if model not in model_funcs:
            return jsonify({'error': 'Invalid model selected'}), 400

        predicted_prices = model_predict_series(model_funcs[model], prices, days)
        current_price = float(prices[-1])
        
        global PREDICTIONS_LIST
        PREDICTIONS_LIST.append({
            'username': session.get('username'),
            'model': model,
            'days': days,
            'current_price': current_price,
            'predicted_price': predicted_prices[-1],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        return jsonify({
            'model': model,
            'predicted_prices': predicted_prices,
            'current_price': current_price
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-predict', methods=['POST'])
@user_required
def ai_predict():
    """Advanced AI prediction (placeholder for actual AI integration)"""
    try:
        data = request.json
        days = int(data.get('days', 30))
        
        response = requests.get(
            'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart',
            params={'vs_currency': 'usd', 'days': '365'},
            timeout=5
        )
        response.raise_for_status()
        historical_data = response.json()
        
        prices = np.array([price for ts, price in historical_data['prices']])
        
        # AI ensemble prediction
        predictions = {
            'ai_ensemble': advanced_ensemble_prediction(prices, days),
            'current_price': float(prices[-1]),
            'confidence': 0.82
        }
        
        # Track predictions
        global PREDICTIONS_LIST
        PREDICTIONS_LIST.append({
            'username': session['username'],
            'model': 'ai_ensemble',
            'predicted_prices': predictions['ai_ensemble'],
            'current_price': predictions['current_price'],
            'timestamp': datetime.now().isoformat()
        })

        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-pdf', methods=['POST'])
@user_required
def download_pdf():
    """Generate and download prediction PDF"""
    try:
        data = request.json
        prediction_data = data.get('predictions', {})
        
        # Create PDF
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#F7931A'),
            spaceAfter=30
        )
        story.append(Paragraph('Bitcoin Price Prediction Report', title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Metadata
        story.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', styles['Normal']))
        story.append(Paragraph(f'User: {session["username"]}', styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Predictions table
        story.append(Paragraph('Price Predictions (30 days)', styles['Heading2']))

        table_data = [['Model', 'Predicted Price (USD)', 'Change %']]
        current_price = prediction_data.get('current_price', 0)

        for model in ['lstm', 'arima', 'gradient_boosting', 'random_forest', 'average']:
            if model in prediction_data:
                pred_price = prediction_data[model]
                change = ((pred_price - current_price) / current_price * 100) if current_price > 0 else 0
                table_data.append([
                    model.upper(),
                    f'${pred_price:,.2f}',
                    f'{change:+.2f}%'
                ])

        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F7931A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3*inch))

        # Add prediction graph
        try:
            import matplotlib.pyplot as plt
            import io as _io
            plt.figure(figsize=(6, 3))
            # Plot actual prices (last 30 days)
            if 'actual_prices' in prediction_data:
                actual_prices = prediction_data['actual_prices']
            else:
                actual_prices = [current_price] * 30
            plt.plot(range(1, len(actual_prices)+1), actual_prices, label='Actual (last 30 days)', color='gray')
            # Plot predictions for each model
            for model in ['lstm', 'arima', 'gradient_boosting', 'random_forest', 'average']:
                if model in prediction_data:
                    plt.plot([30], [prediction_data[model]], 'o', label=f'{model.upper()} Prediction')
            plt.xlabel('Day')
            plt.ylabel('Price (USD)')
            plt.title('Bitcoin Price Prediction')
            plt.legend()
            plt.tight_layout()
            img_buf = _io.BytesIO()
            plt.savefig(img_buf, format='PNG')
            plt.close()
            img_buf.seek(0)
            from reportlab.platypus import Image
            story.append(Image(img_buf, width=5*inch, height=2.5*inch))
            story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            story.append(Paragraph('Graph could not be generated.', styles['Normal']))

        # Add tips and extra content
        story.append(Paragraph('Investment Tips', styles['Heading2']))
        tips = [
            '1. Diversify your investments to reduce risk.',
            '2. Never invest more than you can afford to lose.',
            '3. Stay updated with market news and trends.',
            '4. Use stop-loss orders to manage downside risk.',
            '5. Avoid emotional trading decisions.'
        ]
        for tip in tips:
            story.append(Paragraph(tip, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        story.append(Paragraph('About This Report', styles['Heading2']))
        story.append(Paragraph(
            'This report provides a summary of Bitcoin price predictions using various machine learning models. '
            'The predictions are based on historical price data and are intended to offer insights into potential future trends. '
            'Please note that these predictions are not financial advice and should be used as one of many tools in your investment decision-making process.',
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))

        # Disclaimer
        story.append(Paragraph('Disclaimer', styles['Heading2']))
        story.append(Paragraph(
            'These predictions are for informational purposes only. Bitcoin price is highly volatile and subject to market forces. '
            'Past performance does not guarantee future results. Always conduct your own research before making investment decisions.',
            styles['Normal']
        ))

        doc.build(story)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'btc_prediction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================
# Bitcoin News Endpoint
# ========================

# User real-time price page
@app.route('/user/realtime-price')
def user_realtime_price():
    return render_template('user/realtime_price.html')


# ========================

@app.route('/api/bitcoin-news')
def get_bitcoin_news():
    news_items = []

    # Fetch from NewsAPI (free tier)
    try:
        NEWSAPI_KEY = 'demo'  # Replace 'demo' with your free NewsAPI key
        response = requests.get(
            'https://newsapi.org/v2/everything',
            params={
                'q': 'bitcoin',
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': NEWSAPI_KEY,
                'pageSize': 10
            },
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        for article in data.get('articles', []):
            news_items.append({
                'title': article.get('title', 'No title'),
                'summary': article.get('description', '')[:200],
                'link': article.get('url', '#'),
                'published': article.get('publishedAt', ''),
                'source': 'NewsAPI',
                'image': article.get('urlToImage', '')
            })
    except Exception as e:
        print(f"[v0] NewsAPI error: {str(e)}")

    # Fetch from CoinTelegraph RSS
    try:
        feed = feedparser.parse('https://cointelegraph.com/feed/tag/bitcoin')
        for entry in feed.entries[:10]:
            news_items.append({
                'title': entry.get('title', 'No title'),
                'summary': entry.get('summary', '')[:200],
                'link': entry.get('link', '#'),
                'published': entry.get('published', ''),
                'source': 'CoinTelegraph',
                'image': entry.get('media_content', [{'url': '/placeholder.svg?height=200&width=400'}])[0].get('url', '') if entry.get('media_content') else ''
            })
    except Exception as e:
        print(f"[v0] CoinTelegraph feed error: {str(e)}")

    # Fetch from CryptoPanic API (free tier)
    try:
        response = requests.get(
            'https://cryptopanic.com/api/v1/posts/',
            params={'auth_token': 'free', 'kind': 'news', 'currency': 'bitcoin', 'limit': 5},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        for item in data.get('results', []):
            news_items.append({
                'title': item.get('title', 'No title'),
                'summary': item.get('body', '')[:200],
                'link': item.get('url', '#'),
                'published': item.get('published_at', ''),
                'source': 'CryptoPanic',
                'image': item.get('image', '')
            })
    except Exception as e:
        print(f"[v0] CryptoPanic API error: {str(e)}")

    # Sort by published date (newest first) and limit to 15
    news_items = sorted(news_items, key=lambda x: x.get('published', ''), reverse=True)[:15]
    return jsonify({'news': news_items})
    
    # Add market volatility adjustment
    volatility = np.std(np.diff(prices[-30:]) / prices[-30:-1] * 100) if len(prices) >= 30 else 2
    
    # Confidence-adjusted prediction
    adjustment = 1 + (volatility / 100) * 0.1
    return float(base_predictions * adjustment)

# ========================
# Error Handlers
# ========================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
