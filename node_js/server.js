var express = require('express');
var app = express();
var path = require('path');
var bodyParser = require('body-parser');
var MongoClient = require('mongodb').MongoClient
var db;

//Establish Connection
MongoClient.connect('mongodb://localhost:27017/results', function (err, database) {
   if (err) 
   	throw err
   else
   {
	db = database;
	console.log('Connected to MongoDB');
	//Start app only after connection is ready
	app.listen(3000,'192.168.3.194');
        console.log('I am now listening....')
   }
 });

app.use(bodyParser.json())

app.post('/', function(req, res) {
   // Insert JSON straight into MongoDB
  db.collection('post_data').insert(req.body, function (err, result) {
      if (err)
         res.send('Error');
      else
        res.send('Success');

  });
});
