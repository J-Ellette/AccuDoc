import * as vscode from 'vscode';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export function activate(context: vscode.ExtensionContext) {
    console.log('AccuDoc extension is now active');

    // Register commands
    let scanCommand = vscode.commands.registerCommand('accudoc.scan', async () => {
        await scanRepository();
    });

    let generateCommand = vscode.commands.registerCommand('accudoc.generate', async () => {
        await generateDocumentation();
    });

    let exportCommand = vscode.commands.registerCommand('accudoc.export', async () => {
        await exportDocumentation();
    });

    let searchCommand = vscode.commands.registerCommand('accudoc.search', async () => {
        await smartSearch();
    });

    let qualityCommand = vscode.commands.registerCommand('accudoc.quality', async () => {
        await analyzeQuality();
    });

    let settingsCommand = vscode.commands.registerCommand('accudoc.openSettings', () => {
        vscode.commands.executeCommand('workbench.action.openSettings', 'accudoc');
    });

    let refreshCommand = vscode.commands.registerCommand('accudoc.refreshExplorer', () => {
        vscode.window.showInformationMessage('AccuDoc: Refreshing documentation explorer...');
    });

    // Register providers
    const explorerProvider = new DocumentationExplorerProvider();
    vscode.window.registerTreeDataProvider('accudocExplorer', explorerProvider);

    const qualityProvider = new QualityMetricsProvider();
    vscode.window.registerTreeDataProvider('accudocQuality', qualityProvider);

    // Status bar
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(book) AccuDoc";
    statusBarItem.tooltip = "AccuDoc Documentation Generator";
    statusBarItem.command = 'accudoc.scan';
    statusBarItem.show();

    context.subscriptions.push(
        scanCommand,
        generateCommand,
        exportCommand,
        searchCommand,
        qualityCommand,
        settingsCommand,
        refreshCommand,
        statusBarItem
    );
}

async function getWorkspaceRoot(): Promise<string | undefined> {
    if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
        return vscode.workspace.workspaceFolders[0].uri.fsPath;
    }
    vscode.window.showErrorMessage('No workspace folder open');
    return undefined;
}

async function getPythonCommand(): Promise<string> {
    const config = vscode.workspace.getConfiguration('accudoc');
    const pythonPath = config.get<string>('pythonPath') || 'python';
    const cliPath = config.get<string>('cliPath');
    
    if (cliPath) {
        return `${pythonPath} "${cliPath}"`;
    }
    return `${pythonPath} -m accudoc`;
}

async function scanRepository() {
    const workspaceRoot = await getWorkspaceRoot();
    if (!workspaceRoot) return;

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "AccuDoc: Scanning repository...",
        cancellable: false
    }, async (progress) => {
        try {
            const pythonCmd = await getPythonCommand();
            const { stdout, stderr } = await execAsync(`${pythonCmd} scan "${workspaceRoot}"`);
            
            const outputChannel = vscode.window.createOutputChannel('AccuDoc');
            outputChannel.appendLine(stdout);
            if (stderr) outputChannel.appendLine(stderr);
            outputChannel.show();
            
            vscode.window.showInformationMessage('AccuDoc: Repository scan completed!');
        } catch (error: any) {
            vscode.window.showErrorMessage(`AccuDoc Error: ${error.message}`);
        }
    });
}

async function generateDocumentation() {
    const workspaceRoot = await getWorkspaceRoot();
    if (!workspaceRoot) return;

    const format = await vscode.window.showQuickPick(
        ['markdown', 'html', 'html-dark', 'text'],
        { placeHolder: 'Select output format' }
    );

    if (!format) return;

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "AccuDoc: Generating documentation...",
        cancellable: false
    }, async (progress) => {
        try {
            const pythonCmd = await getPythonCommand();
            const outputFile = path.join(workspaceRoot, `README_generated.${format === 'text' ? 'txt' : format === 'markdown' ? 'md' : 'html'}`);
            
            const { stdout, stderr } = await execAsync(
                `${pythonCmd} export "${workspaceRoot}" -o "${outputFile}" --format ${format}`
            );
            
            const outputChannel = vscode.window.createOutputChannel('AccuDoc');
            outputChannel.appendLine(stdout);
            if (stderr) outputChannel.appendLine(stderr);
            
            vscode.window.showInformationMessage(`Documentation generated: ${outputFile}`, 'Open')
                .then(selection => {
                    if (selection === 'Open') {
                        vscode.workspace.openTextDocument(outputFile).then(doc => {
                            vscode.window.showTextDocument(doc);
                        });
                    }
                });
        } catch (error: any) {
            vscode.window.showErrorMessage(`AccuDoc Error: ${error.message}`);
        }
    });
}

