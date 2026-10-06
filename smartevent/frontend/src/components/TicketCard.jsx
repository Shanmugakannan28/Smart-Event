import { useState } from "react";
import api, { fmtDate, errMsg } from "../api";

export default function TicketCard({ ticket }) {
  const [err, setErr] = useState("");
  const { booking } = ticket;
  const ev = booking.event;

  const download = async () => {
    try {
      const res = await api.get(`/tickets/${ticket.id}/download`, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${ticket.ticket_code}.png`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) { setErr(errMsg(e, "Could not download the ticket")); }
  };

  return (
    <div className={`card ticket ${ticket.status !== "VALID" ? "ticket-dim" : ""}`}>
      <div className="ticket-info">
        <span className={`status status-${ticket.status.toLowerCase()}`}>{ticket.status === "VALID" ? "Valid" : ticket.status === "USED" ? "Used" : "Cancelled"}</span>
        <h3>{ev.title}</h3>
        <p className="muted small">{fmtDate(ev.event_date)}</p>
        <p className="muted small">{ev.location}</p>
        <p className="small">{booking.ticket_quantity} ticket{booking.ticket_quantity > 1 ? "s" : ""}</p>
        <p className="code">{ticket.ticket_code}</p>
        <button className="btn btn-ghost" onClick={download}>Download QR</button>
        {err && <p className="error small">{err}</p>}
      </div>
      <div className="ticket-qr">
        <img src={ticket.qr_code_url} alt={`QR code for ticket ${ticket.ticket_code}`} />
      </div>
    </div>
  );
}
