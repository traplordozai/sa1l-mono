from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Student
from .serializers import StudentSerializer
from applications.models import InternshipApplication
from feedback.models import FeedbackEntry

class StudentProfileView(generics.RetrieveUpdateAPIView):
    """View for student profile management"""
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Student, user=self.request.user)

class StudentDashboardView(APIView):
    """View for student dashboard data"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        student = get_object_or_404(Student, user=request.user)
        
        # Get application statistics
        applications = InternshipApplication.objects.filter(candidate=request.user)
        application_stats = {
            'total': applications.count(),
            'applied': applications.filter(status='applied').count(),
            'interviewing': applications.filter(status='interviewing').count(),
            'offered': applications.filter(status='offered').count(),
            'hired': applications.filter(status='hired').count(),
        }

        # Get feedback statistics
        feedback = FeedbackEntry.objects.filter(target=request.user)
        feedback_stats = {
            'total': feedback.count(),
            'peer': feedback.filter(type='peer').count(),
            'mentor': feedback.filter(type='mentor').count(),
            'self': feedback.filter(type='self').count(),
        }

        return Response({
            'profile': StudentSerializer(student).data,
            'applications': application_stats,
            'feedback': feedback_stats,
        })

class StudentApplicationsView(generics.ListAPIView):
    """View for student applications"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InternshipApplication.objects.filter(candidate=self.request.user)

    def get(self, request):
        applications = self.get_queryset()
        return Response({
            'applications': [{
                'id': app.id,
                'position': app.position,
                'status': app.status,
                'offer_sent_at': app.offer_sent_at,
                'expires_at': app.expires_at,
                'updated_at': app.updated_at,
            } for app in applications]
        })

class StudentFeedbackView(generics.ListAPIView):
    """View for student feedback"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FeedbackEntry.objects.filter(target=self.request.user)

    def get(self, request):
        feedback = self.get_queryset()
        return Response({
            'feedback': [{
                'id': entry.id,
                'type': entry.type,
                'score': entry.score,
                'comments': entry.comments,
                'reviewer': entry.reviewer.username if not entry.anonymous else 'Anonymous',
                'submitted_at': entry.submitted_at,
            } for entry in feedback]
        })

class StudentLearningPlanView(APIView):
    """View for student learning plan"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        student = get_object_or_404(Student, user=request.user)
        return Response({
            'learning_plan': student.survey_data.get('learning_plan', {}),
            'goals': student.survey_data.get('goals', []),
            'skills': student.survey_data.get('skills', []),
        })

    def post(self, request):
        student = get_object_or_404(Student, user=request.user)
        survey_data = student.survey_data or {}
        survey_data.update(request.data)
        student.survey_data = survey_data
        student.save()
        return Response({'status': 'success'}) 