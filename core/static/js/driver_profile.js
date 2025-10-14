document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access");
  const form = document.getElementById("driverProfileForm");
  const msg = document.getElementById("profileMsg");

  // 🧩 0. Ensure this script runs only on driver profile page
  if (!form || !msg) return;

  // 🧩 1. Make sure driver is logged in
  if (!token) {
    msg.textContent = "⚠️ Please log in first.";
    msg.className = "msg error";
    setTimeout(() => (window.location.href = "/login/"), 1200);
    return;
  }

  // 🧩 2. Verify the logged-in user is actually a driver
  async function verifyRole() {
    try {
      const res = await fetch("/api/me/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();

      if (data.role !== "driver") {
        msg.textContent = "⚠️ Only drivers can access this page.";
        msg.className = "msg error";
        setTimeout(() => (window.location.href = "/customer/dashboard/"), 1500);
      }
    } catch (err) {
      console.error("Role verification failed:", err);
      if (msg) {
        msg.textContent = "Something went wrong. Please log in again.";
        msg.className = "msg error";
      }
      setTimeout(() => (window.location.href = "/login/"), 1500);
    }
  }

  verifyRole(); // run once on page load

  // 🧩 3. Handle form submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const license_number = document.getElementById("license").value.trim();
    const vehicle_details = document.getElementById("vehicle").value.trim();
  const location_name = document.getElementById("location_name").value.trim();
    const profile_image = document.getElementById("profile_image").files[0];

    msg.textContent = "Saving profile...";
    msg.className = "msg";

    try {
      const formData = new FormData();
      formData.append("license_number", license_number);
      formData.append("vehicle_details", vehicle_details);
  formData.append("location_name", location_name);
      if (profile_image) formData.append("profile_image", profile_image);

      const res = await fetch("/api/driver/profile/create/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await res.json();
      console.log("PROFILE RESPONSE:", data);

      if (res.ok) {
        msg.textContent = "✅ Profile created successfully!";
        msg.className = "msg success";
        setTimeout(() => (window.location.href = "/driver/dashboard/"), 1200);
      } else {
        msg.textContent = data.error || JSON.stringify(data);
        msg.className = "msg error";
      }
    } catch (err) {
      console.error("PROFILE ERROR:", err);
      msg.textContent = "Something went wrong while saving your profile.";
      msg.className = "msg error";
    }
  });
});