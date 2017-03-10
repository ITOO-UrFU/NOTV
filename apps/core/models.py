import uuid

from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from jsonfield import JSONField

from django.utils.translation import ugettext_lazy as _


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
    status = models.CharField(_("Статус публикации"), max_length=1, choices=STATUSES, default='h')
    startdate = models.DateTimeField(_("Начало события"))
    enddate = models.DateTimeField(_("Конец события"))

    class Meta:
        verbose_name = 'событие'
        verbose_name_plural = 'события'

    def __str__(self):
        return self.title

    def get_users(self):
        registrations = EventUserRegistration.objects.filter(event=self)
        return [registration for registration in registrations]

    def get_type_display(self):
        if self.type:
            return self.type.title
        else:
            return None

    def get_event_slug(self):
        if self.type:
            return self.type.slug
        else:
            return None


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(_('Имя пользователя'), max_length=32, blank=False, default='')
    last_name = models.CharField(_('Фамилия пользователя'), max_length=32, blank=False, default='')
    second_name = models.CharField(_('Отчество пользователя'), max_length=32, blank=True, default='')
    SEXES = (
        ('U', _('Не выбран')),
        ('F', _('Женский')),
        ('M', _('Мужской')),
    )
    sex = models.CharField(max_length=1,
                           choices=SEXES,
                           default='U'
                           )
    alt_email = models.EmailField(_('Альтернативный e-mail'), max_length=254, blank=True)
    country = CountryField(blank=True, default='Russia')
    birthday_date = models.DateField(_('Дата рождения'), null=True, blank=True)
#   roles = models.ManyToManyField(ROLE)  TODO: Сделать модель 'Роль'
    biography = models.TextField(_('Биография пользователя'), blank=True, default='')
    position = models.CharField(_('Должность'), max_length=1024, blank=True, null=True)
    division = models.CharField(_('Подразделение'), max_length=1024, blank=True, null=True)
    organisation = models.CharField(_('Организация'), max_length=1024, blank=True, null=True)
    photo = models.ImageField(_('Фото'), upload_to="media", blank=True, null=True)

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

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'траектория'
        verbose_name_plural = 'траектории'


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_("Код"))
    title = models.CharField(_("Название аудитории"), max_length=256, blank=True, null=True)
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
    slug = models.SlugField(_("Код"), blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'тип мероприятия'
        verbose_name_plural = 'типы мероприятий'


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
