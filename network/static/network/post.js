document.addEventListener('DOMContentLoaded', function() {
    // Load all posts
    load_posts();
});


function load_posts() {
  
    // Clear and show the posts view
    document.querySelector('#posts').innerHTML = '';
    document.querySelector('#posts').style.display = 'block';

    // Get posts and show
    fetch(`/posts`)
    .then(response => response.json())
    .then(posts => {

        // Show posts
        posts.forEach(post => {

            // Create post div
            const post_div = document.createElement('div');
            post_div.classList.add('post');

            // Create text div
            const text_div = document.createElement('div');
            text_div.classList.add('text');
            post_div.appendChild(text_div);

            // Append text
            const text = document.createTextNode(post.text);
            text_div.appendChild(text);
            
            // Create rating div
            const rating_div = document.createElement('div');
            rating_div.classList.add('rating');
            post_div.appendChild(rating_div);

            // Create like div
            const like_div = document.createElement('div');
            like_div.classList.add('like');
            rating_div.appendChild(like_div);

            // Append like img, with event handler to like
            const like_img = document.createElement("img");
            like_img.src = "/static/network/images/thumb_up.png";
            like_img.style.height = "25px";
            like_img.style.width = "80%";
            like_img.addEventListener('click', () => like_post(post.id))
            like_div.appendChild(like_img);
            
            // Append number of likes
            const like_num = document.createTextNode(post.number_of_likes);
            like_div.appendChild(like_num);
            
            // Create dislike div
            const dislike_div = document.createElement('div');
            dislike_div.classList.add('dislike');
            rating_div.appendChild(dislike_div);

            // Append dislike img, with event handler to dislike
            const dislike_img = document.createElement("img");
            dislike_img.src = "/static/network/images/thumb_down.png";
            dislike_img.style.height = "25px";
            dislike_img.style.width = "80%";
            dislike_img.addEventListener('click', () => dislike_post(post.id))
            dislike_div.appendChild(dislike_img);
            
            // Append number of dislikes
            const dislike_num = document.createTextNode(post.number_of_dislikes);
            dislike_div.appendChild(dislike_num);
            
            // Create info div
            const info_div = document.createElement('div');
            info_div.classList.add('info');
            post_div.appendChild(info_div);

            // Create username
            const username_div = document.createElement('div');
            const username_bold = document.createElement('strong');
            const username = document.createTextNode(post.username);

            // Append username
            username_bold.appendChild(username);
            username_div.appendChild(username_bold);
            info_div.appendChild(username_div);

            // Append date and time
            [post.time_created, post.date_created].forEach((date_time) => {

                // Create date and time
                const date_time_div = document.createElement('div');
                const date_time_italic = document.createElement('I');
                const date_time_small = document.createElement('SMALL');
                const date_time_text = document.createTextNode(date_time);

                // Append date and time
                date_time_small.appendChild(date_time_text);
                date_time_italic.appendChild(date_time_small);
                date_time_div.appendChild(date_time_italic);
                info_div.appendChild(date_time_div);
            });

            // Append post div to container div
            document.querySelector('#posts').append(post_div);
        });
    });
}


function like_post(post_id) {

    // PUT request to like the post
    fetch(`/like_post/${post_id}`, {
        method: 'PUT'
    })
    // Listen for result
    .then(result => {

        // Handle result
        if (result.status == 204) {
            load_posts();
        }
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}


function dislike_post(post_id) {

    // PUT request to dislike the post
    fetch(`/dislike_post/${post_id}`, {
        method: 'PUT'
    })
    // Listen for result
    .then(result => {

        // Handle result
        if (result.status == 204) {
            load_posts();
        }
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}
