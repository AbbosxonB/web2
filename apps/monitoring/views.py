from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from apps.tests.models import Test
from apps.logs.models import SystemLog

class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        now = timezone.now()
        five_mins_ago = now - timedelta(minutes=5)

        # 1. Online Users (Active in last 5 mins)
        # Assuming SystemLog tracks 'login' or any action. 
        # Better: Count unique users who logged an action in last 5 mins.
        online_count = SystemLog.objects.filter(timestamp__gte=five_mins_ago).values('user').distinct().count()

        # 2. Active Exams
        active_exams = Test.objects.filter(status='active', start_date__lte=now, end_date__gte=now)
        active_exams_data = [{
            'id': t.id,
            'title': t.title,
            'subject': t.subject.name,
            'group_count': t.groups.count(),
            'start_date': t.start_date,
            'end_date': t.end_date,
            # 'student_count': ... (Calculate if needed, heavy query)
        } for t in active_exams]

        return Response({
            'online_users': online_count,
            'active_exams': active_exams_data,
            'active_exams_count': active_exams.count()
        })

class OnlineUsersDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        now = timezone.now()
        five_mins_ago = now - timedelta(minutes=5)

        # Get unique users active in last 5 mins
        logs = SystemLog.objects.filter(timestamp__gte=five_mins_ago).select_related('user').order_by('-timestamp')
        
        # We need unique users, but we also want their latest timestamp.
        # SystemLog might have multiple entries per user.
        # We'll use a dictionary to deduplicate by user_id
        online_users = {}
        for log in logs:
            if log.user and log.user.id not in online_users:
                # Basic user info
                group_name = "-"
                # Try to get group if student
                if hasattr(log.user, 'student_profile') and log.user.student_profile.group:
                    group_name = log.user.student_profile.group.name

                online_users[log.user.id] = {
                    'id': log.user.id,
                    'full_name': f"{log.user.first_name} {log.user.last_name}",
                    'username': log.user.username,
                    'role': log.user.role,
                    'group': group_name,
                    'last_seen': log.timestamp,
                    'ip': log.ip_address
                }
        
        return Response(list(online_users.values()))

class SecurityAlertView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Fetch logs related to security violations
        # We need to define what 'action' strings constitute a violation.
        # For now, let's assume actions starting with 'Security:' or specific keywords.
        alerts = SystemLog.objects.filter(
            Q(action__icontains='Security') | 
            Q(action__icontains='IP') | 
            Q(action__icontains='Violation')
        ).order_by('-timestamp')[:20]

        data = [{
            'id': l.id,
            'user': l.user.username if l.user else 'Unknown',
            'action': l.action,
            'details': l.details,
            'ip': l.ip_address,
            'timestamp': l.timestamp
        } for l in alerts]

        return Response(data)

class MassControlView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        action = request.data.get('action')
        
        if action == 'pause_all':
            # Pause all ACTIVE tests
            count = Test.objects.filter(status='active').update(status='paused')
            return Response({'status': 'success', 'message': f"{count} ta test pauza qilindi."})
        
        elif action == 'resume_all':
            # Resume all PAUSED tests
            count = Test.objects.filter(status='paused').update(status='active')
            return Response({'status': 'success', 'message': f"{count} ta test davom ettirildi."})
        
        elif action == 'extend_time':
            minutes = int(request.data.get('minutes', 15))
            # Extend ACTIVE tests by X minutes
            from django.db.models import F
            count = Test.objects.filter(status='active').update(end_date=F('end_date') + timedelta(minutes=minutes))
            return Response({'status': 'success', 'message': f"{count} ta test vaqti {minutes} daqiqaga uzaytirildi."})

class ReportViolationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        details = request.data.get('details', 'Suspicious activity detected')
        action_type = request.data.get('type', 'Security Violation')
        
        # Log it
        # Assuming you have a LOGGING logic or SystemLog creation
        # We need to import User from settings if not available, but here we have request.user
        
        SystemLog.objects.create(
            user=request.user,
            action=f"Security: {action_type}",
            details=details,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'status': 'logged'})

def monitoring_page_view(request):
    from django.shortcuts import render
    return render(request, 'monitoring/dashboard.html')
