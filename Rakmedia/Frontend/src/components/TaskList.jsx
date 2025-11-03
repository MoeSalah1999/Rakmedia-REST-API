export default function TaskList({ tasks }) {
  const completed = tasks.filter(t => t.completed);
  const pending = tasks.filter(t => !t.completed);

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div>
        <h3 className="font-semibold text-green-600 mb-2">Completed</h3>
        <ul className="bg-green-50 p-3 rounded-lg shadow">
          {completed.length === 0 ? <li>No completed tasks</li> :
            completed.map(task => <li key={task.id}>✔ {task.title}</li>)}
        </ul>
      </div>

      <div>
        <h3 className="font-semibold text-red-600 mb-2">Pending</h3>
        <ul className="bg-red-50 p-3 rounded-lg shadow">
          {pending.length === 0 ? <li>No pending tasks</li> :
            pending.map(task => <li key={task.id}>⏳ {task.title}</li>)}
        </ul>
      </div>
    </div>
  );
}