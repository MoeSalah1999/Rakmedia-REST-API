import { motion } from "framer-motion";
import { useLocation, useNavigate } from "react-router-dom";
import { LayoutDashboard, User, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const getDashboardPath = () => {
    const type = user?.employee_type?.toLowerCase();
    if (["manager", "officer"].includes(type)) return "/manager-dashboard";
    return "/dashboard";
  };

  const menu = [
    { name: "Dashboard", path: getDashboardPath(), icon: <LayoutDashboard size={20} /> },
    { name: "Profile", path: "/profile", icon: <User size={20} /> },
  ];

  return (
    <motion.aside
      initial={{ x: -200, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="fixed top-0 left-0 h-screen w-60 bg-gradient-to-b from-blue-600 to-blue-800 text-white shadow-lg flex flex-col justify-between"
    >
      <div className="p-6 text-2xl font-bold tracking-tight">Team Portal</div>

      <nav className="flex-1">
        {menu.map((item) => (
          <motion.button
            key={item.path}
            onClick={() => navigate(item.path)}
            whileHover={{ scale: 1.05 }}
            className={`flex items-center gap-3 w-full px-6 py-3 text-left transition-colors duration-200 ${
              location.pathname === item.path
                ? "bg-blue-900 text-white"
                : "text-gray-200 hover:bg-blue-700"
            }`}
          >
            {item.icon}
            <span>{item.name}</span>
          </motion.button>
        ))}
      </nav>

      <div className="p-4 border-t border-blue-700">
        <button
          onClick={logout}
          className="flex items-center gap-2 text-gray-200 hover:text-white w-full"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </motion.aside>
  );
}
