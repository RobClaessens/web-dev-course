document.addEventListener('DOMContentLoaded', function() {
    // Load profile
    load_profile();

    // Load posts, starting at page 1, i.e. 10 most recent posts
    load_posts(1);
});


function load_profile(reload = false) {

    // Return if no profile ID was found
    if (typeof profile_id === 'undefined') { return }

    // Load user
    fetch(`/users/${profile_id}`)
    .then(response => response.json())
    .then(profile => {

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
        const username = document.createTextNode(profile.username);

        // Append username
        username_bold.appendChild(username);
        username_div.appendChild(username_bold);
        info_div.appendChild(username_div);

        // Append date and time
        ['Member since:', profile.date_created].forEach((date_time) => {

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

        // Add 'Follow' or 'Unfollow' button if user is logged on and not checking own profile
        if (user_id && user_id !== profile_id)
        {
            const button_div = document.createElement('div');
            if (!profile.followers.includes(user_id)){
                follow_button = document.createElement('button');
                follow_button.innerHTML = "Follow";
                follow_button.setAttribute("id", 'follow_button');
                follow_button.addEventListener('click', () => follow_profile(profile.id))
                button_div.appendChild(follow_button);
                if (reload) { follow_button.disabled = true; }
            } else {
                unfollow_button = document.createElement('button');
                unfollow_button.classList.add('button');
                unfollow_button.innerHTML = "Unfollow";
                unfollow_button.setAttribute("id", 'follow_button');
                unfollow_button.addEventListener('click', () => unfollow_profile(profile.id))
                button_div.appendChild(unfollow_button);
                if (reload) { unfollow_button.disabled = true; }
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
        follow_div.setAttribute("id", `follow_${profile.id}`);
        rating_div.appendChild(follow_div);

        // Append follow img, with event handler to follow
        const follow_img = document.createElement("img");
        follow_img.src = "/static/network/images/follows.png";
        follow_img.title = "Follows"
        follow_img.style.height = "25px";
        follow_img.style.width = "80%";
        follow_div.appendChild(follow_img);

        // Append number of follows
        const follow_num = document.createTextNode(profile.number_of_follows);
        follow_div.appendChild(follow_num);

        // Create follower div
        const follower_div = document.createElement('div');
        follower_div.classList.add('follower');
        follower_div.setAttribute("id", `follower_${profile.id}`);
        rating_div.appendChild(follower_div);

        // Append follower img, with event handler to follower
        const follower_img = document.createElement("img");
        follower_img.src = "/static/network/images/followers.png";
        follower_img.title = "Followers"
        follower_img.style.height = "25px";
        follower_img.style.width = "80%";
        follower_div.appendChild(follower_img);

        // Append number of followers
        const follower_num = document.createTextNode(profile.number_of_followers);
        follower_div.appendChild(follower_num);
    });
}

function load_posts(page) {

    // Return if no user ID was found, i.e. user is not logged on, no posts will be shown
    if (typeof user_id === 'undefined' || user_id === 0) { return }
    // Check if profile ID is defined, otherwise set to 0, which is unused as user ID, count starts at 1
    if (typeof profile_id === 'undefined') { profile_id = 0; }
    // Check if following is defined, otherwise set to false
    if (typeof following === 'undefined') { following = false; }

    // Clear and show the posts view
    document.querySelector('#posts').innerHTML = '';
    document.querySelector('#posts').style.display = 'block';

    // Get posts and show
    // Optionally these are only posts by followed profiles or by one specific profile
    fetch(`/posts/${following ? 'following' : profile_id}`)
    .then(response => response.json())
    .then(posts => {

        // Show posts
        posts.slice(page * 10 - 10, page * 10).forEach(post => {

            // Create post div
            const post_div = document.createElement('div');
            post_div.setAttribute("id", `post_${post.id}`);
            post_div.classList.add('post');

            // Append post div to container div
            document.querySelector('#posts').append(post_div);

            // Load post
            load_post(post);
        });

        // Create navigation bar at the bottom
        const navigator = document.createElement("NAV");
        navigator.setAttribute("id", "navigator");
        const pages = document.createElement("ul");
        pages.classList.add("pagination")
        navigator.appendChild(pages);

        // Add 'Previous' button if not on the first page
        if (page !== 1) {
            const previous = document.createElement("li");
            previous.classList.add("page-item")
            prev_button = document.createElement('button');
            prev_button.innerHTML = "Previous";
            prev_button.setAttribute("id", 'prev_button');
            prev_button.addEventListener('click', () => load_posts(page - 1))
            previous.appendChild(prev_button);
            pages.appendChild(previous);
        }

        // Add 'Next' button if an additional page of posts is available
        if (Math.floor(posts.length / 10) >= page) {
            const next = document.createElement("li");
            next.classList.add("page-item")
            next_button = document.createElement('button');
            next_button.innerHTML = "Next";
            next_button.setAttribute("id", 'next_button');
            next_button.addEventListener('click', () => load_posts(page + 1))
            next.appendChild(next_button);
            pages.appendChild(next);
        }

        // Append navigation bar to container div
        document.querySelector('#posts').append(navigator);
    });
}


function load_post(post, reload = false, edit = false) {

    // Small subfunction that adjusts the height of the text area element to fit its content
    function adjustTextareaHeight(element) {
        element.style.height =  "auto";
        element.style.height = (element.scrollHeight) + 2 + "px";
    }

    // Check if user ID is defined, otherwise set to 0, which is unused as user ID, count starts at 1
    if (typeof user_id === 'undefined') { user_id = 0; }

    // Get post div
    const post_div = document.getElementById(`post_${post.id}`)

    // Create text div or text area (if edit)
    if (edit) {
        const text_area = document.createElement('textarea');
        text_area.setAttribute("id", `textarea_${post.id}`);
        text_area.classList.add('text');
        text_area.value = post.text
        post_div.appendChild(text_area);
        // Resize height so content fits the text area, also attach event handlers that will resize on input or on resize
        adjustTextareaHeight(text_area);
        text_area.addEventListener('input', function() { adjustTextareaHeight(text_area) });
        window.addEventListener('resize', function() { adjustTextareaHeight(text_area) });
    } else {
        const text_div = document.createElement('div');
        text_div.classList.add('text');
        // For div.innerHTML, \n linebreaks must be parsed to <br>
        text_div.innerHTML = post.text.replaceAll('\n', '<br>');
        post_div.appendChild(text_div);
    }

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
    like_img.title = "Likes"
    like_img.style.height = "25px";
    like_img.style.width = "80%";
    like_img.setAttribute("id", `like_img_${post.id}`);
    if (user_id !== post.user_id) {
        like_img.addEventListener('click', () => like_post(post.id));
        if (reload) { like_img.classList.add('img-disabled'); }
    }
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
    dislike_img.title = "Dislikes"
    dislike_img.style.height = "25px";
    dislike_img.style.width = "80%";
    dislike_img.setAttribute("id", `dislike_img_${post.id}`);
    if (user_id !== post.user_id) {
        dislike_img.addEventListener('click', () => dislike_post(post.id));
        if (reload) { dislike_img.classList.add('img-disabled'); }
    }
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
    
    // Add Edit button, or when editing, add Save button
    if (user_id === post.user_id) {
        if (!edit) {
            const button_div = document.createElement('div');
            edit_button = document.createElement('button');
            edit_button.classList.add('button');
            edit_button.innerHTML = "Edit";
            edit_button.setAttribute("id", `edit_button_${post.id}`);
            edit_button.addEventListener('click', () => reload_post(post.id, edit=true))
            button_div.appendChild(edit_button);
            info_div.appendChild(button_div);
            if (reload) { edit_button.disabled = true; }
        } else {
            const button_div = document.createElement('div');
            edit_button = document.createElement('button');
            edit_button.classList.add('button');
            edit_button.innerHTML = "Save";
            edit_button.setAttribute("id", `edit_button_${post.id}`);
            edit_button.addEventListener('click', () => edit_post(post.id))
            button_div.appendChild(edit_button);
            info_div.appendChild(button_div);
            if (reload) { edit_button.disabled = true; }
        }
    }
}


function like_post(post_id) {

    // PUT request to like the post
    fetch(`/like_post/${post_id}`, {
        method: 'PUT'
    })
    // Listen for result
    .then(result => {

        // Handle result, 200 (existing like removed), 201 (new like created)
        if (result.status == 200 || result.status == 201) {
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

        // Handle result, 200 (existing dislike removed), 201 (new dislike created)
        if (result.status == 200 || result.status == 201) {
            reload_post(post_id);
        }
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}


function edit_post(post_id) {

    // PUT request to edit the post
    fetch(`/edit_post/${post_id}`, {
        method: 'PUT',
        body: JSON.stringify({ text: document.getElementById(`textarea_${post_id}`).value ?? null })
    })
    // Listen for result
    .then(result => {

        // Handle result, 200 (post updated)
        if (result.status == 200) {
            reload_post(post_id);
        }
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}


function follow_profile(profile_id) {

    // PUT request to follow the profile
    fetch(`/follow_profile/${profile_id}`, {
        method: 'PUT'
    })
    // Listen for result
    .then(result => {

        // Handle result
        if (result.status == 204) {
            reload_profile(profile_id);
        }
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}


function unfollow_profile(profile_id) {

    // PUT request to unfollow the profile
    fetch(`/unfollow_profile/${profile_id}`, {
        method: 'PUT'
    })
    // Listen for result
    .then(result => {

        // Handle result
        if (result.status == 204) {
            reload_profile(profile_id);
        }
    })
    // Catch possible errors
    .catch(error => {
        console.log('Error: ', error);
    });
}


function reload_post(post_id, edit = false) {

    // Get element
    const post_div = document.getElementById(`post_${post_id}`);

    // Add nested event handlers for chained animations
    post_div.addEventListener('animationend', () => {
        post_div.addEventListener('animationend', () => {
            // Remove animation classes
            post_div.classList.remove('hide');
            post_div.classList.remove('unhide');
            // Re-enable img clicks, by removing CSS class
            document.getElementById(`like_img_${post_id}`).classList.remove('img-disabled');
            document.getElementById(`dislike_img_${post_id}`).classList.remove('img-disabled');
            // Re-enable edit and save button if present
            const edit_button = document.getElementById(`edit_button_${post_id}`);
            if (edit_button) { edit_button.disabled = false; }
        }, { once: true });

        // Reload post
        fetch(`/post/${post_id}`)
        .then(response => response.json())
        .then(post => {
            // Clear div
            post_div.innerHTML = '';

            // Load post
            load_post(post, reload=true, edit=edit);
        });

        // Add unhide class to trigger unhide animation
        post_div.classList.add('unhide');
    }, { once: true });

    // Add hide class to trigger hide animation
    post_div.classList.add('hide');
}


function reload_profile(profile_id) {

    // Get element
    const profile_div = document.getElementById('profile');

    // Add nested event handlers for chained animations
    profile_div.addEventListener('animationend', () => {
        profile_div.addEventListener('animationend', () => {
            // Remove animation classes
            profile_div.classList.remove('hide');
            profile_div.classList.remove('unhide');
            // Re-enable button
            document.getElementById('follow_button').disabled = false;
        }, { once: true });

        // Load profile
        load_profile(profile, true);

        // Add unhide class to trigger unhide animation
        profile_div.classList.add('unhide');
    }, { once: true });

    // Add hide class to trigger hide animation
    profile_div.classList.add('hide');
}