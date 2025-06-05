/**
 * Dashboard functionality for HealthTracker
 * Manages charts and dashboard interactions
 */

// Global variables to store chart instances
let weeklyChart = null;
let monthlyChart = null;
let yearlyChart = null;

// Initialize weekly chart with data passed from server
function initWeeklyChart(labels, caloriesIn, caloriesBurned) {
  const ctx = document.getElementById('weeklyChart').getContext('2d');
  weeklyChart = createCalorieChart(ctx, labels, caloriesIn, caloriesBurned);
}

// Function to load chart data for monthly and yearly views
function loadChartData(period) {
  // Show loading indicator
  const targetChart = period === 'month' ? 'monthlyChart' : 'yearlyChart';
  const chartElement = document.getElementById(targetChart);
  
  // Simple loading indicator
  chartElement.style.opacity = 0.5;
  
  fetchChartData(period)
    .then(data => {
      if (!data) {
        console.error('No data returned');
        return;
      }
      
      // Create or update the appropriate chart
      const ctx = chartElement.getContext('2d');
      
      if (period === 'month') {
        if (monthlyChart) {
          monthlyChart.destroy();
        }
        monthlyChart = createCalorieChart(ctx, data.labels, data.foodData, data.exerciseData);
      } else if (period === 'year') {
        if (yearlyChart) {
          yearlyChart.destroy();
        }
        yearlyChart = createCalorieChart(ctx, data.labels, data.foodData, data.exerciseData);
      }
      
      // Remove loading indicator
      chartElement.style.opacity = 1;
    })
    .catch(error => {
      console.error(`Error loading ${period} chart data:`, error);
      // Show error message in chart area
      chartElement.style.opacity = 1;
    });
}

// Initialize dashboard elements when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Track active tab for charts
  const chartTabs = document.querySelectorAll('[data-bs-toggle="tab"]');
  chartTabs.forEach(tab => {
    tab.addEventListener('shown.bs.tab', function(event) {
      const targetId = event.target.getAttribute('data-bs-target').replace('#', '');
      
      // Resize charts after tab change to fix rendering issues
      if (targetId === 'weekly' && weeklyChart) {
        weeklyChart.resize();
      } else if (targetId === 'monthly' && monthlyChart) {
        monthlyChart.resize();
      } else if (targetId === 'yearly' && yearlyChart) {
        yearlyChart.resize();
      }
    });
  });

  // Handle natural language input form submissions
  const nlpForm = document.querySelector('form[action="/process_query"]');
  if (nlpForm) {
    nlpForm.addEventListener('submit', function() {
      const submitButton = this.querySelector('button[type="submit"]');
      const originalText = submitButton.innerHTML;
      
      // Show loading state
      submitButton.disabled = true;
      submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
      
      // Form will submit normally
    });
  }
});
