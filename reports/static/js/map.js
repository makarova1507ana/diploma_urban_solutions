// Инициализируем карту и задаем координаты центра (Волгоград)
var map = L.map('map').setView([48.7080, 44.5133], 13); // Координаты центра Волгограда

// Добавляем слой карты от OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Начальная метка в Волгограде
var marker = L.marker([48.7080, 44.5133]).addTo(map); // Начальный маркер в Волгограде
marker.bindPopup("<b>Волгоград</b><br>Это стартовая метка.").openPopup();

// Кэш для геокодирования
var geocodeCache = {};

// Функция для получения адреса по координатам с использованием Nominatim API
function reverseGeocode(lat, lon, callback) {
    var coordinatesKey = `${lat.toFixed(4)}_${lon.toFixed(4)}`; // Создаем уникальный ключ для координат с округлением
    if (geocodeCache[coordinatesKey]) {
        console.log("Используется кэшированный адрес.");
        callback(geocodeCache[coordinatesKey]); // Используем кэшированный результат
    } else {
        var url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&addressdetails=1&lang=ru`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                let address = "Адрес не найден";
                if (data && data.address) {
                    address = buildAddress(data);
                    geocodeCache[coordinatesKey] = address; // Кэшируем результат
                    console.log("Адрес:", address); // Логируем найденный адрес
                }
                document.getElementById('address-search').value = address; // Обновляем строку поиска
                callback(address); // Вызываем callback для обновления подписи метки
            })
            .catch(error => {
                console.error("Ошибка геокодирования:", error);
                document.getElementById('address-search').value = "Ошибка при поиске адреса";
                callback("Ошибка при поиске адреса");
            });
    }
}

// Функция для составления адреса
function buildAddress(data) {
    let address = "";
    if (data.name) address += data.name + ", ";
    if (data.address.road) address += data.address.road + ", ";
    if (data.address.house_number) address += data.address.house_number + ", ";
    if (data.address.city) address += data.address.city + ", ";
    if (data.address.country) address += data.address.country;
    return address || "Адрес не найден";
}

// Обработчик кликов по карте для добавления метки
map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lon = e.latlng.lng;

    // Удаляем старую метку и добавляем новую
    marker.setLatLng([lat, lon]);

    // Получаем адрес для новых координат
    reverseGeocode(lat, lon, function(address) {
        marker.bindPopup("<b>Вы выбрали место:</b><br>" + address).openPopup();
    });

    // Обновляем скрытые поля формы с координатами
    document.getElementById('lat').value = lat;
    document.getElementById('lon').value = lon;

    console.log("Координаты метки:", lat, lon); // Логируем координаты метки
});

// Обработчик изменения масштаба карты
map.on('zoomend', function() {
    var lat = marker.getLatLng().lat;
    var lon = marker.getLatLng().lng;

    // Получаем адрес для текущих координат
    reverseGeocode(lat, lon, function(address) {
        marker.bindPopup("<b>Вы выбрали место:</b><br>" + address).openPopup();
    });

    console.log("Масштаб изменен, текущие координаты метки:", lat, lon); // Логируем координаты после изменения масштаба
});




// Переменные для сохранения выбранного местоположения
var selectedLat = null;
var selectedLon = null;
var selectizeDropdown = null; // Для хранения списка подсказок

// Функция для поиска адреса с использованием Nominatim
function getSuggestions(query, callback) {
    var url = 'https://nominatim.openstreetmap.org/search?q=' + query + '&format=json&addressdetails=1&limit=5';
    fetch(url)
        .then(response => response.json())
        .then(data => {
            var suggestions = data.map(function(item) {
                return {
                    value: item.display_name,
                    lat: item.lat,
                    lon: item.lon
                };
            });
            callback(suggestions);
        });
}

// Инициализация Selectize для автозаполнения
document.getElementById('address-search').addEventListener('input', function(event) {
    var query = event.target.value;
    if (query.length === 0) {
        return;
    }

    getSuggestions(query, function(suggestions) {
        // Если существует открытый список подсказок, его нужно удалить
        if (selectizeDropdown) {
            selectizeDropdown.remove();
        }

        selectizeDropdown = document.createElement('div');
        selectizeDropdown.classList.add('selectize-dropdown');
        suggestions.forEach(function(suggestion) {
            var suggestionItem = document.createElement('div');
            suggestionItem.classList.add('selectize-item');
            suggestionItem.textContent = suggestion.value;
            suggestionItem.addEventListener('click', function() {
                // Устанавливаем выбранное местоположение
                selectedLat = suggestion.lat;
                selectedLon = suggestion.lon;

                // Устанавливаем маркер на карте
                L.marker([selectedLat, selectedLon]).addTo(map)
                    .bindPopup(suggestion.value)
                    .openPopup();

                // Центрируем карту на выбранном местоположении
                map.setView([selectedLat, selectedLon], 13);

                // Обновляем скрытые поля формы
                document.getElementById('lat').value = selectedLat;
                document.getElementById('lon').value = selectedLon;

                // Закрываем список подсказок
                selectizeDropdown.remove();
                selectizeDropdown = null; // Очистка ссылки на список
            });
            selectizeDropdown.appendChild(suggestionItem);
        });

        // Добавляем dropdown с подсказками
        document.querySelector('.search-container').appendChild(selectizeDropdown);
    });
});