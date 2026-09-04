export default function ActionChecklist({ actions }) {
  return (
    <ol style={{ marginTop: 12 }}>
      {actions.map((a) => (
        <li key={a.step} style={{ textDecoration: a.completed ? "line-through" : "none" }}>
          {a.url ? <a href={a.url} target="_blank" rel="noreferrer">{a.title}</a> : a.title}
        </li>
      ))}
    </ol>
  );
}
