import { useEffect, useState } from "react";
import api, { errMsg, imgUrl } from "../api";
import EventCard from "../components/EventCard.jsx";

const CATEGORIES = ["All", "Music", "Tech", "Sports", "Business"];

export default function Home() {
  const [events, setEvents] = useState([]);
  const [category, setCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    setLoading(true);
    const t = setTimeout(async () => {
      try {
        const params = {};
        if (category !== "All") params.category = category;
        if (search.trim()) params.search = search.trim();
        setEvents((await api.get("/events", { params })).data);
        setErr("");
      } catch (e) { setErr(errMsg(e)); }
      finally { setLoading(false); }
    }, 300); // debounce typing
    return () => clearTimeout(t);
  }, [category, search]);

  return (
    <>
      <section className="hero" style={{ backgroundImage: `url(${imgUrl("/static/banners/hero.svg")})` }}>
        <div className="hero-inner">
          <h1>Find your next event</h1>
          <p>Concerts, tech summits, matches and business meetups. Book in a minute and get a QR ticket on your phone.</p>
          <input className="search hero-search" placeholder="Search events by title" aria-label="Search events by title"
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </section>
      <div className="toolbar">
        <div className="chips" role="group" aria-label="Filter by category">
          {CATEGORIES.map((c) => (
            <button key={c} className={`chip ${category === c ? "active" : ""}`} aria-pressed={category === c} onClick={() => setCategory(c)}>{c}</button>
          ))}
        </div>
      </div>
      {err && <p className="error">{err}</p>}
      {loading ? <p className="muted">Loading events…</p>
        : events.length === 0 ? <p className="muted">No events match. Try another category or search term.</p>
        : <div className="grid">{events.map((e) => <EventCard key={e.id} event={e} />)}</div>}
    </>
  );
}
