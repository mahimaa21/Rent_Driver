document.addEventListener("DOMContentLoaded", async () => {
  // ✅ NAVIGATION IS NOW HANDLED BY NavbarManager IN base.html
  // This file is kept for backward compatibility but navigation logic is disabled
  console.log('main.js loaded - navigation handled by NavbarManager');
  
  // ✅ Keep only the logout functionality that's needed
  const navLogout = document.getElementById("navLogout");
  if (navLogout) {
    navLogout.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("userRole"); // ✅ ALSO CLEAR USER ROLE
      window.location.href = "/";
    });
  }
});