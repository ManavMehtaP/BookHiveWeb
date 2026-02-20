import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime, timedelta
import os
from config import Config
import pymysql
from collections import defaultdict
import calendar
from decimal import Decimal

# Set matplotlib style for better appearance
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def get_db_connection():
    """Get database connection"""
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

def get_booking_analytics():
    """Fetch booking data from database"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Get bookings with event details
            cursor.execute("""
                SELECT b.*, e.title, e.genre, e.price, e.event_date
                FROM bookings b
                JOIN events e ON b.event_id = e.id
                WHERE b.booking_status = 'active'
                ORDER BY b.booking_date DESC
            """)
            bookings = cursor.fetchall()
            
            # Convert Decimal to float for easier processing
            for booking in bookings:
                if 'total_price' in booking and isinstance(booking['total_price'], Decimal):
                    booking['total_price'] = float(booking['total_price'])
                if 'price' in booking and isinstance(booking['price'], Decimal):
                    booking['price'] = float(booking['price'])
            
            return bookings
    finally:
        connection.close()

def get_sales_by_genre():
    """Calculate total ticket sales by genre"""
    bookings = get_booking_analytics()
    genre_sales = defaultdict(lambda: {'tickets': 0, 'revenue': 0})
    
    for booking in bookings:
        genre = booking['genre'] or 'Other'
        genre_sales[genre]['tickets'] += booking['seats_booked']
        genre_sales[genre]['revenue'] += booking['total_price']
    
    return genre_sales

def get_sales_trends(period='daily'):
    """Get sales trends over time"""
    bookings = get_booking_analytics()
    sales_data = defaultdict(lambda: {'tickets': 0, 'revenue': 0})
    
    for booking in bookings:
        if period == 'daily':
            date_key = booking['booking_date'].strftime('%Y-%m-%d')
        else:  # monthly
            date_key = booking['booking_date'].strftime('%Y-%m')
        
        sales_data[date_key]['tickets'] += booking['seats_booked']
        sales_data[date_key]['revenue'] += booking['total_price']
    
    return dict(sorted(sales_data.items()))

def get_top_events():
    """Get top-selling events by revenue"""
    bookings = get_booking_analytics()
    event_sales = defaultdict(lambda: {'tickets': 0, 'revenue': 0, 'title': ''})
    
    for booking in bookings:
        event_id = booking['event_id']
        event_sales[event_id]['tickets'] += booking['seats_booked']
        event_sales[event_id]['revenue'] += booking['total_price']
        event_sales[event_id]['title'] = booking['title']
    
    # Sort by revenue and return top 10
    sorted_events = sorted(event_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)
    return dict(sorted_events[:10])

def create_genre_sales_chart():
    """Create bar chart showing total ticket sales by genre"""
    genre_data = get_sales_by_genre()
    
    if not genre_data:
        return None
    
    genres = list(genre_data.keys())
    tickets = [genre_data[genre]['tickets'] for genre in genres]
    revenue = [genre_data[genre]['revenue'] for genre in genres]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle('Sales Performance by Event Genre', fontsize=16, fontweight='bold', color='white')
    
    # Set dark background
    fig.patch.set_facecolor('#1a1a2e')
    ax1.set_facecolor('#16213e')
    ax2.set_facecolor('#16213e')
    
    # Ticket sales bar chart
    bars1 = ax1.bar(genres, tickets, color='#ff5e1a', alpha=0.8)
    ax1.set_title('Total Tickets Sold by Genre', fontsize=14, color='white')
    ax1.set_ylabel('Number of Tickets', fontsize=12, color='white')
    ax1.tick_params(axis='x', colors='white', rotation=45)
    ax1.tick_params(axis='y', colors='white')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', color='white', fontweight='bold')
    
    # Revenue bar chart
    bars2 = ax2.bar(genres, revenue, color='#4a90e2', alpha=0.8)
    ax2.set_title('Total Revenue by Genre', fontsize=14, color='white')
    ax2.set_ylabel('Revenue ($)', fontsize=12, color='white')
    ax2.tick_params(axis='x', colors='white', rotation=45)
    ax2.tick_params(axis='y', colors='white')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:,.0f}', ha='center', va='bottom', color='white', fontweight='bold')
    
    plt.tight_layout()
    
    # Save chart
    chart_path = os.path.join('static', 'charts', 'genre_sales.png')
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, facecolor='#1a1a2e', dpi=300, bbox_inches='tight')
    plt.close()
    
    return chart_path

def create_sales_trend_chart(period='daily'):
    """Create line chart showing sales trends over time"""
    trend_data = get_sales_trends(period)
    
    if not trend_data:
        return None
    
    dates = list(trend_data.keys())
    tickets = [trend_data[date]['tickets'] for date in dates]
    revenue = [trend_data[date]['revenue'] for date in dates]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle(f'Sales Trends ({period.title()})', fontsize=16, fontweight='bold', color='white')
    
    # Set dark background
    fig.patch.set_facecolor('#1a1a2e')
    ax1.set_facecolor('#16213e')
    ax2.set_facecolor('#16213e')
    
    # Convert dates for plotting
    if period == 'daily':
        date_objs = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
        date_format = mdates.DateFormatter('%b %d')
    else:
        date_objs = [datetime.strptime(date, '%Y-%m') for date in dates]
        date_format = mdates.DateFormatter('%b %Y')
    
    # Ticket sales trend
    ax1.plot(date_objs, tickets, marker='o', color='#ff5e1a', linewidth=3, markersize=6)
    ax1.set_title('Ticket Sales Trend', fontsize=14, color='white')
    ax1.set_ylabel('Number of Tickets', fontsize=12, color='white')
    ax1.tick_params(axis='x', colors='white', rotation=45)
    ax1.tick_params(axis='y', colors='white')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(date_format)
    
    # Revenue trend
    ax2.plot(date_objs, revenue, marker='s', color='#4a90e2', linewidth=3, markersize=6)
    ax2.set_title('Revenue Trend', fontsize=14, color='white')
    ax2.set_ylabel('Revenue ($)', fontsize=12, color='white')
    ax2.tick_params(axis='x', colors='white', rotation=45)
    ax2.tick_params(axis='y', colors='white')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(date_format)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = os.path.join('static', 'charts', f'sales_trend_{period}.png')
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, facecolor='#1a1a2e', dpi=300, bbox_inches='tight')
    plt.close()
    
    return chart_path

def create_genre_distribution_pie():
    """Create pie chart showing booking distribution by genre"""
    genre_data = get_sales_by_genre()
    
    if not genre_data:
        return None
    
    genres = list(genre_data.keys())
    tickets = [genre_data[genre]['tickets'] for genre in genres]
    
    # Create custom colors
    colors = ['#ff5e1a', '#4a90e2', '#50c878', '#ffd700', '#9b59b6', '#e74c3c', '#3498db', '#2ecc71']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(tickets, labels=genres, autopct='%1.1f%%', 
                                      colors=colors[:len(genres)], startangle=90,
                                      textprops={'color': 'white', 'fontsize': 10})
    
    # Customize text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Booking Distribution by Genre', fontsize=16, fontweight='bold', color='white', pad=20)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = os.path.join('static', 'charts', 'genre_distribution.png')
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, facecolor='#1a1a2e', dpi=300, bbox_inches='tight')
    plt.close()
    
    return chart_path

def create_top_events_chart():
    """Create horizontal bar chart showing top-selling events"""
    top_events = get_top_events()
    
    if not top_events:
        return None
    
    events = []
    revenues = []
    
    for event_id, data in top_events.items():
        events.append(data['title'][:30] + '...' if len(data['title']) > 30 else data['title'])
        revenues.append(data['revenue'])
    
    # Reverse order for better visualization
    events = events[::-1]
    revenues = revenues[::-1]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    
    # Create horizontal bar chart
    bars = ax.barh(events, revenues, color='#50c878', alpha=0.8)
    
    ax.set_title('Top 10 Events by Revenue', fontsize=16, fontweight='bold', color='white')
    ax.set_xlabel('Revenue ($)', fontsize=12, color='white')
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', colors='white')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + max(revenues) * 0.01, bar.get_y() + bar.get_height()/2.,
                f'${width:,.0f}', ha='left', va='center', color='white', fontweight='bold')
    
    plt.tight_layout()
    
    # Save chart
    chart_path = os.path.join('static', 'charts', 'top_events.png')
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, facecolor='#1a1a2e', dpi=300, bbox_inches='tight')
    plt.close()
    
    return chart_path

def generate_all_charts():
    """Generate all charts and return their paths"""
    charts = {}
    
    try:
        charts['genre_sales'] = create_genre_sales_chart()
        charts['sales_trend_daily'] = create_sales_trend_chart('daily')
        charts['sales_trend_monthly'] = create_sales_trend_chart('monthly')
        charts['genre_distribution'] = create_genre_distribution_pie()
        charts['top_events'] = create_top_events_chart()
    except Exception as e:
        print(f"Error generating charts: {e}")
        return {}
    
    return charts

if __name__ == "__main__":
    # Test chart generation
    print("Generating charts...")
    charts = generate_all_charts()
    print(f"Charts generated: {list(charts.keys())}")
