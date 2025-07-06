var express = require('express')
const router = express.Router();
const incidentDataController = require('../Contollers/incidentDataController')


router.post('/incidents',incidentDataController.validateAndSendData)

module.exports = router;
