<!-- ramani: README.md -->
<h1 align="center">djangX</h1>

<p align="center">
  <strong>Django, with the boilerplate already decided.</strong><br>
  Drop a folder in <code>app/</code> and it is installed and routed. Bootstrap and Sass compile themselves. Security headers are on from the first run.
</p>

<p align="center">
  <a href="https://pypi.org/project/djangx/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/djangx?color=006600&label=pypi&include_prereleases"></a>
  <a href="https://www.python.org/"><img alt="Python 3.14+" src="https://img.shields.io/badge/python-3.14%2B-3776AB?logo=python&logoColor=white"></a>
  <a href="https://www.djangoproject.com/"><img alt="Django 6.1+" src="https://img.shields.io/badge/django-6.1%2B-092E20?logo=django&logoColor=white"></a>
  <a href="https://docs.astral.sh/uv/"><img alt="Built with uv" src="https://img.shields.io/badge/built%20with-uv-DE5FE9"></a>
  <img alt="Status: alpha" src="https://img.shields.io/badge/status-alpha-E95420">
  <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-blue">
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#what-you-get">What you get</a> ·
  <a href="#project-layout">Layout</a> ·
  <a href="#commands">Commands</a> ·
  <a href="#settings">Settings</a> ·
  <a href="#sass-and-bootstrap">Sass &amp; Bootstrap</a> ·
  <a href="#deploying">Deploying</a>
</p>

> **djangX** is a small framework layer on top of Django. It keeps Django's models, views, admin and ORM exactly as they are, and removes the parts of a new project that are the same every time: listing apps, wiring URLs, serving CSS, choosing a database, setting a content security policy and building for deployment. You write `app/blog/`; djangX does the rest.

```console
$ djx startproject mysite && cd mysite
$ djx startapp blog
$ djx runserver
```

## Why

Every Django project starts with the same afternoon: add the app to `INSTALLED_APPS`, add its URLs to the root `urls.py`, wire up static files, bolt on a CSS build, swap SQLite for Postgres in production, remember the middleware order. djangX makes those decisions once, in code you can read, and lets you override any of them in `settings.py`.

## Quick start

