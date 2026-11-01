// Static demo of the portal. Same validation rules as portal/validation.py.
const KEY = "submissions";

const LABELS = {
  name: "Student name",
  reg_no: "Registration number",
  title: "Assignment title",
  url: "Submission URL",
};

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || [];
  } catch (e) {
    return [];
  }
}

function save(list) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
  } catch (e) {
    // storage blocked, keep the list in memory only
  }
}

function isValidUrl(value) {
  try {
    const u = new URL(value);
    return (u.protocol === "http:" || u.protocol === "https:") &&
      u.hostname.includes(".") && !value.includes(" ");
  } catch (e) {
    return false;
  }
}

function validate(data) {
  const errors = [];
  for (const field in LABELS) {
    if (!data[field]) errors.push(LABELS[field] + " is required.");
  }
  if (data.url && !isValidUrl(data.url)) {
    errors.push("Submission URL is not valid. It must start with http:// or https://");
  }
  return errors;
}

let submissions = load();

function render() {
  const rows = document.getElementById("rows");
  rows.innerHTML = "";
  submissions.slice().reverse().forEach((s) => {
    const tr = document.createElement("tr");
    [s.id, s.name, s.reg_no, s.title, s.url, s.submitted_at].forEach((value, i) => {
      const td = document.createElement("td");
      if (i === 4) {
        const a = document.createElement("a");
        a.href = value;
        a.target = "_blank";
        a.textContent = value;
        td.appendChild(a);
      } else {
        td.textContent = value;
      }
      tr.appendChild(td);
    });
    rows.appendChild(tr);
  });
  document.getElementById("count").textContent = submissions.length;
}

document.getElementById("form").addEventListener("submit", (e) => {
  e.preventDefault();
  const data = {};
  for (const field in LABELS) {
    data[field] = document.getElementById(field).value.trim();
  }

  const errorBox = document.getElementById("errors");
  const okBox = document.getElementById("ok");
  const errors = validate(data);

  if (errors.length) {
    errorBox.innerHTML = "<strong>Submission rejected:</strong><ul>" +
      errors.map((m) => "<li>" + m + "</li>").join("") + "</ul>";
    errorBox.classList.remove("hidden");
    okBox.classList.add("hidden");
    return;
  }

  data.id = submissions.length + 1;
  data.submitted_at = new Date().toLocaleString();
  submissions.push(data);
  save(submissions);
  render();

  errorBox.classList.add("hidden");
  okBox.classList.remove("hidden");
  e.target.reset();
});

render();
