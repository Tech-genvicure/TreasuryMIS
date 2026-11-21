
import httpx

from app.core.config import settings


GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def get_access_token() -> str:
    """Obtain an application access token from Microsoft Entra ID."""

    required = {
        "MS_TENANT_ID": settings.MS_TENANT_ID,
        "MS_CLIENT_ID": settings.MS_CLIENT_ID,
        "MS_CLIENT_SECRET": settings.MS_CLIENT_SECRET,
    }

    missing = [key for key, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            f"Missing Microsoft configuration: {', '.join(missing)}"
        )

    token_url = (
        f"https://login.microsoftonline.com/"
        f"{settings.MS_TENANT_ID}/oauth2/v2.0/token"
    )

    response = httpx.post(
        token_url,
        data={
            "client_id": settings.MS_CLIENT_ID,
            "client_secret": settings.MS_CLIENT_SECRET,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        },
        timeout=30.0,
    )

    if response.is_error:
        raise RuntimeError(
            f"Microsoft authentication failed: "
            f"HTTP {response.status_code}. "
            "Check the app credentials and Graph permissions."
        )

    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("Microsoft did not return an access token.")

    return token


def download_treasury_workbook() -> bytes:
    """Download the configured Excel workbook using Microsoft Graph."""

    if not settings.MS_DRIVE_ID or not settings.MS_FILE_ID:
        raise RuntimeError("Microsoft Drive ID or File ID is missing.")

    token = get_access_token()

    download_url = (
        f"{GRAPH_BASE_URL}/drives/{settings.MS_DRIVE_ID}"
        f"/items/{settings.MS_FILE_ID}/content"
    )

    response = httpx.get(
        download_url,
        headers={"Authorization": f"Bearer {token}"},
        follow_redirects=True,
        timeout=60.0,
    )

    if response.is_error:
        raise RuntimeError(
            f"Workbook download failed: HTTP {response.status_code}. "
            "Check the file-specific Graph permission and file ID."
        )

    content = response.content

    if not content:
        raise RuntimeError("Microsoft returned an empty workbook.")

    return content
