document.addEventListener("DOMContentLoaded", function () {
    // Флаг для временного отключения onaddfile
    let skipOnAdd = false;

    // Восстанавливаем данные из sessionStorage для геолокации и выбранной категории
    var storedTopic = JSON.parse(sessionStorage.getItem('selected_topic'));
    var storedLocation = JSON.parse(sessionStorage.getItem('location'));

    if (storedTopic) {
        document.getElementById('id_category').value = storedTopic.id;
    }

    if (storedLocation) {
        document.getElementById('id_latitude').value = storedLocation.lat;
        document.getElementById('id_longitude').value = storedLocation.lon;
        document.getElementById('id_address').value = storedLocation.address;
    }

    // Инициализация FilePond с плагином предпросмотра и проверкой типов и размера файлов
    FilePond.registerPlugin(FilePondPluginImagePreview);
    const pond = FilePond.create(document.querySelector(".filepond"), {
        allowMultiple: true,
        maxFiles: 5,
        instantUpload: false, // отключаем автоматическую загрузку
        labelIdle: 'Перетащите файлы сюда или выберите',
        imagePreviewHeight: 150,
        imageCropAspectRatio: '1:1',
        maxFileSize: '5MB', // Ограничение на размер файла
        acceptedFileTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/heic', 'image/heif'],
        allowFileTypeValidation: true,
        labelFileTypeNotAllowed: 'Недопустимый формат файла',
        fileValidateTypeLabelExpectedTypes: 'Допустимые форматы: jpg, jpeg, png, heic, heif',
        labelFileSizeNotAllowed: 'Файл слишком большой',
        fileValidateSizeLabelFormat: 'Файл слишком большой. Максимальный размер: 5MB',
        // Обработчик добавления файла
        onaddfile: (error, fileItem) => {
            if (skipOnAdd) return; // Если флаг включён, пропускаем проверку
            if (error) {
                console.error(error);
                return;
            }
            // Проверяем MIME тип
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/heic', 'image/heif'];
            if (!allowedTypes.includes(fileItem.fileType)) {
                alert("Недопустимый формат файла. Допустимые форматы: jpg, jpeg, png, heic, heif");
                pond.removeFile(fileItem.id);
                return;
            }
            // Проверка размера файла (на случай, если FilePond не отсеял)
            if (fileItem.file.size > 5 * 1024 * 1024) {
                alert("Файл превышает максимальный размер 5MB");
                pond.removeFile(fileItem.id);
                return;
            }
        }
    });

    // Обработчик отправки формы
    document.getElementById("problemForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Отмена стандартной отправки формы

        const form = this;
        const formData = new FormData(form);

        // Отправляем данные отчета на сервер (без файлов)
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success" && data.report_id) {
                const reportId = data.report_id;

                // Проверяем, есть ли файлы для загрузки
                if (pond.getFiles().length > 0) {
                    // Настраиваем FilePond для загрузки файлов с report_id
                    FilePond.setOptions({
                        server: {
                            process: {
                                url: '/reports/upload/',  // URL для загрузки изображений
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                                },
                                ondata: (formData) => {
                                    formData.append('report_id', reportId);
                                    return formData;
                                }
                            }
                        }
                    });

                    // Сжимаем изображения перед загрузкой
                    const filesToCompress = pond.getFiles().map(fileItem => {
                        return new Promise((resolve, reject) => {
                            new Compressor(fileItem.file, {
                                quality: 0.7, // Степень сжатия (от 0 до 1)
                                maxWidth: 800, // Максимальная ширина
                                maxHeight: 800, // Максимальная высота
                                success(result) {
                                    resolve(result);
                                },
                                error(err) {
                                    reject(err);
                                }
                            });
                        });
                    });

                    Promise.all(filesToCompress)
                        .then(compressedFiles => {
                            // Удаляем все исходные файлы, чтобы не было дубликатов
                            pond.removeFiles();
                            // Отключаем onaddfile, чтобы сжатые файлы не проходили повторную проверку
                            skipOnAdd = true;
                            // Добавляем сжатые файлы
                            const addPromises = compressedFiles.map(file => pond.addFile(file));
                            Promise.all(addPromises).then(() => {
                                skipOnAdd = false; // Включаем обработчик обратно
                                // Загружаем файлы на сервер
                                pond.processFiles().then(() => {
                                    window.location.href = `/reports/report/${reportId}`;
                                });
                            });
                        })
                        .catch(error => {
                            console.error("Ошибка сжатия файлов:", error);
                        });
                } else {
                    // Если файлов нет, сразу перенаправляем
                    window.location.href = `/reports/report/${reportId}`;
                }
            } else {
                alert("Ошибка при создании отчета");
            }
        })
        .catch(error => {
            console.error("Ошибка:", error);
        });
    });
});
