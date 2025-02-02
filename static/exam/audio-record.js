// audio-record.js
async function recordAudio() {
    try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(mediaStream);
        let audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            formData.append('exam_id', window.examId); // ارسال ID آزمون
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            formData.append('csrfmiddlewaretoken', csrftoken);
            console.log("CSRF Token:", csrftoken); // بررسی مقدار CSRF Token

            await fetch('/sound-record/upload-voice/', {
                method: 'POST',
                body: formData,
            });

            mediaStream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        setTimeout(() => {
            mediaRecorder.stop();
        }, 10000); // ضبط به مدت 10 ثانیه

    } catch (err) {
        console.error("Error accessing microphone:", err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setInterval(recordAudio, 30000); // ضبط هر ۳۰ ثانیه
    recordAudio(); // ضبط فوری یک فایل
});