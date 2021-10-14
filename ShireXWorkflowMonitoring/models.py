from django.db import models

class STAFF(models.Model):
    STAFF_CODE = models.CharField(primary_key=True, max_length=4, db_column="STAFF_CODE")        #Unique identifier
    LOGON_NAME = models.CharField(max_length=50)   #User name
    PASSWORD = models.CharField(max_length=10)
    NAME = models.CharField(max_length=50)
    EMPLOYMENT_END_DATE = models.DateTimeField()

    class Meta:
        managed=False
        db_table='STAFF'
