import uuid

from core import fields
from core import models as core_models
from django.db import models
from django.utils.translation import gettext_lazy
from django.db import transaction
from core.datetimes.ad_datetime import datetime
from policy.models import Policy
from payer.models import Payer


class PayTypeChoices(models.TextChoices):
    BANK_TRANSFER = "B", gettext_lazy("Bank transfer")
    CASH = "C", gettext_lazy("Cash")
    MOBILE = "M", gettext_lazy("Mobile phone")
    FUNDING = "F", gettext_lazy("Funding")


class Premium(core_models.VersionedModel):
    id = models.AutoField(db_column="PremiumId", primary_key=True)
    uuid = models.CharField(
        db_column="PremiumUUID", max_length=36, default=uuid.uuid4, unique=True
    )
    policy = models.ForeignKey(
        Policy, models.DO_NOTHING, db_column="PolicyID", related_name="premiums"
    )
    payer = models.ForeignKey(
        Payer,
        models.DO_NOTHING,
        db_column="PayerID",
        blank=True,
        null=True,
        related_name="premiums",
    )
    amount = models.DecimalField(
        db_column="Amount", max_digits=18, decimal_places=2)
    receipt = models.CharField(db_column="Receipt", max_length=50)
    pay_date = fields.DateField(db_column="PayDate")
    pay_type = models.CharField(
        db_column="PayType", max_length=1,
    default='Cash')  # , choices=PayTypeChoices.choices
    is_photo_fee = models.BooleanField(
        db_column="isPhotoFee", blank=True, null=True, default=False
    )
    is_offline = models.BooleanField(
        db_column="isOffline", blank=True, null=True, default=False
    )
    reporting_id = models.IntegerField(
        db_column="ReportingId", blank=True, null=True)
    reporting_commission_id = models.IntegerField(
        db_column="ReportingCommissionID", blank=True, null=True)
    overview_commission_report = models.DateTimeField(
        db_column="OverviewCommissionReport", blank=True, null=True)
    all_details_commission_report = models.DateTimeField(
        db_column="AllDetailsCommissionReport", blank=True, null=True)
    source = models.CharField(
        db_column="Source", max_length=50, blank=True, null=True)
    source_version = models.CharField(
        db_column="SourceVersion", max_length=15, blank=True, null=True)

    audit_user_id = models.IntegerField(db_column="AuditUserID")
    created_date = models.DateTimeField(
        db_column="CreatedDate", default=datetime.now)
    #rowid = models.TextField(db_column='RowID', blank=True, null=True)
    
    def other_premiums(self):
        return self.policy.premiums.aggregate(
            other_premiums = models.Sum(
                'amount',
                filter = models.Q(~models.Q(id=self.id) & models.Q(*core_models.filter_validity(prefix=''),is_photo_fee=False))
            )
        )['other_premiums'] or 0
    class Meta:
        managed = True
        db_table = 'tblPremium'


class PremiumMutation(core_models.UUIDModel, core_models.ObjectMutation):
    premium = models.ForeignKey(
        Premium, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='premiums')

    class Meta:
        managed = True
        db_table = "contribution_PremiumMutation"

#AUTO GENERATE RECEIPT NUMBER HERE INNOCENT

class Receipt(models.Model):
    receipt = models.CharField(max_length=20, unique=True)

    @staticmethod
    def generate_receipt_number():
        last_receipt = Premium.objects.all().order_by('id').last()
        if not last_receipt:
            return 'R000001'
        receipt_number = last_receipt.receipt
        receipt_int = int(receipt_number[1:]) + 1
        new_receipt_number = 'R' + str(receipt_int).zfill(6)
        return new_receipt_number

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            while True:
                self.receipt_number = self.generate_receipt_number()
                if not Receipt.objects.filter(receipt_number=self.receipt_number).exists():
                    break
        super(Receipt, self).save(*args, **kwargs)
