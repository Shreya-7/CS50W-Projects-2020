document.addEventListener('DOMContentLoaded', ()=>{

    // for all posts made by the user
    document.querySelectorAll('.edit-link').forEach(element => {

        element.addEventListener('click', function(){

            // hide all edit areas
            document.querySelectorAll('.edit-area').forEach(element => {
                element.style.display = 'none';
            });

            // show corresponding edit area
            document.getElementById(`edit_area_${this.dataset.post_id}`).style.display = 'block';

            // hide corresponding post
            document.getElementById(`post_content_${this.dataset.post_id}`).style.display = 'none';

            // hide corresponding edit link
            this.style.display = 'none';
            
            // form submission
            document.querySelector(`#edit_area_${this.dataset.post_id} .edit-post-form`).onsubmit = ()=>{
                return editPost(this.dataset.post_id);
            };
        });

    });

    document.querySelectorAll('.like-btn').forEach(element => {

        element.addEventListener('click', toggleLike);

    });

    // set follow listener when profile page loads
    if (window.location.href.indexOf('profile') != -1) {
        document.querySelector('#follow-btn').addEventListener('click', toggleFollow);
    }
    
});

// edit a post asynchronously

function editPost(post_id) {

    fetch(`/edit_post/${post_id}`, {
        method: 'POST',
        body: JSON.stringify({
            content: document.getElementById(`edit_content_${post_id}`).value
        })
    })
    .then(response => response.json())
    .then((response) => {
        
        // reset all displays
        document.getElementById(`edit_area_${post_id}`).style.display = 'none';
        document.getElementById(`post_content_${post_id}`).style.display = 'block';
        document.getElementById(`post_content_${post_id}`).innerHTML = response['content'];
        document.querySelectorAll('.edit-link').forEach(element=>{
            element.style.display = 'inline';
        })

    })
    .catch(error => {
            console.log('Error: ', error);
    });

    // return false to stop page reload
    return false;
}

function toggleLike() {
    
    const post_id = this.dataset.post_id;

    fetch(`/like/${post_id}`, {
        method: 'PUT'
    })
    .then(response => response.json())
    .then((response) => {

        // update like count
        document.getElementById(`like_${post_id}`).innerHTML = response['likes'];

        // update like status
        this.innerHTML = response['liked'];
    });

}

function toggleFollow() {
    
    const username = this.dataset.username;
    
    fetch(`/follow/${username}`, {
        method: 'PUT'
    })
    .then(response => response.json())
    .then((response) => {

        // update follow status
        this.innerHTML = response['followed'];

        // update follow counts
        document.getElementById('followers').innerHTML = response['followers'];
        document.getElementById('following').innerHTML = response['following'];
    });

}

