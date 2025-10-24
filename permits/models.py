from django.db import models

class Permit(models.Model):
	parcel = models.CharField(max_length=50, db_column='Parcel')
	permit_id = models.CharField(max_length=50, db_column='Permit_ ID')
	permit_date = models.DateTimeField(db_column='Permit_date')
	permit_type = models.CharField(max_length=100, db_column='Permit Type')
	estimate_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, db_column='Estimate Cost')
	owner = models.CharField(max_length=255, db_column='OwneratPermitDTE', null=True)
	contractor = models.CharField(max_length=255, db_column='Contractor', null=True)
	desc = models.TextField(db_column='Desc', null=True)

	class Meta:
		managed = False
		db_table = 'GISPermits'

	def __str__(self):
		return f"{self.parcel} - {self.permit_id}"
