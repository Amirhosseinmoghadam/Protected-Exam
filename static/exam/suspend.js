// تایمر برای شمارش معکوس
    let timeRemaining = 60; // 10 minutes in seconds

    function updateTimer() {
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;

        document.getElementById('timer').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        if (timeRemaining > 0) {
            timeRemaining--;
        } else {
            // بازگشت به صفحه آزمون
            window.location.href = '/exam/restart-exam/';
        }
    }

    // اجرا شدن تایمر هر ۱ ثانیه
    setInterval(updateTimer, 1000);