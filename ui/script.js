// --- Modal & Navigation ---

function openAuth() {
  document.getElementById("auth-modal").style.display = "flex";
  showLogin();
}

function closeAuth() {
  document.getElementById("auth-modal").style.display = "none";
  setAuthMsg("");
}

function togglePass(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.type = el.type === "password" ? "text" : "password";
}

function showSignup() {
  document.getElementById("login-form").style.display = "none";
  document.getElementById("signup-form").style.display = "block";
  document.getElementById("modal-title").innerText = "REGISTER PROTOCOL";

  const emailInput = document.getElementById("signup-email");
  if (emailInput) emailInput.focus();
}

function showLogin() {
  document.getElementById("signup-form").style.display = "none";
  document.getElementById("login-form").style.display = "block";
  document.getElementById("modal-title").innerText = "INITIALIZE ACCESS";

  const emailInput = document.getElementById("login-email");
  if (emailInput) emailInput.focus();
}

function handleKey(event, nextId) {
  if (event.key === "Enter") {
    event.preventDefault();

    if (nextId === "LOGIN_BTN") {
      handleLogin();
    } else if (nextId === "SIGNUP_BTN") {
      handleSignup();
    } else {
      const nextElement = document.getElementById(nextId);
      if (nextElement) nextElement.focus();
    }
  }
}

// Global Agent Trigger
document.addEventListener("keydown", (e) => {
  const agentScreen = document.getElementById("agent-screen");

  if (
    e.key === "Enter" &&
    agentScreen &&
    agentScreen.style.display === "flex"
  ) {
    if (!isListening) {
      toggleListening();
    }
  }
});

// --- Auth & Persistence ---

async function handleLogin() {
  const emailInput = document.getElementById("login-email");
  const passInput = document.getElementById("login-pass");

  if (!emailInput || !passInput) {
    console.error("Login form elements not found");
    return;
  }

  const email = emailInput.value.trim();
  const pass = passInput.value;

  if (!email || !pass) {
    setAuthMsg("EMAIL AND PASSWORD REQUIRED.");
    return;
  }

  try {
    setAuthMsg("AUTHENTICATING...");

    const result = await pywebview.api.login(email, pass);

    if (result.success) {
      saveRecentLogin(email);
      onAuthSuccess(result);
    } else {
      setAuthMsg(result.message || "AUTHENTICATION FAILED.");

      if (result.needs_signup) {
        setTimeout(() => {
          setAuthMsg("REDIRECTING TO REGISTRATION...");
          setTimeout(showSignup, 1000);
        }, 1500);
      }
    }
  } catch (error) {
    console.error("Login error:", error);
    setAuthMsg("CONNECTION ERROR. PLEASE TRY AGAIN.");
  }
}

async function handleSignup() {
  const emailInput = document.getElementById("signup-email");
  const passInput = document.getElementById("signup-pass");

  if (!emailInput || !passInput) {
    console.error("Signup form elements not found");
    return;
  }

  const email = emailInput.value.trim();
  const pass = passInput.value;

  if (!email || !pass) {
    setAuthMsg("EMAIL AND PASSWORD REQUIRED.");
    return;
  }

  try {
    setAuthMsg("GENERATING IDENTITY...");

    const result = await pywebview.api.signup(email, pass);

    if (result.success) {
      setAuthMsg("IDENTITY GENERATED. AUTHENTICATING...");

      // Auto-fill login form
      document.getElementById("login-email").value = email;
      document.getElementById("login-pass").value = pass;

      setTimeout(() => {
        showLogin();
        handleLogin();
      }, 1500);
    } else {
      setAuthMsg(result.message || "REGISTRATION FAILED.");
    }
  } catch (error) {
    console.error("Signup error:", error);
    setAuthMsg("CONNECTION ERROR. PLEASE TRY AGAIN.");
  }
}

function onAuthSuccess(user) {
  closeAuth();

  const landingScreen = document.getElementById("landing-screen");
  const agentScreen = document.getElementById("agent-screen");
  const userEmailElement = document.getElementById("current-user-email");

  if (landingScreen) landingScreen.style.display = "none";
  if (agentScreen) agentScreen.style.display = "flex";

  if (userEmailElement && user.email) {
    userEmailElement.innerText = user.email.toUpperCase();
  }

  // Lock Session
  try {
    localStorage.setItem("jarvis_last_session", JSON.stringify(user));
  } catch (error) {
    console.error("Failed to save session:", error);
  }

  addMessage("jarvis", "Neural link active. Systems fully operational.");
}

function handleLogout() {
  try {
    localStorage.removeItem("jarvis_last_session");
  } catch (error) {
    console.error("Failed to clear session:", error);
  }

  location.reload();
}

function saveRecentLogin(email) {
  try {
    let recent = JSON.parse(
      localStorage.getItem("jarvis_recent_logins") || "[]",
    );

    if (!recent.includes(email)) {
      recent.unshift(email);
      recent = recent.slice(0, 3); // Keep only last 3
      localStorage.setItem("jarvis_recent_logins", JSON.stringify(recent));
    }
  } catch (error) {
    console.error("Failed to save recent login:", error);
  }
}

