from datetime import datetime
from app import create_app
from models import User, Trip, TripGuest, db

app = create_app()

# Sample data to populate the database
users = [
    User(username="arush_shah", first_name="Arush", last_name="Shah", 
         email="arushshah1@gmail.com", password="password123"),
    User(username="harrisonRox", first_name="Harrison", last_name="Hur", 
         email="hhur@yahoo.com", password="japan4life")
]

trips = [
    {
        "name": "Spain 2024",
        "host_username": "arush_shah",
        "start_date": datetime(2024, 10, 10),
        "end_date": datetime(2024, 10, 15)
    },
    {
        "name": "Weekend in Vegas",
        "host_username": "harrisonRox",
        "start_date": datetime(2025, 1, 12),
        "end_date": datetime(2025, 1, 15)
    }
]

trip_guests = [
    {"trip_name": "Spain 2024", "guest_username": "harrisonRox", "is_host": False},
    {"trip_name": "Weekend in Vegas", "guest_username": "arush_shah", "is_host": False}
]

def seed_data():
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        print(f"Seeding database at: {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Add users to the session
        db.session.bulk_save_objects(users)
        db.session.flush()  # Flush to assign primary keys

        # Add trips with relationships
        for trip_data in trips:
            host = User.query.filter_by(username=trip_data["host_username"]).first()
            trip = Trip(
                name=trip_data["name"],
                host_username=host.username,  # Assign the username directly
                start_date=trip_data["start_date"],
                end_date=trip_data["end_date"]
            )
            db.session.add(trip)

        db.session.flush()  # Flush again to assign trip IDs

        # Add trip guests with relationships
        for guest_data in trip_guests:
            trip = Trip.query.filter_by(name=guest_data["trip_name"]).first()
            guest = User.query.filter_by(username=guest_data["guest_username"]).first()
            trip_guest = TripGuest(
                trip_id=trip.id,
                guest_username=guest.username,
                is_host=guest_data["is_host"]
            )
            db.session.add(trip_guest)

        db.session.commit()  # Commit all changes
        db.session.expunge_all()  # Clear session to avoid conflicts

        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
