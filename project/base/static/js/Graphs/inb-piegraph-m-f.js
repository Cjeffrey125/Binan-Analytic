document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('pieGraph');
    canvas.width = 200;
    canvas.height = 240;
    const data = {
        labels: ['Female', 'Male'],
        datasets: [{
            label: 'My First Dataset',
            data: [300, 100],
            backgroundColor: ['rgb(255, 99, 132)', 'rgb(54, 162, 235)'],
            hoverOffset: 4,
            borderWidth: 0,
        }],
    };

    const ctx = canvas.getContext('2d');

    const myChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'right',
                    align: 'middle',
                    labels: {
                        boxWidth: 13, 
                    },
                },
            },
            layout: {
                padding: {
                    left: 0,
                    right: 0,
                    top: 0,
                    bottom: 16,
                },
            },
        },
    });
});