You need Python 3.14+ and [Dart Sass](https://sass-lang.com/install) on your `PATH` (any install method works).

```bash
uv tool install djangx          # the djangx and djx commands, everywhere
djx startproject mysite         # create a project
cd mysite
djx startapp blog               # create app/blog
djx migrate
djx runserver                   # builds Sass, serves, live-reloads
```

Prefer pip? `pip install djangx`. Using Postgres or Vercel? Add an extra:

```bash
uv add "djangx[postgres]"       # psycopg 3 with the connection pool
uv add "djangx[vercel]"
```

`djx` and `djangx` are the same command. Run `djx help` for the full list.

## What you get

- 🔎 **Apps find themselves.** Every folder in `app/` that has an `apps.py` is installed as `app.<folder>`. No list to maintain.
- 🛣️ **URLs wire themselves.** Any app with a `urls.py` is mounted at `/<app label>/`. One app (default `app.main`) is the home app, mounted at `/` and placed last so it can be a catch-all.
- 🎨 **Bootstrap and Sass, no Node.** Pick the Bootstrap parts you want with `BOOTSTRAP_INCLUDES`, write `.scss` beside your templates, and Dart Sass compiles both. See [`djangx.contrib.sass`](src/djangx/contrib/sass/README.md).
- ⚡ **Live reload in development.** `django-browser-reload` is added when `DEBUG=True`, and waits for the CSS to finish compiling before it refreshes.
- 🛡️ **Content Security Policy on by default.** Django's built-in CSP middleware, with nonces for scripts and styles and Google Fonts allowed.
- 🗜️ **Compression built in.** Brotli and gzip through `django-http-compression`.
- 🔌 **REST framework included.** Installed, routed at a private login URL, and set to model permissions with anonymous read-only access.
- 🐘 **Database from one variable.** Set `DATABASE_URL` for Postgres. Leave it unset and you get SQLite.
- 🧱 **A tidy `.djangx/` folder.** Generated files live in one git-ignored place, never inside the installed package.
- 🚢 **Deploy workflow included.** One command writes a GitHub Actions workflow that builds a ready-to-run `deploy` branch.
- 🧪 **Checks that explain themselves.** Set `BOOTSTRAP_INCLUDES` without installing the Sass app and the system check tells you exactly what to add.
- 🧹 **Linting wired up.** New projects ship with `pre-commit`, `ruff` through `uv format` and `uv check`, `djlint` for templates and [`ramani`](https://github.com/treeolive-tech/ramani) for path comments.

## Project layout

```text
mysite/
├── app/
│   ├── main/               the home app (created for you)
│   │   ├── apps.py
│   │   └── ...             models, views, urls.py, templates, static
│   └── settings.py         every setting, in one readable file
├── pyproject.toml
├── README.md
└── .pre-commit-config.yaml
```

There is no `manage.py`, `asgi.py` or `wsgi.py` to maintain. In development, `djx` takes the place of `manage.py`. For deployment, `djx createfile` writes them when you need them (see [Deploying](#deploying)).

Generated and local files stay out of git:

```text
.djangx/       generated static files and build stamps
.env*          local environment files
db.sqlite3     the development database
public/        collected static and media files
```

### How apps and URLs are found

```text
app/
├── blog/   apps.py  urls.py     →  installed as app.blog, mounted at /blog/
├── shop/   apps.py  urls.py     →  installed as app.shop, mounted at /shop/
├── main/   apps.py  urls.py     →  installed as app.main, mounted at / (last)
└── notes/  models.py            →  ignored: no apps.py, so not an app
```

Change the home app with `HOME_APP = "app.landing"`, and where it is mounted with `HOME_URL = "start"`.

## Commands

Use `djx` anywhere. Commands that need a project (those that touch `app/settings.py`) are hidden, and refuse to run, outside one.

| Command                                     | What it does                                                                      |
| ------------------------------------------- | --------------------------------------------------------------------------------- |
| `djx startproject NAME`                     | Create a project with settings in `app/` and a first `main` app                   |
| `djx startapp NAME`                         | Create `app/NAME` and set its `AppConfig.name` to `app.NAME`                      |
| `djx runserver`                             | Build Sass if needed, then run Django's development server                        |
| `djx collectstatic`                         | Build Sass, then collect. Sass sources are left out and no confirmation is asked  |
| `djx sass --build`                          | Compile Bootstrap and your Sass by hand (`--if-changed` skips what is up to date) |
| `djx createfile manage\|asgi\|wsgi\|deploy` | Write (or `--remove`) one of the files a deployment needs                         |
| `djx version`                               | Print the installed djangX version                                                |

Everything else Django ships (`migrate`, `makemigrations`, `createsuperuser`, `shell`, `test`) works as usual through `djx`.

### `djx createfile`

```bash
djx createfile manage                 # manage.py in the project root
djx createfile asgi --set             # app/asgi.py, and ASGI_APPLICATION now points at it
djx createfile wsgi --remove --reset  # delete it, point back at djangX's built-in one
djx createfile deploy --overwrite     # .github/workflows/deploy.yml
```

An existing file is never replaced unless you pass `--overwrite`. `--set` and `--reset` edit the matching line in `app/settings.py`.

## Settings

`djx startproject` generates `app/settings.py` with sensible values. The djangX-specific pieces are a few helper calls and some optional settings.

```python
from djangx.core.utils.conf import Conf

INSTALLED_APPS = Conf.installed_apps(defaults=[...], app_dir=APP_DIR, debug=DEBUG)
MIDDLEWARE = Conf.middleware(middlewares=[...], debug=DEBUG)
STATICFILES_DIRS = Conf.staticfiles_dirs([], base_dir=BASE_DIR)
```

| Helper                  | What it adds                                                                                                                           |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `Conf.installed_apps`   | Your discovered `app.*` apps, then your defaults, then `djangx.core`, reload (debug only), compression, REST framework and staticfiles |
| `Conf.middleware`       | Your middleware, then compression, then browser reload (debug only)                                                                    |
| `Conf.staticfiles_dirs` | Your folders, then `.djangx/static` for generated files such as the compiled Bootstrap                                                 |

| Setting              | Default          | What it does                                              |
| -------------------- | ---------------- | --------------------------------------------------------- |
| `HOME_APP`           | `"app.main"`     | The app mounted at the home URL, placed last in the URLs  |
| `HOME_URL`           | `""`             | Where the home app is mounted                             |
| `ADMIN_URL`          | `"admin"`        | Where the admin lives                                     |
| `RELOAD_URL`         | `"__reload__"`   | Browser reload endpoint (debug only)                      |
| `REST_AUTH_URL`      | `"__api-auth__"` | REST framework's login and logout views                   |
| `BOOTSTRAP_INCLUDES` | see Sass section | Which Bootstrap parts to compile, or `None` to switch off |
| `SASS_DART_OPTIONS`  | compressed + map | Passed to the Dart Sass command line                      |
| `SASS_EXECUTABLE`    | `None`           | Use a specific Sass binary                                |
| `SASS_GITIGNORE`     | `True`           | Keep generated CSS out of git automatically               |

### Environment

| Variable        | Effect                                                                   |
| --------------- | ------------------------------------------------------------------------ |
| `DEBUG`         | `true` by default. Set to `false` in production                          |
| `SECRET_KEY`    | Required when `DEBUG` is `false`; a throwaway key is used in development |
| `ALLOWED_HOSTS` | Comma-separated hosts; defaults to `localhost,127.0.0.1`                 |
| `DATABASE_URL`  | A Postgres URL. Unset means SQLite at `db.sqlite3`                       |

Put local values in `.env.local` at the project root. `djx` loads it automatically, and it is git-ignored.

## Sass and Bootstrap

Install Dart Sass once, add the folders you want, and write SCSS.

```django
{% load sass %}
{% bootstrap_css %}
{% sass_css "blog/css/site.css" %}
```

```text
app/blog/static/blog/css/site.scss   ← you write this
app/blog/static/blog/css/site.css    ← generated, served as /static/blog/css/site.css
```

- Bootstrap compiles to your project's `.djangx/static/`, and only the parts listed in `BOOTSTRAP_INCLUDES` are built.
- Your SCSS compiles beside the source, incrementally, and a background watcher rebuilds on every save, partials included.
- Compile errors are printed, not thrown, so the dev server keeps running.
- In production the template tags only emit static URLs, and `djx collectstatic` does the build.

The full guide, with every option, is in [`djangx.contrib.sass`](src/djangx/contrib/sass/README.md).

## Deploying

```bash
djx createfile deploy
```

That writes `.github/workflows/deploy.yml`. On every push to `main` it generates `manage.py`, `app/asgi.py` and `app/wsgi.py`, points `settings.py` at them, and force-pushes the result to a `deploy` branch. Point your host (Vercel, a VPS, anything that runs a Django project) at that branch.

For a production server, set `DEBUG=false`, `SECRET_KEY`, `ALLOWED_HOSTS` and `DATABASE_URL`, install Dart Sass in the build, and run `djx collectstatic`.

Want a server to run it on? [`msingi`](https://github.com/treeolive-tech/msingi) provisions an Ubuntu box (Nginx, Certbot, PostgreSQL, uv) from a single GitHub Actions run.

## Requirements

- Python **3.14+** and Django **6.1+**
- **Dart Sass** on your `PATH` (djangX never installs it for you)
- Installed with djangX: `django-browser-reload`, `django-http-compression[brotli]`, `djangorestframework`, `pillow` and `python-dotenv`

## Status

djangX is **alpha**. The shape of a project is settling, but settings and helpers may still change between releases. Pin a version in `pyproject.toml`, and read the release notes before upgrading.

## Development

```bash
git clone https://github.com/treeolive-tech/djangx.git
cd djangx
uv sync
uv run pre-commit install
```

## License

MIT © Treeolive Tech Ltd. Use it, change it, ship it; just keep the copyright notice.

---

<p align="center">
  <em>"...but the people who know their God shall be strong and do exploits."</em><br>
  Daniel 11:32
</p>
