// Получаем элементы попапа и кнопок
const popup = document.getElementById('popup');
const closePopup = document.getElementById('close-popup');
const profileLink = document.getElementById('profile-link');
const logoutButton = document.getElementById('logout-button');

// Функция для открытия попапа
function openPopup() {
    popup.style.display = 'flex';
}

// Функция для закрытия попапа
function closePopupWindow() {
    popup.style.display = 'none';
}

// Открыть попап, если пользователь аутентифицирован
if (profileLink || logoutButton) {
    profileLink.addEventListener('click', (e) => {
        e.preventDefault();
        openPopup();
    });

    logoutButton.addEventListener('click', (e) => {
        e.preventDefault();
        openPopup();
    });
}

// Закрытие попапа при клике на крестик
closePopup.addEventListener('click', closePopupWindow);

// Закрытие попапа при клике за пределами попапа
window.addEventListener('click', (e) => {
    if (e.target === popup) {
        closePopupWindow();
    }
});
