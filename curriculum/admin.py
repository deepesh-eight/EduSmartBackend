from django.contrib import admin

from curriculum.models import Curriculum, CurriculumPDF


# Register your models here.

@admin.register(Curriculum)
class Curriculum(admin.ModelAdmin):
    list_display = ('curriculum_name', 'select_class', 'primary_subject', 'optional_subject', 'syllabus', 'discription')

@admin.register(CurriculumPDF)
class CurriculumPDF(admin.ModelAdmin):
    list_display = ('curriculum', 'curriculum_pdf_file')