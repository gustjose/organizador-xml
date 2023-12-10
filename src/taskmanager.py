import os, sys
import win32com.client
import xml.etree.ElementTree as ET

task_name = "XML Organizer"

def add_scheduled_task(start_time, frequency):
    script_path = os.path.dirname(os.path.realpath(__file__)) + '\\import_email.py'
    try:
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()

        rootFolder = scheduler.GetFolder('\\')

        taskDef = scheduler.NewTask(0)
        taskDef.RegistrationInfo.Description = task_name

        script_dir = os.path.dirname(os.path.abspath(__file__))
        pythonw_exe = os.path.abspath(os.path.join(script_dir, "..", "venv", "Scripts", "pythonw.exe"))

        # Configurar a ação do script
        execAction = taskDef.Actions.Create(0)
        execAction.ID = 'ExecScript'
        execAction.Path = pythonw_exe  # Use pythonw.exe em vez de python.exe
        execAction.Arguments = f'"{script_path}"'

        # Configurar o gatilho de início
        trigger = taskDef.Triggers.Create(1)  # 1 significa gatilho de início
        trigger.StartBoundary = start_time

        # Configurar a repetição
        repetition = trigger.Repetition
        repetition.Interval = "P1D" if frequency == 'daily' else "P1W"  # Diário ou semanal

        # Adicionar a tarefa ao Agendador de Tarefas
        rootFolder.RegisterTaskDefinition(
            task_name,
            taskDef,
            6,  # ReplaceExisting
            None,  # user and password here if needed
            None,
            3,  # Logon interativo requerido
        )

        return True
    except Exception as e:
        return False

def delete_scheduled_task():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    root_folder = scheduler.GetFolder('\\')
    try:
        root_folder.DeleteTask(task_name, 0)  # 0 significa que a tarefa será removida sem confirmar
        return True
    except Exception as e:
        return False

def get_scheduled_task_info():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    rootFolder = scheduler.GetFolder('\\')

    try:
        task = rootFolder.GetTask(task_name)
        return task.Definition.XmlText
    except Exception as e:
        return None