// src/pages/Dashboard.jsx
import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import {
  CheckCircleIcon,
  ClockIcon,
  PaperClipIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/solid";
import axiosClient from "../api/axiosClient";
import Sidebar from "../components/Sidebar";

/* Toast component */
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

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [filesState, setFilesState] = useState({});
  const [fileInputs, setFileInputs] = useState({});
  const [loading, setLoading] = useState(true);
  const [toasts, setToasts] = useState([]);

  const addToast = (t) => {
    const id = Math.random().toString(36).slice(2, 9);
    setToasts((s) => [...s, { id, ...t }]);
    setTimeout(() => setToasts((s) => s.filter((x) => x.id !== id)), 4000);
  };

  const ensureArray = (maybeArray) =>
    Array.isArray(maybeArray) ? maybeArray : maybeArray ? [maybeArray] : [];
  const getTaskFiles = (task) => {
  const f =
    filesState && Array.isArray(filesState[task.id])
      ? filesState[task.id]
      : ensureArray(task.files);
  return ensureArray(f).filter(
    (x) => x && (x.file || x.description || x.id)
  );
};

  const getFileName = (f) => {
    if (!f) return "file";
    if (f.file) {
      try {
        return typeof f.file === "string"
          ? f.file.split("/").pop()
          : String(f.file);
      } catch {
        return f.description || "file";
      }
    }
    return f.description || "file";
  };

  /* This is for fetching all tasks assigned to the employee from the database */
  useEffect(() => {
    const fetchAllTasks = async () => {
      setLoading(true);
      try {
        let allTasks = [];
        let nextUrl = "tasks/";

        while (nextUrl) {
          const { data } = await axiosClient.get(nextUrl);
          if (Array.isArray(data)) {
            allTasks = [...allTasks, ...data];
            break;
          } else if (data.results) {
            const normalized = data.results.map((t) => ({
              ...t,
              files: ensureArray(t.files),
            }));
            allTasks = [...allTasks, ...normalized];
            nextUrl = data.next
              ? data.next.replace("http://127.0.0.1:8000/api/", "")
              : null;
          } else {
            nextUrl = null;
          }
        }

        setTasks(allTasks);
      } catch (err) {
        console.error("Error fetching tasks:", err);
        addToast({
          title: "Error",
          message: "Failed to load tasks",
          type: "error",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAllTasks();
  }, []);

  /* This is for fetching task-related files */
  const fetchFiles = useCallback(async (taskId) => {
    try {
      const { data } = await axiosClient.get(`tasks/${taskId}/files/`);
      const arr = ensureArray(data);
      setFilesState((prev) => ({ ...prev, [taskId]: arr }));
      addToast({ title: "Files refreshed", type: "success" });
    } catch (err) {
      console.error("Error fetching files:", err);
      addToast({
        title: "Error",
        message: "Failed to refresh files",
        type: "error",
      });
    }
  }, []);


/* This is handles the upload of task-related files */
const handleFileUpload = async (taskId) => {
  const input = fileInputs[taskId];
  if (!input?.file)
    return addToast({
      title: "No file",
      message: "Select a file first",
      type: "error",
    });
  const fd = new FormData();
  fd.append("file", input.file);
  if (input.description) fd.append("description", input.description);

  try {
    await axiosClient.post(`tasks/${taskId}/upload-file/`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    // Re-fetch files and update both task.files and filesState
    const { data } = await axiosClient.get(`tasks/${taskId}/files/`);
    const arr = ensureArray(data);
    setFilesState((prev) => ({ ...prev, [taskId]: arr }));
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, files: arr } : t))
    );

    setFileInputs((prev) => ({ ...prev, [taskId]: {} }));
    addToast({
      title: "Uploaded",
      message: "File uploaded successfully",
      type: "success",
    });
  } catch (err) {
    console.error("Error uploading file:", err);
    addToast({
      title: "Error",
      message: "File upload failed",
      type: "error",
    });
  }
};

  /* This handles download of task-related files */
  const handleDownload = async (fileUrl, fileName) => {
    if (!fileUrl) {
      addToast({
        title: "No URL",
        message: "File URL is missing",
        type: "error",
      });
      return;
    }
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

  /* Updated file deletion logic (same as ManagerDashboard) */
const handleDeleteFile = async (taskId, fileId) => {
  if (!window.confirm("Are you sure you want to delete this file?")) return;

  try {
    await axiosClient.delete(`/tasks/${taskId}/files/${fileId}/`);

    // ✅ Update both local states so UI doesn’t blank out
    setFilesState((prev) => ({
      ...prev,
      [taskId]: (prev[taskId] || []).filter((f) => f.id !== fileId),
    }));
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId
          ? {
              ...t,
              files: ensureArray(t.files).filter((f) => f.id !== fileId),
            }
          : t
      )
    );

    addToast({
      title: "Deleted",
      message: "File removed successfully",
      type: "success",
    });
  } catch (err) {
    console.error("Error deleting file:", err);
    addToast({
      title: "Error",
      message: "Failed to delete file",
      type: "error",
    });
  }
};


  if (loading) {
    return (
      <div className="flex">
        <Sidebar />
        <main className="flex-1 ml-60 bg-gradient-to-b from-indigo-50 to-white min-h-screen p-10">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="bg-white rounded-2xl shadow-lg transition-all border border-gray-100 p-6 animate-pulse"
              >
                <div className="h-6 bg-gray-200 rounded w-1/2 mb-3"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              </div>
            ))}
          </div>
        </main>
        <Toasts toasts={toasts} />
      </div>
    );
  }

  /* The tasks cards in the dashboard main page */
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 ml-60 bg-gradient-to-b from-indigo-50 to-white min-h-screen p-10">
        <motion.h1
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl font-bold text-gray-900 mb-8 text-center"
        >
          My Tasks
        </motion.h1>

        {tasks.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center text-gray-500 mt-20"
          >
            <ClockIcon className="h-14 w-14 text-gray-400 mb-3" />
            <p className="text-lg font-medium">No tasks assigned yet 🎉</p>
          </motion.div>
        ) : (
          <motion.div
            layout
            className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8 overflow-visible"
          >
            {tasks.map((task, i) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all border border-gray-100 p-6 flex flex-col justify-between overflow-hidden"
              >
                <div>
                  <div className="flex justify-between items-start mb-3">
                    <h2 className="text-lg font-semibold text-gray-800">
                      {task.title}
                    </h2>
                    {task.completed ? (
                      <CheckCircleIcon className="h-6 w-6 text-green-500" />
                    ) : (
                      <ClockIcon className="h-6 w-6 text-yellow-500" />
                    )}
                  </div>

                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {task.description || "No description"}
                  </p>

                  <div className="space-y-3">
                    <div className="flex flex-col gap-2 border-t pt-3">
                      <input
                        type="file"
                        onChange={(e) =>
                          setFileInputs((prev) => ({
                            ...prev,
                            [task.id]: {
                              ...prev[task.id],
                              file: e.target.files[0],
                            },
                          }))
                        }
                        className="text-sm text-gray-700 border rounded-md p-1 file:mr-2 file:py-1 file:px-2 file:rounded-md file:border-0 file:text-sm file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                      />
                      <input
                        type="text"
                        placeholder="File description (optional)"
                        value={fileInputs[task.id]?.description || ""}
                        onChange={(e) =>
                          setFileInputs((prev) => ({
                            ...prev,
                            [task.id]: {
                              ...prev[task.id],
                              description: e.target.value,
                            },
                          }))
                        }
                        className="border border-gray-300 p-2 rounded-md text-sm focus:ring-indigo-500 focus:border-indigo-500"
                      />
                      <button
                        onClick={() => handleFileUpload(task.id)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-3 py-2 rounded-md w-full"
                      >
                        Upload File
                      </button>
                    </div>

                    <ul className="list-disc pl-4 text-sm text-gray-700 mt-3">
                      {getTaskFiles(task).map((f) => (
                        <li
                          key={f.id}
                          className="flex items-center gap-2 justify-between"
                        >
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
                          <div className="flex items-center gap-3">
                            <button
                              onClick={() =>
                                handleDownload(f.file, getFileName(f))
                              }
                              className="text-xs text-indigo-600 hover:underline"
                            >
                              <ArrowDownTrayIcon className="h-4 w-4 inline mr-1" />{" "}
                              Download
                            </button>
                            <button
                              onClick={() =>
                                handleDeleteFile(task.id, f.id)
                              }
                              className="text-xs text-red-600 hover:underline"
                            >
                              Delete
                            </button>
                          </div>
                        </li>
                      ))}
                      {getTaskFiles(task).length === 0 && (
                        <li className="text-sm text-gray-500">No files yet</li>
                      )}
                    </ul>
                  </div>
                </div>

                <div className="text-sm text-gray-500 flex justify-between items-center mt-5 pt-3 border-t">
                  <span>Due: {task.due_date || "N/A"}</span>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      task.completed
                        ? "bg-green-100 text-green-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {task.completed ? "Completed" : "Pending"}
                  </span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </main>
      <Toasts toasts={toasts} />
    </div>
  );
}
