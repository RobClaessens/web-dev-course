document.addEventListener('DOMContentLoaded', function() {
    // Load profile
    load_profile();

    // Load all posts
    load_posts();
});


function load_profile() {

    // Return if no user ID was found
    if (typeof user_id === 'undefined') { return }

    // Load user
    fetch(`/users/${user_id}`)
    .then(response => response.json())
    .then(user => {

        // Get profile div
        const profile_div = document.getElementById('profile');
                
        // Clear and show the profile view
        profile_div.innerHTML = '';
        profile_div.style.display = 'flex';

        // Create info div
        const info_div = document.createElement('div');
        info_div.classList.add('info');
        profile_div.appendChild(info_div);

        // Create username
        const username_div = document.createElement('div');
        const username_bold = document.createElement('strong');
        const username = document.createTextNode(user.username);

        // Append username
        username_bold.appendChild(username);
        username_div.appendChild(username_bold);
        info_div.appendChild(username_div);

        // Append date and time
        ['Member since:', user.date_created].forEach((date_time) => {

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

        // NOTE: Current user or chosen user?
        // Add 'Follow' or 'Unfollow' button
        if (user_id !== 'logged_on_user_someone_logged_on')
        {
            const button_div = document.createElement('div');
            if ('logged_on_user_follows'.includes(user_id)){
                follow_button = document.createElement('button');
                follow_button.innerHTML = "Follow";
                follow_button.addEventListener('click', () => follow_profile(user.id))
                button_div.appendChild(follow_button);
            } else {
                unfollow_button = document.createElement('button');
                unfollow_button.classList.add('button');
                unfollow_button.innerHTML = "Unfollow";
                unfollow_button.addEventListener('click', () => follow_profile(user.id))
                button_div.appendChild(unfollow_button);
            }
            info_div.appendChild(button_div);
        }

        // Create rating div
        const rating_div = document.createElement('div');
        rating_div.classList.add('rating');
        profile_div.appendChild(rating_div);
    
        // Create follow div
        const follow_div = document.createElement('div');
        follow_div.classList.add('follow');
        follow_div.setAttribute("id", `follow_${user.id}`);
        rating_div.appendChild(follow_div);

        // Append follow img, with event handler to follow
        const follow_img = document.createElement("img");
        follow_img.src = "/static/network/images/follows.png";
        follow_img.style.height = "25px";
        follow_img.style.width = "80%";
        follow_img.addEventListener('click', () => follow_profile(user.id))
        follow_div.appendChild(follow_img);

        // Append number of follows
        const follow_num = document.createTextNode(user.number_of_follows);
        follow_div.appendChild(follow_num);

        // Create follower div
        const follower_div = document.createElement('div');
        follower_div.classList.add('follower');
        follower_div.setAttribute("id", `follower_${user.id}`);
        rating_div.appendChild(follower_div);

        // Append follower img, with event handler to follower
        const follower_img = document.createElement("img");
        follower_img.src = "/static/network/images/followers.png";
        follower_img.style.height = "25px";
        follower_img.style.width = "80%";
        follower_img.addEventListener('click', () => follower_profile(user.id))
        follower_div.appendChild(follower_img);

        // Append number of followers
        const follower_num = document.createTextNode(user.number_of_followers);
        follower_div.appendChild(follower_num);
    });
}

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
            post_div.setAttribute("id", `post_${post.id}`);
            post_div.classList.add('post');

            // Append post div to container div
            document.querySelector('#posts').append(post_div);

            // Load post
            load_post(post);
        });
    });
}


function load_post(post) {

    // Get post div
    const post_div = document.getElementById(`post_${post.id}`)

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
    like_div.setAttribute("id", `like_${post.id}`);
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
    dislike_div.setAttribute("id", `dislike_${post.id}`);
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
    username_div.addEventListener('click', () => window.open(`/profile/${post.user_id}`, "_self"));

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
            reload_post(post_id);
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
            reload_post(post_id);
        }
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}


function reload_post(post_id) {

    // Get element
    const post_div = document.getElementById(`post_${post_id}`);

    // Add nested event handlers for chained animations
    post_div.addEventListener('animationend', () => {
        post_div.addEventListener('animationend', () => {
            // Remove animation classes
            post_div.classList.remove('hide');
            post_div.classList.remove('unhide');
        }, { once: true });

        // Reload post
        fetch(`/posts/${post_id}`)
        .then(response => response.json())
        .then(post => {
            // Clear div
            post_div.innerHTML = '';

            // Load post
            load_post(post);
        });

        // Add unhide class to trigger unhide animation
        post_div.classList.add('unhide');
    }, { once: true });

    // Add hide class to trigger hide animation
    post_div.classList.add('hide');
}