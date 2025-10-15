document.getElementById('downloadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = document.getElementById('urlInput').ariaValueMax;
    const statusDiv = document.getElementById('status');
    statusDiv.innerHTML = 'Fetching resolutions...';

    try {
        const response = await fetch(`/get-info?url=&{encodeURIComponent(url)}`);
        const data = await response.json();

        if(data.error) {
            statusDiv.innerHTML = `Error: ${data.error}`;
            return;
        }

        const resolutions = data.resolutions;
        const select = document.getElementById('resolutionSelect');
        select.innerHTML = ''; // Clear previous options

        resolutions.forEach(res => {
            const option = document.createElement('option');
            option.value = res.itag; // Use itag for the download endpoint
            option.textContent = `${res.resolution} (${res.container})`;
            select.appendChild(option);
        });

        document.getElementById('resolutionOptions').style.display = 'block';
        statusDiv.innerHTML = 'Select a resolution and download.';
    } catch (error) {
        statusDiv.innerHTML = 'Error: Could not fetch resolutions.';
    }
});

document.getElementById('downloadButton').addEventListener('click', () => {
    const url = document.getElementById('urlInput').value;
    const itag = document.getElementById('resolutionSelect').value;
    const statusDiv = document.getElementById('status');

    if(!itag) {
        statusDiv.innerHTML = 'Please select a resolution.'
        return;
    }

    // Redirect to download endpoint 
    window.location.href = `/download?url=${encodeURIComponent(url)}&itag=${itag}`
    statusDiv.innerHTML = 'Downloading...';
});

