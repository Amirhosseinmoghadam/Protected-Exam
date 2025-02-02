// tab-change.js

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function trackAction(action) {
    fetch('/tab-change/track/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ action: action, exam_id: window.examId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'warning') {
                alert(data.message);
            } else if (data.status === 'redirect') {
                if (data.action === 'permanent_ban') {
                    window.location.href = data.redirect_url; 
                } else {
                    alert(data.message);
                    window.location.href = data.redirect_url;
                }
            }
        });
}

document.addEventListener("visibilitychange", function () {
    const action = document.hidden ? 'tab-hidden' : 'tab-visible';
    trackAction(action);
});

document.addEventListener("mouseleave", function (event) {
    if (event.clientY <= 0 || event.clientX <= 0 ||
        event.clientX >= window.innerWidth || event.clientY >= window.innerHeight) {
        trackAction('mouse-left');
    }
});

document.addEventListener("mouseenter", function () {
    trackAction('mouse-entered');
});