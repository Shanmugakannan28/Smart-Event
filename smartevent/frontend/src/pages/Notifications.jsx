import { useEffect, useState } from "react";
import api, { errMsg, fmtDate } from "../api";

export default function Notifications() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.get("/notifications").then((r) => setItems(r.data)).catch((e) => setErr(errMsg(e))).finally(() => setLoading(false));
  }, []);

  const markRead = async (n) => {
    if (n.is_read) return;
    await api.patch(`/notifications/${n.id}/read`);
    setItems((l) => l.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)));
  };
  const readAll = async () => {
    await api.patch("/notifications/read-all");
    setItems((l) => l.map((x) => ({ ...x, is_read: true })));
  };

  if (loading) return <p className="muted">Loading notifications…</p>;
  return (
    <>
      <div className="head-row">
        <h1>Notifications</h1>
        {items.some((n) => !n.is_read) && <button className="btn btn-ghost" onClick={readAll}>Mark all as read</button>}
      </div>
      {err && <p className="error">{err}</p>}
      {items.length === 0 ? <p className="muted">No notifications yet.</p> : (
        <div className="list">
          {items.map((n) => (
            <div key={n.id} className={`card notif-row ${n.is_read ? "" : "unread"}`} onClick={() => markRead(n)}>
              <span className={`tag tag-type inline`}>{n.type.toLowerCase()}</span>
              <div className="grow">
                <strong>{n.title}</strong>
                <p className="muted small">{n.message}</p>
              </div>
              <span className="muted tiny">{fmtDate(n.created_at)}</span>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
