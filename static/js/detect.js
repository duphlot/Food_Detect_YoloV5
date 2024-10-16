document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('start-recording');
    const stopButton = document.getElementById('stop-recording');
    const downloadButton = document.getElementById('download-video');

    startButton.addEventListener('click', function() {
        fetch('/start_recording', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                alert(data.message);
                downloadButton.style.display = 'none';
            })
            .catch(error => console.error('Error:', error));
    });

    stopButton.addEventListener('click', function() {
        fetch('/stop_recording', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                alert(data.message);
                if (data.filename) {
                    downloadButton.style.display = 'block';
                    downloadButton.setAttribute('data-filename', data.filename);
                }
            })
            .catch(error => console.error('Error:', error));
    });

    downloadButton.addEventListener('click', function() {
        const filename = downloadButton.getAttribute('data-filename');
        if (filename) {
            window.location.href = `/download_video/${filename}`;
        }
    });
});
