import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import supabase_client as db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'lux-salon-finder-super-secret-key-2026')

# ── SESSION-BASED AUTH ────────────────────────────────────────────────────────
# We use Flask session instead of Flask-Login to avoid SQLAlchemy dependency.

def login_user(user):
    session['user_id']   = user['id']
    session['user_name'] = user['name']
    session['is_admin']  = user.get('is_admin', False)

def logout_user():
    session.clear()

def current_user():
    """Returns user dict if logged in, else None."""
    uid = session.get('user_id')
    if uid:
        return db.get_user_by_id(uid)
    return None

def is_authenticated():
    return 'user_id' in session

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated():
            flash("Please log in to continue.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin', False):
            flash("You do not have access to this page.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# Context processor — inject current_user and areas into all templates
@app.context_processor
def inject_globals():
    user = None
    if is_authenticated():
        user = {
            'id':       session.get('user_id'),
            'name':     session.get('user_name'),
            'is_admin': session.get('is_admin', False),
            'is_authenticated': True
        }
    else:
        user = type('AnonUser', (), {'is_authenticated': False, 'is_admin': False, 'name': '', 'id': None})()
    return dict(
        current_user=user,
        all_areas=["Indiranagar", "Lavelle Road", "Koramangala", "Sadashivanagar"]
    )

# ── STARTUP SEED ──────────────────────────────────────────────────────────────
print("Connecting to Supabase via REST API (HTTPS port 443)...")
try:
    db.seed_if_empty()
    print("Supabase connection successful!")
except Exception as e:
    print(f"Supabase seed error: {e}")

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    featured = db.get_all_salons(min_rating=4.7)[:3]
    return render_template('home.html', featured_salons=featured)


@app.route('/salons')
def salons():
    search_query   = request.args.get('search', '').strip()
    selected_areas = request.args.getlist('area')
    selected_prices= request.args.getlist('price')
    min_rating     = request.args.get('rating', type=float)

    salon_list = db.get_all_salons(
        search=search_query or None,
        areas=selected_areas or None,
        prices=selected_prices or None,
        min_rating=min_rating
    )
    return render_template('salons.html',
                           salons=salon_list,
                           search_query=search_query,
                           selected_areas=selected_areas,
                           selected_prices=selected_prices,
                           min_rating=min_rating)


@app.route('/salons/<int:salon_id>', methods=['GET', 'POST'])
def salon_detail(salon_id):
    salon = db.get_salon_by_id(salon_id)
    if not salon:
        flash("Salon not found.", "danger")
        return redirect(url_for('salons'))

    if request.method == 'POST':
        if not is_authenticated():
            flash("You must be logged in to leave a review.", "danger")
            return redirect(url_for('login'))

        rating  = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()

        if not rating or rating < 1 or rating > 5:
            flash("Please provide a valid rating between 1 and 5.", "danger")
        else:
            db.add_review(session['user_id'], salon_id, rating, comment)
            # Recalculate average rating
            reviews = db.get_salon_reviews(salon_id)
            if reviews:
                avg = round(sum(r['rating'] for r in reviews) / len(reviews), 1)
                db.update_salon_rating(salon_id, avg)
            flash("Thank you for your review!", "success")
            return redirect(url_for('salon_detail', salon_id=salon_id))

    services = db.get_salon_services(salon_id)
    reviews  = db.get_salon_reviews(salon_id)

    # Categorize services
    def has(svc, *keywords):
        return any(k in svc['name'].lower() for k in keywords)

    categorized_services = {
        'Hair':          [s for s in services if has(s, 'hair','cut','colour','argan','keratin','blow','balayage','wash','wave','styled')],
        'Skincare':      [s for s in services if has(s, 'facial','skin','glow','hydra','collagen','botanical')],
        'Body & Massage':[s for s in services if has(s, 'massage','spa','therapy','tissue','stone','hammam','aromatherapy','stress relief')],
        'Nails':         [s for s in services if has(s, 'pedicure','manicure','nail','polish','chrome','acrylic')],
    }

    all_cat = [s for cat_svcs in categorized_services.values() for s in cat_svcs]
    uncategorized = [s for s in services if s not in all_cat]
    if uncategorized:
        categorized_services['Other'] = uncategorized
    categorized_services = {k: v for k, v in categorized_services.items() if v}

    return render_template('salon_detail.html',
                           salon=salon,
                           categorized_services=categorized_services,
                           reviews=reviews)


@app.route('/book/<int:service_id>', methods=['GET', 'POST'])
@login_required
def book(service_id):
    service = db.get_service_by_id(service_id)
    if not service:
        flash("Service not found.", "danger")
        return redirect(url_for('salons'))

    salon = db.get_salon_by_id(service['salon_id'])

    if request.method == 'POST':
        date   = request.form.get('date')
        time   = request.form.get('time')
        stylist= request.form.get('stylist')

        if not date or not time or not stylist:
            flash("Please fill in all booking fields.", "danger")
            return redirect(url_for('book', service_id=service_id))

        result = db.create_booking(
            user_id   = session['user_id'],
            salon_id  = service['salon_id'],
            service_id= service_id,
            date=date, time=time, stylist=stylist
        )
        if result:
            flash("Your booking has been successfully confirmed!", "success")
        else:
            flash("Booking failed. Please try again.", "danger")
        return redirect(url_for('dashboard'))

    stylists = ["Senior Stylist - Rohan", "Art Director - Priya",
                "Creative Consultant - David", "No Preference"]
    return render_template('booking.html', service=service, salon=salon, stylists=stylists)


@app.route('/dashboard')
@login_required
def dashboard():
    bookings = db.get_user_bookings(session['user_id'])
    return render_template('dashboard.html', bookings=bookings)


@app.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = db.get_booking_by_id(booking_id)
    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for('dashboard'))

    if booking['user_id'] != session['user_id'] and not session.get('is_admin'):
        flash("Unauthorized action.", "danger")
        return redirect(url_for('dashboard'))

    db.cancel_booking(booking_id)
    flash("Your booking has been cancelled successfully.", "info")
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_authenticated():
        return redirect(url_for('index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = db.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            login_user(user)
            flash(f"Welcome back, {user['name']}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')


@app.route('/signup', methods=['POST'])
def signup():
    if is_authenticated():
        return redirect(url_for('index'))

    name     = request.form.get('name', '').strip()
    email    = request.form.get('email', '').strip()
    phone    = request.form.get('phone', '').strip()
    password = request.form.get('password', '')

    if not name or not email or not password:
        flash("Please fill in all required fields.", "danger")
        return redirect(url_for('login'))

    existing = db.get_user_by_email(email)
    if existing:
        flash("Email address is already registered.", "danger")
        return redirect(url_for('login'))

    pw_hash = generate_password_hash(password)
    new_user = db.create_user(name, email, pw_hash, phone)
    if new_user:
        login_user(new_user)
        flash("Registration successful! Welcome to LUXA SALON.", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Registration failed. Please try again.", "danger")
        return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/admin/select')
@login_required
@admin_required
def admin_select():
    """Prompt admin to pick a salon to manage."""
    salons = db.get_all_salons()
    return render_template('admin_select.html', salons=salons)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_salon':
            name        = request.form.get('name', '').strip()
            area        = request.form.get('area', '').strip()
            price_range = request.form.get('price_range', '$$')
            description = request.form.get('description', '').strip()

            if name and area:
                result = db.add_salon(name, area, price_range, description)
                if result:
                    flash(f"Salon '{name}' added successfully!", "success")
                else:
                    flash("Failed to add salon.", "danger")
            else:
                flash("Name and Area are required fields.", "danger")

        elif action == 'delete_salon':
            salon_id = request.form.get('salon_id', type=int)
            if salon_id:
                db.delete_salon(salon_id)
                flash("Salon deleted successfully.", "success")

        elif action == 'update_booking_status':
            booking_id = request.form.get('booking_id', type=int)
            status     = request.form.get('status')
            if booking_id and status in ['Pending', 'Confirmed', 'Cancelled']:
                db.update_booking_status(booking_id, status)
                flash(f"Booking #{booking_id} status updated to '{status}'.", "success")

        return redirect(url_for('admin'))

    salons   = db.get_all_salons()
    bookings = db.get_all_bookings()
    users    = db.get_all_users()
    return render_template('admin.html', salons=salons, bookings=bookings, users=users)


@app.route('/salon-admin/<int:salon_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def salon_admin(salon_id):
    salon = db.get_salon_by_id(salon_id)
    if not salon:
        flash("Salon not found.", "danger")
        return redirect(url_for('admin'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_booking_status':
            booking_id = request.form.get('booking_id', type=int)
            status     = request.form.get('status')
            if booking_id and status in ['Pending', 'Confirmed', 'Cancelled']:
                db.update_booking_status(booking_id, status)
                flash(f"Booking #{booking_id} updated to '{status}'.", "success")
        return redirect(url_for('salon_admin', salon_id=salon_id))

    bookings = db.get_bookings_by_salon(salon_id)
    return render_template('salon_admin.html', salon=salon, bookings=bookings)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
