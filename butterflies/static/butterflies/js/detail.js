document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('image-modal');
    if (!modal) return;

    const modalImg = document.getElementById('modal-image');
    const closeBtn = document.querySelector('.modal-close');
    const expandableImages = document.querySelectorAll('.expandable-image');

    // Open modal on image click
    expandableImages.forEach(img => {
        img.addEventListener('click', function() {
            modal.classList.add('show');
            modalImg.src = this.src;
        });
    });

    // Close modal on X click
    closeBtn.addEventListener('click', function() {
        modal.classList.remove('show');
    });

    // Close modal on outside click
    modal.addEventListener('click', function(event) {
        if (event.target === modal || event.target === document.querySelector('.modal-instruction')) {
            modal.classList.remove('show');
        }
    });

    // Close modal on Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && modal.classList.contains('show')) {
            modal.classList.remove('show');
        }
    });
});
