from typing import Optional
from urllib.parse import quote

from fastapi import Request, Response, status


def include_user_info_headers(headers, user):
    return {
        **headers,
        "X-OpenWebUI-User-Name": quote(user.name, safe=" "),
        "X-OpenWebUI-User-Id": user.id,
        "X-OpenWebUI-User-Email": user.email,
        "X-OpenWebUI-User-Role": user.role,
    }


def check_etag(request: Request, etag: Optional[str]) -> Optional[Response]:
    """
    Check If-None-Match header and return 304 Not Modified if ETag matches.
    
    This function implements HTTP conditional request handling based on ETag.
    If the client's If-None-Match header matches the file's ETag, returns 304.
    
    Args:
        request: FastAPI Request object
        etag: The file's SHA256 hash (ETag value without quotes)
    
    Returns:
        Response with 304 status if ETag matches, None otherwise.
    """
    if not etag:
        return None
    
    # Format ETag according to HTTP spec (add quotes)
    etag_value = f'"{etag}"'
    
    # Check If-None-Match header
    if_none_match = request.headers.get("if-none-match")
    if if_none_match:
        # Parse comma-separated ETags
        # ETags can be in format: "tag1", "tag2", W/"weak-tag", or *
        etags = []
        for tag in if_none_match.split(","):
            tag = tag.strip()
            # Handle wildcard
            if tag == "*":
                return Response(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    headers={"ETag": etag_value},
                )
            # Remove quotes and weak tag prefix (W/)
            tag = tag.strip('"').strip("'")
            if tag.startswith("W/"):
                tag = tag[2:]
            etags.append(tag.strip())
        
        # Check if our ETag matches any of the provided ETags
        if etag in etags:
            # Return 304 Not Modified
            return Response(
                status_code=status.HTTP_304_NOT_MODIFIED,
                headers={"ETag": etag_value},
            )
    
    return None
