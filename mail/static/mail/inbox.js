document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', () => compose_email({}));

    // By default, load the inbox
    load_mailbox('inbox');

    // Send an email
    document.querySelector('#compose-form').onsubmit = function() {
        fetch('/emails', {
            method: 'POST',
            body: JSON.stringify({
                recipients: document.querySelector('#compose-recipients').value,
                subject: document.querySelector('#compose-subject').value,
                body: document.querySelector('#compose-body').value
                })
            })
            .then((response) => {

                //getting display item
                const banner = document.querySelector('#compose-banner');
                banner.classList.add('alert');

                //if any error occurs
                if(response.status == 400)
                {
                    banner.classList.add('alert-danger');
                    response.json().then(obj => {
                        banner.innerHTML = obj.error;
                    });
                }

                // load sent mailbox after sending email
                else
                {                    
                    response.json().then(obj => {
                        load_mailbox('sent');
                    });
                }
            })
        .catch(error => {
            console.log('Error: ', error);
        });

        return false;
    }
});

//to manage archiving and unarchiving
function archive_manager(email_id, archive_value)
{
    fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: archive_value
        })
      }).then(()=>{
          load_mailbox('inbox');
      });
}

//to display an email
function show_email(link) {

    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#sp-email-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';

    const email_id = link.dataset.email_id;
    const mailbox = link.dataset.mailbox;

    fetch(`/emails/${email_id}`)
    .then((res) => {

        //any error in fetching email
        if(res.status == 404)
        {
            const banner = document.querySelector('#sp-error-banner');
            res.json().then((obj) => {
                console.log('error', obj.error);
                banner.innerHTML = obj.error;
            });
        }
        else 
        {
            const view = document.querySelector('#sp-email-view');
            res.json().then((obj)=>{

                document.querySelector('#email-sender').innerHTML = `<b>From: </b> ${obj['sender']}`;
                document.querySelector('#email-receiver').innerHTML = `<b>To: </b> ${obj['recipients']}`;
                document.querySelector('#email-subject').innerHTML = `<b>Subject: </b> ${obj['subject']}`;
                document.querySelector('#email-time').innerHTML = `<b>Timestamp: </b> ${obj['timestamp']}`;
                document.querySelector('#email-body').innerHTML = obj['body'];

                //get buttons
                const reply = document.querySelector('#reply');
                const archive = document.querySelector('#archive');

                //send the current email as argument to the function
                reply.onclick = () => compose_email(obj);

                if (mailbox == 'inbox')
                {
                    archive.innerHTML = 'Archive';
                    archive.onclick = () => archive_manager(email_id, true);
                }
                else if (mailbox == 'archive')
                {
                    archive.innerHTML = 'Unarchive';
                    archive.onclick = () => archive_manager(email_id, false);
                }

                //mark email as read
                fetch(`/emails/${email_id}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        read: true
                    })
                });
            });            
        }
    });
}

function compose_email(email) {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#sp-email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Clear out composition fields
    recipients = document.querySelector('#compose-recipients');
    subject = document.querySelector('#compose-subject');
    body = document.querySelector('#compose-body');

    if(email['sender'])
    {
        //if replying to own email
        if(email['sender'] == document.querySelector('#compose-sender').value)
            recipients.value = email['recipients'];
        else
            recipients.value = email['sender'];
    }
    else
    {
        recipients.value = '';
        recipients.disabled = false;
    }

    if(email['subject'])
    {
        subjectMatter = '';
        if(email['subject'].slice(0,3)=='Re:')
            subjectMatter = email['subject'];
        else
            subjectMatter = 'Re: '+email['subject'];

        subject.value = subjectMatter;
        subject.disabled = true;
    }
    else
    {
        subject.value = '';
        subject.disabled = false;
    }

    if( email['body'])
    {
        bodyMatter = `On ${email['timestamp']}, ${email['sender']} wrote: \n${email['body']}`
        body.value = bodyMatter;
    }
    else
    {
        body.value = '';
        body.disabled = false;
    }
}

function load_mailbox(mailbox) {

    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#sp-email-view').style.display = 'none';

    // Show the mailbox name
    view = document.querySelector('#emails-view');
    view.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`

    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        
        const element = document.createElement('div');
        element.classList.add('container');

        //if no emails are present in the current mailbox

        if(emails.length == 0) {
            element.innerHTML = 'Nothing to see here!';
        }
        else {
            emails.forEach(function(email){

                const link = document.createElement('a');
                link.dataset.email_id = email['id'];
                link.dataset.mailbox = mailbox;
                link.id = 'sp-email';
                link.addEventListener('click', () => show_email(link));  
    
                const row = document.createElement('div');
                row.classList.add('row', 'mailbox-email', 'rounded-lg', 'border-bottom', 'border-secondary', 'shadow-sm');
                
                if(email['read']==true)
                    row.style.backgroundColor = '#dfdfdf';
    
                //the sender section
                const sender = document.createElement('div');
                sender.classList.add('col-lg-3', 'col-sm-12', 'mailbox-sender');
                if(mailbox=='sent')
                    sender.innerHTML = email['recipients'];
                else
                    sender.innerHTML = email['sender'];
    
                //the subject section
                const subject = document.createElement('div');
                subject.classList.add('col-lg-6', 'col-sm-12', 'mailbox-subject');
                subject.innerHTML = email['subject'];
    
                //the timestamp section
                const time = document.createElement('div');
                time.classList.add('col-lg-3', 'col-sm-12', 'mailbox-time');
                time.innerHTML = email['timestamp'];
    
                row.appendChild(sender);
                row.appendChild(subject);
                row.appendChild(time);
    
                link.appendChild(row)
    
                element.appendChild(link);
            });
    
        }

        view.appendChild(element);
    });
}