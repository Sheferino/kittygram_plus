from rest_framework import serializers

from .models import Cat, Owner, Achievement, AchievementCat


class AchievementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Achievement
        fields = ('id', 'name')


class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ('id', 'first_name', 'last_name', 'cats')


class CatSerializer(serializers.ModelSerializer):
    # чтобы показывать владельца по строкому представлению
    # owner = serializers.StringRelatedField(read_only=True)
    achievements = AchievementSerializer(many=True)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements')

    def create(self, validated_data):
        achievements = validated_data.pop('achievements')

        cat = Cat.objects.create(**validated_data)

        for achievement in achievements:
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement)
            AchievementCat.objects.create(
                achievement=current_achievement, cat=cat)

        return cat

    def update(self, instance, validated_data):
        achievements = validated_data.pop('achievements', None)

        for key, val in validated_data:
            setattr(instance, key, val)
        instance.save()

        # cat = Cat.objects.create(**validated_data)

        for achievement in achievements:
            current_achievement, _ = Achievement.objects.get_or_create(
                **achievement)
            AchievementCat.objects.create(
                achievement=current_achievement, cat=instance)

        return instance
