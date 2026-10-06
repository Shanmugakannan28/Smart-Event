import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { errMsg } from "../api";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    try { await login(email, password); navigate(location.state?.from || "/", { replace: true }); }
    catch (ex) { setErr(errMsg(ex)); }
    finally { setBusy(false); }
  };

  return (
    <form className="card form narrow" onSubmit={submit}>
      <h2>Log in</h2>
      <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" /></label>
      <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" /></label>
      {err && <p className="error">{err}</p>}
      <button className="btn" disabled={busy}>{busy ? "Logging in…" : "Log in"}</button>
      <p className="muted small">New here? <Link to="/register">Create an account</Link></p>
    </form>
  );
}
