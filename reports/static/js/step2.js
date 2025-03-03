document.addEventListener("DOMContentLoaded", function() {
    // Проверяем, есть ли данные в sessionStorage
    var location = JSON.parse(sessionStorage.getItem('location'));

    // Если данные есть, обновляем атрибуты
    if (location) {
        document.querySelectorAll('.topic-item').forEach(function(button) {
            // Обновляем data-lat и data-lon с помощью данных из sessionStorage
            button.setAttribute('data-lat', location.lat || '');
            button.setAttribute('data-lon', location.lon || '');
             button.setAttribute('data-address', location.address || '');
        });
    }
});

document.querySelectorAll('.topic-item').forEach(function(button) {
    button.addEventListener('click', function() {
        var topicId = button.getAttribute('data-topic-id');
        var topicTitle = button.getAttribute('data-title'); // Получаем название темы
        var lat = button.getAttribute('data-lat');
        var lon = button.getAttribute('data-lon');
        var address = button.getAttribute('data-address');

        // Обновляем поля формы
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lon;

        // Сохраняем данные в sessionStorage
        sessionStorage.setItem('selected_topic', JSON.stringify({
            id: topicId,
            title: topicTitle
        }));

        sessionStorage.setItem('location', JSON.stringify({
            lat: lat,
            lon: lon,
            address: address
        }));

        // Добавляем скрытое поле для выбранной темы в форму
        var topicInput = document.createElement('input');
        topicInput.type = 'hidden';
        topicInput.name = 'selected_topic';
        topicInput.value = topicId;
        document.getElementById('problemForm').appendChild(topicInput);

        // Отправляем форму
        document.getElementById('problemForm').submit();
    });
});

// Отображение/скрытие описания темы
document.querySelectorAll('.toggle-description').forEach(function(button) {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        var description = button.closest('.topic-item-container').querySelector('.topic-description');
        description.style.display = description.style.display === 'none' ? 'block' : 'none';
    });
});
