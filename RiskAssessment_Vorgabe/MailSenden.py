#  pip install pydantic
#  pip install pylance
#  pip install camunda-external-task-client-python3

from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
import smtplib

# configuration for the Client
default_config = {
    "maxTasks": 1,
    "lockDuration": 10000,
    "asyncResponseTimeout": 5000,
    "retries": 3,
    "retryTimeout": 5000,
    "sleepSeconds": 30
}

def handle_task(task: ExternalTask) -> TaskResult:
    """
    Sendet ein eMail. Die Angaben dazu werden aus Variablen gelesen:
    fromEmailAddress, toEmailAddress, mailSubject, mailBody
    """
    fromAddress = task.get_variable("fromEmailAddress")
    toAddresses = task.get_variable("toEmailAddresses")
    mailSubject = task.get_variable("mailSubject")
    mailBody = task.get_variable("mailBody")

    try:
        sendMail(fromAddress, toAddresses, mailSubject, mailBody)
    except Exception as e:
        print(f"Exception raised: {e}")
        return task.failure(error_message="task failed",  error_details=f"failed with Exception {e}", 
                                max_retries=2, retry_timeout=2000)
    
    return task.complete({"success": True, "ResultText": "Mail wurde versandt"}) 

    # return task.bpmn_error(error_code="BPMN_ERROR_CODE", error_message="BPMN Error occurred", 
    #                            variables={"ZusatzMsg": "Hier könnte zusätzliche Info zum Fehler stehen", "success": False})


def sendMail(fromAddress, toAddresses, mailSubject, mailBody):
    # Add the From: and To: headers at the start!
    lines = [f"From: {fromAddress}", f"To: {toAddresses}", f"Subject: {mailSubject}"]
    line = mailBody
    lines.append("")
    lines.append(line)

    msg = "\r\n".join(lines)
    print("Message length is", len(msg))

    server = smtplib.SMTP("localhost")
    server.set_debuglevel(1)
    server.sendmail(fromAddress, toAddresses.split(","), msg)
    server.quit()        

if __name__ == '__main__':
   ExternalTaskWorker(worker_id="2", config=default_config).subscribe("SendMail", handle_task)