// src/pages/ManagerDashboard.jsx
import { useState, useEffect } from "react";
import axiosClient from "../api/axiosClient";
import Sidebar from "../components/Sidebar";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronDownIcon,
  ChevronUpIcon,
  CheckCircleIcon,
  ClockIcon,
  PlusCircleIcon,
  TrashIcon,
  PaperClipIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/solid";

/* --- Tiny Tailwind toast system (no deps) --- */
function Toasts({ toasts }) {
  return (
    <div className="fixed top-6 right-6 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`max-w-sm w-full rounded-lg p-3 shadow-lg text-sm ${
            t.type === "success"
              ? "bg-green-50 border border-green-200"
              : "bg-red-50 border border-red-200"
          }`}
        >
          <div className="font-medium text-gray-800">{t.title}</div>
          {t.message && <div className="text-gray-600 mt-1">{t.message}</div>}
        </div>
      ))}
    </div>
  );
}

export default function ManagerDashboard() {
  const [employees, setEmployees] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [tasks, setTasks] = useState({});
  const [form, setForm] = useState({});
  const [fileInputs, setFileInputs] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  const addToast = (t) => {
    const id = Math.random().toString(36).slice(2, 9);
    setToasts((s) => [...s, { id, ...t }]);
    setTimeout(() => setToasts((s) => s.filter((x) => x.id !== id)), 4000);
  };

  const ensureArray = (v) => (Array.isArray(v) ? v : v ? [v] : []);
  const getTaskFiles = (t) => ensureArray(t?.files).filter(Boolean);
  const getFileName = (f) => {
    if (!f) return "file";
    if (typeof f.file === "string") return f.file.split("/").pop();
    return f.description || "file";
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const { data: employeesRes } = await axiosClient.get("/department-employees/");
        const employeesList = Array.isArray(employeesRes)
          ? employeesRes
          : employeesRes.results || [];
        setEmployees(employeesList);

        const { data: tasksRes } = await axiosClient.get("/manager-tasks/");
        const tasksList = Array.isArray(tasksRes)
          ? tasksRes
          : tasksRes.results || [];
        const grouped = {};
        for (const t of tasksList) {
          const k = t.assigned_to;
          if (!grouped[k]) grouped[k] = [];
          t.files = ensureArray(t.files);
          grouped[k].push(t);
        }
        setTasks(grouped);
      } catch {
        addToast({ title: "Error", message: "Failed to load data", type: "error" });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleExpand = (id) => setExpanded((prev) => (prev === id ? null : id));
  const handleChange = (empId, e) =>
    setForm((p) => ({
      ...p,
      [empId]: { ...p[empId], [e.target.name]: e.target.value },
    }));

  /* Handle tasks assignment */
  const handleAssign = async (empId) => {
    const f = form[empId] || {};
    if (!f.title || !f.due_date)
      return addToast({
        title: "Validation",
        message: "Title and due date required",
        type: "error",
      });

    setSaving(true);
    try {
      const payload = { ...f, assigned_to: empId };
      const { data: created } = await axiosClient.post("/manager-tasks/", payload);
      created.files = ensureArray(created.files);

      const input = fileInputs[`new-${empId}`];
      if (input?.file) {
        const fd = new FormData();
        fd.append("file", input.file);
        if (input.description) fd.append("description", input.description);
        await axiosClient.post(`/tasks/${created.id}/upload-file/`, fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }

      setTasks((p) => ({ ...p, [empId]: [created, ...(p[empId] || [])] }));
      setForm((p) => ({ ...p, [empId]: { title: "", description: "", due_date: "" } }));
      setFileInputs((p) => ({ ...p, [`new-${empId}`]: {} }));
      addToast({ title: "Task created", type: "success" });
    } catch {
      addToast({ title: "Error", message: "Failed to assign task", type: "error" });
    } finally {
      setSaving(false);
    }
  };

  /* Handles upload of task-related files */
  const handleFileUpload = async (taskId) => {
    const input = fileInputs[taskId];
    if (!input?.file)
      return addToast({ title: "No file", message: "Select a file", type: "error" });

    const fd = new FormData();
    fd.append("file", input.file);
    if (input.description) fd.append("description", input.description);

    try {
      await axiosClient.post(`/tasks/${taskId}/upload-file/`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setFileInputs((p) => ({ ...p, [taskId]: {} }));
      addToast({ title: "Uploaded", message: "File uploaded", type: "success" });
    } catch {
      addToast({ title: "Error", message: "Upload failed", type: "error" });
    }
  };

  /* Handles download of task-related files */
  const handleDownload = async (fileUrl, fileName) => {
    if (!fileUrl) {
      addToast({
        title: "No URL",
        message: "File URL is missing",
        type: "error",
      });
      return;
    }
    /* Some error handling */
    try {
      const response = await axiosClient.get(fileUrl, { responseType: "blob" });
      const blob = new Blob([response.data]);
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = fileName || "file";
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Error downloading file:", err);
      addToast({ title: "Error", message: "Download failed", type: "error" });
    }
  };

  /** Handles task-related file deletion */
  const handleDeleteFile = async (taskId, fileId, empId) => {
    if (!window.confirm("Delete this file?")) return;
    try {
      await axiosClient.delete(`/tasks/${taskId}/files/${fileId}/`);
      setTasks((prev) => ({
        ...prev,
        [empId]: prev[empId].map((t) =>
          t.id === taskId ? { ...t, files: t.files.filter((f) => f.id !== fileId) } : t
        ),
      }));
      addToast({ title: "Deleted", message: "File deleted", type: "success" });
    } catch {
      addToast({ title: "Error", message: "Delete failed", type: "error" });
    }
  };

  /** Handles task deletion */
  const handleDeleteTask = async (taskId, empId) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    try {
      await axiosClient.delete(`/tasks/${taskId}/`);
      setTasks((prev) => ({
        ...prev,
        [empId]: prev[empId].filter((t) => t.id !== taskId),
      }));
      addToast({ title: "Deleted", message: "Task deleted successfully", type: "success" });
    } catch {
      addToast({ title: "Error", message: "Failed to delete task", type: "error" });
    }
  };

  /** Handles the boolean-value button for completed and incompleted tasks */
  const handleToggleComplete = async (taskId, empId, currentState) => {
    try {
      const { data: updated } = await axiosClient.patch(`/tasks/${taskId}/`, {
        completed: !currentState,
      });

      setTasks((prev) => ({
        ...prev,
        [empId]: prev[empId].map((t) =>
          t.id === taskId ? { ...t, completed: updated.completed } : t
        ),
      }));

      /** Toast notification for task modifications */
      addToast({
        title: "Updated",
        message: updated.completed
          ? "Task marked as complete"
          : "Task marked as incomplete",
        type: "success",
      });
    } catch {
      addToast({ title: "Error", message: "Failed to update task", type: "error" });
    }
  };

  // ---  Filter employees based on search ---
  const filteredEmployees = employees.filter((emp) => {
    const term = searchTerm.toLowerCase();
    return (
      emp.first_name?.toLowerCase().includes(term) ||
      emp.last_name?.toLowerCase().includes(term) ||
      emp.employee_code?.toString().toLowerCase().includes(term)
    );
  });

  if (loading)
    return (
      <div className="flex">
        <Sidebar />
        <main className="flex-1 ml-60 bg-indigo-50 p-10">Loading...</main>
      </div>
    );

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 ml-60 bg-gradient-to-b from-indigo-50 to-white min-h-screen p-10">
        <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">My Employees</h1>

        {/*  Search Field */}
        <div className="max-w-md mx-auto mb-10">
          <input
            type="text"
            placeholder="Search employees by name or employee code..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full border border-gray-300 rounded-lg p-3 shadow-sm focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 outline-none"
          />
        </div>

        {/*  FIXED: Use filteredEmployees instead of employees */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredEmployees.map((emp) => (
            <motion.div
              key={emp.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-md border p-6 overflow-visible"
            >
              <div
                className="flex justify-between items-center cursor-pointer"
                onClick={() => handleExpand(emp.id)}
              >
                <div>
                  <h2 className="text-lg font-semibold">
                    {emp.first_name} {emp.last_name}
                  </h2>
                  <p className="text-sm text-gray-500">{emp.username}</p>
                </div>
                {expanded === emp.id ? (
                  <ChevronUpIcon className="h-6 w-6 text-indigo-600" />
                ) : (
                  <ChevronDownIcon className="h-6 w-6 text-indigo-600" />
                )}
              </div>
              
              {/** Section for assigning new tasks to employees */}
              <AnimatePresence>
                {expanded === emp.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-4 border-t border-gray-200 pt-4 space-y-4"
                  >
                    {/* Task title */}
                    <div className="flex flex-col gap-2">
                      <input
                        type="text"
                        name="title"
                        placeholder="Task title"
                        value={form[emp.id]?.title || ""}
                        onChange={(e) => handleChange(emp.id, e)}
                        className="border p-2 rounded"
                      />
                      {/** Task description */}
                      <textarea
                        name="description"
                        placeholder="Task description"
                        value={form[emp.id]?.description || ""}
                        onChange={(e) => handleChange(emp.id, e)}
                        className="border p-2 rounded"
                      />
                      {/** Task due-date (Deadline) */}
                      <input
                        type="date"
                        name="due_date"
                        value={form[emp.id]?.due_date || ""}
                        onChange={(e) => handleChange(emp.id, e)}
                        className="border p-2 rounded"
                      />

                      {/** Task-related file-upload field  */}
                      <div className="flex flex-wrap gap-2 items-center">
                        <input
                          type="file"
                          onChange={(e) =>
                            setFileInputs((p) => ({
                              ...p,
                              [`new-${emp.id}`]: {
                                ...p[`new-${emp.id}`],
                                file: e.target.files[0],
                              },
                            }))
                          }
                        />
                        <input
                          type="text"
                          placeholder="File description (optional)"
                          value={fileInputs[`new-${emp.id}`]?.description || ""}
                          onChange={(e) =>
                            setFileInputs((p) => ({
                              ...p,
                              [`new-${emp.id}`]: {
                                ...p[`new-${emp.id}`],
                                description: e.target.value,
                              },
                            }))
                          }
                          className="border p-2 rounded flex-1 min-w-[200px]"
                        />
                      </div>

                      {/** Calls the task-assignment function we created earlier */}
                      <button
                        onClick={() => handleAssign(emp.id)}
                        disabled={saving}
                        className={`bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 flex items-center justify-center gap-2 transition ${
                          saving && "opacity-60 cursor-not-allowed"
                        }`}
                      >
                        <PlusCircleIcon className="h-5 w-5" />
                        {saving ? "Assigning..." : "Assign Task"}
                      </button>
                    </div>

                    {/* Tasks List */}
                    {tasks[emp.id]?.length > 0 && (
                      <div className="space-y-3">
                        {tasks[emp.id].map((task) => (
                          <div
                            key={task.id}
                            className="bg-gray-50 border rounded-lg p-3 space-y-2"
                          >
                            <div className="flex justify-between items-center">
                              <div className="font-medium text-sm">{task.title}</div>

                              <div className="flex items-center gap-3">
                                {/* ✅ Completion toggle icon */}
                                <button
                                  onClick={() =>
                                    handleToggleComplete(task.id, emp.id, task.completed)
                                  }
                                  className={
                                    task.completed
                                      ? "text-green-500 hover:text-green-700"
                                      : "text-yellow-500 hover:text-yellow-600"
                                  }
                                  title={
                                    task.completed
                                      ? "Mark as incomplete"
                                      : "Mark as complete"
                                  }
                                >
                                  {task.completed ? (
                                    <CheckCircleIcon className="h-5 w-5" />
                                  ) : (
                                    <ClockIcon className="h-5 w-5" />
                                  )}
                                </button>

                                {/* 🗑 Delete button */}
                                <button
                                  onClick={() => handleDeleteTask(task.id, emp.id)}
                                  className="text-red-500 hover:text-red-700"
                                  title="Delete task"
                                >
                                  <TrashIcon className="h-5 w-5" />
                                </button>
                              </div>
                            </div>

                            {/* Upload + Files */}
                            <div className="flex flex-wrap gap-2 items-center">
                              <input
                                type="file"
                                onChange={(e) =>
                                  setFileInputs((p) => ({
                                    ...p,
                                    [task.id]: {
                                      ...p[task.id],
                                      file: e.target.files[0],
                                    },
                                  }))
                                }
                              />
                              <input
                                type="text"
                                placeholder="File description (optional)"
                                value={fileInputs[task.id]?.description || ""}
                                onChange={(e) =>
                                  setFileInputs((p) => ({
                                    ...p,
                                    [task.id]: {
                                      ...p[task.id],
                                      description: e.target.value,
                                    },
                                  }))
                                }
                                className="border p-1 rounded flex-1 min-w-[200px]"
                              />
                              <button
                                onClick={() => handleFileUpload(task.id)}
                                className="bg-indigo-500 text-white px-3 py-1 rounded text-sm"
                              >
                                Upload
                              </button>
                            </div>

                            {/* Files list */}
                            <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                              {getTaskFiles(task).map((f) => (
                                <li key={f.id} className="flex justify-between items-center">
                                  <div className="flex items-center gap-2">
                                    <PaperClipIcon className="h-4 w-4 text-gray-500" />
                                    <div>
                                      <div>{getFileName(f)}</div>
                                      <div className="text-xs text-gray-400">
                                        {f.uploaded_by_name || "Unknown"} •{" "}
                                        {f.uploaded_at
                                          ? new Date(f.uploaded_at).toLocaleString()
                                          : ""}
                                      </div>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <button
                                      onClick={() =>
                                        handleDownload(f.file, getFileName(f))
                                      }
                                      className="text-xs text-indigo-600"
                                    >
                                      <ArrowDownTrayIcon className="h-4 w-4 inline mr-1" />
                                      Download
                                    </button>
                                    <button
                                      onClick={() =>
                                        handleDeleteFile(task.id, f.id, emp.id)
                                      }
                                      className="text-xs text-red-600"
                                    >
                                      <TrashIcon className="h-4 w-4 inline mr-1" />
                                      Delete
                                    </button>
                                  </div>
                                </li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    )}
                  </motion.div>
                  )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {employees.length === 0 && (
          <div className="text-center text-gray-500 mt-10 text-lg">
            No employees match your search.
          </div>
        )}
      </main>

      {/* Toast container */}
      <Toasts toasts={toasts} />
    </div>
  );
}
