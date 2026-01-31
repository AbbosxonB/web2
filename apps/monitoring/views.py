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
        # Using the new last_activity field
        from django.contrib.auth import get_user_model
        User = get_user_model()
        online_count = User.objects.filter(last_activity__gte=five_mins_ago, role='student').count()

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

        # Get users active in last 5 mins
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(last_activity__gte=five_mins_ago, role='student').select_related('student_profile__group').order_by('-last_activity')
        
        online_users_data = []
        for user in users:
            group_name = "-"
            # Try to get group if student
            if hasattr(user, 'student_profile') and user.student_profile.group:
                group_name = user.student_profile.group.name

            online_users_data.append({
                'id': user.id,
                'full_name': f"{user.first_name} {user.last_name}",
                'username': user.username,
                'role': user.role,
                'group': group_name,
                'last_seen': user.last_activity,
                'ip': None # IP tracking needs middleware or dedicated logic if strict requirement
            })
        
        return Response(online_users_data)

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

class GlobalSettingsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from apps.monitoring.models import GlobalSetting
        val = GlobalSetting.get_value('camera_required_globally', 'false')
        return Response({'camera_required_globally': val == 'true'})

    def post(self, request):
        from apps.monitoring.models import GlobalSetting
        key = request.data.get('key')
        value = request.data.get('value')
        
        if key == 'camera_required_globally':
            GlobalSetting.set_value(key, str(value).lower())
            return Response({'status': 'success', 'key': key, 'value': value})
            
        return Response({'error': 'Invalid key'}, status=400)

class LiveProctoringView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        now = timezone.now()
        thirty_secs_ago = now - timedelta(seconds=30) # Consider online if snap within 30s
        
        # Get latest snapshot for each student/test
        # Efficient way: Group by student/test, take max(timestamp)
        # OR just filter TestSnapshots in last 30s and distinct.
        
        from apps.tests.models import TestSnapshot
        snapshots = TestSnapshot.objects.filter(timestamp__gte=thirty_secs_ago).select_related('student', 'test').order_by('-timestamp')
        
        # Deduplicate manually or via distinct (Postgres only for distinct('student'))
        # Using manual dict for compatibility
        latest_snaps = {}
        for snap in snapshots:
            if snap.student_id not in latest_snaps:
                latest_snaps[snap.student_id] = snap
                
        data = []
        for snap in latest_snaps.values():
            data.append({
                'student_name': snap.student.full_name,
                'student_id': snap.student.student_id,
                'test_title': snap.test.title,
                'image_url': snap.image.url if snap.image else None,
                'timestamp': snap.timestamp,
                'status': 'online' # Logic: if here, it's recent
            })
            
        return Response(data)

def monitoring_page_view(request):
    from django.shortcuts import render
    return render(request, 'monitoring/dashboard.html')
