const express = require('express');
const ytdl = require('ytdl-core');
const cors = require('cors');
const app = express();
const port = 3000; // You can this....

app.use(cors());
app.use(express.json());
app.use(express.static('public')); //Serve static file public folder

// Endpoint to get video info (available resolution)
app.get('/get_info', async(req, res) => {
    const url = req.query.url;
    if(!ytdl.validateURL(url)) {
        return res.status(400).json({ error:'Invalid Youtube Url' });
    }

    try {
        const info = await ytdl.getInfo(url);
        const formats = ytdl.filterFormats(info.formats, 'audioandvideo'); // Get video formats 
        const resolutions = formats.map(formats => ({
            itag: format.itag,
            resolution: format.qualityLabel || 'Unknown',
            container: format.container
        })).filter(format => format.resolution); // Filter for resolutions

        res.json({ resolutions }); // Send back resolutions
    } catch (error) {
        res.status(500).json({ error: 'Error fetching video info' });
    }
});

// Endpoint to download the video 
app.get('/download', async (req, res) => {
    const url = req.query.url;
    const itag = req.query.itag; // Youtube's formats indentifier (e.g., for 720p)

    if(!ytdl.validateURL(url) || !itag) {
        return res.status(400).json({ error: 'Invalid URL or format'});
    }

    try {
        // Check if the video is downloadable
        await ytdl.getInfo(url);
        req.header('Content-Disposition', `attachment; filename="video.mp4"`);
        ytdl(url, { filter: format => format.itag == itag }).pipe(res); // Stream the video
    } catch (error) {
        res.status(500).json({ error: 'Error downloading video' });
    }
});

app.listen(port, () => {
    console.log(`Server running on https://loaclhost:${port}`);
});