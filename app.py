from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import pymysql
from functools import wraps
from config import Config
from datetime import datetime
import re
from data_analyzer import DataAnalyzer, ReportGenerator, filter_events_by_criteria, sort_events, calculate_booking_statistics
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your-secret-key-change-this'
@app.context_processor
def inject_now():
    return {'now': datetime.now}
def track_login(user_id, success=True, ip_address=None, user_agent=None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_login_history 
                (user_id, login_status, ip_address, user_agent)
                VALUES (%s, %s, %s, %s)
            """, (user_id, 'success' if success else 'failed', ip_address, user_agent))
            connection.commit()
    finally:
        connection.close()
EVENT_CATEGORIES = {
    'Music': {'icon': 'fa-music', 'color': '#ff5e1a'},
    'Sports': {'icon': 'fa-futbol', 'color': '#ef4444'},
    'Food & Drink': {'icon': 'fa-utensils', 'color': '#10b981'},
    'Art': {'icon': 'fa-palette', 'color': '#a855f7'},
    'Festivals': {'icon': 'fa-calendar-star', 'color': '#f59e0b'},
    'Comedy': {'icon': 'fa-laugh', 'color': '#f59e0b'},
    'Business': {'icon': 'fa-briefcase', 'color': '#6366f1'}
}
USER_ROLES = {
    'admin': {
        'permissions': ['create_event', 'edit_event', 'delete_event', 'view_dashboard', 'manage_users'],
        'level': 3
    },
    'user': {
        'permissions': ['view_events', 'book_event', 'edit_profile'],
        'level': 1
    }
}
EVENT_STATUS = {
    'active': 'Active',
    'cancelled': 'Cancelled', 
    'postponed': 'Postponed'
}
BOOKING_STATUS = {
    'active': 'Active',
    'cancelled': 'Cancelled'
}
def get_db_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT role FROM users WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if not user or user['role'] != 'admin':
                    flash('Admin access required!', 'error')
                    return redirect(url_for('home'))
        finally:
            connection.close()
        return f(*args, **kwargs)
    return decorated_function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
def get_categories_from_db():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT genre, COUNT(*) as count 
                FROM events 
                WHERE status = 'active' 
                GROUP BY genre 
                ORDER BY count DESC
            """)
            raw_categories = cursor.fetchall()
            categories = []
            for category in raw_categories:
                genre_name = category['genre']
                category_info = EVENT_CATEGORIES.get(genre_name, {
                    'icon': 'fa-calendar',
                    'color': '#6b7280'
                })
                enhanced_category = {
                    'genre': genre_name,
                    'count': category['count'],
                    'icon': category_info['icon'],
                    'color': category_info['color'],
                    'display_name': genre_name.title(),
                    'slug': genre_name.lower().replace(' & ', '-').replace(' ', '-')
                }
                categories.append(enhanced_category)
            return categories
    finally:
        connection.close()
