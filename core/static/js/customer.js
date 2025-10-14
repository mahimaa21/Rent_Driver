document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("access");
  const rideForm = document.getElementById("rideForm");
  const rideMsg = document.getElementById("rideMsg");
  const rideList = document.getElementById("rideList");

  if (!rideForm) return;
  if (!token) {
    window.location.href = "/login/";
    return;
  }

  // -------- VERIFY ROLE --------
  try {
    const res = await fetch("/api/me/", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const me = await res.json();
    if (me.role !== "customer") {
      window.location.href = "/driver/dashboard/";
      return;
    }
  } catch {
    window.location.href = "/login/";
    return;
  }

  // -------- CREATE RIDE REQUEST --------
  rideForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    rideMsg.textContent = "Creating ride...";
    rideMsg.className = "msg";

    const pickup = document.getElementById("pickup").value.trim();
    const dropoff = document.getElementById("dropoff").value.trim();
    const carName = document.getElementById("carName").value.trim();

    try {
      const res = await fetch("/api/rides/create/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          pickup_location: pickup,
          dropoff_location: dropoff,
          vehicle_name: carName,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        rideMsg.textContent = "✅ Ride request created successfully!";
        rideMsg.className = "msg success";
        rideForm.reset();
        loadMyRides();
      } else {
        rideMsg.textContent = data.error || JSON.stringify(data);
        rideMsg.className = "msg error";
      }
    } catch {
      rideMsg.textContent = "Something went wrong. Try again.";
      rideMsg.className = "msg error";
    }
  });

  // -------- LOAD MY RIDES --------
  async function loadMyRides() {
    rideList.innerHTML = "<li>Loading your rides...</li>";

    try {
      const res = await fetch("/api/bookings/my/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const bookings = await res.json();

      if (Array.isArray(bookings) && bookings.length > 0) {
        rideList.innerHTML = "";

        for (const b of bookings) {
          const li = document.createElement("li");
          li.innerHTML = `
            🚗 <strong>${b.ride_request.pickup_location}</strong> → 
            <strong>${b.ride_request.dropoff_location}</strong><br>
            Status: <strong style="text-transform:capitalize;">${b.status}</strong>
          `;

          // Only show Chat button if booking is not cancelled or completed and has a driver
          if (b.driver && b.status !== "cancelled" && b.status !== "completed") {
            const chatBtn = document.createElement("a");
            chatBtn.textContent = "Chat";
            chatBtn.className = "btn btn-secondary btn-sm";
            chatBtn.style.marginLeft = "8px";
            chatBtn.href = `/chat/room/${b.id}/`;
            chatBtn.target = "_blank";
            li.appendChild(chatBtn);
          }

          // 🧨 SHOW CANCEL BUTTON if not completed/cancelled
          if (b.status !== "completed" && b.status !== "cancelled") {
            const cancelBtn = document.createElement("button");
            cancelBtn.textContent = "Cancel Ride";
            cancelBtn.classList.add("btn", "btn-danger", "cancel-btn");
            cancelBtn.dataset.booking = b.id;
            cancelBtn.style.marginTop = "6px";
            li.appendChild(cancelBtn);
          }

          // ⭐ SHOW REVIEW FORM if completed but not reviewed
          if (b.status === "completed") {
            if (!b.review_given) {
              const form = document.createElement("div");
              form.classList.add("rating-form");
              form.dataset.booking = b.id;
              form.innerHTML = `
                <label>⭐ Rate your driver:</label>
                <select class="rating-select">
                  <option value="5">⭐⭐⭐⭐⭐</option>
                  <option value="4">⭐⭐⭐⭐</option>
                  <option value="3">⭐⭐⭐</option>
                  <option value="2">⭐⭐</option>
                  <option value="1">⭐</option>
                </select>
                <input type="text" class="feedback-input" placeholder="Write feedback (optional)">
                <button class="btn btn-primary submit-review">Submit Review</button>
              `;
              li.appendChild(form);
            } else {
              li.innerHTML += `<p style="color:green;">✅ Already reviewed</p>`;
            }
          }

          rideList.appendChild(li);
        }
      } else {
        rideList.innerHTML = "<li>No rides found.</li>";
      }
    } catch (err) {
      console.error(err);
      rideList.innerHTML = "<li>Failed to load rides.</li>";
    }
  }

  // -------- SUBMIT REVIEW --------
  document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("submit-review")) {
      const form = e.target.closest(".rating-form");
      const bookingId = form.dataset.booking;
      const rating = form.querySelector(".rating-select").value;
      const feedback = form.querySelector(".feedback-input").value.trim();

      try {
        const res = await fetch(`/api/reviews/create/${bookingId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ rating, feedback }),
        });

        const data = await res.json();
        if (res.ok) {
          form.outerHTML = `<p style="color:green;">✅ Thank you for your review!</p>`;
        } else {
          alert(data.error || "Error submitting review.");
        }
      } catch {
        alert("Something went wrong while submitting your review.");
      }
    }
  });

  // 🆕 -------- CANCEL RIDE --------
  document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("cancel-btn")) {
      const bookingId = e.target.dataset.booking;
      if (!confirm("Are you sure you want to cancel this ride?")) return;

      try {
        const res = await fetch(`/api/booking/${bookingId}/cancel/`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });

        const data = await res.json();
        if (res.ok) {
          alert("✅ Ride cancelled successfully!");
          loadMyRides(); // Refresh list
        } else {
          alert(data.error || "Failed to cancel ride.");
        }
      } catch {
        alert("Error cancelling ride.");
      }
    }
  });

  // -------- SHOW NEARBY DRIVERS (with auto-refresh on location change) --------
  let lastLat = null, lastLng = null;
  let watchId = null;
  async function loadNearbyDrivers(lat, lng) {
    const nearbyList = document.getElementById("nearbyDriversList");
    if (!nearbyList) return;
    if (lat == null || lng == null) {
      nearbyList.innerHTML = "<li>Detecting your location...</li>";
      return;
    }
    try {
      const res = await fetch(`/api/nearby-drivers/?lat=${lat}&lng=${lng}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const drivers = await res.json();
      if (!Array.isArray(drivers) || !drivers.length) {
        nearbyList.innerHTML = "<li>No nearby drivers found</li>";
        return;
      }
      nearbyList.innerHTML = "";
      drivers.forEach((d) => {
        const li = document.createElement("li");
        li.innerHTML = `🚘 <strong>${d.username}</strong> (${d.vehicle}) — <span style='color:#2563eb;font-weight:bold;'>${d.distance_km} km</span> away`;
        nearbyList.appendChild(li);
      });
    } catch {
      nearbyList.innerHTML = "<li>Failed to load nearby drivers</li>";
    }
  }

  function startLocationWatch() {
    const nearbyList = document.getElementById("nearbyDriversList");
    if (!navigator.geolocation) {
      if (nearbyList) nearbyList.innerHTML = "<li>Geolocation not supported</li>";
      return;
    }
    if (watchId) navigator.geolocation.clearWatch(watchId);
    watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        // Only update if location changed significantly
        if (lastLat === null || lastLng === null || Math.abs(lat - lastLat) > 0.0001 || Math.abs(lng - lastLng) > 0.0001) {
          lastLat = lat;
          lastLng = lng;
          loadNearbyDrivers(lat, lng);
        }
      },
      (err) => {
        if (nearbyList) nearbyList.innerHTML = "<li>Location permission denied</li>";
      },
      { enableHighAccuracy: true, maximumAge: 10000, timeout: 10000 }
    );
  }

  // 🔹 INITIAL LOAD
  loadMyRides();
  startLocationWatch();
});