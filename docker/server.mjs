import { createServer } from 'node:http';

const hostname = '0.0.0.0';
const port = process.env.PORT || 3000;

let dataStore = []; // Simple in-memory data store

const server = createServer((req, res) =>
{
  res.setHeader('Content-Type', 'application/json');

  if (req.url === '/data' && req.method === 'GET')
  {
    // Read all data
    res.statusCode = 200;
    res.end(JSON.stringify(dataStore));
  } else if (req.url === '/data' && req.method === 'POST')
  {
    // Create new data
    let body = '';
    req.on('data', chunk =>
    {
      body += chunk.toString();
    });
    req.on('end', () =>
    {
      const newData = JSON.parse(body);
      dataStore.push(newData);
      res.statusCode = 201;
      res.end(JSON.stringify({ message: 'Data added', data: newData }));
    });
  } else if (req.url.startsWith('/data/') && req.method === 'PUT')
  {
    // Update data by ID
    const id = req.url.split('/')[2];
    let body = '';
    req.on('data', chunk =>
    {
      body += chunk.toString();
    });
    req.on('end', () =>
    {
      const updatedData = JSON.parse(body);
      dataStore[id] = updatedData;
      res.statusCode = 200;
      res.end(JSON.stringify({ message: 'Data updated', data: updatedData }));
    });
  } else if (req.url.startsWith('/data/') && req.method === 'DELETE')
  {
    // Delete data by ID
    const id = req.url.split('/')[2];
    dataStore.splice(id, 1);
    res.statusCode = 200;
    res.end(JSON.stringify({ message: 'Data deleted' }));
  } else
  {
    res.statusCode = 404;
    res.end(JSON.stringify({ message: 'Not Found' }));
  }
});

server.listen(port, hostname, () =>
{
  console.log(`Server running at http://${hostname}:${port}/`);
});
