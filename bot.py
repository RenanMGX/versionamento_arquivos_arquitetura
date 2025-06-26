"""
WARNING:

Please make sure you install the bot dependencies with `pip install --upgrade -r requirements.txt`
in order to get all the dependencies on your Python environment.

Also, if you are using PyCharm or another IDE, make sure that you use the SAME Python interpreter
as your IDE.

If you get an error like:
```
ModuleNotFoundError: No module named 'botcity'
```

This means that you are likely using a different Python interpreter than the one used to install the dependencies.
To fix this, you can either:
- Use the same interpreter as your IDE and install your bot with `pip install --upgrade -r requirements.txt`
- Use the same interpreter as the one used to install the bot (`pip install --upgrade -r requirements.txt`)

Please refer to the documentation for more information at
https://documentation.botcity.dev/tutorials/custom-automations/python-custom/
"""

# Import for integration with BotCity Maestro SDK
from botcity.maestro import * #type: ignore
import traceback
from patrimar_dependencies.gemini_ia import ErrorIA
from patrimar_dependencies.screenshot import screenshot
from main import ExecuteAPP
from Entities.processos import Processos
import os

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False #type: ignore


class Execute:
    @staticmethod
    def start():
        email = maestro.get_credential(label='ConstruCode', key='email')
        password = maestro.get_credential(label='ConstruCode', key='password')
        
        base_path = execution.parameters.get('base_path')
        if base_path:
            if not os.path.exists(str(base_path)):
                raise FileExistsError(f"o caminho '{base_path}' não foi encontrado!") 
        else:
            raise FileExistsError(f"o caminho '{base_path}' não foi encontrado!")
        
        ExecuteAPP.start(maestro=maestro, email=email, password=password, path_ambiente=str(base_path))        
        
        p.add_processado()

if __name__ == '__main__':
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()
    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    task_name = execution.parameters.get('task_name')
    
    p = Processos(1)

    try:
        Execute.start()
        
        maestro.finish_task(
                    task_id=execution.task_id,
                    status=AutomationTaskFinishStatus.SUCCESS,
                    message=f"Tarefa {task_name} finalizada com sucesso",
                    total_items=p.total, # Número total de itens processados
                    processed_items=p.processados, # Número de itens processados com sucesso
                    failed_items=p.falhas # Número de itens processados com falha
        )
        
    except Exception as error:
        ia_response = "Sem Resposta da IA"
        try:
            token = maestro.get_credential(label="GeminiIA-Token-Default", key="token")
            if isinstance(token, str):
                ia_result = ErrorIA.error_message(
                    token=token,
                    message=traceback.format_exc()
                )
                ia_response = ia_result.replace("\n", " ")
        except Exception as e:
            maestro.error(task_id=int(execution.task_id), exception=e)

        maestro.error(task_id=int(execution.task_id), exception=error, screenshot=screenshot(), tags={"IA Response": ia_response})
        maestro.finish_task(
                    task_id=execution.task_id,
                    status=AutomationTaskFinishStatus.FAILED,
                    message=f"Tarefa {task_name} finalizada com Error",
                    total_items=p.total, # Número total de itens processados
                    processed_items=p.processados, # Número de itens processados com sucesso
                    failed_items=p.falhas # Número de itens processados com falha
        )
