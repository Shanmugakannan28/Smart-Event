import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errMsg } from "../api";
import TicketCard from "../components/TicketCard.jsx";

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.get("/tickets").then((r) => setTickets(r.data)).catch((e) => setErr(errMsg(e))).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading tickets…</p>;
  return (
    <>
      <h1>Your tickets</h1>
      {err && <p className="error">{err}</p>}
      {tickets.length === 0 ? <p className="muted">Tickets appear here after payment. <Link to="/">Browse events</Link></p>
        : <div className="list">{tickets.map((t) => <TicketCard key={t.id} ticket={t} />)}</div>}
    </>
  );
}
