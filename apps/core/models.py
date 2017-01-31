import uuid

from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField

from django.utils.translation import ugettext_lazy as _


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Название события"), max_length=256, blank=False)
    description = models.TextField(_("Описание события"), max_length=16384, blank=True, default="")
    startdate = models.DateTimeField(_("Начало события"))
    enddate = models.DateTimeField(_("Конец события"))
    speakers = models.ManyToManyField("Speaker")

    def get_speakers(self):
        return ' '.join([str(speaker.person) for speaker in self.speakers.all()])

    class Meta:
        verbose_name = 'событие'
        verbose_name_plural = 'события'

    def __str__(self):
        return self.title

    get_speakers.short_description = _("Спикеры")


class Speaker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey('Person')

    class Meta:
        verbose_name = 'спикер'
        verbose_name_plural = 'спикеры'

    def __str__(self):
        return str(self.person)


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

    class Meta:
        verbose_name = 'персона'
        verbose_name_plural = 'персоны'

    def __str__(self):
        if self.first_name and self.last_name:
            return ' '.join([str(self.first_name), str(self.last_name)])
        else:
            return str(self.user)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.person.save()
