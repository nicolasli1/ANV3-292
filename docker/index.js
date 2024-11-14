// server.js
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

// Helper function to check if a number is prime
function isPrime(num) {
  if (num <= 1) return false;
  if (num <= 3) return true;
  if (num % 2 === 0 || num % 3 === 0) return false;
  for (let i = 5; i * i <= num; i += 6) {
      if (num % i === 0 || num % (i + 2) === 0) return false;
  }
  return true;
}

// Function to calculate first n primes
function calculatePrimes(n) {
  const primes = [];
  let num = 2;
  while (primes.length < n) {
      if (isPrime(num)) {
          primes.push(num);
      }
      num++;
  }
  return primes;
}

// Defining a route for handling client communication
app.get('/api/message', (req, res) => {
  const name = req.query.name || 'pepito perez'
  const message = `Hello ${name}. This Message is From Server`;
  res.json({ message });
});

// Route to get the first n prime numbers
app.get('/api/primes', (req, res) => {
  const n = parseInt(req.query.n);

  if (isNaN(n) || n <= 0) {
      return res.status(400).json({ error: 'Please provide a valid positive integer for n.' });
  }

  const primes = calculatePrimes(n);
  res.json({ primes });
});


// Starting the server
app.listen(port, () => {
    console.log(`Server is listening at http://localhost:${port}`);
});