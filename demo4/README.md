# Django Multi-App Demo

A Django project with:
- `mainapp` as the central dashboard and authentication app
- `app1`, `app2`, `app3` for separate data apps
- login/signup and CRUD operations for each app
- role-based access control with `admin` and `user` groups

## Setup

1. Install Django:

```powershell
python -m pip install django
```

2. Create database and apply migrations:

```powershell
python manage.py migrate
```

3. Create a superuser for admin access:

```powershell
python manage.py createsuperuser
```

4. Run the server:

```powershell
python manage.py runserver
```

## How it works

- Visit `/signup/` to create a new user. New users are assigned the `user` role.
- Visit `/login/` to authenticate.
- Visit `/dashboard/` to access all apps.
- App-specific CRUD routes:
  - `/app1/`
  - `/app2/`
  - `/app3/`

## RBAC behavior

- Users in the `user` group can manage their own app records only.
- Users in the `admin` group or superusers can view, update, and delete all records.
