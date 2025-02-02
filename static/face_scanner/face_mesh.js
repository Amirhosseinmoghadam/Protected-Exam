function onResults(results) {
            const canvasElement = document.getElementById('output_canvas');
            const canvasCtx = canvasElement.getContext('2d');

            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

            if (results.multiFaceLandmarks) {
                for (const landmarks of results.multiFaceLandmarks) {
                    // Draw face mesh
                    canvasCtx.fillStyle = 'rgba(255,255,255,0.13)';
                    canvasCtx.strokeStyle = '#ff0000';
                    canvasCtx.lineWidth = 1;

                    // Connect landmarks to create mesh
                    for (let i = 0; i < landmarks.length; i++) {
                        const point = landmarks[i];
                        canvasCtx.beginPath();
                        canvasCtx.arc(
                            point.x * canvasElement.width,
                            point.y * canvasElement.height,
                            1,
                            0,
                            2 * Math.PI
                        );
                        canvasCtx.fill();
                    }
                }
            }
            canvasCtx.restore();
        }

        // Initialize canvas size
        document.addEventListener('DOMContentLoaded', function () {
            const canvasElement = document.getElementById('output_canvas');
            canvasElement.width = 640;
            canvasElement.height = 480;
        });

        const faceMesh = new FaceMesh({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
            }
        });

        faceMesh.setOptions({
            maxNumFaces: 1,
            refineLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });

        faceMesh.onResults(onResults);

        const camera = new Camera(document.querySelector('.input_video'), {
            onFrame: async () => {
                await faceMesh.send({image: document.querySelector('.input_video')});
            },
            width: 640,
            height: 480
        });

        camera.start();

