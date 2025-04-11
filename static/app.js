let currentPage = 0;
let totalPages = 1;

async function loadRecords() {
  const query = document.getElementById("search").value;
  const sortBy = document.getElementById("sortBy").value;
  const sortOrder = document.getElementById("sortOrder").value;

  const res = await fetch(`/records?page=${currentPage}&page_size=5&sort_by=${sortBy}&sort_order=${sortOrder}&query=${query}`);
  const data = await res.json();
  const tbody = document.querySelector("#recordsTable tbody");

  tbody.innerHTML = "";
  data.records.forEach((rec) => {
    const tr = document.createElement("tr");
    const date = new Date(rec.date);
    const formattedDate = date.toISOString().split("T")[0];
    tr.innerHTML = `
      <td>${formattedDate}</td>
      <td>${rec.amount}</td>
      <td>${rec.category}</td>
      <td>${rec.title}</td>
      <td>${rec.description || ""}</td>
      <td>
        <button onclick="editRecord(${rec.id}, '${rec.date}', ${rec.amount}, '${rec.category}', '${rec.title}', '${rec.description || ""}')">Edit</button>
        <button onclick="deleteRecord(${rec.id})">Delete</button>
      </td>`;
    tbody.appendChild(tr);
  });

  totalPages = data.total_pages;
  document.getElementById("pageIndicator").textContent = `Page ${currentPage + 1}`;
}

function changePage(direction) {
  if ((direction === -1 && currentPage > 0) || (direction === 1 && currentPage < totalPages - 1)) {
    currentPage += direction;
    loadRecords();
  }
}

function editRecord(id, dateStr, amount, category, title, desc) {
  const date = new Date(dateStr);
  const formattedDate = date.toISOString().split("T")[0];

  document.getElementById("formTitle").textContent = "Edit Record";
  document.getElementById("recordId").value = id;
  document.getElementById("date").value = formattedDate;
  document.getElementById("amount").value = amount;
  document.getElementById("category").value = category;
  document.getElementById("title").value = title;
  document.getElementById("desc").value = desc;
}

async function deleteRecord(id) {
  await fetch(`/records/${id}`, { method: "DELETE" });
  loadRecords();
}

async function submitForm(e) {
  e.preventDefault();

  const id = document.getElementById("recordId").value;
  const record = {
    date: document.getElementById("date").value,
    amount: parseFloat(document.getElementById("amount").value),
    category: document.getElementById("category").value,
    title: document.getElementById("title").value,
    desc: document.getElementById("desc").value,
  };

  if (id) {
    await fetch(`/records/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    });
  } else {
    await fetch("/records", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    });
  }

  document.getElementById("recordForm").reset();
  document.getElementById("formTitle").textContent = "Add New Record";
  document.getElementById("recordId").value = "";
  loadRecords();
}

window.onload = loadRecords;
