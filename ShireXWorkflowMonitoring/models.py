from django.db import models

# Define the STAFF model which maps to the 'STAFF' table in the database - MW
class STAFF(models.Model):
    # Define the STAFF_CODE field as a CharField with a maximum length of 4 characters - MW
    # This field is designated as the primary key for the model and maps to the "STAFF_CODE" column in the database - MW
    STAFF_CODE = models.CharField(primary_key=True, max_length=4, db_column="STAFF_CODE")        # Unique identifier
    # Define the LOGON_NAME field to store the logon name of the staff, with a maximum length of 50 characters - MW
    LOGON_NAME = models.CharField(max_length=50)   # User name
    # Define the PASSWORD field with a maximum length of 10 characters to store the staff's password - MW
    PASSWORD = models.CharField(max_length=10)# Password for the user - MW
    # Define the NAME field to store the staff's name, with a maximum length of 50 characters - MW
    NAME = models.CharField(max_length=50)# Staff's full name - MW
    # Define the EMPLOYMENT_END_DATE field as a DateTimeField to store the employment end date of the staff - MW
    EMPLOYMENT_END_DATE = models.DateTimeField()# Date when the employment ends - MW

    # Meta class to provide additional information about the STAFF model - MW
    class Meta:
        managed = False# Indicates that Django should not handle the creation, modification, or deletion of the table - MW
        db_table = 'STAFF'# Explicitly specify the name of the database table to which this model is mapped - MW
