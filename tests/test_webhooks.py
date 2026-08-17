from app.core.webhooks import encode_event, sign_webhook


def test_webhook_signature_is_stable():
    body = encode_event({"type":"job.completed","data":{"job_id":"1"}})
    assert sign_webhook("secret", body) == sign_webhook("secret", body)
    assert sign_webhook("secret", body) != sign_webhook("other", body)
