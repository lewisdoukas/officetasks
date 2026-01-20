from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from ..models import db, User, Project, Task, TaskComment, ProjectAttachment, Rank
from .forms import LoginForm, UserForm, ProjectForm, TaskForm, AttachmentForm, CommentForm

bp = Blueprint("admin", __name__)

def admin_required():
    if not current_user.is_admin:
        flash("Admins only.", "danger")
        return False
    return True


@bp.route("/")
@login_required
def index():
    if not admin_required():
        return redirect(url_for("public.dashboard"))
    return render_template("admin/users.html", users=User.query.order_by(User.last_name).all())


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # simple login: admin identified by last_name + password
        user = User.query.filter_by(last_name=form.username.data.strip()).first()
        if not user or not user.is_admin or not user.password_hash:
            flash("Invalid credentials.", "danger")
        elif check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for("admin.index"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("admin/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("public.dashboard"))


# ---- USERS ----
@bp.route("/users")
@login_required
def users():
    if not admin_required():
        return redirect(url_for("public.users"))
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template("admin/users.html", users=users)


@bp.route("/users/new", methods=["GET", "POST"])
@login_required
def user_new():
    if not admin_required():
        return redirect(url_for("public.users"))

    form = UserForm()
    if form.validate_on_submit():
        u = User(
            rank=Rank(form.rank.data),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            internal_phone=form.internal_phone.data.strip() if form.internal_phone.data else None,
            mobile_phone=form.mobile_phone.data.strip() if form.mobile_phone.data else None,
            active=bool(form.active.data),
            is_admin=bool(form.is_admin.data),
        )
        if form.is_admin.data and form.password.data:
            u.password_hash = generate_password_hash(form.password.data)
        db.session.add(u)
        db.session.commit()
        flash("User created.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, mode="new")


@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def user_edit(user_id):
    if not admin_required():
        return redirect(url_for("public.users"))

    u = db.session.get(User, user_id)
    if not u:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users"))

    form = UserForm(
        rank=u.rank.value,
        first_name=u.first_name,
        last_name=u.last_name,
        internal_phone=u.internal_phone,
        mobile_phone=u.mobile_phone,
        active=u.active,
        is_admin=u.is_admin
    )
    if form.validate_on_submit():
        u.rank = Rank(form.rank.data)
        u.first_name = form.first_name.data.strip()
        u.last_name = form.last_name.data.strip()
        u.internal_phone = form.internal_phone.data.strip() if form.internal_phone.data else None
        u.mobile_phone = form.mobile_phone.data.strip() if form.mobile_phone.data else None
        u.active = bool(form.active.data)
        u.is_admin = bool(form.is_admin.data)
        if u.is_admin and form.password.data:
            u.password_hash = generate_password_hash(form.password.data)
        if not u.is_admin:
            u.password_hash = None
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_form.html", form=form, mode="edit")


# ---- PROJECTS ----
@bp.route("/projects")
@login_required
def projects():
    if not admin_required():
        return redirect(url_for("public.projects"))
    projects = Project.query.order_by(Project.id.desc()).all()
    return render_template("admin/projects.html", projects=projects)


@bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def project_new():
    if not admin_required():
        return redirect(url_for("public.projects"))

    form = ProjectForm()
    if form.validate_on_submit():
        p = Project(
            title=form.title.data.strip(),
            description=form.description.data,
            status=form.status.data,
        )
        db.session.add(p)
        db.session.commit()
        flash("Project created (add at least one task).", "warning")
        return redirect(url_for("admin.task_new", project_id=p.id))
    return render_template("admin/project_form.html", form=form, mode="new")


@bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def project_edit(project_id):
    if not admin_required():
        return redirect(url_for("public.projects"))

    p = db.session.get(Project, project_id)
    if not p:
        flash("Project not found.", "danger")
        return redirect(url_for("admin.projects"))

    form = ProjectForm(title=p.title, description=p.description, status=p.status)
    if form.validate_on_submit():
        p.title = form.title.data.strip()
        p.description = form.description.data
        p.status = form.status.data
        db.session.commit()
        flash("Project updated.", "success")
        return redirect(url_for("admin.projects"))

    return render_template("admin/project_form.html", form=form, mode="edit")


# ---- TASKS ----
@bp.route("/tasks")
@login_required
def tasks():
    if not admin_required():
        return redirect(url_for("public.tasks"))
    tasks = Task.query.order_by(Task.id.desc()).all()
    return render_template("admin/tasks.html", tasks=tasks)


@bp.route("/tasks/new", methods=["GET", "POST"])
@login_required
def task_new():
    if not admin_required():
        return redirect(url_for("public.tasks"))

    project_id_prefill = request.args.get("project_id", type=int)
    form = TaskForm()

    projects = Project.query.order_by(Project.title).all()
    form.project_id.choices = [(p.id, f"{p.title} (#{p.id})") for p in projects]

    users = User.query.filter_by(active=True).order_by(User.last_name, User.first_name).all()
    form.assignees.choices = [(u.id, f"{u.display_name()} [{u.rank.value}]") for u in users]

    if project_id_prefill and request.method == "GET":
        form.project_id.data = project_id_prefill

    if form.validate_on_submit():
        if not form.assignees.data:
            flash("Task must have at least one assignee.", "danger")
            return render_template("admin/task_form.html", form=form, mode="new")

        t = Task(
            project_id=form.project_id.data,
            title=form.title.data.strip(),
            description=form.description.data,
            assign_date=form.assign_date.data,
            deadline=form.deadline.data,
            delivery_date=form.delivery_date.data,
            status=form.status.data,
            priority=form.priority.data,
        )
        t.assignees = [db.session.get(User, uid) for uid in form.assignees.data]
        db.session.add(t)
        db.session.commit()
        flash("Task created.", "success")
        return redirect(url_for("admin.tasks"))

    return render_template("admin/task_form.html", form=form, mode="new")


@bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def task_edit(task_id):
    if not admin_required():
        return redirect(url_for("public.tasks"))

    t = db.session.get(Task, task_id)
    if not t:
        flash("Task not found.", "danger")
        return redirect(url_for("admin.tasks"))

    form = TaskForm(
        project_id=t.project_id,
        title=t.title,
        description=t.description,
        assign_date=t.assign_date,
        deadline=t.deadline,
        delivery_date=t.delivery_date,
        status=t.status,
        priority=t.priority,
        assignees=[u.id for u in t.assignees],
    )

    projects = Project.query.order_by(Project.title).all()
    form.project_id.choices = [(p.id, f"{p.title} (#{p.id})") for p in projects]

    users = User.query.filter_by(active=True).order_by(User.last_name, User.first_name).all()
    form.assignees.choices = [(u.id, f"{u.display_name()} [{u.rank.value}]") for u in users]

    if form.validate_on_submit():
        if not form.assignees.data:
            flash("Task must have at least one assignee.", "danger")
            return render_template("admin/task_form.html", form=form, mode="edit", task=t)

        t.project_id = form.project_id.data
        t.title = form.title.data.strip()
        t.description = form.description.data
        t.assign_date = form.assign_date.data
        t.deadline = form.deadline.data
        t.delivery_date = form.delivery_date.data
        t.status = form.status.data
        t.priority = form.priority.data
        t.assignees = [db.session.get(User, uid) for uid in form.assignees.data]

        db.session.commit()
        flash("Task updated.", "success")
        return redirect(url_for("admin.tasks"))

    return render_template("admin/task_form.html", form=form, mode="edit", task=t)


# ---- ATTACHMENTS (Project links) ----
@bp.route("/projects/<int:project_id>/attachments")
@login_required
def attachments(project_id):
    if not admin_required():
        return redirect(url_for("public.project_detail", project_id=project_id))
    p = db.session.get(Project, project_id)
    if not p:
        flash("Project not found.", "danger")
        return redirect(url_for("admin.projects"))
    return render_template("admin/attachments.html", project=p)


@bp.route("/projects/<int:project_id>/attachments/new", methods=["GET", "POST"])
@login_required
def attachment_new(project_id):
    if not admin_required():
        return redirect(url_for("public.project_detail", project_id=project_id))
    p = db.session.get(Project, project_id)
    if not p:
        flash("Project not found.", "danger")
        return redirect(url_for("admin.projects"))

    form = AttachmentForm()
    if form.validate_on_submit():
        a = ProjectAttachment(project_id=p.id, label=form.label.data.strip(), path=form.path.data.strip())
        db.session.add(a)
        db.session.commit()
        flash("Attachment link added.", "success")
        return redirect(url_for("admin.attachments", project_id=p.id))
    return render_template("admin/attachment_form.html", form=form, project=p)


# ---- COMMENTS ----
@bp.route("/tasks/<int:task_id>/comments/new", methods=["GET", "POST"])
@login_required
def comment_new(task_id):
    if not admin_required():
        return redirect(url_for("public.task_detail", task_id=task_id))

    t = db.session.get(Task, task_id)
    if not t:
        flash("Task not found.", "danger")
        return redirect(url_for("admin.tasks"))

    form = CommentForm()
    if form.validate_on_submit():
        c = TaskComment(task_id=t.id, author_id=current_user.id, body=form.body.data)
        db.session.add(c)
        db.session.commit()
        flash("Comment added.", "success")
        return redirect(url_for("public.task_detail", task_id=t.id))
    return render_template("admin/comment_form.html", form=form, task=t)
