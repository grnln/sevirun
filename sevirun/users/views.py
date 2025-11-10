from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from users.models import AppUser
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, redirect

@staff_member_required
def admin_users_view(request):
    users = AppUser.objects.all()
    return render(request, 'users/admin_users.html', {'users': users})


@staff_member_required
def admin_edit_user(request, user_id):
    user = get_object_or_404(AppUser, id=user_id)
    return render(request, 'users/admin_edit_user.html', {'user': user})

@staff_member_required
@require_http_methods(['GET', 'POST'])
def admin_delete_user(request, user_id):
    user = get_object_or_404(AppUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('admin_users')
    return render(request, 'users/admin_confirm_delete.html', {'user': user})


@staff_member_required
def admin_create_user(request):
    """Stub create-user view. Replace with a proper ModelForm in a follow-up.
    Currently renders a simple page with instructions and a back link."""
    return render(request, 'users/admin_create_user.html')
