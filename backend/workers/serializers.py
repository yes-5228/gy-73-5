def worker_to_dict(worker):
    return {
        "id": worker.id,
        "name": worker.name,
        "phone": worker.phone,
        "vehicle": worker.vehicle,
        "service_area": worker.service_area,
        "rating": float(worker.rating),
        "review_count": worker.review_count,
        "status": worker.status,
        "status_label": worker.get_status_display(),
    }
