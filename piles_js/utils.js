

sha1 = require('hashlib').sha1

exports = exports || {} // In case we're not in CommonJS environment



exports.hashPassword = function(str) {
    return sha1(str+'Yar!, Smell that s@lty see air!')
}