def get_events_from_db():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.*, u.username as created_by_username, u.full_name as created_by_name
                FROM events e
                LEFT JOIN users u ON e.created_by = u.id
                WHERE e.status = 'active' AND e.event_date >= CURDATE()
                ORDER BY e.event_date ASC
            """)
            events = cursor.fetchall()
            formatted_events = []
            for event in events:
                category_info = EVENT_CATEGORIES.get(event['genre'], {
                    'icon': 'fa-calendar',
                    'color': '#6b7280'
                })
                formatted_event = {
                    'id': event['id'],
                    'title': event['title'],
                    'genre': event['genre'],
                    'location': event['location'],
                    'venue': event.get('venue', ''),
                    'date': str(event['event_date']),
                    'time': format_time(event['event_time']),
                    'end_time': format_time(event['event_end_time']) if event.get('event_end_time') else None,
                    'price': {
                        'amount': float(event['price']),
                        'formatted': f"${float(event['price']):.2f}",
                        'currency': 'USD'
                    },
                    'image_url': event.get('image_url', ''),
                    'description': event.get('description', ''),
                    'created_by': event.get('created_by'),
                    'created_by_username': event.get('created_by_username', ''),
                    'created_by_name': event.get('created_by_name', ''),
                    'seating': {
                        'total': event.get('total_seats', 100),
                        'available': event.get('available_seats', event.get('total_seats', 100)),
                        'occupied': (event.get('total_seats', 100) - event.get('available_seats', event.get('total_seats', 100)))
                    },
                    'category_info': category_info,
                    'status': {
                        'key': event.get('status', 'active'),
                        'display': EVENT_STATUS.get(event.get('status', 'active'), 'Active')
                    },
                    'featured': bool(event.get('featured', False)),
                    'is_upcoming': is_event_upcoming(event['event_date']),
                    'days_until': days_until_event(event['event_date'])
                }
                formatted_events.append(formatted_event)
            return formatted_events
    finally:
        connection.close()
def format_time(time_obj):
    if not time_obj:
        return ''
    if hasattr(time_obj, 'strftime'):
        return time_obj.strftime('%H:%M')
    elif isinstance(time_obj, str):
        return time_obj[:5] if len(time_obj) > 5 else time_obj
    else:
        return str(time_obj)
def is_event_upcoming(event_date):
    if not event_date:
        return False
    return event_date >= datetime.now().date()
def days_until_event(event_date):
    if not event_date:
        return None
    today = datetime.now().date()
    if event_date >= today:
        return (event_date - today).days
    return None
def validate_user_data(user_data):
    errors = []
    username_rules = {
        'pattern': r'^[a-zA-Z0-9_]{3,20}$',
        'min_length': 3,
        'max_length': 20,
        'field_name': 'Username'
    }
    username = user_data.get('username', '').strip()
    if not username:
        errors.append(f"{username_rules['field_name']} is required")
    elif not re.match(username_rules['pattern'], username):
        errors.append(f"{username_rules['field_name']} must be 3-20 characters with letters, numbers, and underscores only")
    elif len(username) < username_rules['min_length'] or len(username) > username_rules['max_length']:
        errors.append(f"{username_rules['field_name']} must be between {username_rules['min_length']} and {username_rules['max_length']} characters")
    email_patterns = {
        'basic': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'field_name': 'Email'
    }
    email = user_data.get('email', '').strip()
    if not email:
        errors.append(f"{email_patterns['field_name']} is required")
    elif not re.match(email_patterns['basic'], email):
        errors.append(f"{email_patterns['field_name']} format is invalid")
    phone_rules = {
        'pattern': r'^[6-9]\d{9}$',
        'length': 10,
        'field_name': 'Phone'
    }
    phone = user_data.get('phone', '').strip()
    if not phone:
        errors.append(f"{phone_rules['field_name']} number is required")
    elif not re.match(phone_rules['pattern'], phone):
        errors.append(f"{phone_rules['field_name']} must be a valid 10-digit number starting with 6-9")
    elif len(phone) != phone_rules['length']:
        errors.append(f"{phone_rules['field_name']} must be exactly {phone_rules['length']} digits")
    password_requirements = {
        'min_length': 6,
        'field_name': 'Password'
    }
    password = user_data.get('password', '')
    confirm_password = user_data.get('confirm_password', '')
    if not password:
        errors.append(f"{password_requirements['field_name']} is required")
    elif len(password) < password_requirements['min_length']:
        errors.append(f"{password_requirements['field_name']} must be at least {password_requirements['min_length']} characters")
    if password != confirm_password:
        errors.append("Passwords do not match")
    fullname = user_data.get('fullname', '').strip()
    if not fullname:
        errors.append("Full name is required")
    elif len(fullname) < 2:
        errors.append("Full name must be at least 2 characters")
    if not user_data.get('terms'):
        errors.append("You must agree to the terms and conditions")
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'field_data': {
            'username': username,
            'email': email,
            'phone': phone,
            'fullname': fullname,
            'password_strength': check_password_strength(password)
        }
    }
def check_password_strength(password):
    if not password:
        return {'score': 0, 'label': 'Very Weak'}
    score = 0
    checks = {
        'length': len(password) >= 8,
        'uppercase': any(c.isupper() for c in password),
        'lowercase': any(c.islower() for c in password),
        'numbers': any(c.isdigit() for c in password),
        'special': any(c in '!@#$%^&*()_+-=' for c in password)
    }
    score = sum(checks.values())
    strength_levels = [
        (0, 2, 'Very Weak'),
        (3, 4, 'Weak'),
        (5, 6, 'Fair'),
        (7, 8, 'Good'),
        (9, 10, 'Strong')
    ]
    for min_score, max_score, label in strength_levels:
        if min_score <= score <= max_score:
            return {'score': score, 'label': label, 'checks': checks}
    return {'score': score, 'label': 'Very Strong', 'checks': checks}
def get_admin_events_from_db(admin_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, genre, location, venue, event_date, event_time, price, 
                       total_seats, available_seats, image_url, description, featured, status
                FROM events 
                WHERE created_by = %s AND status = 'active'
                ORDER BY event_date ASC
            """, (admin_id,))
            events = cursor.fetchall()
            formatted_events = []
            for event in events:
                formatted_events.append({
                    'id': event['id'],
                    'title': event['title'],
                    'genre': event['genre'],
                    'location': event['location'],
                    'venue': event.get('venue', ''),
                    'date': str(event['event_date']),
                    'time': str(event['event_time'])[:5] if event['event_time'] and hasattr(event['event_time'], 'strftime') else str(event['event_time'])[:5] if event['event_time'] else '',
                    'price': float(event['price']),
                    'image_url': event.get('image_url', ''),
                    'description': event.get('description', ''),
                    'total_seats': event.get('total_seats', 100),
                    'available_seats': event.get('available_seats', event.get('total_seats', 100)),
                    'featured': event.get('featured', False)
                })
            return formatted_events
    finally:
        connection.close()
@app.route('/')
def home():
    events = get_events_from_db()
    categories = get_categories_from_db()
    is_admin = False
    if session.get('user_id'):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT role FROM users WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                is_admin = user and user['role'] == 'admin'
        finally:
            connection.close()
    return render_template('index.html', events=events, categories=categories, is_admin=is_admin)
