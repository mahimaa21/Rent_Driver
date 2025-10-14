document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("access");
  const availableRidesList = document.getElementById("availableRides");
  const myBookingsList = document.getElementById("myBookings");
  const msg = document.getElementById("driverMsg");

  // NEW — reviews elements
  const reviewsList = document.getElementById("myReviews");
  const reviewsMsg = document.getElementById("reviewsMsg");
  const avgRatingEl = document.getElementById("avgRating");

  // NEW — stats elements
  const totalRidesEl = document.getElementById("totalRides");
  const ongoingRidesEl = document.getElementById("ongoingRides");

  if (!availableRidesList) return;
  if (!token) {
    window.location.href = "/login/";
    return;
  }

  // -------- VERIFY DRIVER + ID --------
  let driverId = null;
  try {
    const r = await fetch("/api/me/", { headers: { Authorization: `Bearer ${token}` } });
    const me = await r.json();
    if (me.role !== "driver") {
      window.location.href = "/customer/dashboard/";
      return;
    }
    driverId = me.id;
  } catch {
    window.location.href = "/login/";
    return;
  }

  // -------- LOAD AVAILABLE RIDES --------
  async function loadAvailableRides() {
    availableRidesList.innerHTML = "<li>Loading...</li>";
    try {
      const res = await fetch("/api/rides/available/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const rides = await res.json();

      if (!Array.isArray(rides) || !rides.length) {
        availableRidesList.innerHTML = "<li>No available rides</li>";
        return;
      }

      availableRidesList.innerHTML = "";
      rides.forEach((ride) => {
        const li = document.createElement("li");
        li.innerHTML = `
          <strong>🚗 ${ride.pickup_location}</strong> → ${ride.dropoff_location}
          <span style="float:right;">
            <button class="btn btn-primary accept-btn" data-id="${ride.id}">Accept</button>
          </span>`;
        availableRidesList.appendChild(li);
      });

      document.querySelectorAll(".accept-btn").forEach((btn) =>
        btn.addEventListener("click", () => acceptRide(btn.dataset.id))
      );
    } catch {
      availableRidesList.innerHTML = "<li>Error loading rides</li>";
    }
  }

  // -------- ACCEPT RIDE --------
  async function acceptRide(rideId) {
    msg.textContent = "Processing...";
    try {
      const res = await fetch(`/api/booking/create/${rideId}/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();

      if (res.ok) {
        msg.textContent = "✅ Ride accepted successfully!";
        msg.className = "msg success";
        loadAvailableRides();
        loadMyBookings();
      } else {
        msg.textContent = data.error || JSON.stringify(data);
        msg.className = "msg error";
      }
    } catch {
      msg.textContent = "Error accepting ride.";
      msg.className = "msg error";
    }
  }

  // -------- LOAD BOOKINGS --------
  async function loadMyBookings() {
    myBookingsList.innerHTML = "<li>Loading...</li>";
    try {
      const res = await fetch("/api/bookings/my/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const bookings = await res.json();

      if (!Array.isArray(bookings) || !bookings.length) {
        myBookingsList.innerHTML = "<li>No bookings found</li>";
        totalRidesEl.textContent = 0;
        ongoingRidesEl.textContent = 0;
        document.getElementById("earningsRides").textContent = 0;
        document.getElementById("earningsAmount").textContent = "$0";
        return;
      }

      myBookingsList.innerHTML = "";

      // --- NEW: count completed and ongoing rides
      let completedCount = 0;
      let ongoingCount = 0;

      bookings.forEach((b) => {
        if (b.status === "completed") completedCount++;
        if (b.status === "ongoing") ongoingCount++;

        const li = document.createElement("li");
        li.innerHTML = `
          🚗 <strong>${b.ride_request.pickup_location}</strong> → ${b.ride_request.dropoff_location}
          | Status: <span style="color:${b.status === "completed" ? "green" : "orange"};">${b.status}</span>
        `;

        // Only show Chat button if booking is not cancelled or completed and has a customer
        if (b.ride_request && b.ride_request.customer && b.status !== "cancelled" && b.status !== "completed") {
          const chatBtn = document.createElement("a");
          chatBtn.textContent = "Chat";
          chatBtn.className = "btn btn-secondary btn-sm";
          chatBtn.style.marginLeft = "8px";
          chatBtn.href = `/chat/room/${b.id}/`;
          chatBtn.target = "_blank";
          li.appendChild(chatBtn);
        }

        if (b.status === "ongoing") {
          const finishBtn = document.createElement("button");
          finishBtn.className = "btn btn-success finish-btn";
          finishBtn.dataset.id = b.id;
          finishBtn.style.marginLeft = "10px";
          finishBtn.textContent = "Finish Ride";
          li.appendChild(finishBtn);
        }
        // 🆕 show cancelled notice
        if (b.status === "cancelled") {
          li.innerHTML += ` <span style="color:red;">❌ Cancelled by Customer</span>`;
        }

        myBookingsList.appendChild(li);
      });

      // --- Update dashboard counters
      totalRidesEl.textContent = completedCount;
      ongoingRidesEl.textContent = ongoingCount;

      // --- 💰 NEW: Earnings calculation (Fixed $5 per ride)
      const ratePerRide = 5;
      const totalEarnings = completedCount * ratePerRide;
      document.getElementById("earningsRides").textContent = completedCount;
      document.getElementById("earningsAmount").textContent = `$${totalEarnings}`;

      document.querySelectorAll(".finish-btn").forEach((btn) =>
        btn.addEventListener("click", () => finishRide(btn.dataset.id))
      );
    } catch {
      myBookingsList.innerHTML = "<li>Error loading bookings</li>";
      totalRidesEl.textContent = "–";
      ongoingRidesEl.textContent = "–";
    }
  }

  // -------- FINISH RIDE --------
  async function finishRide(bookingId) {
    msg.textContent = "Finishing ride...";
    try {
      const res = await fetch(`/api/booking/${bookingId}/status/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: "completed" }),
      });

      const data = await res.json();
      if (res.ok) {
        msg.textContent = "✅ Ride marked as completed!";
        msg.className = "msg success";
        loadMyBookings();
      } else {
        msg.textContent = data.error || JSON.stringify(data);
        msg.className = "msg error";
      }
    } catch {
      msg.textContent = "Error finishing ride.";
      msg.className = "msg error";
    }
  }

  // -------- LOAD REVIEWS --------
  async function loadMyReviews() {
    if (!reviewsList) return;

    reviewsList.innerHTML = "<li>Loading reviews…</li>";
    reviewsMsg.textContent = "";

    try {
      const res = await fetch(`/api/reviews/driver/${driverId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const reviews = await res.json();

      if (!Array.isArray(reviews) || !reviews.length) {
        reviewsList.innerHTML = "<li>No reviews yet.</li>";
        avgRatingEl.textContent = "–";
        return;
      }

      const avg = reviews.reduce((sum, r) => sum + (Number(r.rating) || 0), 0) / reviews.length;
      avgRatingEl.textContent = `${avg.toFixed(2)} / 5 (${reviews.length})`;

      reviewsList.innerHTML = "";
      reviews.forEach((r) => {
        const stars = "★".repeat(r.rating) + "☆".repeat(5 - r.rating);
        const li = document.createElement("li");
        li.innerHTML = `
          <div><strong>${stars}</strong> <small>by ${r.customer}</small></div>
          ${r.feedback ? `<div style="margin-top:.25rem;">“${r.feedback}”</div>` : ""}
          <small style="opacity:.7;">${new Date(r.created_at).toLocaleString()}</small>
        `;
        reviewsList.appendChild(li);
      });
    } catch {
      reviewsMsg.textContent = "Failed to load reviews.";
      reviewsMsg.className = "msg error";
      reviewsList.innerHTML = "";
    }
  }

  // -------- INITIAL LOAD --------
  loadAvailableRides();
  loadMyBookings();
  // -------- SHOW NEARBY RIDES --------
  async function loadNearbyRides() {
    const nearbyList = document.getElementById("nearbyRidesList");
    if (!nearbyList) return;

    if (!navigator.geolocation) {
      nearbyList.innerHTML = "<li>Geolocation not supported</li>";
      return;
    }

    nearbyList.innerHTML = "<li>Detecting location...</li>";

    navigator.geolocation.getCurrentPosition(async (pos) => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;

      try {
        const res = await fetch(`/api/nearby-rides/?lat=${lat}&lng=${lng}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const rides = await res.json();

        if (!Array.isArray(rides) || !rides.length) {
          nearbyList.innerHTML = "<li>No nearby ride requests</li>";
          return;
        }

        nearbyList.innerHTML = "";
        rides.forEach((r) => {
          const li = document.createElement("li");
          li.innerHTML = `🧍‍♂️ <strong>${r.customer}</strong> — ${r.pickup_location} (${r.distance_km} km)`;
          nearbyList.appendChild(li);
        });
      } catch {
        nearbyList.innerHTML = "<li>Failed to load nearby rides</li>";
      }
    });
  }

  // 🔹 Run all loaders on init
  loadAvailableRides();
  loadMyBookings();
  loadMyReviews();
  loadNearbyRides();
});