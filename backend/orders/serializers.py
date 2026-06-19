from tracking.models import ProgressEvent
from reviews.models import ServiceReview


def worker_summary(worker):
    if not worker:
        return None
    return {
        "id": worker.id,
        "name": worker.name,
        "phone": worker.phone,
        "vehicle": worker.vehicle,
        "rating": float(worker.rating),
        "review_count": worker.review_count if hasattr(worker, "review_count") else 0,
    }


def order_to_dict(order, include_detail=False):
    can_review, review_reason = order.can_review()
    data = {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "origin": order.origin,
        "destination": order.destination,
        "move_date": order.move_date.isoformat(),
        "move_time": order.move_time.strftime("%H:%M"),
        "items": order.items,
        "note": order.note,
        "status": order.status,
        "status_label": order.get_status_display(),
        "exception_status": order.exception_status,
        "exception_status_label": order.get_exception_status_display(),
        "settlement_status": order.settlement_status,
        "settlement_status_label": order.get_settlement_status_display(),
        "can_review": can_review,
        "review_reason": review_reason,
        "claimed_by": worker_summary(order.claimed_by),
        "assigned_to": worker_summary(order.assigned_to),
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }
    if include_detail:
        data["progress"] = [
            {
                "id": event.id,
                "stage": event.stage,
                "stage_label": event.get_stage_display(),
                "message": event.message,
                "created_at": event.created_at.isoformat(),
            }
            for event in ProgressEvent.objects.filter(order=order)
        ]
        review = ServiceReview.get_current_for_order(order)
        data["review"] = (
            {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment,
                "version": review.version,
                "created_at": review.created_at.isoformat(),
            }
            if review
            else None
        )
    return data
