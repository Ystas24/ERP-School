# common/decorators.py
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def _is_teacher(u):
    return hasattr(u, "teacherprofile") or hasattr(u, "teacher_profile")

def _is_student(u):
    return hasattr(u, "studentprofile") or hasattr(u, "student_profile")

def _is_parent(u):
    return hasattr(u, "parentprofile") or hasattr(u, "parent_profile")

def _has_any_role(u, roles: tuple[str, ...]) -> bool:
    if "admin" in roles and u.is_superuser:
        return True
    if "teacher" in roles and _is_teacher(u):
        return True
    if "student" in roles and _is_student(u):
        return True
    if "parent" in roles and _is_parent(u):
        return True
    return False

def role_required(*roles):
    """
    Без аргументів -> просто login_required.
    З ролями -> вхід + перевірка ролей.
    """
    def decorator(view_func):
        if not roles:
            return login_required(view_func)

        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if _has_any_role(request.user, roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, "Недостатньо прав доступу.")
            return redirect("home")
        return _wrapped
    return decorator
