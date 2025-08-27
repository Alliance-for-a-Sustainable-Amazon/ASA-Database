/**
 * required-fields.js
 * This script adds the 'required' attribute to all visible form fields in the specimen form.
 * It only applies to fields that are visibly rendered on the page and skips hidden or disabled fields.
 */
document.addEventListener('DOMContentLoaded', function() {
  // Only apply to specimen form - check for a specific element that indicates we're on the specimen form
  const formTitle = document.querySelector('h2');
  if (!formTitle || !formTitle.textContent.includes('Add Single Record')) {
    return; // Not on the specimen form page, so don't run the script
  }
  
  const form = document.querySelector('form');
  if (!form) return;
  
  console.log('Applying required field validation to specimen form');
  
  // Insert at the beginning of the form
  if (form.firstChild) {
    form.insertBefore(legendDiv, form.firstChild);
  } else {
    form.appendChild(legendDiv);
  }
  
  // Process all inputs, selects and textareas that are visible
  const formElements = form.querySelectorAll('input, select, textarea');
  
  formElements.forEach(function(element) {
    // Skip hidden fields, submit buttons, and already required fields
    if (element.type === 'hidden' || element.type === 'submit' || element.hasAttribute('required')) {
      return;
    }
    
    // Skip fields in hidden containers
    let parent = element.parentElement;
    let isHidden = false;
    while (parent && parent !== form) {
      const style = window.getComputedStyle(parent);
      if (style.display === 'none' || style.visibility === 'hidden') {
        isHidden = true;
        break;
      }
      parent = parent.parentElement;
    }
    
    // Skip disabled fields and fields with 'data-optional' attribute
    if (element.disabled || element.hasAttribute('data-optional')) {
      return;
    }
    
    // Check if element is actually visible (has dimensions)
    const rect = element.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
      isHidden = true;
    }
    
    // Add required attribute to visible fields
    if (!isHidden) {
      // For selects with an empty first option, make sure they have to choose a non-empty option
      if (element.tagName === 'SELECT' && element.options.length > 0 && element.options[0].value === '') {
        element.setAttribute('required', 'required');
      } 
      // For all other field types
      else if (element.tagName !== 'SELECT') {
        element.setAttribute('required', 'required');
      }
      
      // Add visual indicator (red asterisk) to labels
      const label = findLabelForElement(element);
      if (label && !label.innerHTML.includes('*')) {
        label.innerHTML += ' <span style="color: red;">*</span>';
      }
    }
  });
  
  // Helper function to find a label for an element
  function findLabelForElement(element) {
    // First try to find a label with a matching 'for' attribute
    if (element.id) {
      const label = document.querySelector('label[for="' + element.id + '"]');
      if (label) return label;
    }
    
    // Then check if the element is inside a label
    let parent = element.parentElement;
    while (parent) {
      if (parent.tagName === 'LABEL') {
        return parent;
      }
      parent = parent.parentElement;
    }
    
    return null;
  }
  
  // Add form validation message area at the top of the form
  const messageDiv = document.createElement('div');
  messageDiv.id = 'form-validation-message';
  messageDiv.className = 'validation-message';
  messageDiv.style.color = 'red';
  messageDiv.style.marginBottom = '15px';
  messageDiv.style.padding = '10px';
  messageDiv.style.border = '1px solid red';
  messageDiv.style.borderRadius = '5px';
  messageDiv.style.display = 'none';
  messageDiv.textContent = 'Please fill in all required fields marked with *';
  
  // Insert after the legend
  form.insertBefore(messageDiv, legendDiv.nextSibling);
  
  // Show validation message when form is submitted with invalid fields
  form.addEventListener('submit', function(event) {
    // Focus lost trigger validation
    document.activeElement.blur();
    
    // Check for invalid fields after a short delay to allow validation to complete
    setTimeout(function() {
      const invalidFields = form.querySelectorAll(':invalid');
      if (invalidFields.length > 0) {
        messageDiv.style.display = 'block';
        
        // Scroll to the first invalid field
        invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
        invalidFields[0].focus();
        
        // Prevent form submission
        event.preventDefault();
      } else {
        messageDiv.style.display = 'none';
      }
    }, 50);
  });
  
  // Add live validation as user fills out the form
  formElements.forEach(function(element) {
    if (element.hasAttribute('required')) {
      element.addEventListener('blur', function() {
        // Validate the field when focus leaves
        if (!element.validity.valid) {
          element.classList.add('invalid-field');
          // Add custom styling for invalid fields
          element.style.borderColor = '#dc3545';
          element.style.boxShadow = '0 0 0 0.2rem rgba(220, 53, 69, 0.25)';
        } else {
          element.classList.remove('invalid-field');
          // Reset styling
          element.style.borderColor = '';
          element.style.boxShadow = '';
        }
      });
      
      // Clear invalid styling when user starts typing
      element.addEventListener('input', function() {
        element.classList.remove('invalid-field');
        element.style.borderColor = '';
        element.style.boxShadow = '';
      });
    }
  });
});
