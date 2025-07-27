# Exercise 2: Django REST Framework CRUD Application

Django project with a possible solution to the Technical Exercise 2​ for the [Python Engineer position](https://www.python.org/jobs/7929/) at [Prowler](https://prowler.com/).


## Table of contents
- [Requisites](#requisites)
- [Developing](#developing)
  - [A note about this approach](#a-note-about-this-approach)
  - [Install more Python dependencies](#install-more-python-dependencies)
  - [Database changes](#database-changes)
- [Testing](#testing)
- [Debugging](#debugging)
- [Production](#production)
- [About the solution](#about-the-solution)
  - [Data model](#data-model)
  - [Asynchronous scan run](#asynchronous-scan-run)
  - [Improvements](#improvements)


## Requisites
Once the repository is downloaded, the easiest way to start devolping is using [Docker](https://docs.docker.com/engine/install/).

Of course, you can use [Python (3.14)](https://github.com/pyenv/pyenv?tab=readme-ov-file#install-additional-python-versions) and [`uv`](https://docs.astral.sh/uv/getting-started/installation/) for a non containerized approach, but this guide will not cover it. If you still want to go _native_, take a look at the [`Dockerfile`](./Dockerfile), [`entrypoint.sh`](./entrypoint.sh) and [`docker-compose.yml`](./docker-compose.yml) files and check the steps you need.


## Developing
For start the project in a local environment follow this steps:

1. Make a copy of [`.env.template`](./.env.template) as `.env`.

2. Edit `.env` contents as you wish, as the `POSTGRES...` or `SUPER...` variables. You can take a look at [About the solution](#asynchronous-scan-run) to know more of some of them.

3. Start PostgreSQL:
```bash
docker compose up postgres
```

4. Start the Django project, the firt time it will build the image:
```bash
docker compose up api
```

5. Apply the needed migrations, create a **superuser** and populate the database with initial data:
```bash
docker compose exec api python manage.py migrate
docker compose exec api python manage.py populatedb
```

6. Start the [`procrastinate`](https://procrastinate.readthedocs.io/) worker:
```bash
docker compose up worker
```

7. Go to [http://localhost:8000](http://localhost?800) and start browsing the project.


### A note about this approach
Steps 3 to 6 could be condensend as a simple `docker compose up` but I have two reasons:
- As this is an exercise I wanted to show all the components and their initialization processes.
- Step 5 destroys your data, although that is easily adjustable, I wanted to get usable and showable data as fast as possible.


### Install more Python dependencies

As this project uses `uv`, you can check how it manages your project dependencies [here](https://docs.astral.sh/uv/concepts/projects/dependencies/).

So, with a [running local enviornment](#developing) you run:
```bash
docker compose exec api uv [OPTIONS]
```


### Database changes

If you make changes to the data model and want to apply them to the database first you need to create their migration, and then apply it:

``` bash
docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate
```


## Testing
Testing is prettey easy, as you don't need any component running. The aplication uses a memory database and `procrastinate` uses an [`in-memory` connector](https://procrastinate.readthedocs.io/en/stable/howto/django/tests.html#unit-tests).

Just run:
```bash
docker compose up test
```

This will run three processes:
- [`ruff`](https://docs.astral.sh/ruff/) as linter.
- [`ty`](https://docs.astral.sh/ty/) as type checker.
- [`pytest`](https://docs.pytest.org/) as test runner.


## Debugging
Easy debugging in Docker is achieved thanks to [`debugpy`](https://github.com/microsoft/debugpy), so you can debug the project with any IDE or cli that works with the [Debug Adapter Protocol](https://microsoft.github.io/debug-adapter-protocol/). [Here](https://code.visualstudio.com/docs/python/debugging#_example) is how to configure VS Code for using this approach. Don't forget to condigure it with the right ports you set in the `.env` file in the `DEBUG_API_PORT` or `DEBUG_WORKER_PORT` variables.

So, with a [running local enviornment](#developing) you need to stop the service you want to debug and start its debugging version:
- `api`:
```bash
docker compose stop api
docker compose up debug-api
```
- `worker`:
```bash
docker compose stop worker
docker compose up debug-worker
```


## Production

Although this is not a real production environment, a production image can be created, where the application runs directly with [`gunicorn`](https://gunicorn.org/). For achieving that, just modify the `ENVIRONMENT` variable to `production` in the `.env` file. With only that you can follow the same steps as for a [local enviornment](#developing) for getting the application running _as_ in production.

The production image contains the next features:
- A smaller image as not having `uv` installed.
- All Python source code files are compiled to bytecode for a faster startup.
- Gunicorn is used as WSGI server.
- Hotreload is disabled, so the overall perfmance will be slightly better.


## About the solution

As saw in this document, the presented solution leverages its orchestration in Docker with three services:
- `api`
- `worker`
- `postgres`

Also, small componentes are present, such is `uv`, `ruff`, `ty`, `pytest`, `debugpy`, `procrastinate` and [`drf-nested-routers`](https://github.com/alanjds/drf-nested-routers). But let's only take a deeper look at two abstract, but very important parts, [the data model](#data-model) and [how the asynchronous tasks are handled](#asynchronous-scan-run).


### Data model

After reading the exercise requirements I started to develop the data models as `Define relationships between models (e.g., a scan can have many checks, a check can have  many findings)` proposes, with their urls, views, serializers accordingly.

But then I took a look at the [Prowler documentation](https://docs.prowler.com/), where apparently `checks` are main entities: definitions of what to _check_ in each service of each provider. `scans` are the executions of those `checks` against a specific provider, at a specific time, by a specific _user_. So, `findings` are related directly to `scans` and `checks`: what was found during a specific check of a specific scan.

This approach, while different, is easier with only those three entities, as having non-dependant `checks` is too simple. So, I've added providers, where:
- A check belongs to only one provider. One provider can have multiple checks.
- A scan also belongs to only one provider. One provider can have multiple checks.
- Findings belong to only one scan and one check. Scans and checks can have multiple findings.

I've also thought about using users, but I think that was out of the scope (really in time, not in difficulty) of this exercise.

The scan model has a few properties calculated on-the-fly, one in its model, others its view. I'm not a fun of complex properties, like the ones I've done, as with the database starts growing, the performance decrease. I've just implemented them as giving the exercise more different approachs of data handling.

Finally, URLs are created on-the-fly for easy browsing the API, while deactivated when using the API with `?format=json` or with `DEBUG=False` in Django.


### Asynchronous scan run

For running the asynchronous scans I wanted to innovate a little bit, as I've read a ton about [`procrastinate`](https://procrastinate.readthedocs.io/). Of course, I don't think it's a robust tool as Celery is, where for more complex tasks there are [extensions](https://github.com/svfat/awesome-celery) for running even DAGs, closing the gap to tools like [Airflow](https://airflow.apache.org/), [Prefect](https://www.prefect.io/) or [Dagster](https://dagster.io/). But this exercise I found `procrastinate` perfect, and I cite, _leveraging PostgreSQL 13+ to store task definitions, manage locks and dispatch tasks_, so we use the same database for our project and no new component like a broker.

The task I've created is simple, it emulates a scan run by creating its findings. It uses four environment variables:
- `WORKER_CONCURRENCY`: The number of tasks the worker can run simultaniously.
- `CHECK_SLEEP_TIME`: The wait time before _running_ each check.
- `CHECK_EXCEPTION_RATE`: The rate of which a check fails its _execution_, failing the scan.
- `CHECK_SUCCESS_RATE`: The rate of _success_ of each check.


### Improvements

There are a series of improvements for this project. I'll list here the ones I find more interesting:

- Authentication and authorization, so users can manage and see only their scans.

- The code is not typed, something I like to do, but there is too much magic with Django Rest Framework, specially with its `ModelViewSet`. I've never use DRF and I would like to understand it a little bit better before implementing types anotations.

- Using [Uvicorn](https://www.uvicorn.org/) as ASGI server for _await_ views and data access and not blocking the thread. It looks that with DRF is somehting more diffcult than with regular Django, so I didn't enter in that.

- Add a better logging system ([`django-structlog`](https://django-structlog.readthedocs.io/)), with stuff like unique `request_id` ([`django-request-id`](https://django-request-id.readthedocs.io/)), file and line where the log was fired, or even JSON format for the production environment.

- Add [`pre-commit`](https://pre-commit.com/) for ensuring no tested code is commited and add [GitHub Ations](https://github.com/features/actions) for running those tests on the cloud, and also managing possible deploys. **TODO**
