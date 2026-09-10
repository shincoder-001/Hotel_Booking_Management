function validateBookingForm() {

    // Get values
    const name = document.getElementById('name').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const checkin = document.getElementById('checkin').value;
    const checkout = document.getElementById('checkout').value;
    const guests = document.querySelector('input[name="guests"]').value;

    // Name validation
    if (name.length < 3) {
        alert("Name must contain at least 3 characters.");
        return false;
    }

    // Phone validation
    const phonePattern = /^[0-9]{10}$/;

    if (!phonePattern.test(phone)) {
        alert("Please enter a valid 10-digit phone number.");
        return false;
    }

    // Guests validation
    if (guests < 1) {
        alert("Number of guests must be at least 1.");
        return false;
    }

    // Check-in date
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const checkinDate = new Date(checkin);
    const checkoutDate = new Date(checkout);

    if (checkinDate < today) {
        alert("Check-in date cannot be in the past.");
        return false;
    }

    // Check-out must be after check-in
    if (checkoutDate <= checkinDate) {
        alert("Check-out date must be after check-in date.");
        return false;
    }

    return true;
}