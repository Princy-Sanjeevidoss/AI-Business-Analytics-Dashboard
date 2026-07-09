// Dashboard Application State
let currentTab = 'overview';
let currentCrudTab = 'sales';
let crudData = [];
let searchFilteredData = [];
let dropdownOptions = { customers: [], products: [] };

// Chart.js instances (tracked to destroy before re-render)
let charts = {
  revenue: null,
  products: null,
  payments: null,
};

// Check authentication on startup
const token = localStorage.getItem('token');
if (!token) {
  window.location.href = 'login.html';
} else {
  const username = localStorage.getItem('username') || 'admin';
  document.getElementById('user-display-name').textContent = username;
  document.getElementById('user-avatar-initial').textContent = username.charAt(0).toUpperCase();
}

// Initial Loading
async function init() {
  await loadDashboard();
  await loadDropdownData();
}

// 1. Overview Tab & Charts Loader
async function loadDashboard() {
  try {
    const summary = await request('/analytics/summary');
    const monthly = await request('/analytics/monthly-sales');
    const topProducts = await request('/analytics/top-products');
    const payments = await request('/analytics/payment-methods');
    const forecast = await request('/prediction/next-month-revenue');

    // Update Quick Card Statistics
    document.getElementById('card-revenue').textContent = `$${summary.total_revenue.toLocaleString()}`;
    document.getElementById('card-customers').textContent = summary.total_customers;
    document.getElementById('card-sales').textContent = summary.total_sales;
    document.getElementById('card-employees').textContent = summary.total_employees;
    
    // Update forecasting projection
    const forecastVal = forecast && forecast.prediction !== undefined ? forecast.prediction : 0;
    document.getElementById('quick-forecast-val').textContent = `$${forecastVal.toLocaleString()}`;
    document.getElementById('prediction-value').textContent = `$${forecastVal.toLocaleString()}`;

    // Render Charts
    renderRevenueChart(monthly);
    renderProductsChart(topProducts);
    renderPaymentsChart(payments);

    // Compute System Insights
    generateSystemInsights(summary, topProducts, payments);

  } catch (error) {
    console.error("Dashboard render error:", error);
    document.getElementById('insights-list').innerHTML = `<li>⚠️ Failed to fetch metrics: ${error.message}</li>`;
  }
}

// Load lookups for Select inputs in forms (Customers and Products)
async function loadDropdownData() {
  try {
    dropdownOptions.customers = await request('/customers') || [];
    dropdownOptions.products = await request('/products') || [];
  } catch (e) {
    console.warn("Could not load dropdown lookups:", e);
  }
}

// Chart 1: Revenue Line Chart
function renderRevenueChart(monthly) {
  const ctx = document.getElementById('revenue-chart').getContext('2d');
  if (charts.revenue) charts.revenue.destroy();

  const labels = monthly.map(item => item.month);
  const data = monthly.map(item => item.revenue);

  charts.revenue = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Monthly Revenue ($)',
        data,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.15)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#a855f7',
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
      }
    }
  });
}

// Chart 2: Top Products Bar Chart
function renderProductsChart(topProducts) {
  const ctx = document.getElementById('products-chart').getContext('2d');
  if (charts.products) charts.products.destroy();

  const labels = topProducts.map(item => item.product);
  const data = topProducts.map(item => item.sales);

  charts.products = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Units Sold',
        data,
        backgroundColor: 'linear-gradient(to right, #a855f7, #6366f1)',
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(6, 182, 212, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
        ],
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
      }
    }
  });
}

// Chart 3: Payments Doughnut Chart
function renderPaymentsChart(payments) {
  const ctx = document.getElementById('payments-chart').getContext('2d');
  if (charts.payments) charts.payments.destroy();

  const labels = payments.map(item => item.method);
  const data = payments.map(item => item.count);

  charts.payments = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: [
          'rgba(6, 182, 212, 0.85)',
          'rgba(16, 185, 129, 0.85)',
          'rgba(245, 158, 11, 0.85)',
          'rgba(239, 68, 68, 0.85)',
        ],
        borderColor: 'rgba(15, 23, 42, 0.9)',
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#e2e8f0', font: { family: 'Outfit', size: 12 } }
        }
      }
    }
  });
}

