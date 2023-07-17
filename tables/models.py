from django.db import models


class DynamicModelField(models.Model):
    name = models.CharField(max_length=256)
    type = models.CharField(max_length=128)
    options = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.type}"


class DynamicModel(models.Model):
    name = models.CharField(max_length=256, unique=True)
    fields = models.ManyToManyField(DynamicModelField, related_name="models")
    options = models.JSONField(blank=True, null=True)
    admin_opts = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
