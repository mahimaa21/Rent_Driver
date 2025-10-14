// ==================== AUTH.JS ====================
// Handles both Register and Login for Rent a Driver

document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("registerForm");
  const msg = document.getElementById("registerMsg");

  // ==================== REGISTER ====================
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      msg.textContent = "";
      msg.className = "";

      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value.trim();
      const role = document.getElementById("role").value;

      if (!username || !password || !role) {
        msg.textContent = "⚠️ Please fill all fields.";
        msg.className = "msg error";
        return;
      }

      try {
        // --- REGISTER USER ---
        const res = await fetch("/api/register/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password, role }),
        });

        const data = await res.json();

        if (!res.ok) {
          msg.textContent =
            data.error || JSON.stringify(data) || "❌ Registration failed.";
          msg.className = "msg error";
          return;
        }

        msg.textContent = "✅ Registered successfully!";
        msg.className = "msg success";

        // --- AUTO LOGIN ---
        const loginRes = await fetch("/api/token/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });

        if (!loginRes.ok) {
          msg.textContent = "⚠️ Registered but auto-login failed. Please login manually.";
          msg.className = "msg warning";
          return;
        }

        const tokens = await loginRes.json();
        localStorage.setItem("access", tokens.access);
        localStorage.setItem("refresh", tokens.refresh);
        localStorage.setItem("userRole", role);

        // --- REDIRECT BASED ON ROLE ---
        setTimeout(() => {
          if (role === "driver") {
            window.location.href = "/driver/profile/"; // ✅ first setup page
          } else {
            window.location.href = "/customer/dashboard/"; // ✅ directly to customer dash
          }
        }, 800);
      } catch (err) {
        console.error("Registration error:", err);
        msg.textContent = "❌ Something went wrong. Try again later.";
        msg.className = "msg error";
      }
    });
  }

  // ==================== LOGIN ====================
  const loginForm = document.getElementById("loginForm");
  const loginMsg = document.getElementById("loginMsg");

  // ⚠️ Prevent this logic from running on other pages
  const currentPath = window.location.pathname;
  if (loginForm && currentPath.startsWith("/login")) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      loginMsg.textContent = "";
      loginMsg.className = "";

      const username = document.getElementById("loginUsername").value.trim();
      const password = document.getElementById("loginPassword").value.trim();

      if (!username || !password) {
        loginMsg.textContent = "⚠️ Please enter username and password.";
        loginMsg.className = "msg error";
        return;
      }

      try {
        // --- LOGIN USER ---
        const res = await fetch("/api/token/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });

        const data = await res.json();

        if (!res.ok || !data.access) {
          loginMsg.textContent = data.detail || "❌ Invalid credentials.";
          loginMsg.className = "msg error";
          return;
        }

        // --- FETCH USER INFO ---
        const meRes = await fetch("/api/me/", {
          headers: { Authorization: `Bearer ${data.access}` },
        });
        const meData = await meRes.json();

        // --- STORE TOKENS + ROLE ---
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        localStorage.setItem("userRole", meData.role);

        loginMsg.textContent = "✅ Login successful!";
        loginMsg.className = "msg success";

        // --- REDIRECT BASED ON ROLE ---
        setTimeout(() => {
          if (meData.role === "driver") {
            window.location.href = "/driver/dashboard/"; // if already profile set up
          } else {
            window.location.href = "/customer/dashboard/";
          }
        }, 1000);
      } catch (err) {
        console.error("Login error:", err);
        loginMsg.textContent = "❌ Something went wrong. Try again later.";
        loginMsg.className = "msg error";
      }
    });
  }
});