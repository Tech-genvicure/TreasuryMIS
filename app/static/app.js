let currentTable = "funds";
let currentRows = [];
let currentFields = [];

const titles = {
  funds: "Funds Position",
  payables: "Payables",
  receivables: "Receivables",
  borrowings: "Borrowings"
};

function money(v) {
  v = Number(v || 0);
  const sign = v < 0 ? "-" : "";
  v = Math.abs(v);
  if (v >= 10000000) return `${sign}₹${(v / 10000000).toFixed(2)} Cr`;
  if (v >= 100000) return `${sign}₹${(v / 100000).toFixed(2)} L`;
  return `${sign}₹${v.toLocaleString("en-IN", {maximumFractionDigits: 0})}`;
}
function lakhs(v) { return (Number(v || 0) / 100000).toFixed(2); }
function esc(v) { return v == null ? "" : String(v); }
function titleize(s) {
  return s.replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
}

async function loadDashboard() {
  const r = await fetch("/api/dashboard");
  if (!r.ok) return location.href = "/";
  const d = await r.json();

  document.querySelector("#funds").textContent = money(d.funds);
  document.querySelector("#payables").textContent = money(d.payables);
  document.querySelector("#receivables").textContent = money(d.receivables);
  document.querySelector("#net").textContent = money(d.funds + d.receivables - d.payables);

  document.querySelector("#sanctioned").textContent = money(d.borrowing.sanctioned);
  document.querySelector("#disbursed").textContent = money(d.borrowing.disbursed);
  document.querySelector("#outstanding").textContent = money(d.borrowing.outstanding);

  const funds = document.querySelector("#funds-list");
  funds.innerHTML = d.funds_breakdown.map(x => `
    <div class="metric-row">
      <div><div class="metric-name">${esc(x.name)}</div><div class="metric-sub">${esc(x.entity_type)}</div></div>
      <div class="metric-value">${money(x.amount)}</div>
    </div>`).join("") || `<p class="muted">No fund records.</p>`;

  const vendors = document.querySelector("#vendors");
  const maxVendor = Math.max(...d.vendors.map(x => Number(x.amount)), 1);
  vendors.innerHTML = d.vendors.map(x => `
    <div class="bar-row">
      <div class="bar-label"><span>${esc(x.name)}</span><strong>${lakhs(x.amount)} L</strong></div>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.max(2, Number(x.amount) / maxVendor * 100)}%"></div></div>
    </div>`).join("") || `<p class="muted">No unpaid payable records.</p>`;

  const flow = document.querySelector("#cash-flow");
  flow.innerHTML = d.cash_flow.map(x => `
    <div class="cash-row">
      <strong>${esc(x.bucket)}</strong>
      <span class="flow-pill outflow">Out ₹${lakhs(x.payables)} L</span>
      <span class="flow-pill inflow">In ₹${lakhs(x.receivables)} L</span>
    </div>`).join("") || `<p class="muted">No cash-flow records.</p>`;
}

async function initSpreadsheet() {
  document.querySelectorAll(".tab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
      btn.classList.add("active");
      loadTable(btn.dataset.table);
    });
  });
  await loadTable("funds");
}

async function loadTable(key) {
  currentTable = key;
  const r = await fetch(`/api/table/${key}`);
  if (!r.ok) return location.href = "/";
  const d = await r.json();
  currentRows = d.rows;
  currentFields = d.fields;

  document.querySelector("#table-title").textContent = titles[key];
  renderTable();
}

function renderTable() {
  const thead = document.querySelector("#data-table thead");
  const tbody = document.querySelector("#data-table tbody");
  thead.innerHTML = `<tr>${currentFields.map(f => `<th>${titleize(f)}</th>`).join("")}<th>Actions</th></tr>`;

  tbody.innerHTML = currentRows.map(row => `
    <tr data-id="${row.id}">
      ${currentFields.map(f => `<td contenteditable="true" data-field="${f}">${esc(row[f])}</td>`).join("")}
      <td><div class="row-actions">
        <button class="save-btn" onclick="saveRow(this)">Save</button>
        <button class="delete-btn" onclick="deleteRow(this)">Delete</button>
      </div></td>
    </tr>`).join("");
}

function addRow() {
  const tbody = document.querySelector("#data-table tbody");
  const tr = document.createElement("tr");
  tr.dataset.id = "";
  tr.innerHTML = currentFields.map(f => `<td contenteditable="true" data-field="${f}"></td>`).join("") +
    `<td><div class="row-actions"><button class="save-btn" onclick="saveRow(this)">Save</button><button class="delete-btn" onclick="this.closest('tr').remove()">Cancel</button></div></td>`;
  tbody.prepend(tr);
  tr.querySelector("td").focus();
}

function rowData(tr) {
  const data = {};
  tr.querySelectorAll("[data-field]").forEach(td => data[td.dataset.field] = td.textContent.trim());
  return data;
}

async function saveRow(button) {
  const tr = button.closest("tr");
  const id = tr.dataset.id;
  const data = rowData(tr);
  const method = id ? "PUT" : "POST";
  const url = id ? `/api/table/${currentTable}/${id}` : `/api/table/${currentTable}`;

  const r = await fetch(url, {
    method,
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  const result = await r.json();
  if (!r.ok) return alert(result.detail || "Could not save row.");

  await loadTable(currentTable);
}

async function deleteRow(button) {
  const tr = button.closest("tr");
  const id = tr.dataset.id;
  if (!id) return tr.remove();
  if (!confirm("Delete this row?")) return;

  const r = await fetch(`/api/table/${currentTable}/${id}`, {method:"DELETE"});
  if (!r.ok) {
    const result = await r.json();
    return alert(result.detail || "Could not delete row.");
  }
  await loadTable(currentTable);
}
