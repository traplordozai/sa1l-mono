# backend/dashboard/services.py
from datetime import timedelta

from django.db.models import Avg, Count, F, Q, Sum
from django.utils import timezone
from imports.models import ImportLog
from matching.models import Match, MatchingRound
from organizations.models import Organization
from statements.models import Statement
from students.models import Student, StudentAreaRanking, StudentGrade


class DashboardService:
    """
    Service for aggregating dashboard statistics and metrics across domains
    """

    @staticmethod
    def get_dashboard_stats():
        """
        Calculate statistics for the admin dashboard.

        Returns:
            dict: Dictionary containing statistics and metrics
        """
        now = timezone.now()

        # Student statistics
        total_students = Student.objects.count()
        matched_students = Student.objects.filter(is_matched=True).count()
        pending_matches = Student.objects.filter(
            is_active=True, is_matched=False
        ).count()
        approval_needed = Student.objects.filter(admin_approval_needed=True).count()

        # Organization statistics
        organizations = Organization.objects.all()
        total_organizations = organizations.count()
        available_positions = (
            organizations.aggregate(total=Sum("available_positions"))["total"] or 0
        )
        filled_positions = (
            organizations.aggregate(total=Sum("filled_positions"))["total"] or 0
        )

        # Statement statistics
        ungraded_statements = Statement.objects.filter(grade__isnull=True).count()

        # Match statistics by status
        match_status_counts = Match.objects.values("status").annotate(count=Count("id"))
        match_status_dict = {
            item["status"]: item["count"] for item in match_status_counts
        }

        # Match statistics by area of law
        match_area_counts = Match.objects.values("area_of_law").annotate(
            count=Count("id")
        )

        # Get top areas of law by student interest
        top_areas = (
            StudentAreaRanking.objects.values("area__name")
            .annotate(count=Count("student"))
            .order_by("-count")[:5]
        )

        area_matches = {area["area__name"]: area["count"] for area in top_areas}

        # Growth rates (week-over-week)
        week_ago = now - timedelta(days=7)

        previous_student_count = Student.objects.filter(created_at__lt=week_ago).count()
        new_student_count = total_students - previous_student_count
        student_growth_rate = (
            (new_student_count / previous_student_count * 100)
            if previous_student_count > 0
            else 0
        )

        previous_org_count = Organization.objects.filter(
            created_at__lt=week_ago
        ).count()
        new_org_count = total_organizations - previous_org_count
        org_growth_rate = (
            (new_org_count / previous_org_count * 100) if previous_org_count > 0 else 0
        )

        # Return compiled stats
        return {
            # Card metrics
            "total_students": total_students,
            "matched_students": matched_students,
            "pending_matches": pending_matches,
            "approval_needed": approval_needed,
            "total_organizations": total_organizations,
            "available_positions": available_positions,
            "filled_positions": filled_positions,
            "ungraded_statements": ungraded_statements,
            # Chart data
            "match_status_chart": [
                {"status": status, "count": count}
                for status, count in match_status_dict.items()
            ],
            "area_law_chart": [
                {"area": area, "count": count} for area, count in area_matches.items()
            ],
            # Growth metrics
            "student_growth": {
                "rate": round(student_growth_rate, 1),
                "direction": "increase" if student_growth_rate >= 0 else "decrease",
                "new_count": new_student_count,
            },
            "organization_growth": {
                "rate": round(org_growth_rate, 1),
                "direction": "increase" if org_growth_rate >= 0 else "decrease",
                "new_count": new_org_count,
            },
            "match_rate": {
                "percentage": (
                    round((matched_students / total_students * 100), 1)
                    if total_students > 0
                    else 0
                ),
                "total": matched_students,
            },
        }

    @staticmethod
    def get_recent_activity(limit=5):
        """
        Get recent system activity for the dashboard.

        Args:
            limit: Maximum number of activities to return

        Returns:
            list: List of recent activity items
        """
        recent_activity = []

        # Get recent student profile creations/updates
        recent_students = Student.objects.order_by("-updated_at")[:limit]
        for student in recent_students:
            is_new = student.created_at >= (timezone.now() - timedelta(days=1))
            activity_type = "created profile" if is_new else "updated profile"
            recent_activity.append(
                {
                    "id": f"student-{student.id}",
                    "user": f"{student.first_name} {student.last_name}",
                    "action": activity_type,
                    "target": "Student Profile",
                    "date": student.updated_at,
                }
            )

        # Get recent organization updates
        recent_orgs = Organization.objects.order_by("-updated_at")[:limit]
        for org in recent_orgs:
            is_new = org.created_at >= (timezone.now() - timedelta(days=1))
            activity_type = "joined platform" if is_new else "updated profile"
            recent_activity.append(
                {
                    "id": f"org-{org.id}",
                    "user": org.name,
                    "action": activity_type,
                    "target": "Organization Profile",
                    "date": org.updated_at,
                }
            )

        # Get recent matches
        recent_matches = Match.objects.order_by("-created_at")[:limit]
        for match in recent_matches:
            recent_activity.append(
                {
                    "id": f"match-{match.id}",
                    "user": f"{match.student.first_name} {match.student.last_name}",
                    "action": f"matched with {match.organization.name}",
                    "target": "Match",
                    "date": match.created_at,
                }
            )

        # Get recent imports
        recent_imports = ImportLog.objects.order_by("-import_datetime")[:limit]
        for import_log in recent_imports:
            recent_activity.append(
                {
                    "id": f"import-{import_log.id}",
                    "user": import_log.imported_by or "System",
                    "action": f"imported {import_log.import_type}",
                    "target": import_log.file_name,
                    "date": import_log.import_datetime,
                }
            )

        # Sort by date (newest first) and limit to requested amount
        sorted_activity = sorted(
            recent_activity, key=lambda x: x["date"], reverse=True
        )[:limit]

        # Format dates as relative time
        for activity in sorted_activity:
            time_diff = timezone.now() - activity["date"]
            hours_diff = time_diff.total_seconds() / 3600

            if hours_diff < 1:
                minutes = int(time_diff.total_seconds() / 60)
                activity["relative_time"] = (
                    f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                )
            elif hours_diff < 24:
                hours = int(hours_diff)
                activity["relative_time"] = (
                    f"{hours} hour{'s' if hours != 1 else ''} ago"
                )
            elif hours_diff < 48:
                activity["relative_time"] = "yesterday"
            else:
                days = int(hours_diff / 24)
                activity["relative_time"] = f"{days} day{'s' if days != 1 else ''} ago"

        return sorted_activity
