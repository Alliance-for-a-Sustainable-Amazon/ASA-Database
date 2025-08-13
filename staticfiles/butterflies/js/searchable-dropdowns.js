// Standardized script for searchable, clickable dropdowns
document.addEventListener('DOMContentLoaded', function() {
    // Find all select elements in the form - make ALL dropdowns searchable
    document.querySelectorAll('form select:not([disabled])').forEach(select => {
        // Only enhance if it has options
        if (select.options && select.options.length > 1) {
            enhanceSelectWithDropdown(select);
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        document.querySelectorAll('.searchable-dropdown').forEach(dropdown => {
            dropdown.style.display = 'none';
        });
    });
});

// Function to convert a select to input + dropdown
function enhanceSelectWithDropdown(select) {
    if (!select || select.tagName !== 'SELECT') return;
    
    // Create elements
    const wrapper = document.createElement('div');
    wrapper.className = 'searchable-wrapper';
    wrapper.style.width = Math.max(select.offsetWidth, 150) + 'px';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'searchable-input';
    
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = select.name;
    
    const dropdown = document.createElement('div');
    dropdown.className = 'searchable-dropdown';
    dropdown.setAttribute('role', 'listbox');
    
    // Set placeholder based on data attributes or label
    const placeholder = getPlaceholder(select);
    input.placeholder = placeholder;
    
    // Copy accessibility attributes
    if (select.getAttribute('aria-label')) input.setAttribute('aria-label', select.getAttribute('aria-label'));
    if (select.getAttribute('required')) input.setAttribute('required', 'required');
    
    // Process options
    const valueMap = {};
    const allOptions = [];
    
    // Set initial selected value if any
    const selectedOption = select.options[select.selectedIndex];
    if (selectedOption && selectedOption.value) {
        input.value = selectedOption.text;
        hiddenInput.value = selectedOption.value;
    }
    
    // Create dropdown options
    Array.from(select.options).forEach(option => {
        if (!option.value) return;
        
        const optionDiv = document.createElement('div');
        optionDiv.className = 'searchable-option';
        optionDiv.setAttribute('role', 'option');
        optionDiv.textContent = option.text;
        optionDiv.setAttribute('data-value', option.value);
        dropdown.appendChild(optionDiv);
        
        valueMap[option.text] = option.value;
        allOptions.push({
            text: option.text,
            value: option.value,
            element: optionDiv
        });
        
        // Option click handler
        optionDiv.addEventListener('click', function(e) {
            e.stopPropagation();
            input.value = this.textContent;
            hiddenInput.value = this.getAttribute('data-value');
            dropdown.style.display = 'none';
        });
    });
    
    // Input click handler - toggle dropdown
    input.addEventListener('click', function(e) {
        e.stopPropagation();
        
        // Close any open dropdowns first
        document.querySelectorAll('.searchable-dropdown').forEach(el => {
            el.style.display = 'none';
        });
        
        const isShowing = dropdown.style.display === 'block';
        dropdown.style.display = isShowing ? 'none' : 'block';
        
        if (!isShowing) filterDropdown(input.value);
    });
    
    // Input typing handler
    input.addEventListener('input', function() {
        filterDropdown(this.value);
        dropdown.style.display = 'block';
        hiddenInput.value = valueMap[this.value] || '';
    });
    
    // Keyboard navigation
    input.addEventListener('keydown', function(e) {
        if (dropdown.style.display !== 'block') return;
        
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            navigateDropdown(e.key === 'ArrowDown' ? 1 : -1);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            // Find highlighted option or first visible option
            const highlighted = dropdown.querySelector('.highlighted') || 
                                Array.from(dropdown.querySelectorAll('.searchable-option'))
                                     .find(opt => opt.style.display !== 'none');
            
            if (highlighted) {
                input.value = highlighted.textContent;
                hiddenInput.value = highlighted.getAttribute('data-value');
                dropdown.style.display = 'none';
            }
        } else if (e.key === 'Escape') {
            dropdown.style.display = 'none';
        }
    });
    
    // Clear invalid input on blur
    input.addEventListener('blur', function() {
        setTimeout(() => {
            if (!valueMap[input.value]) {
                input.value = '';
                hiddenInput.value = '';
            }
        }, 200);
    });
    
    // Assemble and insert the elements
    wrapper.appendChild(input);
    wrapper.appendChild(hiddenInput);
    wrapper.appendChild(dropdown);
    
    const parent = select.parentNode;
    parent.insertBefore(wrapper, select);
    parent.removeChild(select);
    
    // Helper function to filter dropdown options
    function filterDropdown(searchText) {
        const query = searchText.toLowerCase().trim();
        let visibleCount = 0;
        
        // Clear highlights
        dropdown.querySelector('.highlighted')?.classList.remove('highlighted');
        
        allOptions.forEach(opt => {
            const textLower = opt.text.toLowerCase();
            const isMatch = query === '' || 
                textLower.includes(query) || 
                textLower.split(' ').some(word => word.startsWith(query));
            
            opt.element.style.display = isMatch ? '' : 'none';
            if (isMatch) visibleCount++;
        });
        
        dropdown.style.display = visibleCount > 0 ? 'block' : 'none';
    }
    
    // Helper function for keyboard navigation
    function navigateDropdown(direction) {
        const visibleOptions = Array.from(dropdown.querySelectorAll('.searchable-option'))
            .filter(opt => opt.style.display !== 'none');
        
        if (visibleOptions.length === 0) return;
        
        // Find current highlighted index
        let currentIndex = -1;
        visibleOptions.forEach((opt, i) => {
            if (opt.classList.contains('highlighted')) currentIndex = i;
        });
        
        // Clear existing highlight
        dropdown.querySelector('.highlighted')?.classList.remove('highlighted');
        
        // Calculate new index
        let newIndex = currentIndex + direction;
        if (newIndex < 0) newIndex = visibleOptions.length - 1;
        if (newIndex >= visibleOptions.length) newIndex = 0;
        
        // Apply highlight and scroll
        visibleOptions[newIndex].classList.add('highlighted');
        visibleOptions[newIndex].scrollIntoView({ block: 'nearest' });
    }
}

// Helper function to determine appropriate placeholder text
function getPlaceholder(select) {
    // First priority: Use data-label attribute if present
    if (select.dataset.label) {
        return "Select " + select.dataset.label + "...";
    }
    
    // Second priority: Try to find associated label
    let label = null;
    
    if (select.id) {
        label = document.querySelector('label[for="' + select.id + '"]');
    }
    
    if (!label) {
        const parent = select.parentNode;
        if (parent) label = parent.querySelector('label');
    }
    
    if (label) {
        const labelText = label.textContent.trim().replace(':', '');
        return "Select " + labelText + "...";
    }
    
    // Default
    return "Select...";
}
