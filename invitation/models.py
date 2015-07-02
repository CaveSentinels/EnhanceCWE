from django.db import models

class EmailInvitation(models.Model):
    email_address = models.CharField(max_length=100)



