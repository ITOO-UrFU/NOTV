import hashlib
import os
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from jsonfield import JSONField
from rest_framework.authtoken.models import Token

from .validators import validate_file_extension


def key():
    key = hashlib.md5(os.urandom(128)).hexdigest()
    return key


def generate_new_filename(instance, filename):
    f, ext = os.path.splitext(filename)
    filename = '%s%s' % (uuid.uuid4().hex, ext)
    fullpath = 'documents/' + filename
    return fullpath


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def page_as_dict(page):
    try:
        type = Type.objects.filter(pk=page.type.id).values("title").first()["title"]
    except:
        type = None

    return {
        "id": page.id,
        "slug": page.slug,
        "title": page.title,
        "html": page.html,
        "title_en": page.title_en,
        "html_en": page.html_en,
        "pages": page.get_pages_dict(),
        "keywords": page.keywords,
        "type": type,
        "weight": page.weight,
    }


class RegistrationType(models.Model):
    title = models.CharField(_("Тип регистрации на мероприятие"), max_length=256, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'тип регистрации на событие'
        verbose_name_plural = 'типы регистраций на события'


class EventUserRegistration(models.Model):
    STATUSES = (
        ("r", _("Зарегистрирован")),
        ("y", _("Посетил")),
        ("n", _("Не посетил")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey("Person", verbose_name=_("Персона"))
    event = models.ForeignKey("Event", verbose_name=_("Событие"))
    type = models.ForeignKey("RegistrationType", verbose_name=_("Тип регистрации"))
    status = models.CharField(_("Статус"), choices=STATUSES, max_length=1, default="r")

    class Meta:
        unique_together = ('person', 'event',)

    def __str__(self):
        return " ".join([str(self.person), str(self.event), str(self.type)])

    def get_type_display(self):
        return str(self.type)

    class Meta:
        verbose_name = 'регистрация пользователя на событие'
        verbose_name_plural = 'регистрации пользователей на события'


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Название документа"), max_length=1024, blank=False)
    file = models.FileField(upload_to=generate_new_filename, validators=[validate_file_extension])


class Block(models.Model):
    title = models.CharField(_("Название документа"), max_length=1024, blank=False)
    slug = models.SlugField(_("Код"))


class Event(models.Model):
    STATUSES = (
        ('h', _("Скрыт")),
        ('p', _("Опубликован")),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Название события"), max_length=256, blank=False)
    description = models.TextField(_("Описание события"), max_length=16384, blank=True, default="")
    type = models.ForeignKey("EventType", verbose_name=_("Тип мероприятия"), null=True, blank=True)
    path = models.ForeignKey("Path", verbose_name=_("Траектория"), blank=True, null=True)
    room = models.ForeignKey("Room", verbose_name=_("Комната"), blank=True, null=True)
    line_of_work = models.ForeignKey("LineOfWork", verbose_name=_("Направление работы"), blank=True, null=True)
    block = models.ForeignKey("Block", verbose_name=_("Блок"), blank=True, null=True)
    status = models.CharField(_("Статус публикации"), max_length=1, choices=STATUSES, default='h')
    _startdate = models.DateTimeField(_("Начало события"), blank=True, null=True)
    _enddate = models.DateTimeField(_("Конец события"), blank=True, null=True)

    title_en = models.CharField(_("Название события. Английская версия"), max_length=256, blank=False)
    description_en = models.TextField(_("Описание события. Английская версия"), max_length=16384, blank=True, default="")

    class Meta:
        verbose_name = 'событие'
        verbose_name_plural = 'события'

    def __str__(self):
        return self.title

    def get_users(self):
        registrations = EventUserRegistration.objects.filter(event=self)
        return [registration for registration in registrations]

    def get_speakers(self):
        registrations = EventUserRegistration.objects.filter(event=self).exclude(type__title="Участник")
        return [registration for registration in registrations]

    def get_type_display(self):
        if self.type:
            return self.type.title
        else:
            return None

    def get_block_display(self):
        if self.block:
            return self.block.title
        else:
            return None

    def get_block_slug(self):
        if self.block:
            return self.block.slug
        else:
            return None

    def get_event_slug(self):
        if self.type:
            return self.type.slug
        else:
            return None

    def startdate(self):
        return self._startdate.strftime('%Y-%m-%dT%H:%M:%SZ')

    def enddate(self):
        return self._enddate.strftime('%Y-%m-%dT%H:%M:%SZ')

    def get_line_of_work_display(self):
        if self.line_of_work:
            return self.line_of_work.title
        else:
            return None

    def get_line_of_work_slug(self):
        if self.line_of_work:
            return self.line_of_work.slug
        else:
            return None


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(_('Имя пользователя'), max_length=32, blank=True, default='')
    last_name = models.CharField(_('Фамилия пользователя'), max_length=32, blank=True, default='')
    second_name = models.CharField(_('Отчество пользователя'), max_length=32, blank=True, default='')
    SEXES = (
        ('U', _('Не выбран')),
        ('F', _('Женский')),
        ('M', _('Мужской')),
    )

    PARTICIPATION = (
        ('U', _('Не выбрано')),
        ('O', _('Очно')),
        ('T', _('Трансляции')),
    )

    participation = models.CharField(max_length=1, choices=PARTICIPATION, default='U')
    sex = models.CharField(max_length=1,
                           choices=SEXES,
                           default='U'
                           )
    alt_email = models.EmailField(_('Альтернативный e-mail'), max_length=254, blank=True)
    country = CountryField(blank=True, default='Russia')
    birthday_date = models.DateField(_('Дата рождения'), null=True, blank=True)
    biography = models.TextField(_('Биография пользователя'), blank=True, default='')
    position = models.CharField(_('Должность'), max_length=1024, blank=True, null=True)
    division = models.CharField(_('Подразделение'), max_length=1024, blank=True, null=True)
    organisation = models.CharField(_('Организация'), max_length=1024, blank=True, null=True)
    photo = models.ImageField(_('Фото'), blank=True, null=True)
    phone = models.CharField(_('Телефон'), blank=True, null=True, max_length=32)
    docs = models.ManyToManyField("Document", blank=True)
    karma = models.IntegerField(_("Карма"), default=0)
    institute = models.CharField(_('Институт/Университет'), max_length=1024, blank=True, null=True)
    suggestions = models.CharField(_('Предложение'), max_length=32000, blank=True, null=True)

    biography_en = models.TextField(_('Биография пользователя. Английская версия'), blank=True, default='')
    position_en = models.CharField(_('Должность. Английская версия'), max_length=1024, blank=True, null=True)
    division_en = models.CharField(_('Подразделение. Английская версия'), max_length=1024, blank=True, null=True)
    organisation_en = models.CharField(_('Организация. Английская версия'), max_length=1024, blank=True, null=True)
    institute_en = models.CharField(_('Институт/Университет. Английская версия'), max_length=1024, blank=True, null=True)
    suggestions_en = models.CharField(_('Предложение. Английская версия'), max_length=32000, blank=True, null=True)

    class Meta:
        verbose_name = 'персона'
        verbose_name_plural = 'персоны'

    def __str__(self):
        if self.first_name and self.last_name:
            return ' '.join([str(self.first_name), str(self.last_name)])
        else:
            return str(self.user)

    def get_events(self):
        registrations = EventUserRegistration.objects.filter(person=self)
        return [registration for registration in registrations]

    def get_docs(self):
        return ''.join(['<a href="' + doc.file.url + '">' + doc.title + '</a><br>' for doc in self.docs.all()])

    def is_member(self):
        try:
            eur = EventUserRegistration.objects.filter(person=self)
            if eur:
                return True
        except:
            return False

    get_docs.allow_tags = True


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Person.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.person.save()

class Path(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_("Код"))
    title = models.CharField(_("Название траектории"), max_length=256, blank=True, null=True)
    title_en = models.CharField(_("Название траектории. Английская версия"), max_length=256, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'траектория'
        verbose_name_plural = 'траектории'


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_("Код"))
    title = models.CharField(_("Название аудитории"), max_length=256, blank=True, null=True)
    title_en = models.CharField(_("Название аудитории. Английская версия"), max_length=256, blank=True, null=True)
    address = models.CharField(_("Адрес"), max_length=256, blank=True, null=True)
    housing = models.CharField(_("Корпус"), max_length=256, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'комната'
        verbose_name_plural = 'комнаты'


class Page(models.Model):
    STATUSES = (
        ('h', _("Скрыт")),
        ('p', _("Опубликован")),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_("Код"))
    title = models.CharField(_("Название страницы"), max_length=256, blank=True, null=True)
    html = models.TextField(_("Контент"), blank=True, null=True)
    title_en = models.CharField(_("Название страницы. Английская версия"), max_length=256, blank=True, null=True)
    html_en = models.TextField(_("Контент. Английская версия"), blank=True, null=True)
    pages = models.ManyToManyField("self", verbose_name=_("Вложенные страницы"), blank=True, related_name='+', symmetrical=False)
    keywords = models.TextField("SEO", blank=True, null=True)
    weight = models.IntegerField(_("Вес страницы"), default=100)
    type = models.ForeignKey("Type", verbose_name=_("Тип"), null=True, blank=True)
    status = models.CharField(_("Статус публикации"), max_length=1, choices=STATUSES, default='h')

    def __str__(self):
        return self.slug

    def get_pages_display(self):
        return " ".join([page.slug for page in self.pages.all().order_by('weight')])

    def get_pages_list(self):
        return [page.slug for page in self.pages.all()]

    def get_pages_dict(self):
        return [page_as_dict(page) for page in self.pages.filter(status="p").order_by('weight')]

    class Meta:
        ordering = ['weight']

    class Meta:
        verbose_name = 'страница'
        verbose_name_plural = 'страницы'


class Type(models.Model):
    title = models.CharField(_("Тип страницы"), max_length=256, blank=True, null=True)
    slug = models.SlugField(_("Код"), blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'тип'
        verbose_name_plural = 'типы'


class EventType(models.Model):
    title = models.CharField(_("Тип мероприятия"), max_length=256, blank=True, null=True)
    title_en = models.CharField(_("Тип мероприятия. Английская версия"), max_length=256, blank=True, null=True)
    slug = models.SlugField(_("Код"), blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'тип мероприятия'
        verbose_name_plural = 'типы мероприятий'


class LineOfWork(models.Model):
    slug = models.SlugField(_("Код"), blank=True)
    title = models.CharField(_("Наименование направления работы"), max_length=256, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'направление работы'
        verbose_name_plural = 'направления работы'


class CustomObject(models.Model):
    STATUSES = (
        ('h', _("Скрыт")),
        ('p', _("Опубликован")),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Наименование'), max_length=32, blank=False, default='')
    json = JSONField()
    status = models.CharField(_("Статус публикации"), max_length=1, choices=STATUSES, default='h')

    def __str__(self):
        return self.title
