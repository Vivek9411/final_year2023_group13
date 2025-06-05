/**
 * Meals management functionality
 * Handles meal creation, editing, and management of meal items
 */

document.addEventListener('DOMContentLoaded', function() {
  // Setup food item search with autocomplete
  const setupFoodSearch = () => {
    const searchInputs = document.querySelectorAll('input[id^="food-search-"]');
    
    searchInputs.forEach(input => {
      const mealId = input.id.split('-').pop();
      const resultsDropdown = document.getElementById(`search-results-${mealId}`);
      const hiddenSelect = input.closest('form').querySelector('select[name="custom_item_id"]');
      const selectedFoodDiv = document.getElementById(`selected-food-${mealId}`);
      const selectedFoodName = document.getElementById(`selected-food-name-${mealId}`);
      const selectedFoodCalories = document.getElementById(`selected-food-calories-${mealId}`);
      
      // Debounce function to limit API calls
      let debounceTimer;
      const debounce = (callback, time) => {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(callback, time);
      };
      
      // Search food items via API
      const searchFoodItems = (query) => {
        fetch(`/search_food_items?query=${encodeURIComponent(query)}`)
          .then(response => response.json())
          .then(data => {
            resultsDropdown.innerHTML = '';
            
            if (data.length === 0) {
              const noResults = document.createElement('span');
              noResults.className = 'dropdown-item text-muted';
              noResults.textContent = 'No items found';
              resultsDropdown.appendChild(noResults);
            } else {
              data.forEach(item => {
                const option = document.createElement('a');
                option.className = 'dropdown-item';
                option.href = '#';
                option.textContent = item.display;
                option.dataset.id = item.id;
                option.dataset.name = item.name;
                option.dataset.calories = item.calories;
                
                option.addEventListener('click', (e) => {
                  e.preventDefault();
                  
                  // Set the hidden select value
                  hiddenSelect.value = item.id;
                  
                  // Update the input to show selected item
                  input.value = item.name;
                  
                  // Show the selected food card
                  selectedFoodDiv.classList.remove('d-none');
                  selectedFoodName.textContent = item.name;
                  selectedFoodCalories.textContent = `${item.calories} cal`;
                  
                  // Hide dropdown
                  resultsDropdown.classList.remove('show');
                });
                
                resultsDropdown.appendChild(option);
              });
            }
            
            // Show dropdown
            resultsDropdown.classList.add('show');
          })
          .catch(error => {
            console.error('Error searching food items:', error);
          });
      };
      
      // Handle input events
      input.addEventListener('input', () => {
        const query = input.value.trim();
        
        if (query.length < 2) {
          resultsDropdown.classList.remove('show');
          return;
        }
        
        debounce(() => searchFoodItems(query), 300);
      });
      
      // Hide dropdown when clicking outside
      document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !resultsDropdown.contains(e.target)) {
          resultsDropdown.classList.remove('show');
        }
      });
      
      // Handle focus
      input.addEventListener('focus', () => {
        const query = input.value.trim();
        if (query.length >= 2) {
          searchFoodItems(query);
        }
      });
    });
  };
  
  // Initialize food search
  setupFoodSearch();
  
  // Handle meal form submission
  const mealForm = document.querySelector('form[action="/add_meal"]');
  if (mealForm) {
    mealForm.addEventListener('submit', function(e) {
      const nameInput = document.getElementById('name');
      if (!nameInput.value.trim()) {
        e.preventDefault();
        nameInput.classList.add('is-invalid');
        
        // Add invalid feedback if not present
        let feedback = nameInput.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
          feedback = document.createElement('div');
          feedback.className = 'invalid-feedback';
          nameInput.parentNode.insertBefore(feedback, nameInput.nextSibling);
          feedback.textContent = 'Please enter a meal name';
        }
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
  
  // Handle meal item form submission
  const mealItemForms = document.querySelectorAll('form[action*="add_meal_item"]');
  mealItemForms.forEach(form => {
    form.addEventListener('submit', function(e) {
      let isValid = true;
      
      // Check hidden select
      const foodItemSelect = this.querySelector('select[name="custom_item_id"]');
      if (foodItemSelect && (!foodItemSelect.value || foodItemSelect.value === '')) {
        isValid = false;
        
        // Get the associated search input
        const searchInput = this.querySelector('input[id^="food-search-"]');
        if (searchInput) {
          searchInput.classList.add('is-invalid');
          
          // Add invalid feedback if not present
          let feedback = searchInput.closest('.input-group').nextElementSibling;
          if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            searchInput.closest('.input-group').parentNode.insertBefore(feedback, searchInput.closest('.input-group').nextSibling);
          }
          feedback.textContent = 'Please select a food item';
        }
      } else if (foodItemSelect) {
        const searchInput = this.querySelector('input[id^="food-search-"]');
        if (searchInput) {
          searchInput.classList.remove('is-invalid');
        }
      }
      
      // Check quantity
      const quantityInput = this.querySelector('input[name="quantity"]');
      if (quantityInput) {
        const quantity = parseFloat(quantityInput.value);
        if (isNaN(quantity) || quantity <= 0) {
          isValid = false;
          quantityInput.classList.add('is-invalid');
          
          // Add invalid feedback if not present
          let feedback = quantityInput.nextElementSibling;
          if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            quantityInput.parentNode.insertBefore(feedback, quantityInput.nextSibling);
          }
          feedback.textContent = 'Please enter a valid positive number';
        } else {
          quantityInput.classList.remove('is-invalid');
        }
      }
      
      if (!isValid) {
        e.preventDefault();
        return false;
      }
      
      // Show loading state
      const submitBtn = this.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
      
      // Let the form submit normally
      return true;
    });
  });
  
  // Handle delete buttons for meal items
  const deleteMealItemButtons = document.querySelectorAll('form[action*="delete_meal_item"] button');
  deleteMealItemButtons.forEach(button => {
    button.addEventListener('click', function() {
      this.disabled = true;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
      this.closest('form').submit();
    });
  });
  
  // Handle "Add to Food Log" buttons
  const addToLogForms = document.querySelectorAll('form[action*="add_meal_to_log"]');
  addToLogForms.forEach(form => {
    form.addEventListener('submit', function() {
      const button = this.querySelector('button');
      if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
      }
    });
  });
  
  // Handle delete meal buttons
  const deleteMealButtons = document.querySelectorAll('form[action*="delete_meal"] button[type="submit"]');
  deleteMealButtons.forEach(button => {
    button.addEventListener('click', function() {
      this.disabled = true;
      this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
      this.closest('form').submit();
    });
  });
});
