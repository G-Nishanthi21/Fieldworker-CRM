from django.contrib.auth import get_user_model
from visits.models import Visit

User = get_user_model()


def get_customer(customer_id):
    """accounts.User table la irundhu customer basic info"""
    user = User.objects.filter(id=customer_id).first()

    if not user:
        return {"success": False, "message": "Customer not found"}

    return {
        "success": True,
        "customer": {
            "name": user.get_full_name() or user.username,
            "phone": user.phone_number,
            "email": user.email,
        }
    }


def get_customer_requests(customer_id):
    """Customer book panna ella visit/requests-um list-a eduthukum"""
    visits = Visit.objects.filter(customer_id=customer_id).order_by('-requested_at')

    if not visits.exists():
        return {"success": True, "requests": []}

    request_list = []
    for v in visits:
        request_list.append({
            "id": v.id,
            "status": v.status,
            "worker": v.worker.get_full_name() if v.worker else "Not Assigned",
            "site_address": v.site_address,
            "requested_at": v.requested_at.strftime("%d %b %Y") if v.requested_at else "N/A",
        })

    return {"success": True, "requests": request_list}