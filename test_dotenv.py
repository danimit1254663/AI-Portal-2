from core.config import get_gigachat_config


giga = get_gigachat_config()


print("CLIENT:", giga["client_id"])
print("SECRET:", giga["client_secret"])
print("SCOPE:", giga["scope"])