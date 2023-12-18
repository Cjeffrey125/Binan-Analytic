document.addEventListener('DOMContentLoaded', function () {
    var ctx = document.getElementById('stackBar').getContext('2d');

    const DATA_COUNT = 9;
    const NUMBER_CFG = { count: DATA_COUNT, min: 0, max: 100 };

    const customLabels = [
        'Colegio San Agustin',
        'Citi Global College',
        'Guardians Bonafide For Hope Foundation Philippines',
        'La Consolacion College',
        'Polytechnic University of the Philippines - Biñan Campus',
        'Trimex Colleges", "Trimex Colleges',
        'Saint Michaels College of Laguna',
        'UPH-DR. Jose G. Tamayo Medical University',
        'University of Perpetual Help System Laguna',
    ];

    const backgroundColors = customLabels.map(() => `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 0.5)`);

    const data = {
        labels: customLabels,
        datasets: [
            {
                label: 'Dataset 1',
                data: Array.from({ length: DATA_COUNT }, () => Math.floor(Math.random() * (NUMBER_CFG.max - NUMBER_CFG.min + 1)) + NUMBER_CFG.min),
                backgroundColor: backgroundColors,
            },
        ]
    };

    var stackHorizontalChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    stacked: true,
                },
                y: {
                    stacked: true
                }
            },
            plugins: {
                legend: {
                    display: false, 
                }
            }
        }
    });

    window.addEventListener('resize', function () {
        stackHorizontalChart.resize();
    });
});
