import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import NotificationDropdown from "./NotificationDropdown.jsx";

export default function Navbar() {
  const { isAuthed, user, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <header className="navbar">
      <div className="container nav-inner">
        <Link to="/" className="brand">SmartEvent</Link>
        <nav className="nav-links">
          <NavLink to="/" end>Events</NavLink>
          {isAuthed && (
            <>
              <NavLink to="/bookings">Bookings</NavLink>
              <NavLink to="/payments">Payments</NavLink>
              <NavLink to="/tickets">Tickets</NavLink>
            </>
          )}
        </nav>
        <div className="nav-right">
          {isAuthed ? (
            <>
              <NotificationDropdown />
              <span className="muted hide-sm">{user?.username}</span>
              <button className="btn btn-ghost" onClick={() => { logout(); navigate("/login"); }}>Log out</button>
            </>
          ) : (
            <>
              <Link className="btn btn-ghost" to="/login">Log in</Link>
              <Link className="btn" to="/register">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
