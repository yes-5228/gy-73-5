from django.db import models
from django.db.models import Avg
from django.db.models.functions import Coalesce


class Worker(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_BUSY = "busy"
    STATUS_OFFLINE = "offline"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "可接单"),
        (STATUS_BUSY, "服务中"),
        (STATUS_OFFLINE, "离线"),
    ]

    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=30)
    vehicle = models.CharField(max_length=80)
    service_area = models.CharField(max_length=120)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    review_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def recalculate_rating(self):
        from reviews.models import ServiceReview

        result = (
            ServiceReview.objects.filter(
                order__assigned_to=self,
                is_current=True,
                order__status="completed",
            )
            .aggregate(avg_rating=Coalesce(Avg("rating"), 5.0), count=models.Count("id", distinct=True))
        )

        avg_rating = result["avg_rating"]
        count = result["count"]

        self.rating = round(float(avg_rating), 1)
        self.review_count = count
        self.save(update_fields=["rating", "review_count"])

        return self.rating, self.review_count
