// Функция инициализации игры
function initGame() {
    // Проверка наличия автообновления
    var gameStatus = document.getElementById('game-status');
    var canPlay = document.getElementById('can-play');
    
    if (gameStatus && canPlay) {
        var status = gameStatus.value;
        var playable = canPlay.value === 'True';
        
        // Если игра в процессе и игрок не может ходить - настраиваем автообновление
        if (status === 'in_progress' && !playable) {
            setTimeout(function() {
                window.location.reload();
            }, 2000);
        }
    }
    
    // Добавляем класс активного элемента при клике
    var buttons = document.querySelectorAll('.cell-button');
    if (buttons) {
        buttons.forEach(function(button) {
            button.addEventListener('click', function() {
                this.classList.add('clicked');
            });
        });
    }
}

// Запускаем инициализацию после загрузки страницы
document.addEventListener('DOMContentLoaded', initGame); 