from django.contrib import admin
from django.contrib.admin.sites import site
from django import forms

from .models import AModel, BModel, Index


@admin.register(AModel)
class AModelAdmin(admin.ModelAdmin):
    pass


@admin.register(BModel)
class BModelAdmin(admin.ModelAdmin):
    pass


class IndexForm(forms.ModelForm):
    method = forms.ChoiceField(choices=[(name, name) for name in ["-", "gin", "btree"]], required=True)
    is_unique = forms.BooleanField(required=False)

    class Meta:
        model = Index
        fields = ["indexname", "schemaname", "tablename", "method", "is_unique"]

    def get_initial_for_field(self, field, field_name):
        if field_name in ["is_unique", "method"] and self.instance:
            return getattr(self.instance, field_name)
        return super().get_initial_for_field(field, field_name)


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin):
    form = IndexForm

    list_display = [
        "indexname",
        "schemaname",
        "tablename",
        "method",
        "is_unique",
    ]
    list_filter = ["schemaname", "tablename"]

    readonly_fields = ["indexdef"]

    @admin.display(boolean=True)
    def is_unique(self, index):
        return index.is_unique
