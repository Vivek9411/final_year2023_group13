/**
 * Food items management functionality
 * Handles food item creation, editing, and deletion
 */

document.addEventListener('DOMContentLoaded', function() {
  // Setup data table for food items if it exists
  const foodItemsTable = document.getElementById('foodItemsTable');
  if (foodItemsTable) {
    // Add form validation
    const foodItemForm = document.querySelector('form[action*="food_item"]');
    if (foodItemForm) {
      foodItemForm.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Get all required inputs
        const requiredInputs = this.querySelectorAll('[required]');
        requiredInputs.forEach(input => {
          if (!input.value.trim()) {
            isValid = false;
            input.classList.add('is-invalid');
          } else {
            input.classList.remove('is-invalid');
          }
        });
        
        // Get all numeric inputs
        const numericInputs = this.querySelectorAll('input[type="number"], input[class*="float"]');
        numericInputs.forEach(input => {
          const value = parseFloat(input.value);
          if (isNaN(value) || value < 0) {
            isValid = false;
            input.classList.add('is-invalid');
            
            // Add invalid feedback if not present
            let feedback = input.nextElementSibling;
            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
              feedback = document.createElement('div');
              feedback.className = 'invalid-feedback';
              input.parentNode.insertBefore(feedback, input.nextSibling);
            }
            feedback.textContent = 'Please enter a valid positive number';
          } else {
            input.classList.remove('is-invalid');
          }
        });
        
        if (!isValid) {
          e.preventDefault();
          return false;
        }
        
        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
        
        // Let the form submit normally
        return true;
      });
    }
    
    // Handle delete button confirmations
    const deleteButtons = document.querySelectorAll('button[data-bs-target*="deleteModal"]');
    deleteButtons.forEach(button => {
      button.addEventListener('click', function() {
        const modalId = this.getAttribute('data-bs-target');
        const modal = document.querySelector(modalId);
        
        if (modal) {
          const deleteForm = modal.querySelector('form');
          const deleteButton = deleteForm.querySelector('button[type="submit"]');
          
          deleteButton.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
            deleteForm.submit();
          });
        }
      });
    });
  }
  
  // Add numeric input validation for all numeric fields
  const numericInputs = document.querySelectorAll('input[type="number"], input[name*="calories"], input[name*="protein"], input[name*="carbohydrates"], input[name*="fiber"], input[name*="sugar"], input[name*="sodium"], input[name*="quantity"]');
  
  numericInputs.forEach(input => {
    input.addEventListener('input', function() {
      const value = this.value;
      if (value !== '' && (isNaN(parseFloat(value)) || parseFloat(value) < 0)) {
        this.classList.add('is-invalid');
      } else {
        this.classList.remove('is-invalid');
      }
    });
  });
});
