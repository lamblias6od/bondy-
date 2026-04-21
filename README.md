# Bondy 

A social app to connect and plan outings together. You can see who's nearby, create open plans ("salidas"), and invite people to join them.

Live: [bondy.up.railway.app](https://bondy.up.railway.app)

---

## What it does

- **Nearby users** — see other people in your area
- **Open outings** — create or join plans posted by other users
- **Interests system** — tag your interests so you find more compatible people
- **Messaging** — private conversations with threaded replies
- **Friendship system** — send and accept friend requests
- **Notifications** — in-app alerts for activity on your profile
- **Profile photos** — upload and remove your profile picture
- **Custom 404 page** — because why not

---

## Stack

- **Backend:** Python / Django
- **Database:** PostgreSQL
- **Frontend:** Bootstrap 5, Font Awesome, custom CSS (dark mode with electric blue/cyan accents)
- **Auth:** Django's built-in auth system
- **Hosting:** Railway
- **Local dev:** Docker + TablePlus for the database

---

## Running it locally

```bash
git clone https://github.com/yourusername/bondy.git
cd bondy
pip install -r requirements.txt
```

Set up your `.env` file:

```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/bondy
```

Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

You'll need PostgreSQL running locally (I used Docker for this).

---

## Notes

This is my main personal project. I built it from scratch to practice Django and work with a real database, but also because I genuinely wanted to use something like this.

The design went through a few iterations before I landed on the dark mode look. Still working on it here and there — the UI has some rough edges but the core features all work.

If you want to test it on the live site, you can create a free account.
