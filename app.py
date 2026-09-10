from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

app.secret_key = "royal_palace_secret_key"

from database import get_connection


# =========================
# HOME
# =========================

@app.route('/')
def home():
    return render_template('index.html')


# =========================
# ABOUT
# =========================

@app.route('/about')
def about():
    return render_template('about.html')


# =========================
# ROOMS
# =========================

@app.route('/rooms')
def rooms():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rooms")
    room_list = cursor.fetchall()

    conn.close()

    return render_template(
        'rooms.html',
        rooms=room_list
    )


# =========================
# BOOKING
# =========================

@app.route('/booking', methods=['GET', 'POST'])
def booking():

    message = None

    conn = get_connection()
    cursor = conn.cursor()

    # Get rooms from database
    cursor.execute(
        "SELECT id, name, price FROM rooms"
    )

    rooms = cursor.fetchall()

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        room_type = request.form['room_type']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        guests = request.form['guests']

        # Check checkout date
        if checkout <= checkin:

            conn.close()

            return render_template(
                'booking.html',
                rooms=rooms,
                message="Check-out date must be after check-in date."
            )

        # Get room price
        cursor.execute(
            "SELECT price FROM rooms WHERE name = %s",
            (room_type,)
        )

        room = cursor.fetchone()

        if not room:

            conn.close()

            return render_template(
                'booking.html',
                rooms=rooms,
                message="Selected room does not exist."
            )

        price = float(room[0])

        # Check room availability
        cursor.execute("""
            SELECT id
            FROM bookings
            WHERE room_type = %s
            AND checkin < %s
            AND checkout > %s
        """, (
            room_type,
            checkout,
            checkin
        ))

        existing_booking = cursor.fetchone()

        if existing_booking:

            conn.close()

            return render_template(
                'booking.html',
                rooms=rooms,
                message="Sorry! This room is already booked for these dates."
            )

        # Calculate number of nights
        from datetime import datetime

        checkin_date = datetime.strptime(
            checkin,
            "%Y-%m-%d"
        )

        checkout_date = datetime.strptime(
            checkout,
            "%Y-%m-%d"
        )

        nights = (checkout_date - checkin_date).days

        # Calculate total amount
        total_amount = price * nights

        # Insert booking
        cursor.execute("""
            INSERT INTO bookings
            (
                name,
                email,
                phone,
                room_type,
                checkin,
                checkout,
                guests,
                total_amount
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            email,
            phone,
            room_type,
            checkin,
            checkout,
            guests,
            total_amount
        ))

        # Get newly created booking ID
        booking_id = cursor.lastrowid

        conn.commit()

        # Get complete booking
        cursor.execute(
            "SELECT * FROM bookings WHERE id = %s",
            (booking_id,)
        )

        booking_data = cursor.fetchone()

        conn.close()

        # Show confirmation page
        return render_template(
            'confirmation.html',
            booking=booking_data,
            nights=nights
        )

    conn.close()

    return render_template(
        'booking.html',
        rooms=rooms,
        message=message
    )


# =========================
# CONTACT
# =========================

@app.route('/contact', methods=['GET', 'POST'])
def contact():

    message = None

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        user_message = request.form['message']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO contacts
            (name, email, message)
            VALUES (%s, %s, %s)
        """, (
            name,
            email,
            user_message
        ))

        conn.commit()
        conn.close()

        message = "Your message has been sent!"

    return render_template(
        'contact.html',
        message=message
    )


# =========================
# ADMIN LOGIN
# =========================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    message = None

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # Simple admin credentials
        if username == "admin" and password == "1234":

            session['admin_logged_in'] = True

            return redirect('/admin')

        else:

            message = "Invalid username or password."

    return render_template(
        'admin_login.html',
        message=message
    )


# =========================
# ADMIN LOGOUT
# =========================

@app.route('/admin/logout')
def admin_logout():

    session.pop(
        'admin_logged_in',
        None
    )

    return redirect('/admin/login')


# =========================
# ADMIN DASHBOARD
# =========================

@app.route('/admin')
def admin():

    # Check admin login
    if 'admin_logged_in' not in session:

        return redirect('/admin/login')

    conn = get_connection()
    cursor = conn.cursor()

    # Get rooms
    cursor.execute(
        "SELECT * FROM rooms"
    )

    room_list = cursor.fetchall()

    # Get bookings
    cursor.execute(
        "SELECT * FROM bookings"
    )

    booking_list = cursor.fetchall()

    # Get contact messages
    cursor.execute(
        "SELECT * FROM contacts"
    )

    contact_list = cursor.fetchall()

    conn.close()

    return render_template(
        'admin.html',
        rooms=room_list,
        bookings=booking_list,
        contacts=contact_list
    )


# =========================
# ADD ROOM
# =========================

@app.route('/admin/add_room', methods=['POST'])
def add_room():

    name = request.form['name']
    price = request.form['price']
    description = request.form['description']
    image = request.form['image']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO rooms
        (name, price, description, image)
        VALUES (%s, %s, %s, %s)
    """, (
        name,
        price,
        description,
        image
    ))

    conn.commit()
    conn.close()

    return redirect('/admin')


# =========================
# DELETE ROOM
# =========================

@app.route('/admin/delete_room/<int:room_id>')
def delete_room(room_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM rooms WHERE id = %s",
        (room_id,)
    )

    conn.commit()
    conn.close()

    return redirect('/admin')


# =========================
# EDIT ROOM PAGE
# =========================

@app.route('/admin/edit_room/<int:room_id>')
def edit_room_page(room_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM rooms WHERE id = %s",
        (room_id,)
    )

    room = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_room.html',
        room=room
    )


# =========================
# EDIT ROOM
# =========================

@app.route('/admin/edit_room/<int:room_id>', methods=['POST'])
def edit_room(room_id):

    name = request.form['name']
    price = request.form['price']
    description = request.form['description']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE rooms
        SET name = %s,
            price = %s,
            description = %s
        WHERE id = %s
    """, (
        name,
        price,
        description,
        room_id
    ))

    conn.commit()
    conn.close()

    return redirect('/admin')


# =========================
# RUN APPLICATION
# =========================

if __name__ == '__main__':
    app.run(debug=True)