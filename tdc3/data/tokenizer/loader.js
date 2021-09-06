var csv = require('csv-parser')
var fs = require('fs')
const { ArgumentParser } = require('argparse');
const tokenExtraction = require("./tokenExtraction");

/******** command-line arguments ***********/
const parser = new ArgumentParser({
    description: "Not intended for direct usage. Use extractFromJS.js instead."
});
// parser.add_argument(
//     "--what", { help: "Kind of data to extract", choices: ["tokens", "tokensPerFunction", "tokensPerFunctionMaskName", "conditionals"], required: true });
parser.add_argument(
    "--inputdir", { help: "Directory with data to be tokenized", required: true }); 
parser.add_argument(
    "--outputdir", { help: "Directory to store the tokenized data", required: true });    
const args = parser.parse_args();
/******************************************/
args.what = "tokens"

var timestamp = Date.now();
var files = fs.readdirSync(args.inputdir);

function asyncFunction (file, cb) {
  setTimeout(() => {
    var counter = 0
    allResults = []
    bigstring = ""

     fs.createReadStream(args.inputdir + file)
        .pipe(csv())
        .on('data', function (row) {

            counter++;

            // structure of input file
            // Description, Test, Project_name, Project_URL, Path
            file = row['File'] 
            code = row['Test']
            
            // copied from pa/extractFromJSSingleInstance
            if (args.what == "tokens") {
                tokenExtraction.extractTokensFromFile(code, file, allResults);
            } else if (args.what == "tokensPerFunction") {   
                tokenExtraction.extractTokensPerFunction(code, file, allResults, false);
                console.log("TODO")
                process.exit(1)
            } else if (args.what == "tokensPerFunctionMaskName") {
                // tokenExtraction.extractTokensPerFunction(code, file, allResults, true);
                console.log("TODO")
                process.exit(1)
            } else if (args.what == "conditionals") {
                // const examples = conditionalExtraction.extractExamples(code, file);
                // allResults.push(...examples);
                console.log("TODO")
                process.exit(1)
            }

            // Needs to stringify one element at a time. otherwise it will get lost             
            lastResult = allResults[allResults.length-1]
            allResults = []
            if (lastResult != undefined) {
                // update description in the metadata field
                lastResult['metadata']['description'] = row['Description']            
                // Accumulate JSON results in a big string (bigstring). 
                // Doing this at once results in memory problems; known problem in JSON.stringify.
                tmp = JSON.stringify(lastResult, null, 2)
                if (bigstring === "") bigstring = tmp
                else bigstring = bigstring + ", " + tmp
            }
            
        })
         .on('end', function () {
            /*** show some progress ***/
            now = Date.now()
            time = (now-timestamp)/1000
            timestamp = now
            console.log(`${time} seconds to process ${counter} entries`)

            /*** dump to file to avoid memory exhaustion ***/
            const outfile = args.outputdir + "test_descriptions_tokenized_" + Date.now() + ".json";
            fs.writeFileSync(outfile, "[\n"+bigstring+"\n]", { flag: 'a+' });
        })

    console.log('Tokenized file ', file);
    cb();
  }, 1000);
}

let requests = files.reduce((promiseChain, item) => {
    return promiseChain.then(() => new Promise((resolve) => {
      asyncFunction(item, resolve);
    }));
}, Promise.resolve());
