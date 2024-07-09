from django.db import models

from authentication.models import User


# Create your models here.


class Salary(models.Model):
    school_id = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    joining_date = models.DateField(null=True, blank=True)
    pan_no = models.CharField(max_length=255)
    total_salary = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    in_hand_salary = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    basic_salary = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    hra = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    other_allowances = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    deducted_salary = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    professional_tax = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    tds = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    epf = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    other_deduction = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    incentive = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    net_payable_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    bank_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f'{self.id}'


class SalaryFormat(models.Model):
    salary_structure = models.ForeignKey(Salary, on_delete=models.CASCADE, related_name='salary_structure')
    field_name = models.CharField(max_length=255, null=True, blank=True)
    field_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.id}"


class Fee(models.Model):
    school_id = models.CharField(max_length=255)
    curriculum = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)
    payment_type = models.CharField(max_length=255)
    instalment_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    no_of_instalment = models.IntegerField()
    school_fee = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    total_fee = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    bus_fee = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    canteen_fee = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    miscellaneous_fee = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    min_paid_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    max_total_remain = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.id}"


class FeeFormat(models.Model):
    fee_structure = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='fee_structure')
    field_name = models.CharField(max_length=255, null=True, blank=True)
    field_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.id}"


class DueFeeDetail(models.Model):
    fee_structure = models.ForeignKey(Fee, on_delete=models.CASCADE)
    due_type = models.CharField(max_length=255)
    due_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    last_due_date = models.DateField()
    late_fee = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.id}"