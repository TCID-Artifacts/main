from tokenize import tokenize, ENCODING
import libcst as cst
import token as token_module
from io import BytesIO


def to_token_list(tokenizer):
    tokens = []
    for token in tokenizer:
        if token.type == token_module.NAME:
            if token.string == "True" or token.string == "False":
                tokens.append("LIT:" + token.string)
            else:
                tokens.append("ID:" + token.string)
        elif token.type == token_module.NUMBER:
            tokens.append("LIT:" + token.string)
        elif token.type == token_module.STRING:
            # remove quotes around string
            tokens.append("LIT:" + token.string[1:-1])
        elif token.type == ENCODING:
            continue
        else:
            tokens.append("STD:" + token.string)
    return tokens


def extract_tokens(file):
    with open(file, 'rb') as fp:
        tokenizer = tokenize(fp.readline)
        tokens = to_token_list(tokenizer)
    return [{"data": tokens, "metadata": {"file": file}}]


def extract_tokens_per_function(file, mask_name=False):
    results = []
    with open(file, "r") as fp:
        code = fp.read()
    tree = cst.parse_module(code)
    function_extractor = FunctionExtractor()
    tree.visit(function_extractor)
    for _, functionInfo in function_extractor.idToFunctionInfos.items():
        function = functionInfo.functionNode
        name = function.name.value
        if mask_name:
            function = function.with_deep_changes(function.name, value="MASKED")
        dummy_module = cst.parse_module("")
        code = dummy_module.code_for_node(function).strip()
        tokenizer = tokenize(BytesIO(code.encode('utf-8')).readline)
        tokens = to_token_list(tokenizer)
        results.append({"data": tokens,
                        "metadata": {
                            "file": file,
                            "name": name,
                            "nbCalls": functionInfo.nbCalls
                        }})
    return results


class FunctionExtractor(cst.CSTVisitor):
    def __init__(self):
        self.idToFunctionInfos = {}
        self.nextId = 1
        self.currentFunctionIds = []

    def visit_FunctionDef(self, node: cst.FunctionDef):
        self.idToFunctionInfos[self.nextId] = FunctionInfos(node)
        self.currentFunctionIds.append(self.nextId)
        self.nextId += 1

    def leave_FunctionDef(self, node: cst.FunctionDef):
        poppedId = self.currentFunctionIds.pop()
        assert self.idToFunctionInfos[poppedId].functionNode == node

    def visit_Call(self, node: cst.Call):
        if len(self.currentFunctionIds) > 0:
            currentId = self.currentFunctionIds[-1]
            self.idToFunctionInfos[currentId].nbCalls += 1


class FunctionInfos():
    def __init__(self, functionNode: cst.FunctionDef):
        self.functionNode = functionNode
        self.nbCalls = 0