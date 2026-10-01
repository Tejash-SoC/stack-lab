import { useState } from "react";
import { useAuth } from "./AuthContext";
import { errorMessage } from "./api";

export default function AuthPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(form.username, form.password);
      else await register(form.username, form.email, form.password);
    } catch (err) {
      setError(
        err.response?.status === 401
          ? "Wrong username or password."
          : errorMessage(err)
      );
    } finally {
      setBusy(false);
    }
  };

  const isLogin = mode === "login";

  return (
    <main className="auth">
      <h1 className="brand">Taskboard</h1>
      <p className="lede">Three columns, your tasks, nothing else.</p>

      <form onSubmit={submit} className="auth-form">
        <label>
          Username
          <input value={form.username} onChange={set("username")} required autoFocus />
        </label>
        {!isLogin && (
          <label>
            Email (optional)
            <input type="email" value={form.email} onChange={set("email")} />
          </label>
        )}
        <label>
          Password
          <input
            type="password"
            value={form.password}
            onChange={set("password")}
            minLength={isLogin ? undefined : 8}
            required
          />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="primary" disabled={busy}>
          {busy ? "Please wait…" : isLogin ? "Sign in" : "Create account"}
        </button>
      </form>

      <p className="switch">
        {isLogin ? "New here?" : "Already have an account?"}{" "}
        <button className="link" onClick={() => { setMode(isLogin ? "register" : "login"); setError(""); }}>
          {isLogin ? "Create an account" : "Sign in"}
        </button>
      </p>
    </main>
  );
}