@app.route('/api/events')
def get_events():
    events = get_events_from_db()
    return jsonify(events)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user and user['password_user'] == password:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['user_email'] = user.get('email', '')
                    session['user_phone'] = user.get('phone', '')
                    session['role'] = user['role']
                    track_login(user['id'], success=True, 
                              ip_address=request.remote_addr,
                              user_agent=request.headers.get('User-Agent'))
                    flash(f'Welcome back, {user["full_name"]}!', 'success')
                    return redirect(url_for('home'))
                else:
                    if user:
                        track_login(user['id'], success=False,
                                  ip_address=request.remote_addr,
                                  user_agent=request.headers.get('User-Agent'))
                    flash('Invalid username or password!', 'error')
        finally:
            connection.close()
    return render_template('login.html')
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        user_data = {
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip(),
            'fullname': request.form.get('fullname', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', ''),
            'terms': request.form.get('terms', '')
        }
        validation_result = validate_user_data(user_data)
        if not validation_result['is_valid']:
            return jsonify({
                'success': False, 
                'message': 'Validation failed',
                'errors': validation_result['errors'],
                'field_data': validation_result['field_data']
            })
        connection = get_db_connection()
        try:
            print(f"Attempting to create user with: {validation_result['field_data']}")
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (user_data['username'],))
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Username already exists! Please choose another one.'})
                cursor.execute("SELECT id FROM users WHERE email = %s", (user_data['email'],))
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Email already registered! Please use another email.'})
                insert_query = """
                    INSERT INTO users (username, email, full_name, phone, password_user, role)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    user_data['username'],
                    user_data['email'],
                    user_data['fullname'],
                    user_data['phone'],
                    user_data['password'],
                    'user'
                ))
                print("Query executed, committing...")
                connection.commit()
                print("Commit successful")
                cursor.execute("SELECT id, username, email FROM users WHERE username = %s", (user_data['username'],))
                inserted_user = cursor.fetchone()
                print(f"Verified inserted user: {inserted_user}")
                return jsonify({
                    'success': True, 
                    'message': 'Account created successfully! You can now login.',
                    'user_data': {
                        'id': inserted_user['id'],
                        'username': inserted_user['username'],
                        'email': inserted_user['email']
                    }
                })
        except Exception as e:
            print(f"Database error during signup: {str(e)}")
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'})
        finally:
            connection.close()
    return jsonify({'success': False, 'message': 'Invalid request method.'})
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out!', 'info')
    return redirect(url_for('home'))
@app.route('/admin')
@admin_required
def admin_dashboard():
    admin_events = get_admin_events_from_db(session['user_id'])
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total_bookings FROM bookings WHERE booking_status = 'active'")
            total_bookings = cursor.fetchone()['total_bookings']
            cursor.execute("SELECT COALESCE(SUM(total_price), 0) as total_revenue FROM bookings WHERE booking_status = 'active'")
            total_revenue = cursor.fetchone()['total_revenue']
            cursor.execute("""
                SELECT COUNT(*) as admin_bookings, 
                       COALESCE(SUM(b.total_price), 0) as admin_revenue
                FROM bookings b
                INNER JOIN events e ON b.event_id = e.id
                WHERE b.booking_status = 'active' AND e.created_by = %s
            """, (session['user_id'],))
            admin_stats = cursor.fetchone()
            dashboard_stats = {
                'total_bookings': total_bookings,
                'total_revenue': total_revenue,
                'admin_bookings': admin_stats['admin_bookings'],
                'admin_revenue': admin_stats['admin_revenue']
            }
    finally:
        connection.close()
    return render_template('admin/dashboard.html', events=admin_events, stats=dashboard_stats)
@app.route('/admin/manage-events')
@admin_required
def manage_events():
    admin_events = get_admin_events_from_db(session['user_id'])
    return render_template('admin/manage_events.html', events=admin_events)
@app.route('/admin/edit-event/<int:event_id>', methods=['GET', 'POST'])
@admin_required
def edit_event(event_id):
    connection = get_db_connection()
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SELECT created_by FROM events WHERE id = %s", (event_id,))
            event = cursor.fetchone()
            if not event or event['created_by'] != session['user_id']:
                flash('You can only edit events you created!', 'error')
                return redirect(url_for('manage_events'))
        title = request.form['title']
        genre = request.form['genre']
        location = request.form['location']
        venue = request.form.get('venue', '')
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        event_end_time = request.form['event_end_time']
        price = float(request.form['price'])
        total_seats = int(request.form.get('total_seats', 100))
        available_seats = int(request.form.get('available_seats', total_seats))
        image_url = request.form.get('image_url', '')
        description = request.form['description']
        featured = 'featured' in request.form
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE events SET title = %s, genre = %s, location = %s, venue = %s, 
                                   event_date = %s, event_time = %s, event_end_time = %s, price = %s, 
                                   total_seats = %s, available_seats = %s, 
                                   image_url = %s, description = %s, featured = %s
                    WHERE id = %s AND created_by = %s
                """, (title, genre, location, venue, event_date, event_time, event_end_time, price, 
                      total_seats, available_seats, image_url, description, featured, 
                      event_id, session['user_id']))
            connection.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('manage_events'))
        finally:
            connection.close()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, genre, location, venue, event_date, event_time, event_end_time, price, 
                       total_seats, available_seats, image_url, description, featured, status
                FROM events 
                WHERE id = %s AND created_by = %s
            """, (event_id, session['user_id']))
            event = cursor.fetchone()
            if not event:
                flash('Event not found or you do not have permission to edit it!', 'error')
                return redirect(url_for('manage_events'))
            if event['event_time']:
                try:
                    event_time_str = str(event['event_time'])[:5]  # Get HH:MM format
                except (AttributeError, TypeError):
                    event_time_str = ''
            else:
                event_time_str = ''
            event['event_time_str'] = event_time_str
            if event['event_end_time']:
                try:
                    event_end_time_str = str(event['event_end_time'])[:5]  # Get HH:MM format
                except (AttributeError, TypeError):
                    event_end_time_str = ''
            else:
                event_end_time_str = ''
            event['event_end_time_str'] = event_end_time_str
            return render_template('admin/edit_event.html', event=event)
    finally:
        connection.close()
@app.route('/admin/delete-event/<int:event_id>', methods=['POST'])
@admin_required
def delete_event(event_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT created_by FROM events WHERE id = %s", (event_id,))
            event = cursor.fetchone()
            if not event:
                flash('Event not found!', 'error')
                return redirect(url_for('admin_dashboard'))
            if event['created_by'] != session['user_id']:
                flash('You can only delete events you created!', 'error')
                return redirect(url_for('admin_dashboard'))
            cursor.execute("UPDATE events SET status = 'cancelled' WHERE id = %s", (event_id,))
            connection.commit()
            flash('Event deleted successfully!', 'success')
    finally:
        connection.close()
    return redirect(url_for('admin_dashboard'))
@app.route('/admin/add-event', methods=['GET', 'POST'])
@admin_required
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        location = request.form['location']
        venue = request.form.get('venue', '')
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        event_end_time = request.form['event_end_time']
        price = float(request.form['price'])
        total_seats = int(request.form.get('total_seats', 100))
        available_seats = total_seats
        image_url = request.form.get('image_url', '')
        description = request.form['description']
        featured = 'featured' in request.form
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO events (title, genre, location, venue, event_date, event_time, event_end_time,
                                      price, total_seats, available_seats, image_url, description, 
                                      featured, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, genre, location, venue, event_date, event_time, event_end_time, price, total_seats, 
                      available_seats, image_url, description, featured, session['user_id']))
            connection.commit()
            flash('Event added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        finally:
            connection.close()
    return render_template('admin/add_event.html')
@app.route('/api/book-event', methods=['POST'])
@login_required
def book_event():
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        tickets = int(data.get('tickets', 1))
        notes = data.get('notes', '')
        if not all([event_id, tickets]):
            return jsonify({'success': False, 'message': 'Missing required fields'})
        if tickets <= 0:
            return jsonify({'success': False, 'message': 'Number of tickets must be greater than 0'})
        if tickets > 10:
            return jsonify({'success': False, 'message': 'Maximum 10 tickets can be booked per event'})
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT username, email, full_name, phone FROM users WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if not user:
                    return jsonify({'success': False, 'message': 'User not found'})
                cursor.execute("SELECT title, available_seats, total_seats, price FROM events WHERE id = %s AND status = 'active'", (event_id,))
                event = cursor.fetchone()
                if not event:
                    return jsonify({'success': False, 'message': 'Event not found or not active'})
                if event['available_seats'] < tickets:
                    return jsonify({'success': False, 'message': f'Only {event["available_seats"]} seats available'})
                
                # Check if user already has bookings for this event
                cursor.execute("""
                    SELECT COALESCE(SUM(seats_booked), 0) as total_booked 
                    FROM bookings 
                    WHERE event_id = %s AND user_id = %s AND booking_status = 'active'
                """, (event_id, session['user_id']))
                existing_booking = cursor.fetchone()
                total_booked = existing_booking['total_booked'] if existing_booking else 0
                
                if total_booked + tickets > 10:
                    remaining_allowed = 10 - total_booked
                    return jsonify({'success': False, 'message': f'You already have {total_booked} tickets booked for this event. You can book maximum {remaining_allowed} more tickets (limit: 10 per user).'})
                booking_ref = generate_booking_reference()
                new_available_seats = event['available_seats'] - tickets
                cursor.execute("UPDATE events SET available_seats = %s WHERE id = %s", 
                             (new_available_seats, event_id))
                cursor.execute("""
                    INSERT INTO bookings (event_id, user_id, booking_reference, customer_name, customer_email, 
                                        phone, seats_booked, total_price, booking_status, payment_status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (event_id, session['user_id'], booking_ref, user['full_name'], user['email'], 
                      user['phone'], tickets, tickets * event['price'], 'active', 'paid', notes))
                connection.commit()
                return jsonify({
                    'success': True, 
                    'message': f'Booking confirmed! {tickets} ticket(s) reserved for {event["title"]}',
                    'booking_reference': booking_ref,
                    'remaining_seats': new_available_seats,
                    'total_price': tickets * event['price']
                })
        finally:
            connection.close()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/api/guest-book-event', methods=['POST'])
