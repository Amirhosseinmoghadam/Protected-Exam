// ایجاد یک عنصر ویدیو به صورت نامرئی
    const video = document.createElement('video');
    video.style.display = 'none';
    document.body.appendChild(video);

    // ایجاد یک عنصر canvas به صورت نامرئی
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    // دسترسی به دوربین کاربر
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function (stream) {
        video.srcObject = stream;
        video.play();
      })
      .catch(function (err) {
        console.error("Error accessing camera: ", err);
      });

    // تابع برای گرفتن عکس و ارسال آن
    function captureAndSend() {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = canvas.toDataURL('image/jpeg');

      fetch('/face-scanner/face-match/', {
        method: 'POST',
        body: JSON.stringify({ imageData: imageData, exam_id: window.examId }), // ارسال داده به صورت JSON
        headers: {
          'X-CSRFToken': '{{ csrf_token }}',
          'Content-Type': 'application/json', // تغییر نوع محتوا به JSON
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log('Response received:', data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }

    // اجرای دوره‌ای ارسال درخواست fetch
    setInterval(captureAndSend, 15000); // هر 2 دقیقه