async function exportDocumentation() {
    await generateDocumentation();
}

async function smartSearch() {
    const workspaceRoot = await getWorkspaceRoot();
    if (!workspaceRoot) return;

    const query = await vscode.window.showInputBox({
        placeHolder: 'Enter search query',
        prompt: 'Search across documentation and source files'
    });

    if (!query) return;

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `AccuDoc: Searching for "${query}"...`,
        cancellable: false
    }, async (progress) => {
        try {
            const pythonCmd = await getPythonCommand();
            const { stdout, stderr } = await execAsync(
                `${pythonCmd} search "${workspaceRoot}" "${query}" --json`
            );
            
            const results = JSON.parse(stdout);
            
            if (results.matches && results.matches.length > 0) {
                const items = results.matches.map((match: any) => ({
                    label: match.path,
                    description: `Line ${match.line_number}`,
                    detail: match.line_content
                }));
                
                const selected = await vscode.window.showQuickPick(items, {
                    placeHolder: `Found ${results.matches.length} matches`
                });
                
                if (selected) {
                    const filePath = path.join(workspaceRoot, selected.label);
                    const doc = await vscode.workspace.openTextDocument(filePath);
                    const editor = await vscode.window.showTextDocument(doc);
                    const lineNumber = parseInt(selected.description!.split(' ')[1]) - 1;
                    const position = new vscode.Position(lineNumber, 0);
                    editor.selection = new vscode.Selection(position, position);
                    editor.revealRange(new vscode.Range(position, position));
                }
            } else {
                vscode.window.showInformationMessage('No matches found');
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`AccuDoc Error: ${error.message}`);
        }
    });
}

async function analyzeQuality() {
    const workspaceRoot = await getWorkspaceRoot();
    if (!workspaceRoot) return;

    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "AccuDoc: Analyzing quality...",
        cancellable: false
    }, async (progress) => {
        try {
            const pythonCmd = await getPythonCommand();
            const { stdout, stderr } = await execAsync(
                `${pythonCmd} quality-analyze "${workspaceRoot}" --format json`
            );
            
            const results = JSON.parse(stdout);
            
            const outputChannel = vscode.window.createOutputChannel('AccuDoc Quality');
            outputChannel.appendLine(`Quality Score: ${results.overall_score}/100`);
            outputChannel.appendLine(`Grade: ${results.grade}`);
            outputChannel.appendLine(`\nScores:`);
            outputChannel.appendLine(`  Clarity: ${results.scores.clarity}/100`);
            outputChannel.appendLine(`  Completeness: ${results.scores.completeness}/100`);
            outputChannel.appendLine(`  Accuracy: ${results.scores.accuracy}/100`);
            outputChannel.show();
            
            vscode.window.showInformationMessage(`Quality Score: ${results.overall_score}/100 (${results.grade})`);
        } catch (error: any) {
            vscode.window.showErrorMessage(`AccuDoc Error: ${error.message}`);
        }
    });
}

class DocumentationExplorerProvider implements vscode.TreeDataProvider<DocItem> {
    getTreeItem(element: DocItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: DocItem): Thenable<DocItem[]> {
        if (!element) {
            return Promise.resolve([
                new DocItem('Scan Repository', vscode.TreeItemCollapsibleState.None, 'accudoc.scan'),
                new DocItem('Generate Docs', vscode.TreeItemCollapsibleState.None, 'accudoc.generate'),
                new DocItem('Smart Search', vscode.TreeItemCollapsibleState.None, 'accudoc.search'),
                new DocItem('Quality Analysis', vscode.TreeItemCollapsibleState.None, 'accudoc.quality')
            ]);
        }
        return Promise.resolve([]);
    }
}

class QualityMetricsProvider implements vscode.TreeDataProvider<MetricItem> {
    getTreeItem(element: MetricItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: MetricItem): Thenable<MetricItem[]> {
        if (!element) {
            return Promise.resolve([
                new MetricItem('Overall Score', '--'),
                new MetricItem('Clarity', '--'),
                new MetricItem('Completeness', '--'),
                new MetricItem('Accuracy', '--')
            ]);
        }
        return Promise.resolve([]);
    }
}

class DocItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly command?: string
    ) {
        super(label, collapsibleState);
        if (command) {
            this.command = {
                command: command,
                title: label
            };
        }
    }
}

class MetricItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly value: string
    ) {
        super(`${label}: ${value}`, vscode.TreeItemCollapsibleState.None);
    }
}

export function deactivate() {}
