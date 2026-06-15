import socket
from urllib.parse import urlparse
from extensions import db
from models import User, Salon, Service, Review
from werkzeug.security import generate_password_hash

def init_db(app):
    # Check if database URL is PostgreSQL and verify if it's resolvable
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri and ('postgresql' in db_uri or 'postgres' in db_uri):
        parsed = urlparse(db_uri)
        original_host = parsed.hostname
        port = parsed.port or 6543
        
        # If the host is a Supabase connection pooler, dynamically scan regions to find the active host
        if 'pooler.supabase.com' in original_host:
            regions = ['ap-south-1', 'us-east-1', 'ap-southeast-1', 'eu-central-1', 'us-west-1', 'eu-west-1', 'sa-east-1', 'ca-central-1']
            connected_host = None
            
            for region in regions:
                test_host = f"aws-0-{region}.pooler.supabase.com"
                try:
                    print(f"Scanning region: Testing connection to {test_host}:{port}...")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1.0)
                    sock.connect((test_host, port))
                    sock.close()
                    print(f"Success! Detected active Supabase pooler in {region} region.")
                    connected_host = test_host
                    break
                except Exception as e:
                    # Silent fallback to scan next region
                    pass
            
            if connected_host:
                # Update URI with the working regional pooler host
                new_uri = db_uri.replace(original_host, connected_host)
                app.config['SQLALCHEMY_DATABASE_URI'] = new_uri
                print(f"Updated database configuration to use working host: {connected_host}")
            else:
                print("All regional pooler checks timed out. Falling back to local SQLite.")
                app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salon_finder.db'
        else:
            # Check direct hostname connection
            try:
                print(f"Verifying direct connection to database host: {original_host}:{port}...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect((original_host, port))
                sock.close()
                print("Database host is reachable.")
            except Exception as e:
                print(f"Database connection check failed: {e}")
                print("FALLBACK: Could not connect to remote Supabase database. Using local SQLite instead.")
                app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salon_finder.db'

    db.init_app(app)
    with app.app_context():
        db.create_all()
        seed_data()

def seed_data():
    # Check if we already have salons, if so, do not seed again
    if Salon.query.first() is not None:
        return
        
    print("Seeding database...")
    
    # 1. Create Users
    admin = User(
        name="Admin Manager",
        email="admin@salonlux.in",
        phone="+91 98765 43210",
        is_admin=True
    )
    admin.set_password("adminpassword")
    
    customer = User(
        name="Aarav Sharma",
        email="user@salonlux.in",
        phone="+91 99887 76655",
        is_admin=False
    )
    customer.set_password("userpassword")
    
    db.session.add(admin)
    db.session.add(customer)
    
    # 2. Create Salons
    s1 = Salon(
        name="The Grand Silhouette",
        area="Indiranagar",
        rating=4.9,
        price_range="$$$$",
        description="An ultra-exclusive grooming atelier offering bespoke hair couture, restorative clinical skincare, and luxury holistic therapy under the guidance of internationally certified art directors.",
        image_path="/static/images/salon_1.png"
    )
    
    s2 = Salon(
        name="En Vogue Atelier",
        area="Lavelle Road",
        rating=4.8,
        price_range="$$$$",
        description="Nestled in Bangalore's premier luxury district, En Vogue Atelier features global runway stylists, personalized aesthetics consulting, and premium organic spa treatments within a private, gold-trimmed sanctuary.",
        image_path="/static/images/salon_2.png"
    )
    
    s3 = Salon(
        name="Aura Wellness & Styling",
        area="Koramangala",
        rating=4.7,
        price_range="$$$",
        description="A contemporary glass-walled sanctuary of modern styling and tranquil wellness. Specializing in advanced hair transformations, botanical scalp therapies, and high-fashion nail couture.",
        image_path="/static/images/salon_3.png"
    )
    
    s4 = Salon(
        name="Prism & Polish",
        area="Sadashivanagar",
        rating=4.6,
        price_range="$$$",
        description="A premium beauty boutique focusing on luxury manicures, advanced lash techniques, rejuvenating facial therapy, and custom bridal transformations using global beauty brands.",
        image_path="/static/images/salon_4.png"
    )
    
    db.session.add_all([s1, s2, s3, s4])
    db.session.flush() # Populate IDs for foreign keys
    
    # 3. Add Services
    # Services for Salon 1 (The Grand Silhouette)
    db.session.add_all([
        Service(salon_id=s1.id, name="Royal Signature Haircut", duration=60, price=2500),
        Service(salon_id=s1.id, name="Balayage & Hair Couture", duration=180, price=7500),
        Service(salon_id=s1.id, name="24k Gold Radiance Facial", duration=90, price=5500),
        Service(salon_id=s1.id, name="Lux Hammam Spa Massage", duration=90, price=4500),
        Service(salon_id=s1.id, name="Caviar Deluxe Pedicure", duration=60, price=2200)
    ])
    
    # Services for Salon 2 (En Vogue Atelier)
    db.session.add_all([
        Service(salon_id=s2.id, name="Director's Cut & Styling", duration=60, price=3000),
        Service(salon_id=s2.id, name="Moroccan Argan Therapy", duration=120, price=4800),
        Service(salon_id=s2.id, name="HydraFacial Elite", duration=75, price=6500),
        Service(salon_id=s2.id, name="Aromatherapy Deep Tissue", duration=90, price=4000),
        Service(salon_id=s2.id, name="Luxury Gel Manicure", duration=45, price=1800)
    ])
    
    # Services for Salon 3 (Aura Wellness & Styling)
    db.session.add_all([
        Service(salon_id=s3.id, name="Creative Haircut & Wash", duration=45, price=1500),
        Service(salon_id=s3.id, name="Keratin Intense Infusion", duration=150, price=6000),
        Service(salon_id=s3.id, name="Organic Botanical Facial", duration=60, price=3200),
        Service(salon_id=s3.id, name="Stress Relief Massage", duration=60, price=2800),
        Service(salon_id=s3.id, name="Chrome & Matte Nail Art", duration=60, price=1600)
    ])
    
    # Services for Salon 4 (Prism & Polish)
    db.session.add_all([
        Service(salon_id=s4.id, name="Premium Blow Dry & Styled Waves", duration=45, price=1200),
        Service(salon_id=s4.id, name="Collagen Booster Facial", duration=60, price=4000),
        Service(salon_id=s4.id, name="Hot Stone Body Massage", duration=75, price=3500),
        Service(salon_id=s4.id, name="Acrylic Nail Extensions", duration=90, price=2500),
        Service(salon_id=s4.id, name="Premium Paraffin Pedicure", duration=60, price=1500)
    ])
    
    # 4. Add Reviews
    db.session.add_all([
        Review(user_id=customer.id, salon_id=s1.id, rating=5, comment="Absolutely top-notch! The Royal Signature Haircut was incredible. The stylists understand luxury, and the gold-trimmed decor makes you feel like royalty."),
        Review(user_id=customer.id, salon_id=s2.id, rating=5, comment="En Vogue Atelier is the best in Bangalore. Loved the HydraFacial Elite, my skin is glowing. Extremely professional staff and private rooms."),
        Review(user_id=customer.id, salon_id=s3.id, rating=4, comment="Very peaceful ambiance and beautiful glass interiors. The Keratin treatment did wonders to my frizzy hair. Highly recommend!"),
        Review(user_id=customer.id, salon_id=s4.id, rating=4, comment="Lovely nail art work. A bit busy on weekends, but the wait was worth it. Will visit again.")
    ])
    
    db.session.commit()
    print("Database successfully seeded.")
