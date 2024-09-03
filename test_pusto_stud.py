import csv
from datetime import datetime

from django.db import models
from django.shortcuts import get_object_or_404

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# Задание номер один:
class Player(models.Model):
    """Игрок."""

    player_id = models.CharField(max_length=100)
    sing_up = models.DateField(auto_now_add=True,)


class BoostBaseModel(models.Model):
    """Базовый класс бустов."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE,)
    received = models.DateField(auto_now_add=True,)
    title = models.CharField()

    class Meta:
        abstract = True


class BoostName(BoostBaseModel):
    """Буст Name начисляеммый игроку."""

    class Meta:
        default_related_name = "boost_name"


# задание номер два:
class Player(models.Model):
    player_id = models.CharField(max_length=100)


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class Prize(models.Model):
    title = models.CharField()


class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()


def player_get_prize(level: Level, player: Player, prize: Prize):
    """Присвоение игроку приза за прохождение уровня."""
    PlayerLevel.objects.update_or_create(
        player=player.pk, level=level.pk,
        defaults=dict(
           completed=datetime.now().strftime(DATE_FORMAT),
           is_completed=True,
           score=level.order,
        )
    )
    LevelPrize.objects.create(
        level=level.pk,
        prize=prize.pk,
        received=datetime.now().strftime(DATE_FORMAT)
    )


def create_csv_file(name_file: str = "file.csv"):
    """
    Выгрузку в csv следующих данных: id игрока, название уровня,
    пройден ли уровень, полученный приз за уровень.
    """
    with open(name_file, mode="w", encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter=",", lineterminator="\r")
        file_writer.writerow(
            ["id игрока", "название уровня",
             "пройден ли уровень", "полученный приз за уровень"]
        )
        q_set = PlayerLevel.objects.all()
        for obj in q_set:
            file_writer.writerow([
                obj.player.player_id,
                obj.level.title,
                "Пройден" if obj.is_completed else "Не пройден",
                get_object_or_404(
                    LevelPrize, level=obj.level, received=obj.completed
                ).prize.title
            ])
