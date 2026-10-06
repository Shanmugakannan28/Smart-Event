import { Link } from "react-router-dom";
import { fmtDate, imgUrl, money, toDate } from "../api";

export default function EventCard({ event }) {
  const soldOut = event.available_tickets <= 0;
  const low = !soldOut && event.available_tickets <= 20;
  const d = toDate(event.event_date);
  return (
    <Link to={`/events/${event.id}`} className="card event-card">
      <div className="thumb">
        <img src={imgUrl(event.banner_image)} alt={event.title} loading="lazy" />
        <div className="date-badge" aria-hidden="true">
          <strong>{d.getDate()}</strong>
          <span>{d.toLocaleString("en-IN", { month: "short" })}</span>
        </div>
        <span className={`tag tag-${event.category.toLowerCase()}`}>{event.category}</span>
        {soldOut && <span className="soldout">Sold out</span>}
        {low && <span className="soldout low">Only {event.available_tickets} left</span>}
      </div>
      <div className="card-body">
        <h3>{event.title}</h3>
        <p className="muted small">{event.location}</p>
        <p className="muted small">{fmtDate(event.event_date)}</p>
        <p className="price">{event.ticket_price > 0 ? money(event.ticket_price) : "Free"}</p>
      </div>
    </Link>
  );
}
