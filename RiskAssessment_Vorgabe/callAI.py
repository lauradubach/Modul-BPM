#  pip install pydantic
#  pip install pylance
#  pip install camunda-external-task-client-python3
#  pip install openai

import os
import openai
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

# configuration for the Client
default_config = {
    "maxTasks": 1,
    "lockDuration": 10000,
    "asyncResponseTimeout": 5000,
    "retries": 0,
    "retryTimeout": 5000,
    "sleepSeconds": 30
}

# OpenAI API Key (ersetze mit deinem eigenen Schlüssel)
openai.api_key = os.getenv("OPENAI_API_KEY")

def handle_task(task: ExternalTask) -> TaskResult:
    # Extrahiere den Wert des Textfeldes 'txtPrompt'
    prompt = task.get_variable("txtPrompt")
    print(prompt)

    if not prompt:
        # return task.failure(error_message="txtPrompt ist leer.", error_details="Es wurde kein Prompt bereitgestellt.", max_retries=0, retry_timeout=0)
        return task.bpmn_error(error_code="BPMN_ERROR_PROMPT_EMPTY", error_message="Es wurde kein Prompt bereitgestellt.", 
                                variables={"ZusatzMsg": "Der Prompt müsste eigentlich vom Programm aufbereitet werden aus Angaben der DMN", "success": False})
    

    # Anfrage an das AI-Tool (ChatGPT)
    try:
        response = openai.completions.create(
            model = "gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=150
        )
        ai_response = response.choices[0].text.strip()
        print(ai_response)

        # Setze die AI-Antwort als Prozessvariable
        return task.complete({"aiResponse": ai_response})
    except Exception as e:
        print(e.message)
        return task.failure(error_message=str(e), error_details="Fehler bei der Anfrage an das AI-Tool:" + e.message, max_retries=0, retry_timeout=0)



if __name__ == "__main__":
   ExternalTaskWorker(worker_id="3", config=default_config).subscribe("CallAI", handle_task)    
