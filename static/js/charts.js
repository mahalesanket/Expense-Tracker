function renderDashboardCharts(categories, categoryTotals, monthLabels, monthlyExpenses, monthlyIncome) {
    // Doughnut Chart Setup
    const ctxCat = document.getElementById('categoryChart')?.getContext('2d');
    if (ctxCat) {
        new Chart(ctxCat, {
            type: 'doughnut',
            data: {
                labels: categories,
                datasets: [{
                    data: categoryTotals,
                    backgroundColor: ['#2563EB', '#16A34A', '#F59E0B', '#DC2626', '#8B5CF6', '#EC4899']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Line Overview Chart Setup
    const ctxOverview = document.getElementById('overviewChart')?.getContext('2d');
    if (ctxOverview) {
        new Chart(ctxOverview, {
            type: 'line',
            data: {
                labels: monthLabels,
                datasets: [
                    { label: 'Income', data: monthlyIncome, borderColor: '#16A34A', fill: false, tension: 0.3 },
                    { label: 'Expenses', data: monthlyExpenses, borderColor: '#DC2626', fill: false, tension: 0.3 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}