import { useEffect, useState } from "react";
import api, { errorMessage } from "./api";
import { useAuth } from "./AuthContext";

const COLUMNS = [
  { key: "todo", title: "To do", empty: "Nothing waiting. Add a task above." },
  { key: "doing", title: "In progress", empty: "Move a task here when you start it." },
  { key: "done", title: "Done", empty: "Finished tasks land here." },
];

export default function Board() {
  const { user, logout } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState("");
  const [draft, setDraft] = useState({ title: "", priority: "medium", due_date: "" });

  useEffect(() => {
    api.get("/tasks/").then((r) => setTasks(r.data)).catch((e) => setError(errorMessage(e)));
  }, []);

  const addTask = async (e) => {
    e.preventDefault();
    if (!draft.title.trim()) return;
    try {
      const { data } = await api.post("/tasks/", {
        ...draft,
        due_date: draft.due_date || null,
      });
      setTasks([data, ...tasks]);
      setDraft({ title: "", priority: "medium", due_date: "" });
      setError("");
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const move = async (task, status) => {
    try {
      const { data } = await api.patch(`/tasks/${task.id}/`, { status });
      setTasks(tasks.map((t) => (t.id === task.id ? data : t)));
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const remove = async (task) => {
    try {
      await api.delete(`/tasks/${task.id}/`);
      setTasks(tasks.filter((t) => t.id !== task.id));
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  return (
    <div className="shell">
      <header className="top">
        <h1 className="brand small">Taskboard</h1>
        <div className="who">
          <span>{user.username}</span>
          <button className="link" onClick={logout}>Sign out</button>
        </div>
      </header>

      <form className="add" onSubmit={addTask}>
        <input
          placeholder="What needs doing?"
          value={draft.title}
          onChange={(e) => setDraft({ ...draft, title: e.target.value })}
          maxLength={200}
          aria-label="Task title"
        />
        <select
          value={draft.priority}
          onChange={(e) => setDraft({ ...draft, priority: e.target.value })}
          aria-label="Priority"
        >
          <option value="low">Low priority</option>
          <option value="medium">Medium priority</option>
          <option value="high">High priority</option>
        </select>
        <input
          type="date"
          value={draft.due_date}
          onChange={(e) => setDraft({ ...draft, due_date: e.target.value })}
          aria-label="Due date"
        />
        <button className="primary">Add task</button>
      </form>

      {error && <p className="error" role="alert">{error}</p>}

      <div className="columns">
        {COLUMNS.map((col, i) => {
          const items = tasks.filter((t) => t.status === col.key);
          return (
            <section key={col.key} className="column">
              <h2>
                {col.title} <span className="count">{items.length}</span>
              </h2>
              {items.length === 0 && <p className="empty">{col.empty}</p>}
              {items.map((t) => (
                <article key={t.id} className={`card p-${t.priority}`}>
                  <p className="card-title">{t.title}</p>
                  {t.due_date && <p className="meta">Due {t.due_date}</p>}
                  <div className="actions">
                    {i > 0 && (
                      <button onClick={() => move(t, COLUMNS[i - 1].key)}>
                        Back to {COLUMNS[i - 1].title.toLowerCase()}
                      </button>
                    )}
                    {i < COLUMNS.length - 1 && (
                      <button onClick={() => move(t, COLUMNS[i + 1].key)}>
                        Move to {COLUMNS[i + 1].title.toLowerCase()}
                      </button>
                    )}
                    <button className="danger" onClick={() => remove(t)}>Delete</button>
                  </div>
                </article>
              ))}
            </section>
          );
        })}
      </div>
    </div>
  );
}
