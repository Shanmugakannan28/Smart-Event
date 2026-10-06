import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { errMsg } from "../api";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [f, setF] = useState({ username: "", email: "", password: "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    try { await register(f.username, f.email, f.password); navigate("/"); }
    catch (ex) { setErr(errMsg(ex)); }
    finally { setBusy(false); }
  };

  return (
    <form className="card form narrow" onSubmit={submit}>
      <h2>Create your account</h2>
      <label>Username<input value={f.username} onChange={set("username")} required minLength={3} autoComplete="username" /></label>
      <label>Email<input type="email" value={f.email} onChange={set("email")} required autoComplete="email" /></label>
      <label>Password<input type="password" value={f.password} onChange={set("password")} required minLength={8} autoComplete="new-password" />
        <span className="muted tiny">At least 8 characters</span></label>
      {err && <p className="error">{err}</p>}
      <button className="btn" disabled={busy}>{busy ? "Creating account…" : "Create account"}</button>
      <p className="muted small">Already registered? <Link to="/login">Log in</Link></p>
    </form>
  );
}
