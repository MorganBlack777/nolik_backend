// Main JavaScript for Tic-Tac-Toe application

// Execute when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Alert close functionality
    var alertList = document.querySelectorAll('.alert');
    alertList.forEach(function(alert) {
        var closeButton = alert.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                alert.classList.add('fade');
                setTimeout(function() {
                    alert.remove();
                }, 150);
            });
        }
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-important)');
        alerts.forEach(function(alert) {
            alert.classList.add('fade');
            setTimeout(function() {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 150);
        });
    }, 5000);
    
    // Add confirmation to delete actions
    var deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-update game page if it's in progress
    var gameStatusElement = document.querySelector('#game-status');
    if (gameStatusElement && gameStatusElement.dataset.status === 'in_progress') {
        // Refresh page every 10 seconds if game is in progress and not user's turn
        if (!gameStatusElement.dataset.canPlay || gameStatusElement.dataset.canPlay === 'false') {
            setInterval(function() {
                window.location.reload();
            }, 10000);
        }
    }
}); 