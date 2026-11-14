/* Dashboard Charts Initialization */
document.addEventListener('DOMContentLoaded', function () {
  // ------- Views & Interactions Multi‑Line Chart -------
  const ctxViews = document.getElementById('viewsChart')?.getContext('2d');
  if (ctxViews) {
    new Chart(ctxViews, {
      type: 'line',
      data: {
        labels: window.monthly_labels || [],
        datasets: [
          {
            label: 'Vues',
            data: window.monthly_views || [],
            borderColor: '#2563eb', // esy‑blue‑600
            backgroundColor: 'rgba(37,99,235,0.1)',
            fill: true,
            tension: 0.3,
          },
          {
            label: 'WhatsApp',
            data: window.monthly_whatsapp || [],
            borderColor: '#10b981', // emerald‑600
            backgroundColor: 'rgba(16,185,129,0.1)',
            fill: true,
            tension: 0.3,
          },
          {
            label: 'Appels',
            data: window.monthly_calls || [],
            borderColor: '#6366f1', // indigo‑600
            backgroundColor: 'rgba(99,102,241,0.1)',
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: {
            backgroundColor: '#ffffff',
            titleColor: '#111827',
            bodyColor: '#374151',
            borderColor: '#e5e7eb',
            borderWidth: 1,
          },
        },
        scales: {
          y: { beginAtZero: true },
        },
      },
    });
  }

  // ------- Category Doughnut Chart -------
  const ctxCat = document.getElementById('categoryChart')?.getContext('2d');
  if (ctxCat) {
    const colors = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#ef4444', '#f97316'];
    new Chart(ctxCat, {
      type: 'doughnut',
      data: {
        labels: window.cat_labels || [],
        datasets: [
          {
            data: window.cat_data || [],
            backgroundColor: colors.slice(0, (window.cat_data || []).length),
            borderColor: '#ffffff',
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: {
            backgroundColor: '#ffffff',
            titleColor: '#111827',
            bodyColor: '#374151',
            borderColor: '#e5e7eb',
            borderWidth: 1,
          },
          datalabels: {
            color: '#111827',
            formatter: (value, ctx) => {
              const total = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
              const percent = total ? ((value / total) * 100).toFixed(1) + '%' : '';
              return percent;
            },
          },
        },
      },
    });
  }
});

