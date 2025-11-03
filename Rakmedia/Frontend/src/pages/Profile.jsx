import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { CameraIcon } from "@heroicons/react/24/solid";
import axiosClient from "../api/axiosClient";
import Sidebar from "../components/Sidebar";

export default function Profile() {
  const [employee, setEmployee] = useState(null);
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Fetch current employee profile
  useEffect(() => {
    setLoading(true);
    axiosClient
      .get("employees/me/")
      .then(({ data }) => {
        setEmployee(data);
        setEmail(data.user_email || data.user?.email || "");
      })
      .catch((err) => console.error("Error fetching profile:", err))
      .finally(() => setLoading(false));
  }, []);

  const handleImageChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
    }
  };

  const handleUpdate = async () => {
    if (!employee) return;
    setSaving(true);

    try {
      const formData = new FormData();
      if (file) formData.append("profile_picture", file);
      if (email) formData.append("user_email", email);

      const response = await axiosClient.patch("employees/me/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setEmployee(response.data);
      setPreview(null);
      setFile(null);
      alert("✅ Profile updated successfully!");
    } catch (err) {
      console.error("Error updating profile:", err);
      alert("❌ Failed to update profile. Check server logs.");
    } finally {
      setSaving(false);
    }
  };

  if (loading || !employee) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-50 text-gray-500">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mr-3"></div>
        Loading profile...
      </div>
    );
  }

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 ml-60 min-h-screen flex items-center justify-center bg-gradient-to-b from-blue-50 to-white p-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white shadow-2xl rounded-3xl p-10 w-full max-w-lg text-center border border-gray-100"
        >
          {/* Profile picture */}
          <div className="relative mx-auto w-36 h-36 mb-6">
            <img
              src={preview || employee.profile_picture || "/default-avatar.png"}
              alt="Profile"
              className="rounded-full w-full h-full object-cover border-4 border-indigo-500"
            />
            <label
              htmlFor="file-upload"
              className="absolute bottom-2 right-2 bg-indigo-600 p-2 rounded-full cursor-pointer hover:bg-indigo-700 transition"
            >
              <CameraIcon className="h-5 w-5 text-white" />
              <input
                id="file-upload"
                type="file"
                className="hidden"
                onChange={handleImageChange}
                accept="image/*"
              />
            </label>
          </div>

          <h1 className="text-2xl font-bold text-gray-800 mb-1">
            {employee.username || "Unknown User"}
          </h1>
          <p className="text-gray-600 mb-4">
            <strong>Departments: </strong>{employee.department?.join(", ") || "No department"}
          </p>

          <div className="text-sm text-gray-600 space-y-2 mb-8">
            <p>
              <strong>Employee Code:</strong> {employee.employee_code || "N/A"}
            </p>
            <p>
              <strong>Role:</strong>{" "}
              {employee.job_role || employee.position || "N/A"}
            </p>
            <div className="flex flex-col items-center space-y-2">
              <label className="text-sm font-semibold text-gray-700">
                Email Address:
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 w-64 text-center focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <button
            onClick={handleUpdate}
            disabled={saving}
            className={`px-6 py-2 rounded-full text-white font-medium transition ${
              saving
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-700"
            }`}
          >
            {saving ? "Saving..." : "Update Profile"}
          </button>
        </motion.div>
      </main>
    </div>
  );
}
