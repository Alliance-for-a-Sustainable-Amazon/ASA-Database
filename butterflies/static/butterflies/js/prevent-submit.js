/**
 * prevent-submit.js
 * This script prevents the Enter key from submitting forms unless it's pressed within a textarea 
 * or when a submit button is explicitly clicked.
 */
document.addEventListener('DOMContentLoaded', function() {
  // Get all forms on the page
  const forms = document.querySelectorAll('form');
  
  // Add event listeners to each form
  forms.forEach(function(form) {
    form.addEventListener('keypress', function(e) {
      // Check if Enter key was pressed
      if (e.key === 'Enter' || e.keyCode === 13) {
        // Allow Enter in textareas 
        if (e.target.tagName.toLowerCase() === 'textarea') {
          return true;
        }
        
        // Allow Enter if Shift+Enter is pressed (line break in text inputs)
        if (e.shiftKey) {
          return true;
        }
        
        // Prevent the default action (form submission) for all other cases
        e.preventDefault();
        
        // If you want to move focus to the next field instead
        if (e.target.form) {
          const formElements = Array.from(e.target.form.elements);
          const currentIndex = formElements.indexOf(e.target);
          const nextElement = formElements[currentIndex + 1];
          
          if (nextElement) {
            nextElement.focus();
          }
        }
        
        return false;
      }
    });
  });
  
  // Add explicit click handler for submit buttons
  const submitButtons = document.querySelectorAll('button[type="submit"], input[type="submit"]');
  submitButtons.forEach(function(button) {
    button.addEventListener('click', function(e) {
      // Allow the form submission when the submit button is clicked
    });
  });
});