def guest_book_event():
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        tickets = int(data.get('tickets', 1))
        notes = data.get('notes', '')
        if not all([event_id, name, email, phone, tickets]):
            return jsonify({'success': False, 'message': 'Missing required fields'})
        if tickets <= 0:
            return jsonify({'success': False, 'message': 'Number of tickets must be greater than 0'})
        if tickets > 10:
            return jsonify({'success': False, 'message': 'Maximum 10 tickets can be booked per event'})
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT title, available_seats, total_seats, price FROM events WHERE id = %s AND status = 'active'", (event_id,))
                event = cursor.fetchone()
                if not event:
                    return jsonify({'success': False, 'message': 'Event not found or not active'})
                if event['available_seats'] < tickets:
                    return jsonify({'success': False, 'message': f'Only {event["available_seats"]} seats available'})
                booking_ref = generate_booking_reference()
                new_available_seats = event['available_seats'] - tickets
                cursor.execute("UPDATE events SET available_seats = %s WHERE id = %s", 
                             (new_available_seats, event_id))
                cursor.execute("""
                    INSERT INTO bookings (event_id, booking_reference, customer_name, customer_email, 
                                        phone, seats_booked, total_price, booking_status, payment_status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (event_id, booking_ref, name, email, phone, tickets, tickets * event['price'], 
                      'active', 'paid', notes))
                connection.commit()
                return jsonify({
                    'success': True, 
                    'message': f'Booking confirmed! {tickets} ticket(s) reserved for {event["title"]}',
                    'booking_reference': booking_ref,
                    'remaining_seats': new_available_seats,
                    'total_price': tickets * event['price']
                })
        finally:
            connection.close()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
def generate_booking_reference():
    import random
    import string
    timestamp = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'BK{timestamp}{random_str}'
@app.route('/my-bookings')
@login_required
def my_bookings():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.*, e.title, e.genre, e.event_date, e.event_time, e.location, e.venue, e.image_url
                FROM bookings b
                LEFT JOIN events e ON b.event_id = e.id
                WHERE b.user_id = %s OR (b.user_id IS NULL AND b.customer_email = %s)
                ORDER BY b.booking_date DESC
            """, (session['user_id'], session.get('user_email', '')))
            bookings = cursor.fetchall()
            formatted_bookings = []
            for booking in bookings:
                formatted_bookings.append({
                    'id': booking['id'],
                    'booking_reference': booking.get('booking_reference', ''),
                    'event_title': booking['title'],
                    'event_genre': booking['genre'],
                    'event_date': str(booking['event_date']) if booking['event_date'] else '',
                    'event_time': str(booking['event_time'])[:5] if booking['event_time'] else '',
                    'location': booking['location'],
                    'venue': booking.get('venue', ''),
                    'image_url': booking.get('image_url', ''),
                    'seats_booked': booking['seats_booked'],
                    'total_price': float(booking['total_price']),
                    'booking_status': booking['booking_status'],
                    'payment_status': booking.get('payment_status', 'paid'),
                    'booking_date': str(booking['booking_date']),
                    'notes': booking.get('notes', ''),
                    'customer_name': booking['customer_name'],
                    'customer_email': booking['customer_email'],
                    'phone': booking['phone']
                })
            return render_template('user/bookings.html', bookings=formatted_bookings)
    finally:
        connection.close()
