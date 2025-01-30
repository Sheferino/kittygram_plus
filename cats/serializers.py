from datetime import datetime
from rest_framework import serializers
import webcolors

from .models import Cat, Owner, Achievement, AchievementCat


class Hex2NameColor(serializers.Field):
    # При чтении данных ничего не меняем - просто возвращаем как есть
    def to_representation(self, value):
        return value

    # При записи код цвета конвертируется в его название
    def to_internal_value(self, data):
        # Доверяй, но проверяй
        try:
            # Если имя цвета существует, то конвертируем код в название
            data = webcolors.hex_to_name(data)
        except ValueError:
            # Иначе возвращаем ошибку
            raise serializers.ValidationError('Для этого цвета нет имени')
        # Возвращаем данные в новом формате
        return data


class AchievementSerializer(serializers.ModelSerializer):
    ach_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'ach_name')


class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ('id', 'first_name', 'last_name', 'cats')


class CatSerializer(serializers.ModelSerializer):
    # чтобы показывать владельца по строкому представлению
    # owner = serializers.StringRelatedField(read_only=True)
    achievements = AchievementSerializer(many=True, required=False)
    age = serializers.SerializerMethodField()
    # color = Hex2NameColor() # кастомные цвета в RGB

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements',
                  'age')

    # переопределяем методы create и update, чтобы сохранять achievements
    def create(self, validated_data):
        # вынимаем achievements
        achievements = validated_data.pop('achievements', None)
        cat = Cat.objects.create(**validated_data)
        # сохраняем achievements, если они есть
        if achievements:
            for achievement in achievements:
                current_achievement, _ = Achievement.objects.get_or_create(
                    **achievement)
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat)
        return cat

    def update(self, instance, validated_data):
        # вынимаем achievements
        achievements = validated_data.pop('achievements', None)
        # сохраняем изменённые поля
        for key, val in validated_data:
            setattr(instance, key, val)
        instance.save()
        # сохраняем achievements, если они есть
        if achievements:
            for achievement in achievements:
                current_achievement, _ = Achievement.objects.get_or_create(
                    **achievement)
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=instance)

        return instance

    def get_age(self, obj):
        return datetime.now().year - obj.birth_year
