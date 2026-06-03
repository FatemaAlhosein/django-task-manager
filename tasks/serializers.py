from rest_framework import serializers
from .models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'color']


class TaskSerializer(serializers.ModelSerializer):
    category_name    = serializers.CharField(source='category.name', read_only=True)
    category_color   = serializers.CharField(source='category.color', read_only=True)
    recurrence_label = serializers.SerializerMethodField()
    is_overdue       = serializers.SerializerMethodField()

    class Meta:
        model  = Task
        fields = [
            'id', 'title', 'description', 'priority', 'completed',
            'due_date', 'recurrence', 'recurrence_weekday', 'recurrence_label',
            'category', 'category_name', 'category_color',
            'is_overdue', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_recurrence_label(self, obj):
        return obj.recurrence_label()

    def get_is_overdue(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        return (
            not obj.completed and
            obj.due_date is not None and
            obj.due_date < today
        )

    def validate(self, data):
        # Only allow categories that belong to the current user
        request = self.context.get('request')
        category = data.get('category')
        if category and request and category.user != request.user:
            raise serializers.ValidationError({'category': 'Invalid category.'})
        return data
