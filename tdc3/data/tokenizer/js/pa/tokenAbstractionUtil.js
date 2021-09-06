(function () {

    const jsExtractionUtil = require("../pa/jsExtractionUtil");

    function getOrCreateTokenStr(tokenMap, token, prefix) {
        const origTokenStr = jsExtractionUtil.tokenToString(token, true);
        let abstractTokenStr = tokenMap.get(origTokenStr);
        if (abstractTokenStr == undefined) {
            abstractTokenStr = prefix + (tokenMap.size + 1);
            tokenMap.set(origTokenStr, abstractTokenStr);
        }
        return abstractTokenStr;
    }

    function abstractIdsLits(tokenSeqs) {
        const idMap = new Map();
        const litMap = new Map();

        for (let seqIdx = 0; seqIdx < tokenSeqs.length; seqIdx++) {
            const tokens = tokenSeqs[seqIdx];
            for (let tokenIdx = 0; tokenIdx < tokens.length; tokenIdx++) {
                const token = tokens[tokenIdx];
                if (jsExtractionUtil.isId(token)) {
                    const abstractTokenStr = getOrCreateTokenStr(idMap, token, "ID");
                    token.value = abstractTokenStr;
                    tokens[tokenIdx] = token;
                } else if (jsExtractionUtil.isLit(token)) {
                    const abstractTokenStr = getOrCreateTokenStr(litMap, token, "LIT");
                    token.value = abstractTokenStr;
                    tokens[tokenIdx] = token;
                }
            }
        }
    }

    module.exports.abstractIdsLits = abstractIdsLits;

})();