const video = document.getElementById('webcam');
const captureButton = document.getElementById('capture');
const messages = document.getElementById('messages');

// درخواست دسترسی به دوربین
navigator.mediaDevices.getUserMedia({
    video: true
})
    .then(function (stream) {
        video.srcObject = stream;
    })
    .catch(function (err) {
        console.log("خطا در دسترسی به دوربین: " + err);
    });
let mediaRecorder;
let recordedBlobs;

navigator.mediaDevices.getUserMedia({video: true, audio: false})
    .then(stream => {
        video.srcObject = stream;
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            if (event.data && event.data.size > 0) {
                recordedBlobs.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const videoBlob = new Blob(recordedBlobs, {type: 'video/webm'});
            const formData = new FormData();
            formData.append('video', videoBlob, 'recorded_video.webm');

            messages.innerText = "Sending video...";

            fetch('/face-scanner/scan-face/', {
                method: 'POST',
                headers: {'X-CSRFToken': '{{ csrf_token }}'},
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        messages.innerText = "Error: " + data.error;
                        messages.style.color = "red";
                    } else {
                        messages.innerText = "Face scanned successfully!";
                        messages.style.color = "green";
                        // هدایت به صفحه quiz_page بعد از 3 ثانیه
                        setTimeout(() => {
                            window.location.href = "/accounts/quiz/";
                        }, 3000);
                    }
                })
                .catch(err => {
                    messages.innerText = "Error: " + err.message;
                    messages.style.color = "red";
                })
                .finally(() => {
                    captureButton.disabled = false;
                    captureButton.innerText = "Start Recording";
                });
        };
    })
    .catch(err => {
        messages.innerText = "Error accessing webcam: " + err.message;
        messages.style.color = "red";
    });

captureButton.addEventListener('click', () => {
    if (mediaRecorder.state === 'inactive') {
        recordedBlobs = [];
        mediaRecorder.start();
        captureButton.innerText = "Stop Recording";
        messages.innerText = "Recording... Please slowly turn your head.";
        setTimeout(() => {
            mediaRecorder.stop();
            messages.innerText = "Processing video...";
        }, 5000); // Stop recording after 5 seconds
    } else {
        mediaRecorder.stop();
        messages.innerText = "Processing video...";
    }
    captureButton.disabled = true;
});