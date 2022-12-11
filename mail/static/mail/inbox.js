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
    document.querySelector('#email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#email-view').style.display = 'none';
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
            email_div.innerHTML = `${email.subject} from ${email.sender} at ${email.timestamp}`;
            if (email.read) {
                email_div.classList.add('read_email_div');
            } else {
                email_div.classList.add('unread_email_div');
            }

            // Add event listener to open email on click
            email_div.addEventListener('click', () => load_email(email.id));

            // Append div to container div
            document.querySelector('#emails-view').append(email_div);

        });
    });
}

function load_email(email_id) {

    // Show the mail and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';

    // Show header name
    document.querySelector('#email-view').innerHTML = '';

    // Get mail and show in view
    fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {

        // Create reply button
        const reply_button = document.createElement('button');
        reply_button.className = 'btn btn-sm btn-outline-primary';
        reply_button.style.marginRight = '5px';

        // Set content
        reply_button.innerHTML = 'Reply';
        reply_button.addEventListener('click', () => reply_email(email_id));

        // Create archive button
        const archive_button = document.createElement('button');
        archive_button.className = 'btn btn-sm btn-outline-primary';
        archive_button.style.marginRight = '5px';

        // Set content and event based on archived status
        if (email.archived === true) {
            archive_button.innerHTML = 'Unarchive';
            archive_button.addEventListener('click', () => archive_email(email_id, false));
        } else {
            archive_button.innerHTML = 'Archive';
            archive_button.addEventListener('click', () => archive_email(email_id, true));
        }

        // Append buttons
        document.querySelector('#email-view').append(reply_button);
        document.querySelector('#email-view').append(archive_button);

        // Add horizontal ruler
        const hr = document.createElement('hr');
        document.querySelector('#email-view').append(hr);

        // Set array with email attributes, and iterate over them
        const email_attrs = ['sender', 'recipients', 'subject', 'timestamp', 'body']
        for (email_attr of email_attrs) {

            // Create new div
            const email_attr_div = document.createElement('div');

            // Create text and assign CSS class
            if (email_attr === 'body' ||  email_attr === 'timestamp') {
                email_attr_div.innerHTML = email[email_attr];
                email_attr_div.classList.add(`email_${email_attr}`);
            } else {
                email_attr_div.innerHTML = `${email_attr.toUpperCase()}: ${email[email_attr]}`;
                email_attr_div.classList.add(`email_${email_attr}`);
            }

            // Append div to container div
            document.querySelector('#email-view').append(email_attr_div);

        }
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });

    // PUT request to set the email to read status
    fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          read: true
        })
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
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
    }))
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}

function archive_email(email_id, archived_bool) {

    // PUT request to set the email to read status
    fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: archived_bool
        })
    })
    // Listen for result
    .then(result => {

        // Handle result
        if (result.status == 204) {
            load_mailbox('inbox');
        }
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}

function reply_email(email_id) {

    // First call email composition
    compose_email()

    // Fetch mail
    fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {

        // Now prefill composition fields
        document.querySelector('#compose-recipients').value = email.sender;
        if (email.subject.startsWith('RE:')) {
            document.querySelector('#compose-subject').value = email.subject;
        } else {
            document.querySelector('#compose-subject').value = `RE: ${email.subject}`;
        }
        document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:\n${email.body}`;

    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}
