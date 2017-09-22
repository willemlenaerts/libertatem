from django.db import models
# Create your models here.
class voornamen_lijst(models.Model):
    Voornaam = models.CharField(max_length=255)
    
class m_be_alles(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_be_alles(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)   

class m_vl_alles(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_vl_alles(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  

class m_br_alles(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_br_alles(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  

class m_wal_alles(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_wal_alles(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  

class m_be_18(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_be_18(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)

class m_be_18_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_be_18_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  
 
class m_be_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_be_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  

class m_vl_18(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_vl_18(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)

class m_vl_18_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_vl_18_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  
 
class m_vl_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_vl_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  
    
class m_br_18(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_br_18(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)

class m_br_18_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_br_18_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  
 
class m_br_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_br_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0) 

class m_wal_18(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_wal_18(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)

class m_wal_18_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_wal_18_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  
 
class m_wal_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)
class v_wal_65(models.Model):
    Rang = models.IntegerField(default=0)
    Voornaam = models.CharField(max_length=255)
    Aantal = models.IntegerField(default=0)  
