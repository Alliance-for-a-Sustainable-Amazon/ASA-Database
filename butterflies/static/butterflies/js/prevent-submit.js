/**
 * prevent-submit.js
 * This script prevents the Enter key from submitting forms unless it's pressed within a textarea 
 * or when a submit button is explicitly clicked.
 * 
 * Modified to handle required fields validation - still prevents form submission on Enter
 * but focuses on the next field as before.
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
        
        // Trigger field validation without submitting
        if (e.target.checkValidity) {
          e.target.checkValidity();
        }
        
        // Move focus to the next field instead
        if (e.target.form) {
          const formElements = Array.from(e.target.form.elements).filter(el => 
            !el.disabled && 
            el.type !== 'hidden' && 
            getComputedStyle(el).display !== 'none' &&
            el.tabIndex !== -1
          );
          
          const currentIndex = formElements.indexOf(e.target);
          const nextElement = formElements[currentIndex + 1];
          
          if (nextElement) {
            nextElement.focus();
            
            // If it's a select element, trigger the dropdown
            if (nextElement.tagName.toLowerCase() === 'select') {
              // Simulate a click to open the dropdown
              const clickEvent = new MouseEvent('mousedown', {
                bubbles: true,
                cancelable: true,
                view: window
              });
              nextElement.dispatchEvent(clickEvent);
            }
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
      // Validate all fields before allowing submission
      const form = button.form;
      if (form) {
        const requiredFields = form.querySelectorAll('[required]');
        let allValid = true;
        
        requiredFields.forEach(field => {
          if (!field.checkValidity()) {
            allValid = false;
            field.classList.add('invalid-field');
          }
        });
        
        // Let the form's own validation handle the rest
      }
    });
  });
});
