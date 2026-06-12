"""
Supabase REST API Client
Uses HTTPS (port 443) - bypasses blocked PostgreSQL ports 5432/6543 entirely.
All data operations go through Supabase's PostgREST API.
"""
import requests
import os

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://ryewzzdytcehcizcqshc.supabase.co')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ5ZXd6emR5dGNlaGNpemNxc2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA5MTU5MjgsImV4cCI6MjA5NjQ5MTkyOH0.MpvvZc4wgX_M4dF4KvPBlVr98sRHbivjaY3HgBRZZ90')

def _headers(service_role=False):
    return {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

def _url(table):
    return f'{SUPABASE_URL}/rest/v1/{table}'


# ── GENERIC CRUD ──────────────────────────────────────────────────────────────

def select(table, filters=None, order=None, limit=None, single=False):
    """SELECT rows from a table. Returns list of dicts (or single dict)."""
    params = {'select': '*'}
    if filters:
        params.update(filters)
    if order:
        params['order'] = order
    if limit:
        params['limit'] = limit

    headers = _headers()
    if single:
        headers['Accept'] = 'application/vnd.pgrst.object+json'

    resp = requests.get(_url(table), headers=headers, params=params, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 406 and single:
        return None
    return [] if not single else None


def insert(table, data):
    """INSERT a row. Returns the inserted row dict or None."""
    resp = requests.post(_url(table), headers=_headers(), json=data, timeout=10)
    if resp.status_code in (200, 201):
        result = resp.json()
        return result[0] if isinstance(result, list) and result else result
    print(f"[Supabase INSERT error] {resp.status_code}: {resp.text}")
    return None


def update(table, data, filters):
    """UPDATE rows matching filters. Returns list of updated rows."""
    resp = requests.patch(_url(table), headers=_headers(), json=data, params=filters, timeout=10)
    if resp.status_code in (200, 204):
        return resp.json() if resp.text else []
    print(f"[Supabase UPDATE error] {resp.status_code}: {resp.text}")
    return []


def delete(table, filters):
    """DELETE rows matching filters."""
    resp = requests.delete(_url(table), headers=_headers(), params=filters, timeout=10)
    return resp.status_code in (200, 204)


# ── SALONS ────────────────────────────────────────────────────────────────────

def get_all_salons(search=None, areas=None, prices=None, min_rating=None):
    params = {'select': '*'}
    if areas:
        params['area'] = f'in.({",".join(areas)})'
    if prices:
        params['price_range'] = f'in.({",".join(prices)})'
    if min_rating:
        params['rating'] = f'gte.{min_rating}'
    if search:
        params['or'] = f'(name.ilike.*{search}*,area.ilike.*{search}*,description.ilike.*{search}*)'

    resp = requests.get(_url('salons'), headers=_headers(), params=params, timeout=10)
    salons = resp.json() if resp.status_code == 200 else []

    # Attach services list to each salon for search-by-service filtering
    if search:
        service_resp = requests.get(
            _url('services'),
            headers=_headers(),
            params={'name': f'ilike.*{search}*', 'select': 'salon_id'},
            timeout=10
        )
        if service_resp.status_code == 200:
            matching_salon_ids = {s['salon_id'] for s in service_resp.json()}
            all_salon_ids = {s['id'] for s in salons}
            missing_ids = matching_salon_ids - all_salon_ids
            if missing_ids:
                extra = select('salons', filters={'id': f'in.({",".join(str(i) for i in missing_ids)})'})
                salons.extend(extra)

    return salons


def get_salon_by_id(salon_id):
    resp = requests.get(
        _url('salons'),
        headers=_headers(),
        params={'id': f'eq.{salon_id}', 'select': '*'},
        timeout=10
    )
    rows = resp.json() if resp.status_code == 200 else []
    return rows[0] if rows else None


def get_salon_services(salon_id):
    return select('services', filters={'salon_id': f'eq.{salon_id}'}, order='name.asc')


def get_salon_reviews(salon_id):
    reviews = select('reviews', filters={'salon_id': f'eq.{salon_id}'}, order='created_at.desc')
    # Attach user name to each review
    user_ids = list({r['user_id'] for r in reviews})
    if user_ids:
        user_resp = requests.get(
            _url('users'),
            headers=_headers(),
            params={'id': f'in.({",".join(str(u) for u in user_ids)})', 'select': 'id,name'},
            timeout=10
        )
        if user_resp.status_code == 200:
            user_map = {u['id']: u['name'] for u in user_resp.json()}
            for r in reviews:
                r['user_name'] = user_map.get(r['user_id'], 'Guest')
    return reviews


def add_salon(name, area, price_range, description):
    return insert('salons', {
        'name': name,
        'area': area,
        'price_range': price_range,
        'description': description,
        'rating': 5.0,
        'image_path': '/static/images/salon_hero.png'
    })


def delete_salon(salon_id):
    return delete('salons', {'id': f'eq.{salon_id}'})


def update_salon_rating(salon_id, new_rating):
    update('salons', {'rating': new_rating}, {'id': f'eq.{salon_id}'})


# ── SERVICES ──────────────────────────────────────────────────────────────────

def get_service_by_id(service_id):
    rows = select('services', filters={'id': f'eq.{service_id}'})
    return rows[0] if rows else None


# ── USERS ─────────────────────────────────────────────────────────────────────

def get_user_by_email(email):
    rows = select('users', filters={'email': f'eq.{email}'})
    return rows[0] if rows else None


def get_user_by_id(user_id):
    rows = select('users', filters={'id': f'eq.{user_id}'})
    return rows[0] if rows else None


def create_user(name, email, password_hash, phone='', is_admin=False):
    return insert('users', {
        'name': name,
        'email': email,
        'password_hash': password_hash,
        'phone': phone,
        'is_admin': is_admin
    })


def get_all_users():
    return select('users', order='id.asc')


# ── BOOKINGS ──────────────────────────────────────────────────────────────────

def create_booking(user_id, salon_id, service_id, date, time, stylist):
    return insert('bookings', {
        'user_id': user_id,
        'salon_id': salon_id,
        'service_id': service_id,
        'date': date,
        'time': time,
        'stylist': stylist,
        'status': 'Confirmed'
    })


def get_user_bookings(user_id):
    bookings = select('bookings', filters={'user_id': f'eq.{user_id}'}, order='date.desc,time.desc')
    return _enrich_bookings(bookings)


def get_all_bookings():
    bookings = select('bookings', order='date.desc,time.desc')
    return _enrich_bookings(bookings)


def get_bookings_by_salon(salon_id):
    """Get all bookings for a specific salon, with customer details."""
    bookings = select('bookings', filters={'salon_id': f'eq.{salon_id}'}, order='date.desc,time.desc')
    return _enrich_bookings(bookings)


def cancel_booking(booking_id):
    update('bookings', {'status': 'Cancelled'}, {'id': f'eq.{booking_id}'})


def update_booking_status(booking_id, status):
    return update('bookings', {'status': status}, {'id': f'eq.{booking_id}'})


def get_booking_by_id(booking_id):
    rows = select('bookings', filters={'id': f'eq.{booking_id}'})
    return rows[0] if rows else None


def _enrich_bookings(bookings):
    """Attach salon_name, service_name, and customer details to each booking dict."""
    if not bookings:
        return bookings

    salon_ids   = list({b['salon_id']   for b in bookings})
    service_ids = list({b['service_id'] for b in bookings})
    user_ids    = list({b['user_id']    for b in bookings})

    salon_map, service_map, user_map = {}, {}, {}
    if salon_ids:
        resp = requests.get(_url('salons'), headers=_headers(),
                            params={'id': f'in.({",".join(str(i) for i in salon_ids)})', 'select': 'id,name'}, timeout=10)
        if resp.status_code == 200:
            salon_map = {s['id']: s['name'] for s in resp.json()}

    if service_ids:
        resp = requests.get(_url('services'), headers=_headers(),
                            params={'id': f'in.({",".join(str(i) for i in service_ids)})', 'select': 'id,name,price,duration'}, timeout=10)
        if resp.status_code == 200:
            service_map = {s['id']: s for s in resp.json()}

    if user_ids:
        resp = requests.get(_url('users'), headers=_headers(),
                            params={'id': f'in.({",".join(str(i) for i in user_ids)})', 'select': 'id,name,email,phone'}, timeout=10)
        if resp.status_code == 200:
            user_map = {u['id']: u for u in resp.json()}

    for b in bookings:
        b['salon_name']   = salon_map.get(b['salon_id'],   'Unknown Salon')
        svc = service_map.get(b['service_id'], {})
        b['service_name'] = svc.get('name', 'Unknown Service')
        b['service_price']= svc.get('price', 0)
        
        usr = user_map.get(b['user_id'], {})
        b['user_name']    = usr.get('name', f"User #{b['user_id']}")
        b['user_email']   = usr.get('email', 'N/A')
        b['user_phone']   = usr.get('phone', 'N/A')
    return bookings


# ── REVIEWS ───────────────────────────────────────────────────────────────────

def add_review(user_id, salon_id, rating, comment):
    return insert('reviews', {
        'user_id': user_id,
        'salon_id': salon_id,
        'rating': rating,
        'comment': comment
    })


# ── SEED ──────────────────────────────────────────────────────────────────────

def seed_if_empty():
    """Seed Supabase tables if salons table is empty."""
    from werkzeug.security import generate_password_hash

    salons = select('salons', limit=1)
    if salons:
        print("Supabase already has data. Skipping seed.")
        return

    print("Seeding Supabase via REST API...")

    # Users
    admin_hash = generate_password_hash('adminpassword')
    user_hash  = generate_password_hash('userpassword')
    admin = create_user('Admin Manager', 'admin@salonlux.in', admin_hash, '+91 98765 43210', True)
    customer = create_user('Aarav Sharma', 'user@salonlux.in', user_hash, '+91 99887 76655', False)

    if not admin or not customer:
        print("Seed: Users may already exist, fetching existing records.")
        admin    = get_user_by_email('admin@salonlux.in')
        customer = get_user_by_email('user@salonlux.in')

    # Salons
    salon_data = [
        {'name': 'The Grand Silhouette', 'area': 'Indiranagar', 'rating': 4.9, 'price_range': '₹₹₹₹',
         'description': 'An ultra-exclusive grooming atelier offering bespoke hair couture, restorative clinical skincare, and luxury holistic therapy under the guidance of internationally certified art directors.',
         'image_path': '/static/images/salon_1.png'},
        {'name': 'En Vogue Atelier', 'area': 'Lavelle Road', 'rating': 4.8, 'price_range': '₹₹₹₹',
         'description': "Nestled in Bangalore's premier luxury district, En Vogue Atelier features global runway stylists, personalized aesthetics consulting, and premium organic spa treatments within a private, gold-trimmed sanctuary.",
         'image_path': '/static/images/salon_2.png'},
        {'name': 'Aura Wellness & Styling', 'area': 'Koramangala', 'rating': 4.7, 'price_range': '₹₹₹',
         'description': 'A contemporary glass-walled sanctuary of modern styling and tranquil wellness. Specializing in advanced hair transformations, botanical scalp therapies, and high-fashion nail couture.',
         'image_path': '/static/images/salon_3.png'},
        {'name': 'Prism & Polish', 'area': 'Sadashivanagar', 'rating': 4.6, 'price_range': '₹₹₹',
         'description': 'A premium beauty boutique focusing on luxury manicures, advanced lash techniques, rejuvenating facial therapy, and custom bridal transformations using global beauty brands.',
         'image_path': '/static/images/salon_4.png'}
    ]

    created_salons = []
    for s in salon_data:
        result = insert('salons', s)
        if result:
            created_salons.append(result)
            print(f"  ✓ Salon created: {s['name']} (id={result.get('id')})")

    if len(created_salons) < 4:
        print("  Fetching all salons after insert...")
        created_salons = select('salons', order='id.asc')

    # Map by name
    salon_map = {s['name']: s['id'] for s in created_salons}

    services = [
        # The Grand Silhouette
        {'salon_id': salon_map.get('The Grand Silhouette'), 'name': 'Royal Signature Haircut',    'duration': 60,  'price': 2500},
        {'salon_id': salon_map.get('The Grand Silhouette'), 'name': 'Balayage & Hair Couture',    'duration': 180, 'price': 7500},
        {'salon_id': salon_map.get('The Grand Silhouette'), 'name': '24k Gold Radiance Facial',   'duration': 90,  'price': 5500},
        {'salon_id': salon_map.get('The Grand Silhouette'), 'name': 'Lux Hammam Spa Massage',     'duration': 90,  'price': 4500},
        {'salon_id': salon_map.get('The Grand Silhouette'), 'name': 'Caviar Deluxe Pedicure',     'duration': 60,  'price': 2200},
        # En Vogue Atelier
        {'salon_id': salon_map.get('En Vogue Atelier'), 'name': "Director's Cut & Styling",       'duration': 60,  'price': 3000},
        {'salon_id': salon_map.get('En Vogue Atelier'), 'name': 'Moroccan Argan Therapy',         'duration': 120, 'price': 4800},
        {'salon_id': salon_map.get('En Vogue Atelier'), 'name': 'HydraFacial Elite',              'duration': 75,  'price': 6500},
        {'salon_id': salon_map.get('En Vogue Atelier'), 'name': 'Aromatherapy Deep Tissue',       'duration': 90,  'price': 4000},
        {'salon_id': salon_map.get('En Vogue Atelier'), 'name': 'Luxury Gel Manicure',            'duration': 45,  'price': 1800},
        # Aura Wellness & Styling
        {'salon_id': salon_map.get('Aura Wellness & Styling'), 'name': 'Creative Haircut & Wash', 'duration': 45,  'price': 1500},
        {'salon_id': salon_map.get('Aura Wellness & Styling'), 'name': 'Keratin Intense Infusion','duration': 150, 'price': 6000},
        {'salon_id': salon_map.get('Aura Wellness & Styling'), 'name': 'Organic Botanical Facial','duration': 60,  'price': 3200},
        {'salon_id': salon_map.get('Aura Wellness & Styling'), 'name': 'Stress Relief Massage',   'duration': 60,  'price': 2800},
        {'salon_id': salon_map.get('Aura Wellness & Styling'), 'name': 'Chrome & Matte Nail Art', 'duration': 60,  'price': 1600},
        # Prism & Polish
        {'salon_id': salon_map.get('Prism & Polish'), 'name': 'Premium Blow Dry & Styled Waves',  'duration': 45,  'price': 1200},
        {'salon_id': salon_map.get('Prism & Polish'), 'name': 'Collagen Booster Facial',          'duration': 60,  'price': 4000},
        {'salon_id': salon_map.get('Prism & Polish'), 'name': 'Hot Stone Body Massage',           'duration': 75,  'price': 3500},
        {'salon_id': salon_map.get('Prism & Polish'), 'name': 'Acrylic Nail Extensions',          'duration': 90,  'price': 2500},
        {'salon_id': salon_map.get('Prism & Polish'), 'name': 'Premium Paraffin Pedicure',        'duration': 60,  'price': 1500},
    ]

    for svc in services:
        if svc['salon_id']:
            insert('services', svc)

    # Reviews
    if customer:
        customer_id = customer['id'] if isinstance(customer, dict) else customer.id
        reviews = [
            {'user_id': customer_id, 'salon_id': salon_map.get('The Grand Silhouette'),    'rating': 5, 'comment': 'Absolutely top-notch! The Royal Signature Haircut was incredible. The stylists understand luxury, and the gold-trimmed decor makes you feel like royalty.'},
            {'user_id': customer_id, 'salon_id': salon_map.get('En Vogue Atelier'),        'rating': 5, 'comment': 'En Vogue Atelier is the best in Bangalore. Loved the HydraFacial Elite, my skin is glowing. Extremely professional staff and private rooms.'},
            {'user_id': customer_id, 'salon_id': salon_map.get('Aura Wellness & Styling'), 'rating': 4, 'comment': 'Very peaceful ambiance and beautiful glass interiors. The Keratin treatment did wonders to my frizzy hair. Highly recommend!'},
            {'user_id': customer_id, 'salon_id': salon_map.get('Prism & Polish'),          'rating': 4, 'comment': 'Lovely nail art work. A bit busy on weekends, but the wait was worth it. Will visit again.'},
        ]
        for rev in reviews:
            if rev['salon_id']:
                insert('reviews', rev)

    print("Supabase seeding complete!")
