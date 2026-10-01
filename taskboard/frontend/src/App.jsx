import { useAuth } from "./AuthContext";
import AuthPage from "./AuthPage";
import Board from "./Board";

export default function App() {
  const { user, loading } = useAuth();
  if (loading) return <p className="center-note">Loading your board…</p>;
  return user ? <Board /> : <AuthPage />;
}
