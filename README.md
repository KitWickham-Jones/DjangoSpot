# Spotify OAuth Django Project

This project is a Django-based web application that demonstrates secure integration with the Spotify Web API using OAuth 2.0 authentication.

## Features

-   **Spotify OAuth 2.0 Authentication**: Securely authenticate users with their Spotify accounts.
-   **Recent Plays Retrieval**: Fetch and display a user's recently played tracks from Spotify.
-   **Artist and Genre Data**: Store and relate artist, song, and genre information in a normalized PostgreSQL database schema.
-   **Token Refresh Handling**: Automatically refresh expired Spotify access tokens using refresh tokens.
-   **Bulk Database Operations**: Efficiently write and read large batches of Spotify data using Django ORM bulk operations.
-   **Error Handling & User Feedback**: Robust error handling with user-friendly messages and HTTP status codes.
-   **Modern Django Practices**: Uses class-based views, static and service methods, and clear separation of concerns.

## Tech Stack

-   **Backend**: Python 3, Django 5
-   **Database**: PostgreSQL
-   **Containerization**: Docker (for local development and deployment)
-   **Frontend**: Minimal HTML templates (for demonstration)

## Project Structure

```
backend/
  OAuthCon/
    app/
      api/
        models.py        # Django models for Artist, ListenData, GenreData
        views.py         # Class-based views for login, callback, recent plays, genres
        SpotifyService.py# Service layer for Spotify API and DB logic
        templates/
          navigate.html  # User-facing template
        ...
      spotify/
        settings.py      # Django settings (PostgreSQL, apps, etc.)
        urls.py          # URL routing
    docker-compose.yml   # For local dev
```

## How It Works

1. **User logs in with Spotify** via the `/api/login/` endpoint.
2. **OAuth callback** stores access and refresh tokens in the session.
3. **Recent plays** are fetched from Spotify and written to the database.
4. **Artist and genre data** are normalized and related using foreign keys.
5. **Token refresh** is handled automatically if the access token expires.
6. **All data** can be queried and displayed via Django views or the admin.

---

**Author:** Kit Wickham-Jones
