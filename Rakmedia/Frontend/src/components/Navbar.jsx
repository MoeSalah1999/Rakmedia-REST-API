import { useNavigate } from "react-router-dom";
import { UserCircleIcon, ArrowRightOnRectangleIcon } from "@heroicons/react/24/outline";

export default function Navbar({ user, onLogout }) {
  const navigate = useNavigate();

  return (
    <nav className="flex items-center justify-between bg-indigo-600 text-white p-4 shadow-lg">
      <h1 className="text-2xl font-semibold tracking-tight">Employee Dashboard</h1>

      <div className="flex items-center gap-6">
        <button
          onClick={() => navigate("/profile")}
          className="flex items-center gap-2 hover:text-gray-200"
        >
          <UserCircleIcon className="h-6 w-6" />
          <span>{user?.username}</span>
        </button>

        <button
          onClick={onLogout}
          className="flex items-center gap-2 hover:text-gray-200"
        >
          <ArrowRightOnRectangleIcon className="h-6 w-6" />
          <span>Logout</span>
        </button>
      </div>
    </nav>
  );
}
