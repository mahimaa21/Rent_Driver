// core/static/js/emergency.js
document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access");
  const form = document.getElementById("emergencyForm");
  const phoneInput = document.getElementById("emergencyPhone");
  const msg = document.getElementById("emergencyMsg");
  const alertBtn = document.getElementById("alertBtn");
  const alertMsg = document.getElementById("alertMsg");
  const alertList = document.getElementById("alertList");

  // 🔒 Redirect if not logged in
  if (!token) {
    console.warn("No token found. Redirecting to login...");
    window.location.href = "/login/";
    return;
  }

  // =============== SAVE CONTACT =================
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      msg.textContent = "Saving contact...";
      msg.className = "msg info";

      try {
        const res = await fetch("/emergency/api/set/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            phone_number: phoneInput.value,
          }),
        });

        const data = await res.json();
        if (res.ok) {
          msg.textContent = data.message || "✅ Contact saved successfully!";
          msg.className = "msg success";
        } else {
          msg.textContent = data.error || "❌ Failed to save contact";
          msg.className = "msg error";
        }
      } catch (err) {
        console.error(err);
        msg.textContent = "⚠️ Network error while saving contact";
        msg.className = "msg error";
      }
    });
  }

  // =============== TRIGGER ALERT =================
  if (alertBtn) {
    alertBtn.addEventListener("click", async () => {
      alertMsg.textContent = "🚨 Sending alert...";
      alertMsg.className = "msg info";

      try {
        const res = await fetch("/emergency/api/alert/", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await res.json();
        if (res.ok) {
          alertMsg.textContent = data.message || "🚨 Alert sent!";
          alertMsg.className = "msg success";
          loadAlerts();
        } else {
          alertMsg.textContent = data.error || "❌ Failed to send alert";
          alertMsg.className = "msg error";
        }
      } catch (err) {
        console.error(err);
        alertMsg.textContent = "⚠️ Network error while sending alert";
        alertMsg.className = "msg error";
      }
    });
  }

  // =============== LOAD ALERT HISTORY =================
  async function loadAlerts() {
    if (!alertList) return;

    alertList.innerHTML = "<li>Loading...</li>";

    try {
      const res = await fetch("/emergency/api/history/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();

      if (Array.isArray(data) && data.length > 0) {
        alertList.innerHTML = "";
        data.forEach((a) => {
          const li = document.createElement("li");
          li.textContent = `📞 ${a.contact} | ${a.status.toUpperCase()} | ${new Date(
            a.time
          ).toLocaleString()}`;
          alertList.appendChild(li);
        });
      } else {
        alertList.innerHTML = "<li>No alerts found.</li>";
      }
    } catch (err) {
      console.error(err);
      alertList.innerHTML = "<li>⚠️ Failed to load alerts.</li>";
    }
  }

  loadAlerts();
});