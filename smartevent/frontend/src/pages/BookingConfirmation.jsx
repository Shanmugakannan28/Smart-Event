import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { errMsg, fmtDate, money } from "../api";
import TicketCard from "../components/TicketCard.jsx";

export default function BookingConfirmation() {
  const { bookingId } = useParams();
  const [booking, setBooking] = useState(null);
  const [ticket, setTicket] = useState(null);
  const [payment, setPayment] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const b = (await api.get(`/bookings/${bookingId}`)).data;
        setBooking(b);
        if (b.booking_status === "CONFIRMED") {
          setTicket((await api.get("/tickets", { params: { booking_id: bookingId } })).data[0] || null);
          const pays = (await api.get("/payments")).data.filter((p) => p.booking_id === b.id && p.status === "SUCCESS");
          setPayment(pays[0] || null);
        }
      } catch (e) { setErr(errMsg(e)); }
    })();
  }, [bookingId]);

  if (err) return <p className="error">{err}</p>;
  if (!booking) return <p className="muted">Loading…</p>;

  if (booking.booking_status !== "CONFIRMED")
    return (
      <div className="card form narrow">
        <h2>Booking not confirmed</h2>
        <p className="muted">This booking is {booking.booking_status.toLowerCase()}.</p>
        {booking.booking_status === "PENDING" && <Link className="btn" to={`/payment/${booking.id}`}>Complete payment</Link>}
      </div>
    );

  return (
    <div className="confirm">
      <div className="success-banner">
        <h1>Payment received. You're going!</h1>
        <p>Booking #{booking.id} for {booking.event.title} is confirmed.</p>
      </div>
      <div className="card receipt">
        <p className="line"><span>Event date</span><span>{fmtDate(booking.event.event_date)}</span></p>
        <p className="line"><span>Tickets</span><span>{booking.ticket_quantity}</span></p>
        <p className="line"><span>Amount paid</span><strong>{money(booking.total_price)}</strong></p>
        {payment && <p className="line"><span>Payment ref</span><span className="code-sm">{payment.transaction_id}</span></p>}
        {payment && <p className="line"><span>Method</span><span>{payment.method}{payment.card_last4 ? ` ending ${payment.card_last4}` : ""}</span></p>}
      </div>
      {ticket && <TicketCard ticket={ticket} />}
      <div className="actions">
        <Link className="btn" to="/tickets">View all tickets</Link>
        <Link className="btn btn-ghost" to="/bookings">Booking history</Link>
      </div>
    </div>
  );
}
