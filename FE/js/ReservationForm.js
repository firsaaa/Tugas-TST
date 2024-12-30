import React, { useState } from 'react';

function ReservationForm() {
    const [userName, setUserName] = useState('');
    const [seatNumber, setSeatNumber] = useState('');
    const [reservationDate, setReservationDate] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();

        const response = await fetch("http://localhost:8000/api/secure/reservations", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-Key": "your_api_key_here",
            },
            body: JSON.stringify({
                user_name: userName,
                seat_number: seatNumber,
                reservation_date: reservationDate,
            }),
        });

        if (response.ok) {
            alert("Reservation Successful!");
            setUserName('');
            setSeatNumber('');
            setReservationDate('');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <label>
                Name:
                <input type="text" value={userName} onChange={(e) => setUserName(e.target.value)} required />
            </label>
            <label>
                Seat Number:
                <input type="text" value={seatNumber} onChange={(e) => setSeatNumber(e.target.value)} required />
            </label>
            <label>
                Reservation Date:
                <input type="date" value={reservationDate} onChange={(e) => setReservationDate(e.target.value)} required />
            </label>
            <button type="submit">Reserve</button>
        </form>
    );
}

export default ReservationForm;
