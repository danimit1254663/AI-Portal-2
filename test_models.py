from gigachat import GigaChat

from core.config import get_gigachat_config


giga = get_gigachat_config()


client = GigaChat(

    credentials=giga["credentials"],

    scope=giga["scope"],

    verify_ssl_certs=False

)


models = client.get_models()


for model in models.data:

    print(model.id_)