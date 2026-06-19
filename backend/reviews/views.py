import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from orders.models import MoveOrder
from workers.models import Worker

from .models import ServiceReview


def review_to_dict(review, include_history=False):
    data = {
        "id": review.id,
        "order_id": review.order_id,
        "rating": review.rating,
        "comment": review.comment,
        "version": review.version,
        "is_current": review.is_current,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat(),
    }
    if include_history:
        history = ServiceReview.get_history_for_order(review.order)
        data["history"] = [
            {
                "id": h.id,
                "rating": h.rating,
                "comment": h.comment,
                "version": h.version,
                "is_current": h.is_current,
                "created_at": h.created_at.isoformat(),
            }
            for h in history
        ]
    return data


@csrf_exempt
@require_http_methods(["POST"])
def create_review(request, order_id):
    order = get_object_or_404(MoveOrder, pk=order_id)

    can_review, reason = order.can_review()
    if not can_review:
        return JsonResponse({"error": reason}, status=400)

    payload = json.loads(request.body.decode("utf-8"))
    rating = payload.get("rating")
    comment = payload.get("comment", "")

    if rating is None or not (1 <= int(rating) <= 5):
        return JsonResponse({"error": "评分必须在1-5星之间"}, status=400)

    review, created = ServiceReview.create_or_update(
        order=order,
        rating=int(rating),
        comment=comment,
    )

    if order.assigned_to:
        worker = Worker.objects.get(pk=order.assigned_to.id)
        worker.recalculate_rating()

    status_code = 201 if created else 200
    return JsonResponse(review_to_dict(review, include_history=True), status=status_code)


@require_http_methods(["GET"])
def review_list(_request):
    reviews = ServiceReview.objects.filter(is_current=True).select_related("order")
    return JsonResponse({"reviews": [review_to_dict(review) for review in reviews]})


@require_http_methods(["GET"])
def review_detail(request, order_id):
    order = get_object_or_404(MoveOrder, pk=order_id)
    review = ServiceReview.get_current_for_order(order)
    if not review:
        return JsonResponse({"review": None, "can_review": order.can_review()[0]})
    return JsonResponse({"review": review_to_dict(review, include_history=True), "can_review": True})


@require_http_methods(["GET"])
def review_history(request, order_id):
    order = get_object_or_404(MoveOrder, pk=order_id)
    history = ServiceReview.get_history_for_order(order)
    return JsonResponse(
        {
            "order_id": order_id,
            "history": [
                {
                    "id": h.id,
                    "rating": h.rating,
                    "comment": h.comment,
                    "version": h.version,
                    "is_current": h.is_current,
                    "created_at": h.created_at.isoformat(),
                }
                for h in history
            ],
        }
    )
