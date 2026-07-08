async function loadDashboard() {
  try {
    const summary = await request('/analytics/summary');
    const monthly = await request('/analytics/monthly-sales');
    const topProducts = await request('/analytics/top-products');

    const cards = document.getElementById('summary-cards');
    cards.innerHTML = `
      <div class="card"><h3>Total Revenue</h3><p>$${summary.total_revenue}</p></div>
      <div class="card"><h3>Customers</h3><p>${summary.total_customers}</p></div>
      <div class="card"><h3>Sales</h3><p>${summary.total_sales}</p></div>
      <div class="card"><h3>Employees</h3><p>${summary.total_employees}</p></div>
    `;

    const revenueCtx = document.getElementById('revenue-chart').getContext('2d');
    new Chart(revenueCtx, {
      type: 'line',
      data: {
        labels: monthly.map((item) => item.month),
        datasets: [{ label: 'Revenue', data: monthly.map((item) => item.revenue), borderColor: '#3b82f6', fill: false }],
      },
    });

    const productsCtx = document.getElementById('products-chart').getContext('2d');
    new Chart(productsCtx, {
      type: 'bar',
      data: {
        labels: topProducts.map((item) => item.product),
        datasets: [{ label: 'Units Sold', data: topProducts.map((item) => item.sales), backgroundColor: '#60a5fa' }],
      },
    });

    document.getElementById('insights-list').innerHTML = `
      <li>Revenue is tracking at $${summary.total_revenue} across ${summary.total_sales} sales.</li>
      <li>${summary.total_customers} customers are currently in the database.</li>
      <li>Top performing products are updated from the analytics endpoint.</li>
    `;
  } catch (error) {
    document.getElementById('summary-cards').innerHTML = `<div class="card">${error.message}</div>`;
  }
}

loadDashboard();
