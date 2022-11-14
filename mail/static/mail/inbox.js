document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);

    // Trigger POST request to send mail
     document.querySelector('#compose-form').addEventListener('submit', send_email);

    // By default, load the inbox
    load_mailbox('inbox');
});

function compose_email() {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';

    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    // Get mails and show
    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {

        // Show emails
        emails.forEach(email => {

            // Create new div
            const email_div = document.createElement('div');

            // Create text and assign CSS class based on status
            email_div.innerHTML = `*${email.subject}* from *${email.sender}* at ${email.timestamp}`;
            if (email.read) {
                email_div.classList.add('read_email_div');
            } else {
                email_div.classList.add('unread_email_div');
            }

            // Add event listener to open email on click
            email_div.addEventListener('click', function() {
                console.log('This email_div has been clicked!')
            });

            // Append div to container div
            document.querySelector('#emails-view').append(email_div);

        });
    });
}

function send_email(event) {

    // Prevent default, i.e. prevent the actual submit event, which is fully replaced by following code
    event.preventDefault()

    // POST request to send an email
    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
          recipients: document.querySelector('#compose-recipients').value,
          subject: document.querySelector('#compose-subject').value,
          body: document.querySelector('#compose-body').value
        })
    })
    // Listen for response and result in one block, to be able to access both the status and message
    .then(response => response.json().then(result => {

        // Handle result
        if (response.status == 201) {
            load_mailbox('sent');
            console.log(result.message);
        } else {
            console.log(result.error);
        }
    // Catch possible errors
    }))
    .catch(error => {
        console.log('Error: ', error);
    });
}