import uuid
import os
from django.core.exceptions import ValidationError
from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Comment, CommentImage, Topic, Report
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

class CommentForm(forms.ModelForm):
    images = forms.ImageField(widget=MultiFileInput(attrs={'multiple': 'multiple'}), required=False)

    class Meta:
        model = Comment
        fields = ['text', 'images']

    def clean_images(self):
        images = self.files.getlist('images')
        if images:
            if len(images) > 5:
                raise ValidationError("Можно загрузить не более 5 изображений.")

            allowed_formats = ['image/jpeg', 'image/png', 'image/heic', 'image/heif']
            for image in images:
                if image.content_type not in allowed_formats:
                    raise ValidationError(
                        f"Неподдерживаемый формат файла: {image.name}. Допустимые форматы: JPG, JPEG, PNG, HEIC, HEIF."
                    )
                if image.size > 5 * 1024 * 1024:
                    raise ValidationError(f"Изображение {image.name} слишком большое. Максимальный размер: 5 МБ.")
        return images


    def save(self, report, user, commit=True):
        # Сохраняем комментарий (без изображений)
        instance = super().save(commit=False)
        instance.report = report
        instance.user = user

        if commit:
            instance.save()

        # Сохраняем изображения, если они есть
        images = self.files.getlist('images')
        if images:
            for image in images:
                unique_image_name = self.get_unique_image_name(image)
                # Сжимаем изображение и сохраняем
                compressed_image = self.compress_image(image, unique_image_name)
                # Создаем объект CommentImage с сжатыми изображениями
                CommentImage.objects.create(comment=instance, image=compressed_image)

        return instance

    def compress_image(self, image, unique_name):
        """
        Сжимает изображение до указанных размеров и возвращает сжатое изображение с новым именем.
        """
        img = Image.open(image)
        img_format = img.format

        max_width = 800
        max_height = 800

        img.thumbnail((max_width, max_height))

        img_io = BytesIO()
        img.save(img_io, format=img_format, quality=85)
        img_io.seek(0)

        # Используем уникальное имя для файла
        compressed_image = InMemoryUploadedFile(
            img_io, None, unique_name, image.content_type, img_io.tell(), None
        )
        return compressed_image

    def get_unique_image_name(self, image):
        """ Генерирует уникальное имя для изображения """
        extension = os.path.splitext(image.name)[1]  # Получаем расширение файла
        unique_name = str(uuid.uuid4()) + extension  # Генерируем уникальное имя
        return unique_name


class ReportForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        required=True,
        label="Категория проблемы",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    title = forms.CharField(
        min_length=5,
        max_length=100,
        required=True,
        label="Название проблемы",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    latitude = forms.FloatField(
        required=True,
        widget=forms.HiddenInput()
    )
    longitude = forms.FloatField(
        required=True,
        widget=forms.HiddenInput()
    )
    address = forms.CharField(
        required=True,
        label="Адрес",
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly", "style": "display: none;"})
    )
    description = forms.CharField(
        required=False,
        max_length=350,
        label="Описание проблемы",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4, "style": "resize: none;"})
    )

    class Meta:
        model = Report
        fields = ["category", "title", "latitude", "longitude", "address", "description"]

