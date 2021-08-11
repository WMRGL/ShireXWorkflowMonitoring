from django.db import models

class STAFF(models.Model):
    STAFF_CODE = models.CharField(primary_key=True, max_length=50, db_column="STAFF_CODE")        #Unique identifier
    EMPLOYEE_NUMBER = models.CharField(max_length=30)   #User name
    PASSWORD = models.CharField(max_length=10)
    NAME = models.CharField(max_length=50)

    class Meta:
        managed=False
        db_table='STAFF'