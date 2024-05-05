from django.contrib import admin

from curriculum.models import Curriculum, CurriculumPDF


# Register your models here.

@admin.register(CurriculumPDF)
class CurriculumPDF(admin.ModelAdmin):
    list_display = ('curriculum', 'curriculum_pdf_file')