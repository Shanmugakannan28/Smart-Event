import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errMsg, fmtDate, money, imgUrl } from "../api";

export default function BookingHistory() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = () => api.get("/bookings").then((r) => setRows(r.data)).catch((e) => setErr(errMsg(e))).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const cancel = async (b) => {
    const msg = b.booking_status === "CONFIRMED"
      ? `Cancel this booking? ${money(b.total_price)} will be refunded.` : "Cancel this booking?";
    if (!window.confirm(msg)) return;
    setBusyId(b.id); setErr("");
    try { await api.post(`/bookings/${b.id}/cancel`); await load(); }
    catch (e) { setErr(errMsg(e)); }
    finally { setBusyId(null); }
  };

  if (loading) return <p className="muted">Loading bookings…</p>;
  return (
    <>
      <h1>Your bookings</h1>
      {err && <p className="error">{err}</p>}
      {rows.length === 0 ? <p className="muted">No bookings yet. <Link to="/">Browse events</Link></p> : (
        <div className="list">
          {rows.map((b) => (
            <div key={b.id} className="card row-card">
              <img src={imgUrl(b.event.banner_image)} alt="" />
              <div className="grow">
                <h3>{b.event.title}</h3>
                <p className="muted small">{fmtDate(b.event.event_date)} · {b.ticket_quantity} ticket{b.ticket_quantity > 1 ? "s" : ""}</p>
                <p><strong>{money(b.total_price)}</strong> <span className={`status status-${b.booking_status.toLowerCase()}`}>{b.booking_status.toLowerCase()}</span></p>
              </div>
              <div className="row-actions">
                {b.booking_status === "PENDING" && <Link className="btn" to={`/payment/${b.id}`}>Pay now</Link>}
                {b.booking_status === "CONFIRMED" && <Link className="btn btn-ghost" to={`/booking-confirmation/${b.id}`}>View ticket</Link>}
                {b.booking_status !== "CANCELLED" && (
                  <button className="btn btn-danger" disabled={busyId === b.id} onClick={() => cancel(b)}>
                    {busyId === b.id ? "Cancelling…" : b.booking_status === "CONFIRMED" ? "Cancel and refund" : "Cancel"}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
