from django.contrib import admin

from .models import DynamicModel, DynamicModelField


@admin.register(DynamicModel)
class DynamicModelsAdmin(admin.ModelAdmin):
    list_display = ("name", "options")


@admin.register(DynamicModelField)
class DynamicModelFieldAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "options")
    list_filter = ("type",)
