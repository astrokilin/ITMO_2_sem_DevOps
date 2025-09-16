import React from "react";
const API_URL = "http://localhost:8000/api/notes";

function App() {
  const [notes, setNotes] = React.useState([]);
  const [title, setTitle] = React.useState("");
  const [content, setContent] = React.useState("");
  const [sendToTelegram, setSendToTelegram] = React.useState(false);

  // загрузка заметок
  React.useEffect(() => {
    fetch(API_URL)
      .then((res) => res.json())
      .then(setNotes)
      .catch(console.error);
  }, []);

  // создание заметки
  const handleCreate = async (e) => {
    e.preventDefault();
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content, send_to_telegram: sendToTelegram }),
    });
    const newNote = await res.json();
    setNotes([...notes, newNote]);
    setTitle("");
    setContent("");
    setSendToTelegram(false);
  };

  // обновление заметки
  const handleUpdate = async (id, updated) => {
    const res = await fetch(`${API_URL}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated),
    });
    const data = await res.json();
    setNotes(notes.map((n) => (n._id === id ? data : n)));
  };

  // удаление заметки
  const handleDelete = async (id) => {
    await fetch(`${API_URL}/${id}`, { method: "DELETE" });
    setNotes(notes.filter((n) => n._id !== id));
  };

  return (
    <div>
      <h1>Заметки</h1>

      {/* форма создания */}
      <form onSubmit={handleCreate}>
        <input
          className="note-title"
          type="text"
          placeholder="Заголовок"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <br />
        <textarea
          className="note-content"
          placeholder="Содержание"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
        <br />
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "15px",
            marginTop: "10px",
          }}
        >
          <label style={{ display: "flex", alignItems: "center", gap: "5px" }}>
            <input
              type="checkbox"
              checked={sendToTelegram}
              onChange={(e) => setSendToTelegram(e.target.checked)}
            />
            Сохранить в Telegram
          </label>
          <button type="submit">Создать</button>
        </div>
      </form>

      <hr />

      {/* список заметок */}
      {notes.map((note) => (
        <Note
          key={note._id}
          note={note}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}

function Note({ note, onUpdate, onDelete }) {
  const [isEditing, setIsEditing] = React.useState(false);
  const [title, setTitle] = React.useState(note.title);
  const [content, setContent] = React.useState(note.content);

  const handleSave = () => {
    onUpdate(note._id, { title, content });
    setIsEditing(false);
  };

  return (
    <div className="note">
      {isEditing ? (
        <>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="note-title"
            style={{ width: "100%", marginBottom: "10px" }}
          />
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="note-content"
            style={{ width: "100%", height: "60px" }}
          />
          <br />
          <button onClick={handleSave}>Сохранить</button>
          <button onClick={() => setIsEditing(false)}>Отмена</button>
        </>
      ) : (
        <>
          <div className="note-title">{note.title}</div>
          <div className="note-content">{note.content}</div>
          <div
            style={{
              display: "flex",
              gap: "10px",
              justifyContent: "flex-start",
              marginTop: "5px",
            }}
          >
            <button onClick={() => setIsEditing(true)}>Редактировать</button>
            <button onClick={() => onDelete(note._id)}>Удалить</button>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
