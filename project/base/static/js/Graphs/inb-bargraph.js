document.addEventListener('DOMContentLoaded', function () {
    var ctx = document.getElementById('barGraph').getContext('2d');

    const labels = ['1st Year', '2nd Year', '3rd Year', '4th Year', '5th Year'];
    const data = {
        labels: labels,
        datasets: [
            {
                label: 'Combined Datasets',
                data: [10, 20, 30, 20, 15], 
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(255, 205, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)' 
                ],
                borderColor: [
                    'rgb(255, 99, 132)',
                    'rgb(255, 159, 64)',
                    'rgb(255, 205, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(153, 102, 255)' 
                ],
                borderWidth: 1
            }
        ]
    };

    var barChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: false  
                }
            }
        }
    });

    window.addEventListener('resize', function () {
        barChart.resize();
    });
});
