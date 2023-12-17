document.addEventListener('DOMContentLoaded', function () {
    var ctx = document.getElementById('lineGraph').getContext('2d');

    const data = {
        labels: ['2018', '2019', '2020', '2023', '2024', '2025'],
        datasets: [
            {
                label: 'Accepted',
                data: [40, 40, 25, 50, 45, 35, 60],
                borderColor: '#50DD89', 
                backgroundColor: '#50DD89', 
            },
            {
                label: 'Applied',
                data: [40, 60, 40, 70, 65, 55, 80],
                borderColor: '#0085FF', 
                backgroundColor: '#0085FF', 
            }
        ]
    };

    var myChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
        }
    });
});
