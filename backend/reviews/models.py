from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction


class ServiceReview(models.Model):
    order = models.ForeignKey(
        "orders.MoveOrder", related_name="service_reviews", on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-version"]
        unique_together = ["order", "version"]

    def __str__(self):
        return f"订单 {self.order_id}: {self.rating} 星 (版本 {self.version})"

    @classmethod
    @transaction.atomic
    def create_or_update(cls, order, rating, comment=""):
        existing_current = cls.objects.filter(order=order, is_current=True).first()

        if existing_current:
            if existing_current.rating == rating and existing_current.comment == comment:
                return existing_current, False

            existing_current.is_current = False
            existing_current.save(update_fields=["is_current", "updated_at"])
            new_version = existing_current.version + 1
        else:
            new_version = 1

        new_review = cls.objects.create(
            order=order,
            rating=rating,
            comment=comment,
            version=new_version,
            is_current=True,
        )

        return new_review, True

    @classmethod
    def get_current_for_order(cls, order):
        return cls.objects.filter(order=order, is_current=True).first()

    @classmethod
    def get_history_for_order(cls, order):
        return cls.objects.filter(order=order).order_by("-version")
