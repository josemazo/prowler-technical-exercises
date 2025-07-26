# Exercise 2: Django REST Framework CRUD Application

# TODO
- [ ] Documentation in code
- [ ] Add more logging
- [ ] Documentation
- [ ] GitHub CI / CD for tests

## Sandboxing
About the data model
Taking a look to the Prowler documentation, it seems that `checks` are main entities: definitions of what to _check_ in
each service of each provider.
`scans` are the executions of those `checks` against a specific provider, at a specific time, by a specific user.
So, `findings` are related directly to `scans` and `checks`: what was found during a specific check of a specific scan.

But `Define relationships between models (e.g., a scan can have many checks, a check can have  many findings)` striked
me, and I developed those models, the urls (`rest_framework_nested`) and views accordingly.

I'll change it for what I found in the Prowler documentation, adding `providers`, as having non-dependant `checks` looks too simple.

TODO: Comment about auth

TODO: Comment about uvicorn on exercise 3 or 2

TODO: Comment about better logging

Notes
- No auth for simplicity
- uvicorn on excercise 3 or 2
- Request ID
- Better logging content (file and line, request id), json & proper access log for production
- migraet and populate are out of docker compose because they can be desctrucive, also i'm not a fan of magic docker compose commands (`docker compose up` and everything is running), you loose _perspective_ of what is happening, but if the project is really huge and complex to configurate, is a good option
