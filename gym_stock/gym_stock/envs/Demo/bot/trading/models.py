from django.db import models

# Create your models here.

class BotDetail(models.Model):
    name = models.CharField(max_length = 10)
    capital = models.FloatField(blank = False, null = False)
    class Meta:
        ordering = ('name', )

    def __str__(self):
        return "%s"%(self.name)

class BotAction(models.Model):
    name = models.ForeignKey(BotDetail , on_delete = models.CASCADE)
    date = models.DateField(blank= True, null = True)
    action = models.CharField(max_length = 4)
    symbol = models.CharField(max_length = 10)
    volume = models.FloatField(blank=True, null = True)
    averagePrice = models.FloatField(blank=True, null = True)
    class Meta:
        ordering = ('name', 'symbol', 'date')

    def __str__(self):
        return "%s"%(self.name)

class BotPortfolio(models.Model):
    name = models.ForeignKey(BotDetail, on_delete= models.CASCADE)
    symbol = models.CharField(max_length=10)
    volume = models.FloatField(blank=True, null=True)
    averagePrice = models.FloatField(blank=True, null = True)
    marketPrice = models.FloatField(blank=True, null = True)
    profit = models.FloatField(blank=True, null = True)
    class Meta:
        ordering = ('name', 'symbol', )

    def __str__(self):
        return "%s"%(self.name)