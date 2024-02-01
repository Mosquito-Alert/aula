$(document).ready(function(){
     // Your data for the chart
    var data = {
      labels: all_labels,
      datasets: [{
        data: all_data,
        backgroundColor: ["#6a176e","#932667","#bc3754","#dd513a","#f37819","#fca50a","#f6d746"]
      }]
    };

    // Configuration options
    var options = {
      cutoutPercentage: 50, // Adjust the cutout percentage to create a donut chart
      responsive: true,
      plugins: {
          legend: {
            position: 'right', // Position the legend to the right
            align: 'center',    // Align the legend to the start of the container
            fullWidth: false    // Do not use the full width of the container
          }
      }
    };

    // Get the canvas element
    var ctx = document.getElementById('myDonutChart').getContext('2d');

    // Create the donut chart
    var myDonutChart = new Chart(ctx, {
      type: 'doughnut',
      data: data,
      options: options
    });

});
