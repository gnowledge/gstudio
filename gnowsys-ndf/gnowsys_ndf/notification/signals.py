import django.dispatch


# pylint: disable-msg=C0103
emitted_notices = django.dispatch.Signal(
    providing_args=["batches", "sent", "sent_actual", "run_time"]
)