@app.route('/api/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.*, e.available_seats, e.title
                FROM bookings b
                LEFT JOIN events e ON b.event_id = e.id
                WHERE b.id = %s AND (b.user_id = %s OR (b.user_id IS NULL AND b.customer_email = %s))
            """, (booking_id, session['user_id'], session.get('user_email', '')))
            booking = cursor.fetchone()
            if not booking:
                return jsonify({'success': False, 'message': 'Booking not found or access denied'})
            if booking['booking_status'] == 'cancelled':
                return jsonify({'success': False, 'message': 'Booking is already cancelled'})
            cursor.execute("UPDATE bookings SET booking_status = 'cancelled' WHERE id = %s", (booking_id,))
            new_available_seats = booking['available_seats'] + booking['seats_booked']
            cursor.execute("UPDATE events SET available_seats = %s WHERE id = %s", 
                         (new_available_seats, booking['event_id']))
            connection.commit()
            return jsonify({
                'success': True,
                'message': f'Booking for {booking["title"]} has been cancelled successfully'
            })
    finally:
        connection.close()
@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.*, e.title, e.genre, e.event_date, e.event_time, e.location, 
                       u.username, u.full_name as user_full_name
                FROM bookings b
                LEFT JOIN events e ON b.event_id = e.id
                LEFT JOIN users u ON b.user_id = u.id
                ORDER BY b.booking_date DESC
            """)
            bookings = cursor.fetchall()
            return render_template('admin/bookings.html', bookings=bookings)
    finally:
        connection.close()
