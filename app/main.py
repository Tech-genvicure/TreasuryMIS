import os
from contextlib import asynccontextmanager
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .auth import current_user, hash_password, verify_password
from .db import (
    TABLES,
    dashboard_data,
    delete_row,
    fetch_rows,
    get_conn,
    init_db,
    insert_row,
    update_row,
)
from .services import backup_database

load_dotenv()

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    scheduler.add_job(
        backup_database,
        "cron",
        hour=23,
        minute=55,
        id="daily_backup",
        replace_existing=True,
    )

    scheduler.start()

    yield

    scheduler.shutdown(wait=False)


app = FastAPI(
    title=os.getenv("APP_NAME", "Treasury MIS"),
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "change-me"),
    max_age=60 * 60 * 8,
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(
    directory="app/templates"
)


def login_redirect():
    return RedirectResponse(
        "/",
        status_code=303,
    )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    if current_user(request):
        return RedirectResponse(
            "/dashboard",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):

    with get_conn() as conn:

        user = conn.execute(
            """
            SELECT
                id,
                username,
                password_hash,
                role
            FROM users
            WHERE username = %s
            """,
            (username.strip(),),
        ).fetchone()

    if not user or not verify_password(
        password,
        user["password_hash"],
    ):

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid username or password."
            },
            status_code=401,
        )

    request.session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
    }

    return RedirectResponse(
        "/dashboard",
        status_code=303,
    )


@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return login_redirect()


@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(request: Request):

    user = current_user(request)

    if not user:
        return login_redirect()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "reporting_date": date.today().strftime(
                "%d %b %Y"
            ),
        },
    )


@app.get(
    "/spreadsheet",
    response_class=HTMLResponse,
)
def spreadsheet(request: Request):

    user = current_user(request)

    if not user:
        return login_redirect()

    return templates.TemplateResponse(
        request=request,
        name="spreadsheet.html",
        context={
            "user": user,
            "tables": TABLES,
        },
    )


def protected(request: Request):

    if not current_user(request):
        return JSONResponse(
            {"detail": "Not authenticated"},
            status_code=401,
        )

    return None


@app.get("/api/dashboard")
def api_dashboard(request: Request):

    denied = protected(request)

    if denied:
        return denied

    return dashboard_data()


@app.get("/api/table/{key}")
def api_table(
    request: Request,
    key: str,
):

    denied = protected(request)

    if denied:
        return denied

    if key not in TABLES:
        return JSONResponse(
            {"detail": "Unknown table"},
            status_code=404,
        )

    return {
        "rows": fetch_rows(key),
        "fields": TABLES[key]["fields"],
    }


@app.post("/api/table/{key}")
async def api_insert(
    request: Request,
    key: str,
):

    denied = protected(request)

    if denied:
        return denied

    if key not in TABLES:
        return JSONResponse(
            {"detail": "Unknown table"},
            status_code=404,
        )

    try:

        data = await request.json()

        row_id = insert_row(
            key,
            data,
        )

        return {
            "id": row_id
        }

    except Exception as exc:

        return JSONResponse(
            {"detail": str(exc)},
            status_code=400,
        )


@app.put("/api/table/{key}/{row_id}")
async def api_update(
    request: Request,
    key: str,
    row_id: int,
):

    denied = protected(request)

    if denied:
        return denied

    if key not in TABLES:
        return JSONResponse(
            {"detail": "Unknown table"},
            status_code=404,
        )

    try:

        data = await request.json()

        update_row(
            key,
            row_id,
            data,
        )

        return {
            "ok": True
        }

    except Exception as exc:

        return JSONResponse(
            {"detail": str(exc)},
            status_code=400,
        )


@app.delete("/api/table/{key}/{row_id}")
def api_delete(
    request: Request,
    key: str,
    row_id: int,
):

    denied = protected(request)

    if denied:
        return denied

    if key not in TABLES:
        return JSONResponse(
            {"detail": "Unknown table"},
            status_code=404,
        )

    try:

        delete_row(
            key,
            row_id,
        )

        return {
            "ok": True
        }

    except Exception as exc:

        return JSONResponse(
            {"detail": str(exc)},
            status_code=400,
        )


@app.get("/download/excel")
def download_excel(request: Request):

    from fastapi.responses import FileResponse
    from .services import export_excel

    if not current_user(request):
        return login_redirect()

    path = export_excel()

    return FileResponse(
        path,
        filename=path.name,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )