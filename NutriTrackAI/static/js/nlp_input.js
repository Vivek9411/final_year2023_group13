/**
 * Natural language processing input functionality
 * Handles the natural language input form and provides suggestions
 */

document.addEventListener('DOMContentLoaded', function() {
  const nlpInput = document.getElementById('query');
  const suggestionsContainer = document.createElement('div');
  suggestionsContainer.className = 'suggestions-container mt-2';
  
  // Only setup if we have the NLP input field
  if (nlpInput) {
    // Insert suggestions container after the input
    nlpInput.parentNode.insertBefore(suggestionsContainer, nlpInput.nextSibling);
    
    // Example patterns to help users
    const examplePatterns = [
      "I ate two apples",
      "I ran for 30 minutes",
      "I had a banana and a glass of milk",
      "I walked for 45 minutes",
      "I ate a bowl of rice",
      "I cycled for an hour",
      "I had three eggs for breakfast",
      "I did yoga for 20 minutes"
    ];
    
    // Add examples as suggestions
    const suggestionsList = document.createElement('div');
    suggestionsList.className = 'form-text mb-2';
    suggestionsList.innerHTML = '<strong>Examples:</strong>';
    suggestionsContainer.appendChild(suggestionsList);
    
    const examplesList = document.createElement('div');
    examplesList.className = 'd-flex flex-wrap gap-2';
    
    examplePatterns.forEach(pattern => {
      const pill = document.createElement('span');
      pill.className = 'badge bg-secondary';
      pill.textContent = pattern;
      pill.style.cursor = 'pointer';
      pill.addEventListener('click', () => {
        nlpInput.value = pattern;
        nlpInput.focus();
      });
      examplesList.appendChild(pill);
    });
    
    suggestionsContainer.appendChild(examplesList);
    
    // Handle input changes
    nlpInput.addEventListener('input', function() {
      if (this.value.length > 0) {
        suggestionsContainer.classList.add('d-none');
      } else {
        suggestionsContainer.classList.remove('d-none');
      }
    });
    
    // Show examples when input is focused
    nlpInput.addEventListener('focus', function() {
      if (this.value.length === 0) {
        suggestionsContainer.classList.remove('d-none');
      }
    });
  }
  
  // Process the form data
  const processingForm = document.getElementById('nlp-form');
  if (processingForm) {
    processingForm.addEventListener('submit', function(e) {
      const input = document.getElementById('query').value.trim();
      
      if (input.length === 0) {
        e.preventDefault();
        return false;
      }
      
      // Show loading state
      const submitBtn = this.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
      
      // Let the form submit normally
      return true;
    });
  }
});
