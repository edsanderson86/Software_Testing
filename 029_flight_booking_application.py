# flight_booking.py
# Run with: python flight_booking.py

import sqlite3
from pathlib import Path

DB_PATH = Path("flights.db")


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def setup():
    with connect() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                departure TEXT NOT NULL,
                seats INTEGER NOT NULL CHECK (seats >= 0)
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                flight_id INTEGER NOT NULL,
                passenger_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',
                FOREIGN KEY (flight_id) REFERENCES flights(id)
            );
        """)

        count = connection.execute(
            "SELECT COUNT(*) FROM flights"
        ).fetchone()[0]

        if count == 0:
            connection.executemany(
                """
                INSERT INTO flights
                    (origin, destination, departure, seats)
                VALUES (?, ?, ?, ?)
                """,
                [
                    ("London", "Paris", "2026-10-15 09:00", 3),
                    ("London", "Rome", "2026-10-16 12:30", 2),
                    ("Paris", "London", "2026-10-18 18:00", 4),
                ],
            )


def search_flights(origin, destination):
    with connect() as connection:
        return connection.execute(
            """
            SELECT id, origin, destination, departure, seats
            FROM flights
            WHERE LOWER(origin) = LOWER(?)
              AND LOWER(destination) = LOWER(?)
            ORDER BY departure
            """,
            (origin.strip(), destination.strip()),
        ).fetchall()


def book_flight(flight_id, passenger_name):
    passenger_name = passenger_name.strip()
    if not passenger_name:
        raise ValueError("Passenger name is required")

    with connect() as connection:
        updated = connection.execute(
            """
            UPDATE flights
            SET seats = seats - 1
            WHERE id = ? AND seats > 0
            """,
            (flight_id,),
        )

        if updated.rowcount != 1:
            raise ValueError("Flight not found or no seats available")

        cursor = connection.execute(
            """
            INSERT INTO bookings (flight_id, passenger_name)
            VALUES (?, ?)
            """,
            (flight_id, passenger_name),
        )
        return cursor.lastrowid


def cancel_booking(booking_id):
    with connect() as connection:
        booking = connection.execute(
            """
            SELECT flight_id
            FROM bookings
            WHERE id = ? AND status = 'confirmed'
            """,
            (booking_id,),
        ).fetchone()

        if booking is None:
            raise ValueError("Confirmed booking not found")

        connection.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ?",
            (booking_id,),
        )
        connection.execute(
            "UPDATE flights SET seats = seats + 1 WHERE id = ?",
            (booking["flight_id"],),
        )


def show_bookings():
    with connect() as connection:
        return connection.execute(
            """
            SELECT bookings.id, bookings.passenger_name,
                   bookings.status, flights.origin,
                   flights.destination, flights.departure
            FROM bookings
            JOIN flights ON flights.id = bookings.flight_id
            ORDER BY bookings.id
            """
        ).fetchall()


def main():
    setup()

    while True:
        print("\nFLIGHT BOOKING")
        print("1. Search flights")
        print("2. Book a flight")
        print("3. View bookings")
        print("4. Cancel a booking")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                origin = input("From: ")
                destination = input("To: ")
                flights = search_flights(origin, destination)

                if not flights:
                    print("No matching flights.")
                for flight in flights:
                    print(
                        f"{flight['id']}: {flight['origin']} -> "
                        f"{flight['destination']} | {flight['departure']} | "
                        f"{flight['seats']} seats left"
                    )

            elif choice == "2":
                flight_id = int(input("Flight ID: "))
                passenger = input("Passenger name: ")
                booking_id = book_flight(flight_id, passenger)
                print(f"Booking confirmed. Reference: {booking_id}")

            elif choice == "3":
                bookings = show_bookings()
                if not bookings:
                    print("No bookings yet.")
                for booking in bookings:
                    print(
                        f"{booking['id']}: {booking['passenger_name']} | "
                        f"{booking['origin']} -> {booking['destination']} | "
                        f"{booking['departure']} | {booking['status']}"
                    )

            elif choice == "4":
                booking_id = int(input("Booking reference: "))
                cancel_booking(booking_id)
                print("Booking cancelled.")

            elif choice == "5":
                print("Goodbye.")
                break

            else:
                print("Choose a number from 1 to 5.")

        except ValueError as error:
            print("Error:", error)


if __name__ == "__main__":
    main()