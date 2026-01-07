document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function showMessage(text, type = "info") {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove("hidden");
    setTimeout(() => messageDiv.classList.add("hidden"), 4000);
  }

  function createParticipantsSection(participants = []) {
    const container = document.createElement("div");
    container.className = "participants";
    const header = document.createElement("h5");
    header.textContent = "Participants";
    const count = document.createElement("span");
    count.className = "participants-count";
    count.textContent = participants.length;
    header.appendChild(count);
    container.appendChild(header);

    const list = document.createElement("ul");
    list.className = "participants-list";
    participants.forEach((p) => {
      const li = document.createElement("li");
      li.textContent = p;
      list.appendChild(li);
    });
    container.appendChild(list);
    return container;
  }

  // Render a single activity card; returns DOM element and a function to update participants
  function renderActivityCard(name, activity) {
    const card = document.createElement("div");
    card.className = "activity-card";
    const title = document.createElement("h4");
    title.textContent = name;
    card.appendChild(title);

    if (activity.description) {
      const desc = document.createElement("p");
      desc.textContent = activity.description;
      card.appendChild(desc);
    }

    const meta = document.createElement("div");
    meta.className = "activity-meta";
    if (activity.schedule) {
      const sched = document.createElement("small");
      sched.textContent = activity.schedule;
      meta.appendChild(sched);
    }
    card.appendChild(meta);

    const participantsSection = createParticipantsSection(activity.participants || []);
    card.appendChild(participantsSection);

    // updater function
    function addParticipant(email) {
      const ul = participantsSection.querySelector(".participants-list");
      const li = document.createElement("li");
      li.textContent = email;
      ul.appendChild(li);
      const cnt = participantsSection.querySelector(".participants-count");
      cnt.textContent = parseInt(cnt.textContent || "0", 10) + 1;
    }

    return { card, addParticipant };
  }

  // Flatten activities, handling nested groups (like Gym Class)
  function flattenActivities(data) {
    const flat = [];
    Object.entries(data).forEach(([name, value]) => {
      if (value && typeof value === "object" && !Array.isArray(value) && value.description && value.participants) {
        flat.push({ name, activity: value });
      } else if (value && typeof value === "object") {
        // group with sub-activities
        Object.entries(value).forEach(([subName, subVal]) => {
          if (subVal && typeof subVal === "object" && subVal.description && subVal.participants) {
            const fullName = `${name} - ${subName}`;
            flat.push({ name: fullName, activity: subVal });
          }
        });
      }
    });
    return flat;
  }

  // Load activities and render
  async function loadActivities() {
    activitiesList.innerHTML = "";
    activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';
    try {
      const res = await fetch("/activities");
      if (!res.ok) throw new Error("Failed to fetch activities");
      const data = await res.json();
      const flat = flattenActivities(data);
      if (flat.length === 0) {
        activitiesList.innerHTML = "<p>No activities available.</p>";
        return;
      }

      // map for updating after signup
      const updaters = new Map();

      flat.forEach(({ name, activity }) => {
        const { card, addParticipant } = renderActivityCard(name, activity);
        activitiesList.appendChild(card);
        // option value is encoded key used in API path; use the exact name from server keys if possible
        activitySelect.appendChild(new Option(name, name));
        updaters.set(name, addParticipant);
      });

      // store updaters for signup handler
      signupForm.updaters = updaters;
    } catch (err) {
      activitiesList.innerHTML = `<p class="error">Could not load activities.</p>`;
      console.error(err);
    }
  }

  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const activityName = activitySelect.value;
    if (!email || !activityName) {
      showMessage("Please enter an email and choose an activity.", "error");
      return;
    }
    try {
      const encoded = encodeURIComponent(activityName);
      const res = await fetch(`/activities/${encoded}/signup?email=${encodeURIComponent(email)}`, {
        method: "POST",
      });
      if (res.ok) {
        const updaters = signupForm.updaters || new Map();
        const updater = updaters.get(activityName);
        if (updater) updater(email);
        showMessage(`Signed up ${email} for ${activityName}`, "success");
        signupForm.reset();
      } else {
        const data = await res.json().catch(() => null);
        showMessage(data?.detail || "Signup failed", "error");
      }
    } catch (err) {
      console.error(err);
      showMessage("Signup failed (network error)", "error");
    }
  });

  // initial load
  loadActivities();
});
