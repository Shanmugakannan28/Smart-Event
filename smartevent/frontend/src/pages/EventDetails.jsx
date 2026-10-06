import { useEffect, useState } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import api, { errMsg, fmtDate, money, imgUrl } from "../api";
import { useAuth } from "../context/AuthContext.jsx";

export default function EventDetails() {
  const { id } = useParams();
  const { isAuthed } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [event, setEvent] = useState(null);
  const [qty, setQty] = useState(1);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.get(`/events/${id}`).then((r) => setEvent(r.data)).catch((e) => setErr(errMsg(e))).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className="muted">Loading event…</p>;
  if (!event) return <p className="error">{err || "Event not found"}</p>;

  const maxQty = Math.min(10, event.available_tickets);
  const soldOut = event.available_tickets <= 0;

  const book = async () => {
    if (!isAuthed) return navigate("/login", { state: { from: location.pathname } });
    setErr(""); setBusy(true);
    try {
      const { data } = await api.post("/bookings", { event_id: event.id, ticket_quantity: qty });
      navigate(`/payment/${data.id}`);
    } catch (e) { setErr(errMsg(e)); }
    finally { setBusy(false); }
  };

  return (
    <div className="detail">
      <img className="banner" src={imgUrl(event.banner_image)} alt={event.title} />
      <div className="detail-grid">
        <div>
          <span className={`tag tag-${event.category.toLowerCase()} inline`}>{event.category}</span>
          <h1>{event.title}</h1>
          <p className="muted">{fmtDate(event.event_date)} · {event.location}</p>
          <p className="desc">{event.description}</p>
        </div>
        <aside className="card booking-box">
          <p className="price big">{money(event.ticket_price)} <span className="muted small">per ticket</span></p>
          <p className="muted small">{soldOut ? "No tickets left" : `${event.available_tickets} tickets left`}</p>
          <label>Tickets
            <div className="qty">
              <button type="button" onClick={() => setQty(Math.max(1, qty - 1))} disabled={qty <= 1} aria-label="Fewer tickets">−</button>
              <span>{qty}</span>
              <button type="button" onClick={() => setQty(Math.min(maxQty, qty + 1))} disabled={qty >= maxQty} aria-label="More tickets">+</button>
            </div>
          </label>
          <p className="total"><span>Total</span><strong>{money(event.ticket_price * qty)}</strong></p>
          {err && <p className="error small">{err}</p>}
          <button className="btn block" onClick={book} disabled={soldOut || busy}>
            {soldOut ? "Sold out" : busy ? "Reserving…" : isAuthed ? "Book and pay" : "Log in to book"}
          </button>
          <p className="muted tiny">Tickets are held for 15 minutes while you pay.</p>
        </aside>
      </div>
    </div>
  );
}
