import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errMsg, fmtDate, money } from "../api";

export default function PaymentHistory() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.get("/payments").then((r) => setRows(r.data)).catch((e) => setErr(errMsg(e))).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading payments…</p>;
  return (
    <>
      <h1>Payment history</h1>
      {err && <p className="error">{err}</p>}
      {rows.length === 0 ? <p className="muted">No payments yet. <Link to="/">Browse events</Link></p> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Date</th><th>Booking</th><th>Method</th><th>Amount</th><th>Status</th><th>Reference</th></tr></thead>
            <tbody>
              {rows.map((p) => (
                <tr key={p.id}>
                  <td>{fmtDate(p.created_at)}</td>
                  <td>#{p.booking_id}</td>
                  <td>{p.method}{p.card_last4 ? ` ····${p.card_last4}` : ""}</td>
                  <td>{money(p.amount)}</td>
                  <td>
                    <span className={`status status-${p.status.toLowerCase()}`}>{p.status.toLowerCase()}</span>
                    {p.failure_reason && <div className="muted tiny">{p.failure_reason}</div>}
                    {p.refunded_at && <div className="muted tiny">Refunded {fmtDate(p.refunded_at)}</div>}
                  </td>
                  <td className="code-sm">{p.transaction_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
