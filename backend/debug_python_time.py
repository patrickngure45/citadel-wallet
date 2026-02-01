import datetime

print(f" datetime.now(): {datetime.datetime.now()}")
print(f"datetime.utcnow(): {datetime.datetime.utcnow()}")
print(f"   Now + UTC: {datetime.datetime.now(datetime.timezone.utc)}")
