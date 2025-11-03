export default function ProfileCard({ profile }) {
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("profile_picture", file);
    await api.patch(`/employees/${profile.id}/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    alert("Profile picture updated!");
  };

  return (
    <div className="p-6 bg-white rounded-xl shadow-md w-full max-w-md">
      <img
        src={profile.profile_picture || "/default-avatar.png"}
        alt="Profile"
        className="w-32 h-32 rounded-full mx-auto object-cover mb-4"
      />
      <h3 className="text-xl font-bold text-center">
        {profile.first_name} {profile.last_name}
      </h3>
      <p className="text-center text-gray-600 mb-4">{profile.email}</p>

      <div className="flex justify-center">
        <label className="bg-blue-600 text-white px-4 py-2 rounded cursor-pointer">
          Upload New Picture
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleImageUpload}
          />
        </label>
      </div>
    </div>
  );
}