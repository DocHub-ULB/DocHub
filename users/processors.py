def user(request):
    if hasattr(request, 'user') and request.user.is_authenticated() :
        return {'user':request.user.get_profile() }
    return {}