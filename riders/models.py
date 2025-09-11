# riders/models.py
from django.db import models

# === Riders (existing table: ADA_Riders_q) ===
class AdaRiderQ(models.Model):
    # Choose a stable PK; NEW_ID looks like the natural integer key in your data.
    NEW_ID = models.IntegerField(primary_key=True)

    # Columns per your dump (case-insensitive in SQL Server)
    adaid      = models.CharField(max_length=255, blank=True, null=True)
    ADD1       = models.CharField(max_length=255, blank=True, null=True)      # extra address line?
    aptstname  = models.CharField(max_length=255, blank=True, null=True)      # street name
    aptstnum   = models.CharField(max_length=50,  blank=True, null=True)      # street number
    aptunit    = models.CharField(max_length=50,  blank=True, null=True)      # apartment/unit
    ehid       = models.CharField(max_length=255, blank=True, null=True)
    fname      = models.CharField(max_length=255, blank=True, null=True)
    Inactive   = models.BooleanField(default=False)                            # BIT in SQL Server
    lname      = models.CharField(max_length=255, blank=True, null=True)
    missaddr   = models.CharField(max_length=255, blank=True, null=True)      # maybe mailing addr?
    Notes      = models.TextField(blank=True, null=True)
    RDRN       = models.CharField(max_length=255, blank=True, null=True)      # rider number?
    zip        = models.CharField(max_length=20,  blank=True, null=True)

    class Meta:
        db_table = 'ADA_Riders_q'
        managed = False  # don't let Django manage/create/drop this table
        indexes = [
            models.Index(fields=['lname', 'fname']),
            models.Index(fields=['adaid']),
        ]

    def __str__(self):
        return f"{self.lname or ''}, {self.fname or ''} ({self.adaid or 'no ADA ID'})"


# === Ticket Purchases (existing table: ADA_Ticket_Purchases_t) ===
class AdaTicketPurchasesT(models.Model):
    # Pick a primary key; NEW_ID is present in your dump. If TransID is unique in your DB, you can switch to that.
    NEW_ID    = models.IntegerField(primary_key=True)

    bkqty     = models.IntegerField(blank=True, null=True)
    chknum    = models.CharField(max_length=255, blank=True, null=True)
    deptenter = models.CharField(max_length=255, blank=True, null=True)
    ehid      = models.CharField(max_length=255, blank=True, null=True)
    fname     = models.CharField(max_length=255, blank=True, null=True)
    inpermail = models.CharField(max_length=255, blank=True, null=True)
    lname     = models.CharField(max_length=255, blank=True, null=True)
    maildate  = models.DateTimeField(blank=True, null=True)
    old_transid = models.CharField(max_length=255, blank=True, null=True)
    paytype   = models.CharField(max_length=255, blank=True, null=True)
    puramt    = models.IntegerField(blank=True, null=True)    # int in your list
    purdate   = models.DateTimeField(blank=True, null=True)
    TransID   = models.IntegerField(blank=True, null=True)

    # Join key hint: there's no explicit FK, but you have fname/lname/ehid/adaid in other tables.
    # If purchases relate to riders by (fname,lname) or another key, we can query by matching fields.

    class Meta:
        db_table = 'ADA_Ticket_Purchases_t'
        managed = False
        indexes = [
            models.Index(fields=['purdate']),
        ]


# === Purchases (existing table: ADA_Purchases_q) – optional if you need it ===
class AdaPurchasesQ(models.Model):
    NEW_ID    = models.IntegerField(primary_key=True)
    adaid     = models.CharField(max_length=255, blank=True, null=True)
    bkqty     = models.IntegerField(blank=True, null=True)
    chknum    = models.CharField(max_length=255, blank=True, null=True)
    deptenter = models.CharField(max_length=255, blank=True, null=True)
    ehid      = models.CharField(max_length=255, blank=True, null=True)
    fname     = models.CharField(max_length=255, blank=True, null=True)
    inpermail = models.CharField(max_length=255, blank=True, null=True)
    lname     = models.CharField(max_length=255, blank=True, null=True)
    maildate  = models.DateTimeField(blank=True, null=True)
    old_transid = models.CharField(max_length=255, blank=True, null=True)
    paytype   = models.CharField(max_length=255, blank=True, null=True)
    puramt    = models.IntegerField(blank=True, null=True)
    purdate   = models.DateTimeField(blank=True, null=True)
    TransID   = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'ADA_Purchases_q'
        managed = False
        indexes = [
            models.Index(fields=['purdate']),
        ]
