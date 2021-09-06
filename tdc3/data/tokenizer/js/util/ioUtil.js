(function() {

    const fs = require("fs");

    function readFiles(filesArg) {
        let files;
        if (filesArg.length == 1 && filesArg[0].endsWith(".txt")) {
            files = fs.readFileSync(filesArg[0], { encoding: "utf8" }).split(/\r?\n/);
            files = files.filter(f => f.length > 0);
        } else {
            files = filesArg;
        }
        return files;
    }

    module.exports.readFiles = readFiles;

})();