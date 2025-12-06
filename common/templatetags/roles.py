# common/templatetags/roles.py
from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def has_role(context, role):
    u = context["request"].user
    if not u.is_authenticated:
        return False
    if role == "admin":
        return u.is_superuser
    return any([
        role == "teacher" and (hasattr(u, "teacherprofile") or hasattr(u, "teacher_profile")),
        role == "student" and (hasattr(u, "studentprofile") or hasattr(u, "student_profile")),
        role == "parent"  and (hasattr(u, "parentprofile")  or hasattr(u, "parent_profile")),
    ])