@app.route('/api/admin/update-booking-status/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        payment_status = data.get('payment_status')
        if not new_status or new_status not in ['active', 'cancelled']:
            return jsonify({'success': False, 'message': 'Invalid booking status'})
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT b.*, e.available_seats
                    FROM bookings b
                    LEFT JOIN events e ON b.event_id = e.id
                    WHERE b.id = %s
                """, (booking_id,))
                booking = cursor.fetchone()
                if not booking:
                    return jsonify({'success': False, 'message': 'Booking not found'})
                old_status = booking['booking_status']
                if old_status != 'cancelled' and new_status == 'cancelled':
                    new_available_seats = booking['available_seats'] + booking['seats_booked']
                    cursor.execute("UPDATE events SET available_seats = %s WHERE id = %s", 
                                 (new_available_seats, booking['event_id']))
                elif old_status == 'cancelled' and new_status != 'cancelled':
                    if booking['available_seats'] >= booking['seats_booked']:
                        new_available_seats = booking['available_seats'] - booking['seats_booked']
                        cursor.execute("UPDATE events SET available_seats = %s WHERE id = %s", 
                                     (new_available_seats, booking['event_id']))
                    else:
                        return jsonify({'success': False, 'message': 'Not enough seats available to restore booking'})
                update_query = "UPDATE bookings SET booking_status = %s"
                params = [new_status]
                if payment_status:
                    update_query += ", payment_status = %s"
                    params.append(payment_status)
                update_query += " WHERE id = %s"
                params.append(booking_id)
                cursor.execute(update_query, params)
                connection.commit()
                return jsonify({
                    'success': True,
                    'message': f'Booking status updated to {new_status}'
                })
        finally:
            connection.close()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
@app.route('/api/admin/booking-details/<int:booking_id>')
@admin_required
def get_booking_details(booking_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.*, e.title, e.genre, e.event_date, e.event_time, e.location, e.venue,
                       e.description, e.price as event_price, e.total_seats, e.available_seats,
                       u.username, u.email, u.full_name, u.phone as user_phone
                FROM bookings b
                LEFT JOIN events e ON b.event_id = e.id
                LEFT JOIN users u ON b.user_id = u.id
                WHERE b.id = %s
            """, (booking_id,))
            booking = cursor.fetchone()
            if not booking:
                return jsonify({'success': False, 'message': 'Booking not found'})
            return jsonify({
                'success': True,
                'booking': booking
            })
    finally:
        connection.close()
