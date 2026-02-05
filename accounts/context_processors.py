def student_profile(request):
    if request.user.is_authenticated:
        return {
            'student_profile': getattr(request.user, 'studentprofile', None)
        }
    return {}
