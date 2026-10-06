import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api, { errMsg, fmtDate, money, toDate, imgUrl } from "../api";

const METHODS = [
  { id: "CARD", label: "Card" },
  { id: "UPI", label: "UPI" },
  { id: "NETBANKING", label: "Net banking" },
  { id: "WALLET", label: "Wallet" },
];
const BANKS = ["State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank"];

const groupCard = (v) => v.replace(/\D/g, "").slice(0, 19).replace(/(.{4})/g, "$1 ").trim();
const fmtExpiry = (v) => {
  const d = v.replace(/\D/g, "").slice(0, 4);
  return d.length > 2 ? `${d.slice(0, 2)}/${d.slice(2)}` : d;
};

export default function Payment() {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [booking, setBooking] = useState(null);
  const [method, setMethod] = useState("CARD");
  const [f, setF] = useState({ card_name: "", card_number: "", card_expiry: "", card_cvv: "", upi_id: "", bank: BANKS[0] });
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [left, setLeft] = useState(null);

  useEffect(() => {
    api.get(`/bookings/${bookingId}`)
      .then((r) => {
        if (r.data.booking_status === "CONFIRMED") navigate(`/booking-confirmation/${bookingId}`, { replace: true });
        else setBooking(r.data);
      })
      .catch((e) => setErr(errMsg(e)))
      .finally(() => setLoading(false));
  }, [bookingId, navigate]);

  // Countdown for the ticket hold
  useEffect(() => {
    if (!booking?.expires_at) return;
    const tick = () => setLeft(Math.max(0, Math.floor((toDate(booking.expires_at) - Date.now()) / 1000)));
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, [booking]);

  if (loading) return <p className="muted">Loading checkout…</p>;
  if (!booking) return <p className="error">{err || "Booking not found"}</p>;
  if (booking.booking_status === "CANCELLED" || left === 0)
    return (
      <div className="card form narrow">
        <h2>This booking has expired</h2>
        <p className="muted">The tickets were released. Pick the event again to book.</p>
        <button className="btn" onClick={() => navigate(`/events/${booking.event_id}`)}>Back to event</button>
      </div>
    );

  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const mm = left != null ? `${String(Math.floor(left / 60)).padStart(2, "0")}:${String(left % 60).padStart(2, "0")}` : "";

  const pay = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    const body = { booking_id: booking.id, method };
    if (method === "CARD") Object.assign(body, { card_name: f.card_name, card_number: f.card_number, card_expiry: f.card_expiry, card_cvv: f.card_cvv });
    if (method === "UPI") body.upi_id = f.upi_id;
    if (method === "NETBANKING") body.bank = f.bank;
    try {
      const { data } = await api.post("/payments/pay", body);
      if (data.payment.status === "SUCCESS") navigate(`/booking-confirmation/${booking.id}`, { replace: true });
      else setErr(`${data.message}. Try again or use another method.`);
    } catch (ex) { setErr(errMsg(ex)); }
    finally { setBusy(false); }
  };

  const ev = booking.event;
  return (
    <div className="checkout">
      <form className="card form" onSubmit={pay}>
        <h2>Pay for your tickets</h2>
        <div className="tabs" role="tablist">
          {METHODS.map((m) => (
            <button type="button" role="tab" aria-selected={method === m.id} key={m.id}
              className={`tab ${method === m.id ? "active" : ""}`} onClick={() => { setMethod(m.id); setErr(""); }}>{m.label}</button>
          ))}
        </div>

        {method === "CARD" && (
          <>
            <label>Name on card<input value={f.card_name} onChange={set("card_name")} required autoComplete="cc-name" /></label>
            <label>Card number
              <input inputMode="numeric" placeholder="1234 5678 9012 3456" value={f.card_number}
                onChange={(e) => setF({ ...f, card_number: groupCard(e.target.value) })} required autoComplete="cc-number" /></label>
            <div className="row">
              <label>Expiry<input placeholder="MM/YY" value={f.card_expiry} onChange={(e) => setF({ ...f, card_expiry: fmtExpiry(e.target.value) })} required autoComplete="cc-exp" /></label>
              <label>CVV<input type="password" inputMode="numeric" maxLength={4} value={f.card_cvv}
                onChange={(e) => setF({ ...f, card_cvv: e.target.value.replace(/\D/g, "") })} required autoComplete="cc-csc" /></label>
            </div>
          </>
        )}
        {method === "UPI" && (
          <label>UPI ID<input placeholder="name@bank" value={f.upi_id} onChange={set("upi_id")} required /></label>
        )}
        {method === "NETBANKING" && (
          <label>Bank<select value={f.bank} onChange={set("bank")}>{BANKS.map((b) => <option key={b}>{b}</option>)}</select></label>
        )}
        {method === "WALLET" && <p className="muted">You'll be charged from your SmartEvent wallet balance.</p>}

        {err && <p className="error" role="alert">{err}</p>}
        <button className="btn" disabled={busy}>{busy ? "Processing payment…" : `Pay ${money(booking.total_price)}`}</button>
        <p className="muted tiny">Demo gateway. Test card 4111 1111 1111 1111 succeeds; a card ending 0002 is declined. Card numbers and CVV are never stored.</p>
      </form>

      <aside className="card summary">
        <h3>Order summary</h3>
        <img src={imgUrl(ev.banner_image)} alt="" />
        <p><strong>{ev.title}</strong></p>
        <p className="muted small">{fmtDate(ev.event_date)}<br />{ev.location}</p>
        <p className="line"><span>{booking.ticket_quantity} × {money(ev.ticket_price)}</span><span>{money(booking.total_price)}</span></p>
        <p className="total"><span>Total</span><strong>{money(booking.total_price)}</strong></p>
        {mm && <p className={`hold ${left < 120 ? "urgent" : ""}`}>Tickets held for {mm}</p>}
      </aside>
    </div>
  );
}