// Generate Automated Natural Language Insights
function generateSystemInsights(summary, topProducts, payments) {
  const listEl = document.getElementById('insights-list');
  let itemsHtml = '';

  if (summary.total_revenue > 0) {
    const avgSale = (summary.total_revenue / summary.total_sales).toFixed(2);
    itemsHtml += `<li>📈 **Revenue Performance:** Total volume stands at **$${summary.total_revenue.toLocaleString()}** with an average transaction value of **$${avgSale}**.</li>`;
  }

  if (topProducts && topProducts.length > 0) {
    itemsHtml += `<li>🔥 **Top Selling Product:** **${topProducts[0].product}** is leading demand with **${topProducts[0].sales}** units ordered.</li>`;
  }

  if (payments && payments.length > 0) {
    // Sort to find largest method
    const primaryPay = [...payments].sort((a,b) => b.count - a.count)[0];
    itemsHtml += `<li>💳 **Preferred Billing:** The most popular payment method is **${primaryPay.method}** (recorded **${primaryPay.count}** times).</li>`;
  } else {
    itemsHtml += `<li>🔍 No payments recorded in the database yet.</li>`;
  }

  // Convert markdown-like syntax to HTML formatting
  listEl.innerHTML = itemsHtml.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

// 2. Tab Navigation System
function switchTab(tabName) {
  currentTab = tabName;

  // Toggle active styling on navigation items
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
  });

  const targetNavItem = Array.from(document.querySelectorAll('.nav-item')).find(item => 
    item.textContent.toLowerCase().includes(tabName.replace('-', ' '))
  );
  if (targetNavItem) targetNavItem.classList.add('active');

  // Toggle visible pane
  document.querySelectorAll('.tab-content').forEach(pane => {
    pane.classList.remove('active');
  });
  document.getElementById(`tab-${tabName}`).classList.add('active');

  // Update headers
  const titleText = document.getElementById('panel-title-text');
  const subtitleText = document.getElementById('panel-subtitle-text');

  if (tabName === 'overview') {
    titleText.textContent = "Business Dashboard";
    subtitleText.textContent = "Real-time metrics and system indicators";
    loadDashboard();
  } else if (tabName === 'data-manager') {
    titleText.textContent = "Database Management";
    subtitleText.textContent = "Create, view, modify, and delete customer logs";
    loadCrudData(currentCrudTab);
  } else if (tabName === 'prediction') {
    titleText.textContent = "Revenue Forecasting";
    subtitleText.textContent = "Predict next month income using regression modeling";
    loadDashboard();
  }
}

// 3. Data Manager CRUD tabs
async function switchCrudTab(crudTab) {
  currentCrudTab = crudTab;
  
  document.querySelectorAll('.crud-tab').forEach(tab => {
    tab.classList.remove('active');
  });
  document.getElementById(`crud-tab-${crudTab}`).classList.add('active');
  updateImportLabel();
  
  document.getElementById('crud-search').value = '';
  await loadCrudData(crudTab);
}

function updateImportLabel() {
  const label = document.getElementById('import-entity-label');
  if (label) {
    label.textContent = capitalize(currentCrudTab);
  }
}

// Fetch lists from backend
async function loadCrudData(entity) {
  try {
    crudData = await request(`/${entity}`) || [];
    searchFilteredData = [...crudData];
    renderCrudTable();
  } catch (error) {
    alert(`Failed to load ${entity}: ` + error.message);
  }
}

