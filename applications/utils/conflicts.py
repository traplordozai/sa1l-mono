from internships.models import Internship
from applications.models import Application
from django.db.models import Q
from django.utils import timezone

def detect_conflicts(user):
    """
    Detect potential conflicts for a user's internships and applications.
    
    Returns a list of conflict dictionaries with details about each conflict found.
    Possible conflict types:
    - overlap: Internship date ranges overlap
    - competing_offers: Multiple active offers
    - expired_offer: Offer past expiration date
    """
    conflicts = []

    # Check for overlapping internships
    internships = Internship.objects.filter(user=user)
    for i in internships:
        overlapping = internships.exclude(id=i.id).filter(
            start_date__lte=i.end_date,
            end_date__gte=i.start_date,
        )
        if overlapping.exists():
            conflicts.append({
                "type": "overlap",
                "internship_id": i.id,
                "overlapping_ids": list(overlapping.values_list('id', flat=True))
            })

    # Check for multiple active offers
    active_offers = Application.objects.filter(
        candidate=user,
        status="offered",
        expires_at__gt=timezone.now()
    )
    if active_offers.count() > 1:
        conflicts.append({
            "type": "competing_offers",
            "count": active_offers.count(),
            "offer_ids": list(active_offers.values_list('id', flat=True))
        })

    # Check for expired offers that haven't been marked as stale
    expired_offers = Application.objects.filter(
        candidate=user,
        status="offered",
        expires_at__lt=timezone.now()
    )
    for offer in expired_offers:
        conflicts.append({
            "type": "expired_offer",
            "application_id": offer.id,
            "expired_at": offer.expires_at
        })

    return conflicts

def get_conflict_details(conflict):
    """
    Get detailed information about a specific conflict.
    """
    if conflict["type"] == "overlap":
        internship = Internship.objects.get(id=conflict["internship_id"])
        overlapping = Internship.objects.filter(id__in=conflict["overlapping_ids"])
        return {
            "message": f"Internship '{internship.name}' overlaps with {len(overlapping)} other internships",
            "internship": {
                "id": internship.id,
                "name": internship.name,
                "period": f"{internship.start_date} to {internship.end_date}"
            },
            "overlapping": [
                {
                    "id": i.id,
                    "name": i.name,
                    "period": f"{i.start_date} to {i.end_date}"
                }
                for i in overlapping
            ]
        }
    
    elif conflict["type"] == "competing_offers":
        offers = Application.objects.filter(id__in=conflict["offer_ids"])
        return {
            "message": f"You have {conflict['count']} competing offers",
            "offers": [
                {
                    "id": offer.id,
                    "position": offer.position,
                    "expires_at": offer.expires_at
                }
                for offer in offers
            ]
        }
    
    elif conflict["type"] == "expired_offer":
        offer = Application.objects.get(id=conflict["application_id"])
        return {
            "message": f"Offer for {offer.position} expired at {conflict['expired_at']}",
            "offer": {
                "id": offer.id,
                "position": offer.position,
                "expired_at": offer.expires_at
            }
        }

    return None

def resolve_overlap_conflict(internship_id, action="withdraw"):
    """
    Resolve an overlapping internship conflict.
    Actions: withdraw, adjust_dates
    """
    internship = Internship.objects.get(id=internship_id)
    if action == "withdraw":
        internship.status = "withdrawn"
        internship.save()
        return True
    return False

def resolve_competing_offers(user, accepted_application_id):
    """
    Resolve competing offers by accepting one and rejecting others.
    """
    Application.objects.filter(
        candidate=user,
        status="offered"
    ).exclude(
        id=accepted_application_id
    ).update(status="rejected")
    
    accepted = Application.objects.get(id=accepted_application_id)
    accepted.status = "hired"
    accepted.save()
    
    return True

def get_user_conflicts_summary(user):
    """
    Get a summary of all conflicts for a user.
    """
    conflicts = detect_conflicts(user)
    return {
        "total_conflicts": len(conflicts),
        "overlap_count": sum(1 for c in conflicts if c["type"] == "overlap"),
        "competing_offers": sum(1 for c in conflicts if c["type"] == "competing_offers"),
        "expired_offers": sum(1 for c in conflicts if c["type"] == "expired_offer"),
        "conflicts": [get_conflict_details(c) for c in conflicts]
    }
