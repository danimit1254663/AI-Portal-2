
from ai.memory import (
    remember,
    context,
    add_history,
    get_history
)



print(
    remember(
        "Меня зовут Алекс"
    )
)



add_history(
    "user",
    "Привет Джарвис"
)



print(
    context()
)



print(
    get_history()
)