// Render dynamic CRUD table
function renderCrudTable() {
  const headEl = document.getElementById('crud-table-head');
  const bodyEl = document.getElementById('crud-table-body');
  
  headEl.innerHTML = '';
  bodyEl.innerHTML = '';

  if (searchFilteredData.length === 0) {
    bodyEl.innerHTML = `<tr><td colspan="10" style="text-align: center; color: var(--text-muted); padding: 40px;">No records found. Click "+ Add Record" to insert data.</td></tr>`;
    return;
  }

  // Build Headers and Rows according to data properties
  const headers = getTableHeaders(currentCrudTab);
  
  // Render Head
  let headHtml = '<tr>';
  headers.forEach(h => {
    headHtml += `<th>${h.label}</th>`;
  });
  headHtml += `<th style="text-align: right;">Actions</th></tr>`;
  headEl.innerHTML = headHtml;

  // Render Body
  searchFilteredData.forEach(row => {
    let rowHtml = '<tr>';
    headers.forEach(h => {
      let val = row[h.key];
      if (h.key.includes('date')) {
        // Clean display of dates
        val = val ? val.substring(0, 10) : '';
      }
      if (h.key === 'total_amount' || h.key === 'price' || h.key === 'salary' || h.key === 'amount') {
        val = `$${parseFloat(val).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      }
      if (h.key === 'customer_id') {
        const cust = dropdownOptions.customers.find(c => c.id === val);
        val = cust ? `${cust.name} (ID: ${val})` : `Customer ${val}`;
      }
      if (h.key === 'product_id') {
        const prod = dropdownOptions.products.find(p => p.id === val);
        val = prod ? `${prod.name} (ID: ${val})` : `Product ${val}`;
      }
      rowHtml += `<td>${val === null || val === undefined ? '' : val}</td>`;
    });
    
    // Action buttons
    rowHtml += `
      <td style="text-align: right;">
        <div class="action-buttons" style="justify-content: flex-end;">
          <button class="btn btn-secondary btn-sm" onclick="editRecord(${row.id})" style="padding: 4px 8px;">✏️</button>
          <button class="btn btn-danger btn-sm" onclick="deleteRecord(${row.id})" style="padding: 4px 8px;">🗑️</button>
        </div>
      </td>
    </tr>`;
    bodyEl.innerHTML += rowHtml;
  });
}

// Setup table columns layout
function getTableHeaders(entity) {
  switch (entity) {
    case 'sales':
      return [
        { label: 'ID', key: 'id' },
        { label: 'Customer', key: 'customer_id' },
        { label: 'Product', key: 'product_id' },
        { label: 'Quantity', key: 'quantity' },
        { label: 'Total Price', key: 'total_amount' },
        { label: 'Date Ordered', key: 'sale_date' }
      ];
    case 'products':
      return [
        { label: 'ID', key: 'id' },
        { label: 'Product Name', key: 'name' },
        { label: 'Category', key: 'category' },
        { label: 'Price', key: 'price' },
        { label: 'Stock Level', key: 'stock' }
      ];
    case 'customers':
      return [
        { label: 'ID', key: 'id' },
        { label: 'Full Name', key: 'name' },
        { label: 'Email Address', key: 'email' },
        { label: 'Phone', key: 'phone' },
        { label: 'City Location', key: 'city' },
        { label: 'Join Date', key: 'join_date' }
      ];
    case 'employees':
      return [
        { label: 'ID', key: 'id' },
        { label: 'Full Name', key: 'name' },
        { label: 'Role / Designation', key: 'role' },
        { label: 'Department', key: 'department' },
        { label: 'Salary ($)', key: 'salary' }
      ];
    case 'payments':
      return [
        { label: 'ID', key: 'id' },
        { label: 'Customer ID', key: 'customer_id' },
        { label: 'Amount Paid', key: 'amount' },
        { label: 'Method', key: 'payment_method' },
        { label: 'Payment Date', key: 'payment_date' }
      ];
  }
}

// 4. Searching Filter handler
function handleSearch(query) {
  const q = query.toLowerCase();
  searchFilteredData = crudData.filter(row => {
    return Object.values(row).some(val => 
      String(val).toLowerCase().includes(q)
    );
  });
  renderCrudTable();
}

function openDataUpload() {
  document.getElementById('data-upload-input').click();
}

function showUploadStatus(message, type = '') {
  const statusEl = document.getElementById('upload-status');
  if (!statusEl) return;

  statusEl.textContent = message;
  statusEl.className = `upload-status active ${type}`.trim();
}

async function handleDataUpload(event) {
  const fileInput = event.target;
  const file = fileInput.files && fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  showUploadStatus(`Importing ${file.name} into ${capitalize(currentCrudTab)}...`);

  try {
    const result = await request(`/import/${currentCrudTab}`, {
      method: 'POST',
      body: formData,
    });

    const skippedText = result.skipped ? ` ${result.skipped} row(s) skipped.` : '';
    showUploadStatus(`Imported ${result.imported} row(s) into ${capitalize(currentCrudTab)}.${skippedText}`, result.skipped ? 'error' : 'success');
    await loadDropdownData();
    await loadCrudData(currentCrudTab);
    if (currentTab === 'overview') await loadDashboard();
  } catch (error) {
    showUploadStatus(`Upload failed: ${error.message}`, 'error');
  } finally {
    fileInput.value = '';
  }
}

// 5. CRUD Modals Operations
let modalMode = 'add'; // 'add' or 'edit'

function openCrudModal(mode, recordId = null) {
  modalMode = mode;
  document.getElementById('modal-error').style.display = 'none';
  document.getElementById('crud-modal-overlay').style.display = 'flex';
  
  const titleEl = document.getElementById('modal-title');
  const submitBtn = document.getElementById('modal-submit-btn');
  const formContent = document.getElementById('modal-form-content');
  
  titleEl.textContent = mode === 'add' ? `Add New ${capitalize(currentCrudTab.slice(0, -1))}` : `Edit ${capitalize(currentCrudTab.slice(0, -1))}`;
  submitBtn.textContent = mode === 'add' ? 'Save Record' : 'Apply Changes';

  // Build inputs depending on CRUD context
  formContent.innerHTML = buildFormFields(currentCrudTab);

  if (mode === 'edit' && recordId) {
    const record = crudData.find(r => r.id === recordId);
    if (record) {
      document.getElementById('form-record-id').value = record.id;
      populateFormFields(record);
    }
  } else {
    document.getElementById('form-record-id').value = '';
    // Pre-populate date fields with current date
    const today = new Date().toISOString().substring(0, 10);
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput) dateInput.value = today;
  }
}

function closeCrudModal() {
  document.getElementById('crud-modal-overlay').style.display = 'none';
}

// Generate input elements for CRUD form
function buildFormFields(entity) {
  // Pre-load lookup drop-downs
  const customerSelectOptions = dropdownOptions.customers.map(c => `<option value="${c.id}">${c.name} (ID: ${c.id})</option>`).join('');
  const productSelectOptions = dropdownOptions.products.map(p => `<option value="${p.id}">${p.name} ($${p.price} | Stock: ${p.stock})</option>`).join('');

  switch (entity) {
    case 'sales':
      return `
        <div class="form-group">
          <label>Customer</label>
          <select id="field-customer_id" required>${customerSelectOptions}</select>
        </div>
        <div class="form-group">
          <label>Product</label>
          <select id="field-product_id" onchange="calculateSaleTotal()" required>${productSelectOptions}</select>
        </div>
        <div class="form-group">
          <label>Quantity</label>
          <input type="number" id="field-quantity" min="1" value="1" oninput="calculateSaleTotal()" required />
        </div>
        <div class="form-group">
          <label>Total Price ($)</label>
          <input type="number" step="0.01" id="field-total_amount" required readonly style="background: rgba(15, 23, 42, 0.4);" />
        </div>
        <div class="form-group">
          <label>Date Ordered</label>
          <input type="date" id="field-sale_date" required />
        </div>
      `;
    case 'products':
      return `
        <div class="form-group">
          <label>Product Name</label>
          <input type="text" id="field-name" placeholder="E.g., Smart Laptop" required />
        </div>
        <div class="form-group">
          <label>Category</label>
          <input type="text" id="field-category" placeholder="E.g., Electronics" required />
        </div>
        <div class="form-group">
          <label>Unit Price ($)</label>
          <input type="number" step="0.01" id="field-price" min="0" required />
        </div>
        <div class="form-group">
          <label>Stock Level</label>
          <input type="number" id="field-stock" min="0" required />
        </div>
      `;
    case 'customers':
      return `
        <div class="form-group">
          <label>Customer Full Name</label>
          <input type="text" id="field-name" placeholder="E.g., John Doe" required />
        </div>
        <div class="form-group">
          <label>Email Address</label>
          <input type="email" id="field-email" placeholder="E.g., john@example.com" required />
        </div>
        <div class="form-group">
          <label>Phone Number</label>
          <input type="text" id="field-phone" placeholder="E.g., +1 555-0199" />
        </div>
        <div class="form-group">
          <label>City Location</label>
          <input type="text" id="field-city" placeholder="E.g., San Francisco" />
        </div>
        <div class="form-group">
          <label>Join Date</label>
          <input type="date" id="field-join_date" required />
        </div>
      `;
    case 'employees':
      return `
        <div class="form-group">
          <label>Employee Name</label>
          <input type="text" id="field-name" placeholder="E.g., Asha Kumar" required />
        </div>
        <div class="form-group">
          <label>Role</label>
          <input type="text" id="field-role" placeholder="E.g., Sales Manager" required />
        </div>
        <div class="form-group">
          <label>Department</label>
          <input type="text" id="field-department" placeholder="E.g., Sales" />
        </div>
        <div class="form-group">
          <label>Salary ($)</label>
          <input type="number" step="0.01" id="field-salary" required />
        </div>
      `;
    case 'payments':
      return `
        <div class="form-group">
          <label>Customer</label>
          <select id="field-customer_id" required>${customerSelectOptions}</select>
        </div>
        <div class="form-group">
          <label>Amount Paid ($)</label>
          <input type="number" step="0.01" id="field-amount" required />
        </div>
        <div class="form-group">
          <label>Payment Method</label>
          <select id="field-payment_method" required>
            <option value="Card">Credit/Debit Card</option>
            <option value="Cash">Cash</option>
            <option value="UPI">UPI</option>
            <option value="Bank Transfer">Bank Transfer</option>
          </select>
        </div>
        <div class="form-group">
          <label>Payment Date</label>
          <input type="date" id="field-payment_date" required />
        </div>
      `;
  }
}

// Autofill/bind values to form inputs in Edit mode
function populateFormFields(record) {
  Object.keys(record).forEach(key => {
    const el = document.getElementById(`field-${key}`);
    if (el) {
      if (el.type === 'date') {
        el.value = record[key] ? record[key].substring(0, 10) : '';
      } else {
        el.value = record[key];
      }
    }
  });
}

// Automatically calculate Sale total amount on form input
function calculateSaleTotal() {
  const prodSelect = document.getElementById('field-product_id');
  const qtyInput = document.getElementById('field-quantity');
  const amountInput = document.getElementById('field-total_amount');
  
  if (!prodSelect || !qtyInput || !amountInput) return;

  const prodId = parseInt(prodSelect.value);
  const qty = parseInt(qtyInput.value) || 0;
  
  const product = dropdownOptions.products.find(p => p.id === prodId);
  if (product) {
    amountInput.value = (parseFloat(product.price) * qty).toFixed(2);
  }
}

// Handle Add/Edit form submission
async function handleFormSubmit(event) {
  event.preventDefault();
  const errorEl = document.getElementById('modal-error');
  errorEl.style.display = 'none';

  const recordId = document.getElementById('form-record-id').value;
  const payload = {};
  
  // Extract inputs
  const inputs = document.querySelectorAll('#modal-form-content input, #modal-form-content select, #modal-form-content textarea');
  inputs.forEach(input => {
    const key = input.id.replace('field-', '');
    let val = input.value;
    
    // Type conversion based on key properties
    if (key === 'quantity' || key === 'customer_id' || key === 'product_id' || key === 'stock') {
      val = parseInt(val);
    } else if (key === 'total_amount' || key === 'price' || key === 'salary' || key === 'amount') {
      val = parseFloat(val);
    }
    payload[key] = val;
  });

  try {
    let response;
    if (modalMode === 'add') {
      response = await request(`/${currentCrudTab}`, {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    } else {
      response = await request(`/${currentCrudTab}/${recordId}`, {
        method: 'PUT',
        body: JSON.stringify(payload)
      });
    }

    if (response) {
      closeCrudModal();
      await loadDropdownData(); // Refresh lookup drop-down definitions
      await loadCrudData(currentCrudTab); // Refresh table view
    }
  } catch (error) {
    errorEl.textContent = "Error saving: " + (error.message || error);
    errorEl.style.display = 'block';
  }
}

// Edit handler
function editRecord(recordId) {
  openCrudModal('edit', recordId);
}

// Delete Handler
async function deleteRecord(recordId) {
  if (!confirm("Are you sure you want to delete this record? This action cannot be undone.")) return;
  try {
    await request(`/${currentCrudTab}/${recordId}`, { method: 'DELETE' });
    await loadDropdownData();
    await loadCrudData(currentCrudTab);
  } catch (error) {
    alert("Error deleting record: " + error.message);
  }
}

// 6. ML Model Training Request
async function trainMLModel() {
  const trainBtn = document.getElementById('btn-train-model');
  const statusEl = document.getElementById('training-status');
  
  trainBtn.disabled = true;
  trainBtn.textContent = 'Training Model...';
  statusEl.textContent = 'Mapping variables, fitting weights... please wait.';
  
  try {
    const result = await request('/prediction/train', { method: 'POST' });
    statusEl.textContent = 'Success! Model fit completed. Projecting revenue...';
    setTimeout(async () => {
      // Reload dashboard predictions
      await loadDashboard();
      trainBtn.disabled = false;
      trainBtn.textContent = 'Re-Train Model';
      statusEl.textContent = 'Model successfully re-trained. Metrics active.';
    }, 1000);
  } catch (e) {
    statusEl.textContent = 'Model training error: ' + e.message;
    trainBtn.disabled = false;
    trainBtn.textContent = 'Re-Train Model';
  }
}

// 7. Chatbot Drawer interactions
function toggleChat() {
  const chatWidget = document.getElementById('chat-widget');
  chatWidget.classList.toggle('active');
  
  if (chatWidget.classList.contains('active')) {
    document.getElementById('chat-input').focus();
  }
}

async function sendChatMessage() {
  const inputEl = document.getElementById('chat-input');
  const historyEl = document.getElementById('chat-history');
  const message = inputEl.value.trim();
  
  if (!message) return;
  
  // Render user message bubble
  historyEl.innerHTML += `<div class="chat-bubble chat-bubble-user">${escapeHtml(message)}</div>`;
  inputEl.value = '';
  historyEl.scrollTop = historyEl.scrollHeight;

  // Render typing indicator bubble
  const typingId = 'typing-' + Date.now();
  historyEl.innerHTML += `
    <div class="chat-bubble chat-bubble-assistant" id="${typingId}">
      <div class="typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    </div>
  `;
  historyEl.scrollTop = historyEl.scrollHeight;

  try {
    const response = await request('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message })
    });
    
    // Remove typing bubble and render result
    const typingBubble = document.getElementById(typingId);
    if (typingBubble) typingBubble.remove();
    
    const formattedReply = formatMarkdown(response.reply || "No reply received from analytics engine.");
    historyEl.innerHTML += `<div class="chat-bubble chat-bubble-assistant">${formattedReply}</div>`;
  } catch (e) {
    const typingBubble = document.getElementById(typingId);
    if (typingBubble) typingBubble.remove();
    historyEl.innerHTML += `<div class="chat-bubble chat-bubble-assistant">⚠️ Assistant failed to respond: ${e.message}</div>`;
  }
  historyEl.scrollTop = historyEl.scrollHeight;
}

function handleChatKeyDown(event) {
  if (event.key === 'Enter') {
    sendChatMessage();
  }
}

// Formatting helpers
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatMarkdown(text) {
  // Bold formatting
  let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Bullet lists
  if (formatted.includes('- ')) {
    const lines = formatted.split('\n');
    let inList = false;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].startsWith('- ')) {
        const content = lines[i].substring(2);
        if (!inList) {
          lines[i] = '<ul><li>' + content + '</li>';
          inList = true;
        } else {
          lines[i] = '<li>' + content + '</li>';
        }
      } else {
        if (inList) {
          lines[i] = '</ul>' + lines[i];
          inList = false;
        }
      }
    }
    if (inList) {
      lines[lines.length - 1] += '</ul>';
    }
    formatted = lines.join('\n');
  }

  // Convert newlines to breaks
  return formatted.replace(/\n/g, '<br>');
}

// Run initial configurations
updateImportLabel();
init();
