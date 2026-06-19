from django.db import models


class MoveOrder(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CLAIMED = "claimed"
    STATUS_ASSIGNED = "assigned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "待抢单"),
        (STATUS_CLAIMED, "已抢单"),
        (STATUS_ASSIGNED, "已派单"),
        (STATUS_IN_PROGRESS, "服务中"),
        (STATUS_COMPLETED, "已完成"),
    ]

    EXCEPTION_NONE = "none"
    EXCEPTION_OPEN = "open"
    EXCEPTION_CLOSED = "closed"
    EXCEPTION_CHOICES = [
        (EXCEPTION_NONE, "无异常"),
        (EXCEPTION_OPEN, "异常未关闭"),
        (EXCEPTION_CLOSED, "异常已关闭"),
    ]

    SETTLEMENT_PENDING = "pending"
    SETTLEMENT_CONFIRMED = "confirmed"
    SETTLEMENT_CHOICES = [
        (SETTLEMENT_PENDING, "结算待确认"),
        (SETTLEMENT_CONFIRMED, "结算已确认"),
    ]

    customer_name = models.CharField(max_length=50)
    customer_phone = models.CharField(max_length=30)
    origin = models.CharField(max_length=160)
    destination = models.CharField(max_length=160)
    move_date = models.DateField()
    move_time = models.TimeField()
    items = models.TextField(blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    exception_status = models.CharField(
        max_length=20, choices=EXCEPTION_CHOICES, default=EXCEPTION_NONE
    )
    settlement_status = models.CharField(
        max_length=20, choices=SETTLEMENT_CHOICES, default=SETTLEMENT_PENDING
    )
    claimed_by = models.ForeignKey(
        "workers.Worker",
        related_name="claimed_orders",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    assigned_to = models.ForeignKey(
        "workers.Worker",
        related_name="assigned_orders",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer_name}: {self.origin} -> {self.destination}"

    def can_review(self):
        if self.status != self.STATUS_COMPLETED:
            return False, "服务未完成，暂不能评价"
        if self.exception_status == self.EXCEPTION_OPEN:
            return False, "订单存在未关闭异常，暂不能评价"
        if self.settlement_status != self.SETTLEMENT_CONFIRMED:
            return False, "结算未确认，暂不能评价"
        return True, ""
