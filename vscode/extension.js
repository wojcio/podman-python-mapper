const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('dml');
    context.subscriptions.push(diagnosticCollection);

    // Validate on save and open
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(doc => validateDocument(doc, diagnosticCollection))
    );
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(doc => validateDocument(doc, diagnosticCollection))
    );

    // Initial validation for open editors
    if (vscode.window.activeTextEditor) {
        validateDocument(vscode.window.activeTextEditor.document, diagnosticCollection);
    }
}

/**
 * @param {vscode.TextDocument} doc
 * @param {vscode.DiagnosticCollection} collection
 */
function validateDocument(doc, collection) {
    if (doc.languageId !== 'dml') return;

    const pythonPath = vscode.workspace.getConfiguration('dml').get('pythonPath') || 'python3';
    // We assume the parser.py is in the same workspace or we can find it
    // For this project, it is in ../src/parser.py relative to the extension in /vscode
    const parserPath = path.join(vscode.workspace.rootPath || '', 'src', 'parser.py');

    if (!fs.existsSync(parserPath)) {
        vscode.window.showWarningMessage('DML Parser (src/parser.py) not found in workspace. Validation disabled.');
        return;
    }

    const content = doc.getText();
    const tempFile = path.join(require('os').tmpdir(), 'vsc_dml_temp.map');
    fs.writeFileSync(tempFile, content);

    // Run the parser to check for syntax errors
    const proc = spawn(pythonPath, [parserPath, tempFile, '/dev/null']);
    let stderr = '';

    proc.stderr.on('data', (data) => {
        stderr += data.toString();
    });

    proc.on('close', (code) => {
        const diagnostics = [];
        if (code !== 0) {
            // Parse stderr for error message and line number
            // Typical format: SyntaxError: ... at position ...
            // Or Traceback ... File "...", line 123
            const lineMatch = stderr.match(/line (\d+)/);
            const msgMatch = stderr.match(/SyntaxError: (.*)/) || stderr.match(/Error: (.*)/);
            
            if (lineMatch && msgMatch) {
                const line = parseInt(lineMatch[1]) - 1;
                const range = new vscode.Range(line, 0, line, 100);
                diagnostics.push(new vscode.Diagnostic(range, msgMatch[1], vscode.DiagnosticSeverity.Error));
            } else if (msgMatch) {
                // Fallback to first line if line not found
                const range = new vscode.Range(0, 0, 0, 100);
                diagnostics.push(new vscode.Diagnostic(range, msgMatch[1], vscode.DiagnosticSeverity.Error));
            }
        }
        collection.set(doc.uri, diagnostics);
        fs.unlinkSync(tempFile);
    });
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
