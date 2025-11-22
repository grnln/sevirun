from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from users.models import AppUser
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import IntegrityError

@staff_member_required(login_url='login')
def admin_users_view(request):
    prev_page = request.GET.get('from', '/')

    users = AppUser.objects.all()
    return render(request, 'users/admin_users.html', {'users': users, 'from': prev_page})

@staff_member_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def admin_edit_user(request, user_id):
    user = get_object_or_404(AppUser, id=user_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        password = request.POST.get('password', '')

        if not email:
            messages.error(request, 'El correo electrónico es obligatorio.')
            return redirect('admin_edit_user', user_id=user.id)

        user.name = name
        user.surname = surname

        if AppUser.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'El correo ya está en uso por otro usuario.')
            return redirect('admin_edit_user', user_id=user.id)

        user.email = email
        user.phone_number = phone_number
        user.address = address
        user.city = city
        user.postal_code = postal_code

        if password:
            user.set_password(password)

        try:
            user.save()
        except IntegrityError:
            messages.error(request, 'El correo ya está en uso por otro usuario.')
            return redirect('admin_edit_user', user_id=user.id)
        except Exception as e:
            messages.error(request, f'Error al guardar cambios: {e}')
            return redirect('admin_edit_user', user_id=user.id)

        messages.success(request, 'Cambios guardados correctamente.')
        return redirect('admin_users')

    # GET
    return render(request, 'users/admin_edit_user.html', {'user': user})

@staff_member_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def admin_delete_user(request, user_id):
    user = get_object_or_404(AppUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('admin_users')
    # GET
    return render(request, 'users/admin_confirm_delete.html', {'user': user})


@staff_member_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def admin_create_user(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        password = request.POST.get('password', '')
        is_staff_val = request.POST.get('is_staff', '0')
        is_staff = True if is_staff_val in ('1', 'true', 'True') else False

        if not email or not password:
            messages.error(request, 'Por favor, completa los campos obligatorios (email, contraseña).')
            return redirect('admin_create_user')

        extra = {
            'name': name,
            'surname': surname,
            'phone_number': phone_number,
            'address': address,
            'city': city,
            'postal_code': postal_code,
            'is_staff': is_staff,
            'is_superuser': False,
        }

        if AppUser.objects.filter(email=email).exists():
            messages.error(request, 'Ya existe un usuario con ese correo electrónico.')
            return redirect('admin_create_user')

        try:
            AppUser.objects.create_user(email=email, password=password, **extra)
        except IntegrityError:
            messages.error(request, 'Ya existe un usuario con ese correo electrónico.')
            return redirect('admin_create_user')
        except Exception as e:
            messages.error(request, f'Error al crear el usuario: {e}')
            return redirect('admin_create_user')

        messages.success(request, 'Usuario creado correctamente.')
        return redirect('admin_users')

    # GET
    return render(request, 'users/admin_create_user.html')
