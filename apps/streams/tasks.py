from streamkit.celery import app


@app.task
def test(message):
    print(message)