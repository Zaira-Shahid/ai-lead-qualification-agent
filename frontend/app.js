(function () {
  const messagesEl = document.getElementById("messages");
  const formEl = document.getElementById("chat-form");
  const inputEl = document.getElementById("chat-input");
  const sendButtonEl = document.getElementById("send-button");
  const errorBannerEl = document.getElementById("error-banner");
  const qualPanelEl = document.getElementById("qualification-panel");
  const qualScoreEl = document.getElementById("qual-score");
  const qualStatusEl = document.getElementById("qual-status");
  const qualReviewEl = document.getElementById("qual-review");

  let sessionId = null;
  let qualificationRequested = false;

  function addMessage(text, role, variant) {
    const el = document.createElement("div");
    el.className = "message " + role + (variant ? " " + variant : "");
    el.textContent = text;
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return el;
  }

  function showError(text) {
    errorBannerEl.textContent = text;
    errorBannerEl.hidden = false;
  }

  function clearError() {
    errorBannerEl.hidden = true;
    errorBannerEl.textContent = "";
  }

  function setLoading(isLoading) {
    inputEl.disabled = isLoading;
    sendButtonEl.disabled = isLoading;
  }

  function showQualificationResult(data) {
    qualScoreEl.textContent = data.lead_score;
    qualStatusEl.textContent = data.qualification_status;
    qualReviewEl.textContent = data.requires_human_review ? "Yes" : "No";
    qualPanelEl.hidden = false;
  }

  async function sendMessage(message) {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: message }),
    });

    if (!response.ok) {
      throw new Error("Request failed with status " + response.status);
    }

    return response.json();
  }

  async function requestQualification() {
    const response = await fetch("/api/qualify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });

    if (!response.ok) {
      throw new Error("Qualification request failed with status " + response.status);
    }

    return response.json();
  }

  formEl.addEventListener("submit", async function (event) {
    event.preventDefault();

    const message = inputEl.value.trim();
    if (!message) {
      return;
    }

    clearError();
    addMessage(message, "user");
    inputEl.value = "";

    setLoading(true);
    const loadingEl = addMessage("NovaCare Assistant is typing...", "loading");

    try {
      const data = await sendMessage(message);
      sessionId = data.session_id;

      loadingEl.remove();

      const variant = data.status === "emergency" || data.status === "error" ? data.status : null;
      addMessage(data.reply, "assistant", variant);

      if (data.status === "ready_for_qualification" && !qualificationRequested) {
        qualificationRequested = true;
        try {
          const qualData = await requestQualification();
          showQualificationResult(qualData);
        } catch (qualError) {
          showError("Could not retrieve your qualification result. Please try again.");
        }
      }
    } catch (error) {
      loadingEl.remove();
      showError("Sorry, we couldn't reach the assistant. Please check your connection and try again.");
    } finally {
      setLoading(false);
      inputEl.focus();
    }
  });

  addMessage(
    "Hi! Welcome to NovaCare Clinic. What type of service are you interested in?",
    "assistant"
  );
})();