@app.route('/api/analytics')
def analytics_api():
    if not session.get('user_id') or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.*, u.username as created_by_username, u.full_name as created_by_name
                FROM events e
                LEFT JOIN users u ON e.created_by = u.id
                WHERE e.status = 'active' AND e.event_date >= CURDATE()
                ORDER BY e.event_date ASC
            """)
            events = cursor.fetchall()
            cursor.execute("SELECT id, username, email, full_name, role, created_at FROM users ORDER BY created_at DESC")
            users = cursor.fetchall()
            cursor.execute("""
                SELECT b.*, e.title as event_title, e.genre as event_genre
                FROM bookings b
                LEFT JOIN events e ON b.event_id = e.id
                ORDER BY b.booking_date DESC
            """)
            bookings = cursor.fetchall()
        connection.close()
        analyzer = DataAnalyzer()
        formatted_events = get_events_from_db()
        events_analysis = analyzer.analyze_event_trends(formatted_events)
        users_analysis = analyzer.analyze_user_patterns(users)
        booking_stats = calculate_booking_statistics(bookings)
        report_generator = ReportGenerator(analyzer)
        dashboard_data = report_generator.generate_dashboard_data(formatted_events, users)
        return jsonify({
            'success': True,
            'data': {
                'events_analysis': events_analysis,
                'users_analysis': users_analysis,
                'booking_statistics': booking_stats,
                'dashboard_metrics': dashboard_data['metrics'],
                'chart_data': dashboard_data['charts'],
                'insights': dashboard_data['insights'],
                'data_summary': analyzer.export_data_summary(formatted_events, users)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Analytics error: {str(e)}'}), 500
@app.route('/api/events/filter', methods=['POST'])
def filter_events_api():
    try:
        all_events = get_events_from_db()
        filters = {}
        if request.json:
            filter_data = request.json
            filters = {}
            if 'genre' in filter_data and filter_data['genre']:
                filters['genre'] = filter_data['genre']
            if 'price_range' in filter_data:
                try:
                    min_price = float(filter_data['price_range'].get('min', 0))
                    max_price = float(filter_data['price_range'].get('max', float('inf')))
                    filters['price_range'] = (min_price, max_price)
                except (ValueError, TypeError):
                    pass
            if 'date_range' in filter_data:
                try:
                    start_date_str = filter_data['date_range'].get('start')
                    end_date_str = filter_data['date_range'].get('end')
                    if start_date_str:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    else:
                        start_date = None
                    if end_date_str:
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    else:
                        end_date = None
                    if start_date or end_date:
                        filters['date_range'] = (start_date, end_date)
                except (ValueError, TypeError):
                    pass
            if 'min_seats' in filter_data:
                try:
                    min_seats = int(filter_data['min_seats'])
                    filters['min_seats'] = min_seats
                except (ValueError, TypeError):
                    pass
        filtered_events = filter_events_by_criteria(all_events, filters)
        sort_by = request.json.get('sort_by', 'date') if request.json else 'date'
        reverse_sort = request.json.get('reverse', False) if request.json else False
        sorted_events = sort_events(filtered_events, sort_by, reverse_sort)
        return jsonify({
            'success': True,
            'events': sorted_events,
            'total_count': len(sorted_events),
            'filters_applied': filters,
            'sort_applied': {'field': sort_by, 'reverse': reverse_sort}
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Filter error: {str(e)}'}), 500
@app.route('/api/reports/generate')
def generate_report_api():
    if not session.get('user_id') or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    try:
        events = get_events_from_db()
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email, full_name, role, created_at FROM users ORDER BY created_at DESC")
            users = cursor.fetchall()
        connection.close()
        analyzer = DataAnalyzer()
        report_generator = ReportGenerator(analyzer)
        report_type = request.args.get('type', 'summary')
        if report_type == 'summary':
            report_text = report_generator.generate_summary_report(events, users)
            return jsonify({
                'success': True,
                'report_type': 'summary',
                'report_text': report_text,
                'generated_at': datetime.now().isoformat()
            })
        elif report_type == 'dashboard':
            dashboard_data = report_generator.generate_dashboard_data(events, users)
            return jsonify({
                'success': True,
                'report_type': 'dashboard',
                'data': dashboard_data,
                'generated_at': datetime.now().isoformat()
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid report type'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Report generation error: {str(e)}'}), 500
@app.route('/api/event-details/<int:event_id>')
def get_event_details(event_id):
    try:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, title, description, image_url, genre, location, venue, 
                           event_date, event_time, price, total_seats, available_seats
                    FROM events 
                    WHERE id = %s
                """, (event_id,))
                event = cursor.fetchone()
                if not event:
                    return jsonify({'success': False, 'message': 'Event not found'})
                if event['event_date']:
                    event['date'] = event['event_date'].strftime('%Y-%m-%d')
                else:
                    event['date'] = 'TBD'
                if event['event_time']:
                    if isinstance(event['event_time'], str):
                        event['time'] = event['event_time']
                    elif hasattr(event['event_time'], 'strftime'):
                        event['time'] = event['event_time'].strftime('%H:%M')
                    elif hasattr(event['event_time'], 'total_seconds'):
                        total_seconds = int(event['event_time'].total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        event['time'] = f"{hours:02d}:{minutes:02d}"
                    else:
                        event['time'] = str(event['event_time'])
                    event.pop('event_time', None)
                else:
                    event['time'] = 'TBD'
                    event.pop('event_time', None)
                event.pop('event_date', None)
                return jsonify({'success': True, 'event': event})
        finally:
            connection.close()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
def get_user_profile_data(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email, full_name, phone, role, created_at FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return None
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
            profile = cursor.fetchone()
            cursor.execute("SELECT * FROM user_statistics WHERE user_id = %s", (user_id,))
            statistics = cursor.fetchone()
            cursor.execute("SELECT * FROM user_preferences WHERE user_id = %s", (user_id,))
            preferences = cursor.fetchone()
            cursor.execute("""
                SELECT b.*, e.title, e.event_date, e.event_time, e.location, e.genre
                FROM bookings b
                LEFT JOIN events e ON b.event_id = e.id
                WHERE b.user_id = %s
                ORDER BY b.booking_date DESC
                LIMIT 10
            """, (user_id,))
            recent_bookings = cursor.fetchall()
            cursor.execute("""
                SELECT ur.*, e.title as event_title
                FROM user_reviews ur
                LEFT JOIN events e ON ur.event_id = e.id
                WHERE ur.user_id = %s
                ORDER BY ur.created_at DESC
                LIMIT 5
            """, (user_id,))
            reviews = cursor.fetchall()
            return {
                'user': user,
                'profile': profile or {},
                'statistics': statistics or {},
                'preferences': preferences or {},
                'recent_bookings': recent_bookings,
                'reviews': reviews
            }
    finally:
        connection.close()
def update_user_statistics(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_bookings,
                    COALESCE(SUM(total_price), 0) as total_spent,
                    COUNT(CASE WHEN e.event_date >= CURDATE() THEN 1 END) as upcoming_bookings,
                    COUNT(CASE WHEN e.event_date < CURDATE() THEN 1 END) as past_bookings,
                    COUNT(CASE WHEN b.booking_status = 'cancelled' THEN 1 END) as cancelled_bookings,
                    COALESCE(AVG(b.total_price), 0) as average_booking_value,
                    COALESCE(MAX(b.total_price), 0) as most_expensive_booking,
                    MAX(b.booking_date) as last_booking_date
                FROM bookings b
                LEFT JOIN events e ON b.event_id = e.id
                WHERE b.user_id = %s
            """, (user_id,))
            stats = cursor.fetchone()
            cursor.execute("""
                SELECT e.genre, COUNT(*) as count
                FROM bookings b
                LEFT JOIN events e ON b.event_id = e.id
                WHERE b.user_id = %s AND b.booking_status != 'cancelled'
                GROUP BY e.genre
                ORDER BY count DESC
                LIMIT 1
            """, (user_id,))
            favorite_cat = cursor.fetchone()
            cursor.execute("""
                INSERT INTO user_statistics 
                (user_id, total_bookings, total_spent, upcoming_bookings, past_bookings, 
                 cancelled_bookings, average_booking_value, most_expensive_booking, 
                 last_booking_date, favorite_category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                total_bookings = VALUES(total_bookings),
                total_spent = VALUES(total_spent),
                upcoming_bookings = VALUES(upcoming_bookings),
                past_bookings = VALUES(past_bookings),
                cancelled_bookings = VALUES(cancelled_bookings),
                average_booking_value = VALUES(average_booking_value),
                most_expensive_booking = VALUES(most_expensive_booking),
                last_booking_date = VALUES(last_booking_date),
                favorite_category = VALUES(favorite_category)
            """, (user_id, stats['total_bookings'], stats['total_spent'], 
                  stats['upcoming_bookings'], stats['past_bookings'], 
                  stats['cancelled_bookings'], stats['average_booking_value'], 
                  stats['most_expensive_booking'], stats['last_booking_date'],
                  favorite_cat['genre'] if favorite_cat else None))
            connection.commit()
    finally:
        connection.close()
@app.route('/profile')
@login_required
def user_profile():
    profile_data = get_user_profile_data(session['user_id'])
    if not profile_data:
        flash('User profile not found!', 'error')
        return redirect(url_for('home'))
    return render_template('user/profile.html', **profile_data)
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET 
                        full_name = %s, 
                        phone = %s, 
                        email = %s
                    WHERE id = %s
                """, (request.form['full_name'], request.form['phone'], 
                      request.form['email'], session['user_id']))
                cursor.execute("""
                    INSERT INTO user_profiles 
                    (user_id, bio, date_of_birth, address, city, state, country, zip_code)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    bio = VALUES(bio),
                    date_of_birth = VALUES(date_of_birth),
                    address = VALUES(address),
                    city = VALUES(city),
                    state = VALUES(state),
                    country = VALUES(country),
                    zip_code = VALUES(zip_code)
                """, (session['user_id'], request.form.get('bio', ''),
                      request.form.get('date_of_birth') or None,
                      request.form.get('address', ''), request.form.get('city', ''),
                      request.form.get('state', ''), request.form.get('country', ''),
                      request.form.get('zip_code', '')))
                connection.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('user_profile'))
        finally:
            connection.close()
    profile_data = get_user_profile_data(session['user_id'])
    return render_template('user/edit_profile.html', **profile_data)
@app.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    if request.method == 'POST':
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_preferences 
                    (user_id, email_notifications, sms_notifications, promotional_emails,
                     booking_reminders, event_recommendations, newsletter_subscription,
                     language_preference, timezone, currency_preference, theme_preference)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    email_notifications = VALUES(email_notifications),
                    sms_notifications = VALUES(sms_notifications),
                    promotional_emails = VALUES(promotional_emails),
                    booking_reminders = VALUES(booking_reminders),
                    event_recommendations = VALUES(event_recommendations),
                    newsletter_subscription = VALUES(newsletter_subscription),
                    language_preference = VALUES(language_preference),
                    timezone = VALUES(timezone),
                    currency_preference = VALUES(currency_preference),
                    theme_preference = VALUES(theme_preference)
                """, (session['user_id'],
                      'email_notifications' in request.form,
                      'sms_notifications' in request.form,
                      'promotional_emails' in request.form,
                      'booking_reminders' in request.form,
                      'event_recommendations' in request.form,
                      'newsletter_subscription' in request.form,
                      request.form.get('language_preference', 'en'),
                      request.form.get('timezone', 'UTC'),
                      request.form.get('currency_preference', 'USD'),
                      request.form.get('theme_preference', 'auto')))
                connection.commit()
                flash('Settings updated successfully!', 'success')
                return redirect(url_for('profile_settings'))
        finally:
            connection.close()
    profile_data = get_user_profile_data(session['user_id'])
    return render_template('user/settings.html', **profile_data)
@app.route('/profile/security', methods=['GET', 'POST'])
@login_required
def profile_security():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if not all([current_password, new_password, confirm_password]):
            flash('All password fields are required!', 'error')
            return redirect(url_for('profile_security'))
        if new_password != confirm_password:
            flash('New passwords do not match!', 'error')
            return redirect(url_for('profile_security'))
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return redirect(url_for('profile_security'))
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT password_user FROM users WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if not user or user['password_user'] != current_password:
                    flash('Current password is incorrect!', 'error')
                    return redirect(url_for('profile_security'))
                cursor.execute("UPDATE users SET password_user = %s WHERE id = %s", 
                             (new_password, session['user_id']))
                connection.commit()
                flash('Password changed successfully!', 'success')
                return redirect(url_for('profile_security'))
        finally:
            connection.close()
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM user_login_history 
                WHERE user_id = %s 
                ORDER BY login_time DESC 
                LIMIT 10
            """, (session['user_id'],))
            login_history = cursor.fetchall()
    finally:
        connection.close()
    return render_template('user/security.html', login_history=login_history)
@app.route('/profile/add-review', methods=['POST'])
@login_required
def add_review():
    """Add a review for an event"""
    try:
        event_id = request.form.get('event_id')
        booking_id = request.form.get('booking_id')
        rating = int(request.form.get('rating'))
        review_text = request.form.get('review_text', '')
        review_title = request.form.get('review_title', '')
        would_recommend = 'would_recommend' in request.form
        if not all([event_id, booking_id, rating]) or rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Invalid review data'})
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT b.id, b.user_id 
                    FROM bookings b 
                    WHERE b.id = %s AND b.user_id = %s AND b.booking_status = 'active'
                """, (booking_id, session['user_id']))
                booking = cursor.fetchone()
                if not booking:
                    return jsonify({'success': False, 'message': 'Invalid booking'})
                cursor.execute("""
                    INSERT INTO user_reviews 
                    (user_id, event_id, booking_id, rating, review_text, review_title, would_recommend)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    rating = VALUES(rating),
                    review_text = VALUES(review_text),
                    review_title = VALUES(review_title),
                    would_recommend = VALUES(would_recommend),
                    updated_at = CURRENT_TIMESTAMP
                """, (session['user_id'], event_id, booking_id, rating, 
                      review_text, review_title, would_recommend))
                connection.commit()
                return jsonify({'success': True, 'message': 'Review added successfully!'})
        finally:
            connection.close()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
if __name__ == '__main__':
    app.run(debug=True,port=5002)