function loadRecentLogins() {
  try {
    const recent = JSON.parse(
      localStorage.getItem("jarvis_recent_logins") || "[]",
    );
    const container = document.getElementById("recent-logins-container");
    const list = document.getElementById("recent-logins-list");

    if (!container || !list) return;

    if (recent.length > 0) {
      container.style.display = "block";
      list.innerHTML = "";

      recent.forEach((email) => {
        const chip = document.createElement("div");
        chip.className = "login-chip";
        chip.innerText = email.split("@")[0].substring(0, 10).toUpperCase();
        chip.title = email;
        chip.onclick = () => {
          const emailInput = document.getElementById("login-email");
          const passInput = document.getElementById("login-pass");

          if (emailInput) emailInput.value = email;
          if (passInput) passInput.focus();
        };
        list.appendChild(chip);
      });
    }
  } catch (error) {
    console.error("Failed to load recent logins:", error);
  }
}

function setAuthMsg(msg) {
  const el = document.getElementById("auth-msg");

  if (!el) return;

  el.innerText = msg;
  el.style.opacity = msg ? 1 : 0;
}

// --- Voice Commands ---

function addMessage(role, text) {
  const chatBox = document.getElementById("chat-box");

  if (!chatBox) {
    console.error("Chat box not found");
    return;
  }

  const msgDiv = document.createElement("div");
  msgDiv.className = `glass-bubble ${role}-msg`;
  msgDiv.innerText = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

let isListening = false;

async function toggleListening() {
  if (isListening) {
    console.log("Already listening, ignoring request");
    return;
  }

  isListening = true;

  const btn = document.getElementById("mic-btn");
  const core = document.getElementById("visualizer-core");
  const status = document.getElementById("status-text");

  if (btn) btn.classList.add("active");
  if (core) core.style.transform = "translate(-50%, -50%) scale(1.3)";
  if (status) status.innerText = "LISTENING...";

  try {
    const result = await pywebview.api.start_voice_session();

    if (result) {
      if (result.scanning) {
        if (status) status.innerText = "CALIBRATING...";

        setTimeout(() => {
          if (status) status.innerText = "SYSTEM READY";
          resetMic();
        }, 4000);
      } else if (result.user_input) {
        addMessage("user", result.user_input);
        addMessage("jarvis", result.ai_response);

        if (status) status.innerText = "RESPONDING...";

        setTimeout(() => {
          if (status) status.innerText = "SYSTEM STANDBY";
        }, 2000);
      } else {
        if (status) status.innerText = "NO INPUT DETECTED";

        setTimeout(() => {
          if (status) status.innerText = "SYSTEM STANDBY";
        }, 2000);
      }
    } else {
      if (status) status.innerText = "READY FOR INPUT";
    }
  } catch (error) {
    console.error("Voice session error:", error);

    if (status) status.innerText = "SYSTEM ERROR";

    addMessage(
      "jarvis",
      "I encountered an error. Please check the console for details.",
    );

    setTimeout(() => {
      if (status) status.innerText = "SYSTEM STANDBY";
    }, 3000);
  } finally {
    resetMic();
  }
}

function resetMic() {
  isListening = false;

  const btn = document.getElementById("mic-btn");
  const core = document.getElementById("visualizer-core");
  const status = document.getElementById("status-text");

  if (btn) btn.classList.remove("active");
  if (core) core.style.transform = "translate(-50%, -50%) scale(1)";

  if (status && status.innerText === "LISTENING...") {
    status.innerText = "SYSTEM STANDBY";
  }
}

// --- Initialization ---

window.onload = async () => {
  console.log("JARVIS UI Loading...");

  loadRecentLogins();

  try {
    const saved = localStorage.getItem("jarvis_last_session");

    if (saved) {
      const user = JSON.parse(saved);

      console.log("Attempting session restore for:", user.email);

      try {
        const check = await pywebview.api.verify_session(
          user.user_id,
          user.email,
        );

        if (check.success) {
          console.log("Session restored successfully");
          onAuthSuccess(user);
        } else {
          console.log("Session verification failed");
          localStorage.removeItem("jarvis_last_session");
        }
      } catch (error) {
        console.error("Session verification error:", error);
        localStorage.removeItem("jarvis_last_session");
      }
    } else {
      console.log("No saved session found");
    }
  } catch (error) {
    console.error("Session restore error:", error);
  }

  console.log("JARVIS UI Ready");
};

// Error handler for unhandled promise rejections
window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled promise rejection:", event.reason);

  const status = document.getElementById("status-text");
  if (status) {
    status.innerText = "SYSTEM ERROR";
    setTimeout(() => {
      status.innerText = "SYSTEM STANDBY";
    }, 3000);
  }
});

// --- Text Input Alternative ---
function handleTextInput(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    sendTextCommand();
  }
}

async function sendTextCommand() {
  const input = document.getElementById('text-input');
  const text = input.value.trim();
  
  if (!text) return;
  
  // Clear input
  input.value = '';
  
  // Add to chat
  addMessage(text, 'user');
  
  try {
    const response = await fetch('/api/text_query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    
    const data = await response.json();
    
    if (data && data.ai_response) {
      addMessage(data.ai_response, 'assistant');
    } else {
      addMessage('No response from JARVIS', 'system');
    }
  } catch (error) {
    console.error('Text command error:', error);
    addMessage('Error sending command', 'system');
  }
}
