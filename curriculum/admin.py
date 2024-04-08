from django.contrib import admin

from curriculum.models import Curriculum, CurriculumPDF


# Register your models here.

@admin.register(Curriculum)
class Curriculum(admin.ModelAdmin):
    list_display = ('academic_session', 'exam_board', 'subject_name_code', 'class_name', 'section', 'curriculum_name')

@admin.register(CurriculumPDF)
class CurriculumPDF(admin.ModelAdmin):
    list_display = ('curriculum', 'curriculum_pdf_file')