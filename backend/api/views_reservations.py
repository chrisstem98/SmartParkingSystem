import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import ParkingLot, Reservation


def _parse_iso_datetime(value: str):
    """
    Parse ISO datetime string into a timezone-aware datetime.
    Accepts:
    - "2025-12-30T10:00:00"
    - "2025-12-30T10:00:00Z"
    - "2025-12-30T10:00:00+02:00"
    """
    if not isinstance(value, str) or not value.strip():
        return None

    v = value.strip()

    # Django parse_datetime may not like trailing "Z"
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"

    dt = parse_datetime(v)
    if dt is None:
        return None

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())

    return dt


def _serialize_reservation(r: Reservation):
    return {
        "id": r.id,
        "site": r.lot.code,
        "device_id": r.device_id,
        "start_time": r.start_time.isoformat(),
        "end_time": r.end_time.isoformat(),
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@csrf_exempt
@require_http_methods(["POST"])
def create_reservation(request):
    """
    Mobile endpoint: create a new reservation.
    Expects JSON body with:
    - site
    - device_id
    - start_time (ISO)
    - end_time (ISO)
    """
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    site = payload.get("site")
    device_id = payload.get("device_id")
    start_time_raw = payload.get("start_time")
    end_time_raw = payload.get("end_time")

    if not all([site, device_id, start_time_raw, end_time_raw]):
        return JsonResponse({"error": "Missing required fields"}, status=400)

    lot = get_object_or_404(ParkingLot, code=site)

    start_dt = _parse_iso_datetime(start_time_raw)
    end_dt = _parse_iso_datetime(end_time_raw)

    if start_dt is None or end_dt is None:
        return JsonResponse({"error": "Invalid datetime format (ISO expected)"}, status=400)

    if end_dt <= start_dt:
        return JsonResponse({"error": "end_time must be after start_time"}, status=400)

    now = timezone.now()
    if start_dt < now:
        return JsonResponse({"error": "start_time cannot be in the past"}, status=400)

    # Simple rule: 1 active reservation per device per lot (MVP)
    active_exists = Reservation.objects.filter(
        lot=lot,
        device_id=device_id,
        status=Reservation.STATUS_ACTIVE,
        end_time__gte=now,
    ).exists()

    if active_exists:
        return JsonResponse(
            {"error": "Active reservation already exists for this parking"},
            status=409,
        )

    reservation = Reservation.objects.create(
        lot=lot,
        device_id=device_id,
        start_time=start_dt,
        end_time=end_dt,
        status=Reservation.STATUS_ACTIVE,
    )

    return JsonResponse(_serialize_reservation(reservation), status=201)


@require_http_methods(["GET"])
def list_reservations(request):
    """
    Admin + Mobile listing endpoint.

    - If device_id is provided:
        returns reservations for this device (mobile "My reservations")
      GET /api/reservations/list/?device_id=...

    - If device_id is NOT provided:
        returns ALL reservations (admin table)
      GET /api/reservations/list/
    """
    device_id = request.GET.get("device_id")

    qs = Reservation.objects.select_related("lot")

    if device_id:
        qs = qs.filter(device_id=device_id)

    data = [_serialize_reservation(r) for r in qs]

    return JsonResponse({"reservations": data}, status=200)


@csrf_exempt
@require_http_methods(["DELETE"])
def cancel_reservation(request, reservation_id):
    """
    Cancel endpoint:
    - Admin: can cancel by ID without device_id
      DELETE /api/reservations/<id>/

    - Mobile: can also send device_id (optional), but not required now
      DELETE /api/reservations/<id>/?device_id=...
    """
    # If device_id is provided, enforce ownership. If not, allow admin-style cancel.
    device_id = request.GET.get("device_id")

    if device_id:
        reservation = get_object_or_404(Reservation, id=reservation_id, device_id=device_id)
    else:
        reservation = get_object_or_404(Reservation, id=reservation_id)

    reservation.status = Reservation.STATUS_CANCELLED
    reservation.save(update_fields=["status"])

    return JsonResponse({"status": "cancelled", "id": reservation.id}, status=200)
