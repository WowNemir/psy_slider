// Define a function to draw the graph
function drawGraph() {
    // Get the canvas element
    var ctx = document.getElementById('userGraph').getContext('2d');

    // Static data for the chart
    var data = {
        labels: ['Choice 1', 'Choice 2', 'Choice 3', 'Choice 4'],
        datasets: [{
            label: 'User Choices',
            data: [10, 20, 15, 25], // Static counts for each choice
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    };

    // Create the chart
    var userGraph = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });
}

// Call the drawGraph function when the DOM content is loaded
document.addEventListener('DOMContentLoaded', drawGraph);
