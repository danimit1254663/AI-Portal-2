from commands.windows import windows_command
from ai.giga_ai import GigaAI
from ai.memory import remember
from commands.time_control import get_time

ai=GigaAI()



def handle_command(text):


    memory=remember(text)


    if memory:

        return memory

    result = get_time(text)

    if result:
        return result

    result=windows_command(text)


    if result:

        return result



    return ai.ask(text)