document.addEventListener('DOMContentLoaded', async function() {
  const chatBox = document.getElementById('chatBox');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const bookingId = window.BOOKING_ID;
  const token = localStorage.getItem('access');

  // Get current user info for message alignment
  let currentUser = { username: '' };
  try {
    const res = await fetch('/api/me/', { headers: { 'Authorization': `Bearer ${token}` } });
    if (res.ok) currentUser = await res.json();
  } catch {}

  function appendMessage(sender, message, timestamp) {
    const div = document.createElement('div');
    div.className = 'chat-message';
    if (sender === currentUser.username) {
      div.classList.add('me');
    }
    div.innerHTML = `<b>${sender}</b><br>${message}<span class='chat-time'>${timestamp}</span>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  async function loadMessages() {
    chatBox.innerHTML = '';
    const res = await fetch(`/chat/api/messages/${bookingId}/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    data.messages.forEach(m => appendMessage(m.sender, m.message, m.timestamp));
  }

  chatForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    await fetch(`/chat/api/messages/${bookingId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ message: msg })
    });
    chatInput.value = '';
    loadMessages();
  });

  // Poll for new messages every 2 seconds
  setInterval(loadMessages, 2000);
  loadMessages();
});