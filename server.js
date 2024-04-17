const express = require('express');
const path = require('path');
const childProcess = require('child_process');

const fs = require('fs');
const axios = require('axios');
const { Worker, isMainThread, parentPort } = require('worker_threads');
const { spawn } = require('child_process');

const app = express();
const port = process.env.PORT || 3000
const DB = 'downloads'


app.use(express.static(path.join(__dirname)));
app.use('/node_modules', express.static(path.join(__dirname, 'node_modules')));


async function downloadFile(url)
{
  const fileUrl = url;
  const fileName = path.basename(fileUrl) + ".png";
  const filePath = path.join(__dirname, DB, fileName);

 
  if (fs.existsSync(filePath)) {
     return;
  }
 
  try {
     const response = await axios.get(fileUrl, { responseType: 'arraybuffer' });
     fs.writeFileSync(filePath, response.data, 'binary');
 
  } catch (error) {
     console.error('Error downloading file:', error);
  }
};


app.get('/stream', async (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const { xMin, yMin, xMax, yMax, z, pattern, model } = req.query;


  const download_process = spawn('python3', [path.join(__dirname, 'downloader.py'), xMin, yMin, xMax, yMax, z, pattern]);
  model_process = null;
  if (model.endsWith('640.pth'))
  {
    model_process = spawn('python3', [path.join(__dirname, 'model_640.py'), xMin, yMin, xMax, yMax, z, pattern, model]);
  }
  else
  {
    model_process = spawn('python3', [path.join(__dirname, 'model.py'), xMin, yMin, xMax, yMax, z, pattern, model]);
  }
  

  const download_processPromise = new Promise((resolve) => {
    download_process.stdout.on('data', (data) => {
      if (res.closed)
      {
        res.end();
        download_process.kill();
        model_process.kill();
        return;
      }
      res.write(`data: i:${data.length / 3}\n\n`);
    });

    download_process.stderr.on('data', (data) => {
      console.log(String(data));
    });


    download_process.on('close', (code) => {
      console.log(`Process 1 exited with code ${code}`);
      resolve();
    });
  });

  
  const model_processPromise = new Promise((resolve) => {
    model_process.stdout.on('data', (data) => {
      if (res.closed)
      {
        res.end();
        download_process.kill();
        model_process.kill();
        return;
      }

      const regex_x = /x=(\d+)/;
      const regex_y = /y=(\d+)/;
      const filenames = String(data).split('\n');

      //const match_x = filename.match(regex_x);
      //const match_y = filename.match(regex_y);
      
      

      for (var i = 0; i <  filenames.length - 1; ++i)
      {
        const match_x = filenames[i].match(regex_x);
        const match_y = filenames[i].match(regex_y);
        
        //console.log('file: ' + filenames[i])
        //console.log(match_x[1])
        //console.log(match_y[1])


        const fileContent = fs.readFileSync(filenames[i], 'utf-8');
        res.write(`data: x:${match_x[1]} y:${match_y[1]} points:${fileContent}\n\n`)
      }
      //console.log(String(data));
      //res.write(`data: j:${data.length / 3}\n\n`);
    });

    model_process.stderr.on('data', (data) => {
      if (res.closed)
      {
        res.end();
        download_process.kill();
        model_process.kill();
        return;
      }
      console.log(String(data));
    });

    model_process.on('close', (code) => {
      console.log(`Process 2 exited with code ${code}`);
      resolve();
    });
  });

  console.log("done");


  await Promise.all([download_processPromise, model_processPromise/*, download_process2Promise*/]);

  res.end();
});


app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
