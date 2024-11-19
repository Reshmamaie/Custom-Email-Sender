# Custom-Email-Sender
Tools, Frameworks and libraries used are:
1. Pycharm, Flask, Flask-mail
2. Pandas, smtplib, schedule, openai

   
HTML, CSS for frontend development (audio and background image)


Python and llm like openai can be used to schedule the emails at the same time.
The user should create his credentials and than log in. No need to create new credentials repeatedly. Once created it will be saved on the server.
A CSV file with details of users are given. In the main page we can type any email address, the message prompt by which you want to develop our business and scheduling time.
Scheduling time is optional because if we give ay particular time, at that the mail will be sent.If any time is not given than the mail will be sent immediately.
If the email given is not found in the csv file, than it shows the email is not found.
If the email id is found than it will show the status of the email.
We have also used Email Throttling to control the rate of control of how many emails are sent per minute.
Once the user submits the form, the emails are processed, customized and sent using SMTP server or an external email API.
