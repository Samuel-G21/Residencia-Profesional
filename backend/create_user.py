from app import create_app
from app.models import db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    if not User.query.filter_by(username='admin').first():
        hashed = generate_password_hash('admin')
        user = User(username='admin', password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        print("Admin user created")
    else:
        print("Admin user already exists")
