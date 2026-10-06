import { useEffect, useRef, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import api, { fmtDate } from "../api";

export default function NotificationDropdown() {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const ref = useRef(null);

  const loadCount = useCallback(async () => {
    try { setCount((await api.get("/notifications/unread-count")).data.count); } catch { /* ignore */ }
  }, []);
  const loadItems = useCallback(async () => {
    try { setItems((await api.get("/notifications")).data.slice(0, 6)); } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    loadCount();
    const t = setInterval(loadCount, 30000);
    return () => clearInterval(t);
  }, [loadCount]);

  useEffect(() => {
    const close = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const toggle = () => { if (!open) loadItems(); setOpen(!open); };
  const markRead = async (n) => {
    if (n.is_read) return;
    await api.patch(`/notifications/${n.id}/read`);
    setItems((l) => l.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)));
    setCount((c) => Math.max(0, c - 1));
  };
  const readAll = async () => {
    await api.patch("/notifications/read-all");
    setItems((l) => l.map((x) => ({ ...x, is_read: true })));
    setCount(0);
  };

  return (
    <div className="notif" ref={ref}>
      <button className="bell" onClick={toggle} aria-label={`Notifications, ${count} unread`}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <path d="M18 8a6 6 0 10-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 01-3.4 0" />
        </svg>
        {count > 0 && <span className="badge">{count > 9 ? "9+" : count}</span>}
      </button>
      {open && (
        <div className="dropdown">
          <div className="dropdown-head">
            <strong>Notifications</strong>
            {count > 0 && <button className="link" onClick={readAll}>Mark all as read</button>}
          </div>
          {items.length === 0 && <p className="muted pad">You're all caught up.</p>}
          {items.map((n) => (
            <div key={n.id} className={`notif-item ${n.is_read ? "" : "unread"}`} onClick={() => markRead(n)}>
              <div className="notif-title">{n.title}</div>
              <div className="muted small">{n.message}</div>
              <div className="muted tiny">{fmtDate(n.created_at)}</div>
            </div>
          ))}
          <Link to="/notifications" className="dropdown-foot" onClick={() => setOpen(false)}>View all notifications</Link>
        </div>
      )}
    </div>
  );
}
