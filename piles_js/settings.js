exports = exports || {}
// Settings
exports.settings = JSON.parse(fs.readFileSync('settings.json','r'))

exports.setting = function(name) {
    return exports.settings[name]
}