from ingest.models import Signal

if __name__ == '__main__':
    s = Signal(
        source='webhook',
        parsed_text='hello world',
        sender='+1234567890',
        metadata={'url': 'http://example.com'}
    )
    # pydantic v2: use model_dump_json
    print(s.model_dump_json(indent=2))
