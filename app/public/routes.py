from datetime import date
from flask import Blueprint, render_template, request
from ..models import db, User, Project, Task

bp = Blueprint("public", __name__)

@bp.route("/")
def dashboard():
    users_count = User.query.count()
    projects_count = Project.query.count()
    tasks_count = Task.query.count()
    overdue_count = Task.query.filter(Task.deadline.isnot(None), Task.delivery_date.is_(None), Task.deadline < date.today()).count()

    latest_tasks = Task.query.order_by(Task.id.desc()).limit(10).all()
    return render_template(
        "public/dashboard.html",
        users_count=users_count,
        projects_count=projects_count,
        tasks_count=tasks_count,
        overdue_count=overdue_count,
        latest_tasks=latest_tasks
    )

@bp.route("/users")
def users():
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template("public/users.html", users=users)

@bp.route("/users/<int:user_id>")
def user_detail(user_id):
    u = db.session.get(User, user_id)
    return render_template("public/user_detail.html", user=u)

@bp.route("/projects")
def projects():
    projects = Project.query.order_by(Project.id.desc()).all()
    return render_template("public/projects.html", projects=projects)

@bp.route("/projects/<int:project_id>")
def project_detail(project_id):
    p = db.session.get(Project, project_id)
    return render_template("public/project_detail.html", project=p)

@bp.route("/tasks")
def tasks():
    status = request.args.get("status") or None
    assignee_id = request.args.get("assignee_id", type=int)
    project_id = request.args.get("project_id", type=int)
    overdue = request.args.get("overdue")

    q = Task.query
    if status:
        q = q.filter(Task.status == status)
    if project_id:
        q = q.filter(Task.project_id == project_id)
    if overdue == "1":
        q = q.filter(Task.deadline.isnot(None), Task.delivery_date.is_(None), Task.deadline < date.today())
    if assignee_id:
        q = q.join(Task.assignees).filter(User.id == assignee_id)

    tasks = q.order_by(Task.id.desc()).all()

    users = User.query.order_by(User.last_name, User.first_name).all()
    projects = Project.query.order_by(Project.title).all()

    return render_template(
        "public/tasks.html",
        tasks=tasks,
        users=users,
        projects=projects,
        selected_project_id=project_id,
        selected_assignee_id=assignee_id,
        selected_status=status,
        selected_overdue=(overdue == "1"),
    )

@bp.route("/tasks/<int:task_id>")
def task_detail(task_id):
    t = db.session.get(Task, task_id)
    return render_template("public/task_detail.html", task=t)
