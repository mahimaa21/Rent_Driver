document.addEventListener("DOMContentLoaded", () => {
  const leaderboardList = document.getElementById("leaderboardList");
  const leaderboardMsg = document.getElementById("leaderboardMsg");
  const token = localStorage.getItem("access");

  if (!leaderboardList) return;
  if (!token) {
    leaderboardMsg.textContent = "⚠️ Please log in first.";
    leaderboardMsg.className = "msg error";
    setTimeout(() => (window.location.href = "/login/"), 1200);
    return;
  }

  async function loadLeaderboard() {
    leaderboardList.innerHTML = "<li>Loading leaderboard...</li>";

    try {
      const res = await fetch("/api/leaderboard/drivers/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();

      if (res.ok && data.length > 0) {
        leaderboardList.innerHTML = "";
        data.forEach((driver, index) => {
          const li = document.createElement("li");
          li.innerHTML = `
            <span>#${index + 1}. ${driver.username}</span>
            <span>${driver.total_completed} rides</span>
          `;
          leaderboardList.appendChild(li);
        });
      } else {
        leaderboardList.innerHTML = "<li>No leaderboard data yet.</li>";
      }
    } catch (err) {
      console.error("Leaderboard Error:", err);
      leaderboardMsg.textContent = "Failed to load leaderboard.";
      leaderboardMsg.className = "msg error";
    }
  }

  loadLeaderboard();
});