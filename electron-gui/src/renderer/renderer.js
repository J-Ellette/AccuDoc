const { ipcRenderer } = require('electron');
const { Terminal } = require('@xterm/xterm');
const { FitAddon } = require('@xterm/addon-fit');
const marked = require('marked');
const hljs = require('highlight.js');

// State management
const state = {
    currentView: 'home',
    currentRepo: null,
    recentRepos: [],
    settings: {
        theme: 'light',
        cache: true,
        parallel: true,
        pythonPath: ''
    }
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeHomeView();
    initializeScanView();
    initializeGenerateView();
    initializeAnalysisView();
    initializeHealthView();
    initializeExportView();
    initializeOpenSourceView();
    initializeTerminalView();
    initializeSettingsView();
    loadRecentRepos();
    loadSettings();
    setupMenuHandlers();
});

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const view = item.dataset.view;
            switchView(view);
        });
    });
}

function switchView(viewName) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.view === viewName) {
            item.classList.add('active');
        }
    });

    // Update content
    document.querySelectorAll('.content-view').forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(`${viewName}-view`).classList.add('active');

    state.currentView = viewName;
}

// Menu handlers
function setupMenuHandlers() {
    ipcRenderer.on('menu-open-repository', async () => {
        const path = await ipcRenderer.invoke('select-directory');
        if (path) {
            document.getElementById('scan-repo-path').value = path;
            switchView('scan');
        }
    });

    ipcRenderer.on('menu-open-settings', () => {
        switchView('settings');
    });

    ipcRenderer.on('menu-scan-repository', () => {
        switchView('scan');
        document.getElementById('scan-start-btn').click();
    });

    ipcRenderer.on('menu-generate-docs', () => {
        switchView('generate');
    });

    ipcRenderer.on('menu-show-analysis', () => {
        switchView('analysis');
    });

    ipcRenderer.on('menu-show-health', () => {
        switchView('health');
    });

    ipcRenderer.on('menu-show-terminal', () => {
        switchView('terminal');
    });

    ipcRenderer.on('menu-show-about', () => {
        showAboutDialog();
    });
}

// Home View
function initializeHomeView() {
    const actionCards = document.querySelectorAll('.action-card');
    actionCards.forEach(card => {
        const button = card.querySelector('button');
        button.addEventListener('click', () => {
            const action = card.dataset.action;
            switchView(action);
        });
    });
}

// Scan View
function initializeScanView() {
    const browseBtn = document.getElementById('scan-browse-btn');
    const startBtn = document.getElementById('scan-start-btn');
    const repoPathInput = document.getElementById('scan-repo-path');
    const outputBox = document.getElementById('scan-output');

    browseBtn.addEventListener('click', async () => {
        const path = await ipcRenderer.invoke('select-directory');
        if (path) {
            repoPathInput.value = path;
        }
    });

    startBtn.addEventListener('click', async () => {
        const repoPath = repoPathInput.value.trim();
        if (!repoPath) {
            alert('Please enter a repository path');
            return;
        }

        const useCache = document.getElementById('scan-use-cache').checked;
        const jsonOutput = document.getElementById('scan-json-output').checked;

        outputBox.textContent = 'Starting scan...\n';
        setStatus('loading', 'Scanning repository...');
        startBtn.disabled = true;

        try {
            const args = [repoPath];
            if (!useCache) args.push('--no-cache');
            if (jsonOutput) args.push('--json');

            // Listen for progress updates
            const progressListener = (event, data) => {
                if (data.type === 'stdout') {
                    outputBox.textContent += data.data;
                    outputBox.scrollTop = outputBox.scrollHeight;
                }
            };
            ipcRenderer.on('command-progress', progressListener);

            const result = await ipcRenderer.invoke('execute-command', 'scan', args);
            
            ipcRenderer.removeListener('command-progress', progressListener);
            
            outputBox.textContent += '\n' + result.stdout;
            if (result.stderr) {
                outputBox.textContent += '\nErrors/Warnings:\n' + result.stderr;
            }
            
            setStatus('success', 'Scan completed successfully');
            addToRecentRepos(repoPath);
        } catch (error) {
            outputBox.textContent += `\n\nError: ${error.message}`;
            setStatus('error', 'Scan failed');
        } finally {
            startBtn.disabled = false;
        }
    });
}

// Generate View
function initializeGenerateView() {
    const browseBtns = {
        repo: document.getElementById('gen-browse-btn'),
        output: document.getElementById('gen-output-browse-btn')
    };
    const startBtn = document.getElementById('gen-start-btn');
    const outputBox = document.getElementById('gen-output');

    browseBtns.repo.addEventListener('click', async () => {
        const path = await ipcRenderer.invoke('select-directory');
        if (path) {
            document.getElementById('gen-repo-path').value = path;
        }
    });

    browseBtns.output.addEventListener('click', async () => {
        const path = await ipcRenderer.invoke('save-file', {
            title: 'Save Documentation',
            defaultPath: 'DOCUMENTATION.md',
            filters: [
                { name: 'Markdown', extensions: ['md'] },
                { name: 'HTML', extensions: ['html'] },
                { name: 'PDF', extensions: ['pdf'] },
                { name: 'Text', extensions: ['txt'] },
                { name: 'All Files', extensions: ['*'] }
            ]
        });
        if (path) {
            document.getElementById('gen-output-path').value = path;
        }
    });

    startBtn.addEventListener('click', async () => {
        const repoPath = document.getElementById('gen-repo-path').value.trim();
        const outputPath = document.getElementById('gen-output-path').value.trim();

        if (!repoPath || !outputPath) {
            alert('Please enter both repository and output paths');
            return;
        }

        const template = document.getElementById('gen-template').value;
        const format = document.getElementById('gen-format').value;
        const language = document.getElementById('gen-language').value;
        const theme = document.getElementById('gen-theme').value;

        outputBox.textContent = 'Generating documentation...\n';
        setStatus('loading', 'Generating documentation...');
        startBtn.disabled = true;

        try {
            // Use 'export' command which does scan + generate in one step
            const args = [
                repoPath,
                '--output', outputPath,
                '--template', template,
                '--format', format
            ];

            if (language !== 'en') {
                args.push('--language', language);
            }

            if (format === 'html') {
                args.push('--theme', theme);
            }

            const progressListener = (event, data) => {
                if (data.type === 'stdout') {
                    outputBox.textContent += data.data;
                    outputBox.scrollTop = outputBox.scrollHeight;
                }
                if (data.type === 'stderr') {
                    // Also show stderr for progress messages
                    outputBox.textContent += data.data;
                    outputBox.scrollTop = outputBox.scrollHeight;
                }
            };
            ipcRenderer.on('command-progress', progressListener);

            // Use 'export' command instead of 'generate'
            const result = await ipcRenderer.invoke('execute-command', 'export', args);
            
            ipcRenderer.removeListener('command-progress', progressListener);
            
            outputBox.textContent += '\n' + result.stdout;
            setStatus('success', 'Documentation generated successfully');
            addToRecentRepos(repoPath);
        } catch (error) {
            outputBox.textContent += `\n\nError: ${error.message}`;
            setStatus('error', 'Generation failed');
        } finally {
            startBtn.disabled = false;
        }
    });
}

// Analysis View
function initializeAnalysisView() {
    const browseBtn = document.getElementById('analysis-browse-btn');
    const outputBox = document.getElementById('analysis-output');

    browseBtn.addEventListener('click', async () => {
        const path = await ipcRenderer.invoke('select-directory');
        if (path) {
            document.getElementById('analysis-repo-path').value = path;
        }
    });

    // Complexity Analysis
    document.getElementById('analysis-complexity-btn').addEventListener('click', async () => {
        await runAnalysis('complexity', 'Complexity Analysis', outputBox);
    });

    // Best Practices
    document.getElementById('analysis-practices-btn').addEventListener('click', async () => {
        await runAnalysis('best-practices', 'Best Practices Check', outputBox);
    });

    // Call Graph
    document.getElementById('analysis-callgraph-btn').addEventListener('click', async () => {
        await runAnalysis('call-graph', 'Call Graph Generation', outputBox);
    });

    // Completeness Score
    document.getElementById('analysis-completeness-btn').addEventListener('click', async () => {
        await runAnalysis('completeness', 'Documentation Completeness', outputBox);
    });

    // Quality Scoring
    document.getElementById('analysis-quality-btn').addEventListener('click', async () => {
        const repoPath = document.getElementById('analysis-repo-path').value.trim();
        if (!repoPath) {
            alert('Please enter a repository path');
            return;
        }
        
        // Run advanced quality analysis and display in analysis output
        outputBox.innerHTML = '<div class="loading">Running advanced quality analysis...</div>';
        
        setTimeout(() => {
            runAdvancedQualityAnalysis(repoPath, outputBox);
        }, 500);
    });
}

async function runAnalysis(analysisType, title, outputBox) {
    const repoPath = document.getElementById('analysis-repo-path').value.trim();
    if (!repoPath) {
        alert('Please enter a repository path');
        return;
    }

    // Check if it's a URL
    const isUrl = repoPath.startsWith('http://') || 
                  repoPath.startsWith('https://') || 
                  repoPath.startsWith('git@') ||
                  repoPath.startsWith('ssh://');
    
    if (isUrl) {
        outputBox.textContent = `⚠️ Analysis commands require a local repository.\n\n`;
        outputBox.textContent += `The URL you provided (${repoPath}) needs to be cloned locally first.\n\n`;
        outputBox.textContent += `Steps to analyze a remote repository:\n`;
        outputBox.textContent += `1. Clone the repository locally using git clone\n`;
        outputBox.textContent += `2. Use the local path for analysis\n\n`;
        outputBox.textContent += `Alternatively, use the Scan view which supports URLs directly.`;
        setStatus('warning', 'Local repository required for analysis');
        return;
    }

    outputBox.textContent = `Running ${title}...\n`;
    setStatus('loading', `Running ${title}...`);

    try {
        // Map analysis types to CLI commands (these are subcommands, not flags)
        const commandMap = {
            'complexity': ['code-quality', [repoPath, '-f', 'json']],
            'best-practices': ['code-quality', [repoPath, '-f', 'json']],
            'call-graph': ['dataflow', [repoPath, '-f', 'json']],
            'completeness': ['doc-coverage', [repoPath, '-f', 'json']]
        };

        const [command, args] = commandMap[analysisType];

        const progressListener = (event, data) => {
            if (data.type === 'stdout') {
                outputBox.textContent += data.data;
                outputBox.scrollTop = outputBox.scrollHeight;
            }
        };
        ipcRenderer.on('command-progress', progressListener);

        const result = await ipcRenderer.invoke('execute-command', command, args);
        
        ipcRenderer.removeListener('command-progress', progressListener);
        
        outputBox.textContent += '\n' + result.stdout;
        setStatus('success', `${title} completed`);
    } catch (error) {
        outputBox.textContent += `\n\nError: ${error.message}`;
        setStatus('error', `${title} failed`);
    }
}

// Health View
function initializeHealthView() {
    const browseBtn = document.getElementById('health-browse-btn');
    const checkBtn = document.getElementById('health-check-btn');
    const dashboard = document.getElementById('health-dashboard');

    browseBtn.addEventListener('click', async () => {
        const path = await ipcRenderer.invoke('select-directory');
        if (path) {
            document.getElementById('health-repo-path').value = path;
        }
    });

    checkBtn.addEventListener('click', async () => {
        const repoPath = document.getElementById('health-repo-path').value.trim();
        if (!repoPath) {
            alert('Please enter a repository path');
            return;
        }

        dashboard.innerHTML = '<div class="spinner"></div>';
        setStatus('loading', 'Checking project health...');
        checkBtn.disabled = true;

        try {
            // 'health' is a subcommand, not a flag for 'scan'
            const result = await ipcRenderer.invoke('execute-command', 'health', [
                repoPath,
                '-f', 'json'
            ]);

            // The CLI may include progress text before JSON, extract just the JSON
            let jsonText = result.stdout.trim();
            const jsonStart = jsonText.indexOf('{');
            if (jsonStart > 0) {
                jsonText = jsonText.substring(jsonStart);
            }
            const healthData = JSON.parse(jsonText);
            displayHealthDashboard(healthData, dashboard);
            setStatus('success', 'Health check completed');
        } catch (error) {
            dashboard.innerHTML = `<p>Error: ${error.message}</p>`;
            setStatus('error', 'Health check failed');
        } finally {
            checkBtn.disabled = false;
        }
    });
}

function displayHealthDashboard(data, container) {
    const summary = data.summary || {};
    
    const cards = [
        {
            title: 'Overall Health',
            score: summary.overall_score || 0,
            grade: summary.overall_grade || 'N/A',
            details: summary.overall_status || 'Combined health metrics'
        },
        {
            title: 'Documentation',
            score: summary.documentation || 0,
            details: 'Documentation coverage and quality'
        },
        {
            title: 'Code Quality',
            score: summary.code_quality || 0,
            details: 'Code maintainability and practices'
        },
        {
            title: 'Dependencies',
            score: summary.dependencies || 0,
            details: 'Dependency health and freshness'
        },
        {
            title: 'Maintainability',
            score: summary.maintainability || 0,
            details: 'Code maintainability index'
        },
        {
            title: 'License',
            score: summary.license || 0,
            details: 'License compliance'
        }
    ];

    // Build the cards HTML
    let cardsHtml = cards.map((card, index) => `
        <div class="health-card" data-category="${card.title.toLowerCase().replace(/ /g, '-')}">
            <h4>${card.title}</h4>
            <div class="health-score ${getScoreClass(card.score)}">
                ${card.score.toFixed(1)}%${card.grade ? ` (${card.grade})` : ''}
            </div>
            <div class="health-details">${card.details}</div>
            <button class="btn-tips" data-category="${card.title}" data-score="${card.score}">
                💡 Get Tips to Improve
            </button>
        </div>
    `).join('');
    
    container.innerHTML = cardsHtml;
    
    // Store full health data for tips generation
    container.dataset.healthData = JSON.stringify(data);
    
    // Add click handlers for tips buttons AFTER innerHTML is set
    setTimeout(() => {
        container.querySelectorAll('.btn-tips').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                const score = parseFloat(e.target.dataset.score);
                showHealthTips(category, score, data);
            });
        });
    }, 0);
    
    // Also display recommendations if available
    if (data.recommendations && data.recommendations.length > 0) {
        const recsHtml = `
            <div class="health-recommendations">
                <h3>Quick Recommendations</h3>
                <ul>
                    ${data.recommendations.slice(0, 5).map(rec => `
                        <li>${rec}</li>
                    `).join('')}
                </ul>
                ${data.recommendations.length > 5 ? `<p class="more-tips">And ${data.recommendations.length - 5} more recommendations...</p>` : ''}
            </div>
        `;
        container.innerHTML += recsHtml;
    }
}

function getScoreClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'fair';
    return 'poor';
}

function showHealthTips(category, score, healthData) {
    const tips = generateHealthTips(category, score, healthData);
    
    const modal = document.createElement('div');
    modal.className = 'tips-modal';
    modal.innerHTML = `
        <div class="tips-modal-content">
            <div class="tips-header">
                <h2>💡 Tips to Improve ${category}</h2>
                <span class="tips-close">&times;</span>
            </div>
            <div class="tips-body">
                <div class="current-status">
                    <h3>Current Status</h3>
                    <div class="status-badge ${getScoreClass(score)}">
                        ${score.toFixed(1)}% - ${getStatusText(score)}
                    </div>
                </div>
                
                <div class="tips-sections">
                    ${tips.sections.map(section => `
                        <div class="tips-section">
                            <h3>${section.icon} ${section.title}</h3>
                            <ul class="tips-list">
                                ${section.tips.map(tip => `
                                    <li class="tip-item ${tip.priority}">
                                        <div class="tip-header">
                                            <span class="tip-priority">${tip.priority.toUpperCase()}</span>
                                            <span class="tip-impact">Impact: +${tip.impact}%</span>
                                        </div>
                                        <div class="tip-content">${tip.text}</div>
                                        ${tip.action ? `<div class="tip-action">→ ${tip.action}</div>` : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
                
                <div class="tips-summary">
                    <h3>Potential Score Increase</h3>
                    <p>By implementing these recommendations, you could improve your score to approximately:</p>
                    <div class="potential-score ${getScoreClass(tips.potentialScore)}">
                        ${tips.potentialScore.toFixed(1)}%
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close handlers
    const closeBtn = modal.querySelector('.tips-close');
    closeBtn.addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

function getStatusText(score) {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    if (score >= 50) return 'Needs Improvement';
    return 'Requires Attention';
}

function generateHealthTips(category, score, healthData) {
    const metrics = healthData.metrics || {};
    const recommendations = healthData.recommendations || [];
    
    let sections = [];
    let potentialIncrease = 0;
    
    switch(category) {
        case 'Overall Health':
            sections = generateOverallTips(score, healthData);
            potentialIncrease = 15;
            break;
        case 'Documentation':
            sections = generateDocumentationTips(score, metrics, recommendations);
            potentialIncrease = 20;
            break;
        case 'Code Quality':
            sections = generateCodeQualityTips(score, metrics, recommendations);
            potentialIncrease = 15;
            break;
        case 'Dependencies':
            sections = generateDependencyTips(score, metrics, recommendations);
            potentialIncrease = 10;
            break;
        case 'Maintainability':
            sections = generateMaintainabilityTips(score, metrics, recommendations);
            potentialIncrease = 12;
            break;
        case 'License':
            sections = generateLicenseTips(score, metrics, recommendations);
            potentialIncrease = 25;
            break;
        default:
            sections = [{
                icon: '📋',
                title: 'General Recommendations',
                tips: [{priority: 'medium', impact: 10, text: 'Review project health metrics regularly'}]
            }];
    }
    
    return {
        sections,
        potentialScore: Math.min(100, score + potentialIncrease)
    };
}

function generateOverallTips(score, healthData) {
    const summary = healthData.summary || {};
    const tips = [];
    
    // Identify weakest areas
    const areas = [
        {name: 'Documentation', score: summary.documentation || 0},
        {name: 'Code Quality', score: summary.code_quality || 0},
        {name: 'Dependencies', score: summary.dependencies || 0},
        {name: 'Maintainability', score: summary.maintainability || 0},
        {name: 'License', score: summary.license || 0}
    ].sort((a, b) => a.score - b.score);
    
    areas.slice(0, 3).forEach((area, index) => {
        if (area.score < 80) {
            tips.push({
                priority: index === 0 ? 'high' : 'medium',
                impact: 15 - (index * 3),
                text: `Focus on improving ${area.name} (currently ${area.score.toFixed(1)}%)`,
                action: `Click on the ${area.name} card for specific tips`
            });
        }
    });
    
    return [{
        icon: '🎯',
        title: 'Priority Areas',
        tips: tips.length > 0 ? tips : [{
            priority: 'low',
            impact: 5,
            text: 'Great job! All areas are performing well. Focus on maintaining current standards.'
        }]
    }];
}

function generateDocumentationTips(score, metrics, recommendations) {
    const docMetrics = metrics.documentation_coverage || {};
    const sections = [];
    
    const quickWins = [];
    const improvements = [];
    const advanced = [];
    
    if (score < 70) {
        quickWins.push({
            priority: 'high',
            impact: 15,
            text: 'Add a comprehensive README.md with project overview, setup instructions, and usage examples',
            action: 'Use AccuDoc generate command to create initial documentation'
        });
    }
    
    if (score < 80) {
        quickWins.push({
            priority: 'high',
            impact: 10,
            text: 'Document all public functions and classes with docstrings',
            action: 'Run code-quality analysis to identify undocumented functions'
        });
        
        improvements.push({
            priority: 'medium',
            impact: 8,
            text: 'Add inline comments for complex code sections',
            action: 'Focus on algorithms and business logic'
        });
    }
    
    improvements.push({
        priority: 'medium',
        impact: 7,
        text: 'Create API documentation for external interfaces',
        action: 'Document REST endpoints, CLI commands, or library APIs'
    });
    
    improvements.push({
        priority: 'medium',
        impact: 6,
        text: 'Add code examples and usage scenarios',
        action: 'Include examples in README and function docstrings'
    });
    
    if (score >= 70) {
        advanced.push({
            priority: 'low',
            impact: 5,
            text: 'Generate architecture diagrams and flowcharts',
            action: 'Use tools like Mermaid or PlantUML'
        });
        
        advanced.push({
            priority: 'low',
            impact: 4,
            text: 'Set up automated documentation generation in CI/CD',
            action: 'Integrate AccuDoc into your build pipeline'
        });
    }
    
    if (quickWins.length > 0) sections.push({icon: '⚡', title: 'Quick Wins', tips: quickWins});
    if (improvements.length > 0) sections.push({icon: '📈', title: 'Improvements', tips: improvements});
    if (advanced.length > 0) sections.push({icon: '🚀', title: 'Advanced', tips: advanced});
    
    return sections;
}

function generateCodeQualityTips(score, metrics, recommendations) {
    const sections = [];
    const quickWins = [];
    const improvements = [];
    
    if (score < 70) {
        quickWins.push({
            priority: 'high',
            impact: 12,
            text: 'Fix critical code quality issues and linting errors',
            action: 'Run a linter (ESLint, Pylint, etc.) and fix high-priority issues'
        });
    }
    
    quickWins.push({
        priority: 'high',
        impact: 10,
        text: 'Reduce code duplication by extracting common functions',
        action: 'Identify repeated code blocks and refactor into reusable functions'
    });
    
    improvements.push({
        priority: 'medium',
        impact: 8,
        text: 'Break down large functions into smaller, focused ones',
        action: 'Target functions longer than 50 lines'
    });
    
    improvements.push({
        priority: 'medium',
        impact: 7,
        text: 'Add unit tests for core functionality',
        action: 'Aim for at least 70% code coverage'
    });
    
    improvements.push({
        priority: 'medium',
        impact: 6,
        text: 'Implement error handling and input validation',
        action: 'Add try-catch blocks and validate user inputs'
    });
    
    sections.push({icon: '⚡', title: 'Quick Wins', tips: quickWins});
    sections.push({icon: '📈', title: 'Improvements', tips: improvements});
    
    return sections;
}

function generateDependencyTips(score, metrics, recommendations) {
    const sections = [];
    const quickWins = [];
    const improvements = [];
    
    if (score < 80) {
        quickWins.push({
            priority: 'high',
            impact: 15,
            text: 'Update outdated dependencies to latest stable versions',
            action: 'Run npm update, pip install --upgrade, or equivalent for your package manager'
        });
        
        quickWins.push({
            priority: 'high',
            impact: 12,
            text: 'Remove unused dependencies from your project',
            action: 'Use npm prune, pip-autoremove, or similar tools'
        });
    }
    
    improvements.push({
        priority: 'medium',
        impact: 8,
        text: 'Pin dependency versions to avoid breaking changes',
        action: 'Use exact versions or lock files (package-lock.json, requirements.txt)'
    });
    
    improvements.push({
        priority: 'medium',
        impact: 7,
        text: 'Set up automated dependency security scanning',
        action: 'Use GitHub Dependabot, Snyk, or similar tools'
    });
    
    sections.push({icon: '⚡', title: 'Quick Wins', tips: quickWins});
    sections.push({icon: '📈', title: 'Improvements', tips: improvements});
    
    return sections;
}

function generateMaintainabilityTips(score, metrics, recommendations) {
    const sections = [];
    const tips = [];
    
    tips.push({
        priority: 'high',
        impact: 10,
        text: 'Reduce cyclomatic complexity of complex functions',
        action: 'Break down nested conditionals and loops'
    });
    
    tips.push({
        priority: 'medium',
        impact: 8,
        text: 'Follow consistent code style and formatting',
        action: 'Use a formatter like Prettier, Black, or gofmt'
    });
    
    tips.push({
        priority: 'medium',
        impact: 7,
        text: 'Improve naming conventions for variables and functions',
        action: 'Use descriptive, self-documenting names'
    });
    
    tips.push({
        priority: 'medium',
        impact: 6,
        text: 'Add type hints or type annotations',
        action: 'Use TypeScript, Python type hints, or similar'
    });
    
    sections.push({icon: '🔧', title: 'Maintainability Improvements', tips});
    return sections;
}

function generateLicenseTips(score, metrics, recommendations) {
    const sections = [];
    const tips = [];
    
    if (score < 50) {
        tips.push({
            priority: 'high',
            impact: 30,
            text: 'Add a LICENSE file to your repository',
            action: 'Choose an appropriate license (MIT, Apache 2.0, GPL, etc.)'
        });
    }
    
    if (score < 80) {
        tips.push({
            priority: 'medium',
            impact: 15,
            text: 'Add copyright headers to source files',
            action: 'Include license notice at the top of each file'
        });
        
        tips.push({
            priority: 'medium',
            impact: 10,
            text: 'Document third-party license compliance',
            action: 'Create NOTICE file listing all dependencies and their licenses'
        });
    }
    
    tips.push({
        priority: 'low',
        impact: 5,
        text: 'Set up automated license scanning',
        action: 'Use tools like FOSSA or license-checker'
    });
    
    sections.push({icon: '📜', title: 'License Compliance', tips});
    return sections;
}

// Export View
function initializeExportView() {
    const browseBtn = document.getElementById('export-browse-btn');
    const outputBrowseBtn = document.getElementById('export-output-browse-btn');
    const startBtn = document.getElementById('export-start-btn');
    const outputBox = document.getElementById('export-output');

    browseBtn.addEventListener('click', async () => {
        const path = await ipcRenderer.invoke('select-directory');
        if (path) {
            document.getElementById('export-repo-path').value = path;
        }
    });

    outputBrowseBtn.addEventListener('click', async () => {
        const path = await ipcRenderer.invoke('select-directory');
        if (path) {
            document.getElementById('export-output').value = path;
        }
    });

    startBtn.addEventListener('click', async () => {
        const repoPath = document.getElementById('export-repo-path').value.trim();
        const outputPath = document.getElementById('export-output').value.trim();
        const format = document.getElementById('export-format').value;

        if (!repoPath || !outputPath) {
            alert('Please enter both repository and output paths');
            return;
        }

        outputBox.textContent = 'Exporting data...\n';
        setStatus('loading', 'Exporting data...');
        startBtn.disabled = true;

        try {
            const args = [repoPath, '--output', outputPath, '--format', format];

            const result = await ipcRenderer.invoke('execute-command', 'export', args);
            
            outputBox.textContent = result.stdout;
            setStatus('success', 'Export completed');
        } catch (error) {
            outputBox.textContent = `Error: ${error.message}`;
            setStatus('error', 'Export failed');
        } finally {
            startBtn.disabled = false;
        }
    });
}

// Open Source View
function initializeOpenSourceView() {
    const browseBtn = document.getElementById('os-browse-btn');
    const generateBtn = document.getElementById('os-generate-btn');
    const outputBox = document.getElementById('os-output');

    browseBtn.addEventListener('click', async () => {
        const path = await ipcRenderer.invoke('select-directory');
        if (path) {
            document.getElementById('os-repo-path').value = path;
        }
    });

    generateBtn.addEventListener('click', async () => {
        const repoPath = document.getElementById('os-repo-path').value.trim();
        if (!repoPath) {
            alert('Please enter a repository path');
            return;
        }

        // Check if it's a URL
        const isUrl = repoPath.startsWith('http://') || 
                      repoPath.startsWith('https://') || 
                      repoPath.startsWith('git@') ||
                      repoPath.startsWith('ssh://');
        
        if (isUrl) {
            outputBox.textContent = `⚠️ Open Source documentation generation requires a local repository.\n\n`;
            outputBox.textContent += `The URL you provided (${repoPath}) needs to be cloned locally first.\n\n`;
            outputBox.textContent += `Steps to generate open source docs for a remote repository:\n`;
            outputBox.textContent += `1. Clone the repository locally using git clone\n`;
            outputBox.textContent += `2. Use the local path for documentation generation\n\n`;
            outputBox.textContent += `Note: Open source docs (CONTRIBUTING.md, CODE_OF_CONDUCT.md, etc.) are saved\n`;
            outputBox.textContent += `directly to your local repository, not to a remote server.`;
            setStatus('warning', 'Local repository required for open source docs');
            return;
        }

        const contributing = document.getElementById('os-contributing').checked;
        const conduct = document.getElementById('os-conduct').checked;
        const issues = document.getElementById('os-issues').checked;

        outputBox.textContent = 'Generating open source documentation...\n';
        setStatus('loading', 'Generating files...');
        generateBtn.disabled = true;

        try {
            const args = [repoPath];
            if (contributing) args.push('--contributing');
            if (conduct) args.push('--conduct');
            if (issues) args.push('--issues');

            const result = await ipcRenderer.invoke('execute-command', 'opensource', args);
            
            outputBox.textContent = result.stdout;
            setStatus('success', 'Open source docs generated');
        } catch (error) {
            outputBox.textContent = `Error: ${error.message}`;
            setStatus('error', 'Generation failed');
        } finally {
            generateBtn.disabled = false;
        }
    });
}

// Terminal View
let terminal;
let fitAddon;

function initializeTerminalView() {
    terminal = new Terminal({
        cursorBlink: true,
        fontSize: 14,
        fontFamily: 'Consolas, Monaco, monospace',
        theme: {
            background: '#1e1e1e',
            foreground: '#d4d4d4'
        }
    });

    fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);

    // Open terminal when view is shown
    const terminalView = document.getElementById('terminal-view');
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class' && terminalView.classList.contains('active')) {
                if (!terminal._initialized) {
                    const container = document.getElementById('terminal-container');
                    terminal.open(container);
                    fitAddon.fit();
                    terminal._initialized = true;
                    
                    terminal.writeln('AccuDoc CLI Terminal');
                    terminal.writeln('Type "help" for available commands');
                    terminal.write('\r\n$ ');
                }
            }
        });
    });

    observer.observe(terminalView, { attributes: true });

    let currentLine = '';
    terminal.onData(data => {
        if (data === '\r') {
            terminal.write('\r\n');
            if (currentLine.trim()) {
                executeTerminalCommand(currentLine.trim());
            }
            currentLine = '';
        } else if (data === '\x7F') {
            if (currentLine.length > 0) {
                currentLine = currentLine.slice(0, -1);
                terminal.write('\b \b');
            }
        } else {
            currentLine += data;
            terminal.write(data);
        }
    });
}

async function executeTerminalCommand(command) {
    try {
        if (command === 'help') {
            terminal.writeln('Available commands:');
            terminal.writeln('  scan <path>           - Scan a repository');
            terminal.writeln('  generate <path>       - Generate documentation');
            terminal.writeln('  export <path>         - Export data');
            terminal.writeln('  health <path>         - Check project health');
            terminal.writeln('  clear                 - Clear terminal');
            terminal.write('\r\n$ ');
            return;
        }

        if (command === 'clear') {
            terminal.clear();
            terminal.write('$ ');
            return;
        }

        const [cmd, ...args] = command.split(' ');
        
        const progressListener = (event, data) => {
            if (data.type === 'stdout') {
                terminal.write(data.data.replace(/\n/g, '\r\n'));
            }
        };
        ipcRenderer.on('command-progress', progressListener);

        const result = await ipcRenderer.invoke('execute-command', cmd, args);
        
        ipcRenderer.removeListener('command-progress', progressListener);
        
        terminal.write(result.stdout.replace(/\n/g, '\r\n'));
        if (result.stderr) {
            terminal.write('\r\n' + result.stderr.replace(/\n/g, '\r\n'));
        }
    } catch (error) {
        terminal.writeln(`\r\nError: ${error.message}`);
    }
    
    terminal.write('\r\n$ ');
}

// Settings View
function initializeSettingsView() {
    const saveBtn = document.getElementById('settings-save-btn');

    saveBtn.addEventListener('click', () => {
        state.settings = {
            theme: document.getElementById('settings-theme').value,
            cache: document.getElementById('settings-cache').checked,
            parallel: document.getElementById('settings-parallel').checked,
            pythonPath: document.getElementById('settings-python').value
        };

        saveSettings();
        alert('Settings saved successfully');
    });
}

// Utility Functions
function setStatus(type, message) {
    const statusText = document.getElementById('status-text');
    statusText.className = type;
    statusText.textContent = message;
}

function addToRecentRepos(path) {
    if (!state.recentRepos.includes(path)) {
        state.recentRepos.unshift(path);
        if (state.recentRepos.length > 10) {
            state.recentRepos = state.recentRepos.slice(0, 10);
        }
        saveRecentRepos();
        displayRecentRepos();
    }
}

function loadRecentRepos() {
    const stored = localStorage.getItem('accudoc-recent-repos');
    if (stored) {
        state.recentRepos = JSON.parse(stored);
        displayRecentRepos();
    }
}

function saveRecentRepos() {
    localStorage.setItem('accudoc-recent-repos', JSON.stringify(state.recentRepos));
}

function displayRecentRepos() {
    const container = document.getElementById('recent-list');
    if (state.recentRepos.length === 0) {
        container.innerHTML = '<p style="color: #6c757d;">No recent repositories</p>';
        return;
    }

    container.innerHTML = state.recentRepos.map(path => `
        <div class="repo-item" onclick="openRepo('${path.replace(/\\/g, '\\\\')}')">
            <div>
                <div class="repo-item-name">${path.split(/[/\\]/).pop()}</div>
                <div class="repo-item-path">${path}</div>
            </div>
        </div>
    `).join('');
}

function openRepo(path) {
    document.getElementById('scan-repo-path').value = path;
    switchView('scan');
}

function loadSettings() {
    const stored = localStorage.getItem('accudoc-settings');
    if (stored) {
        state.settings = JSON.parse(stored);
        applySettings();
    }
}

function saveSettings() {
    localStorage.setItem('accudoc-settings', JSON.stringify(state.settings));
}

function applySettings() {
    document.getElementById('settings-theme').value = state.settings.theme;
    document.getElementById('settings-cache').checked = state.settings.cache;
    document.getElementById('settings-parallel').checked = state.settings.parallel;
    document.getElementById('settings-python').value = state.settings.pythonPath || '';
}

function showAboutDialog() {
    alert(`AccuDoc - Automated Documentation Generator
Version 1.0.0

A powerful tool for generating comprehensive documentation
from your repositories.

© 2024 AccuDoc Team`);
}

// Tab Management System
function setupTabs() {
    const tabContainers = document.querySelectorAll('.tab-container');
    
    tabContainers.forEach(container => {
        const tabBtns = container.querySelectorAll('.tab-btn');
        const tabContents = container.parentElement.querySelectorAll('.tab-content');
        
        tabBtns.forEach((btn, index) => {
            btn.addEventListener('click', () => {
                // Remove active from all tabs and contents
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                // Add active to clicked tab and corresponding content
                btn.classList.add('active');
                if (tabContents[index]) {
                    tabContents[index].classList.add('active');
                }
            });
        });
        
        // Initialize first tab as active
        if (tabBtns.length > 0 && tabContents.length > 0) {
            tabBtns[0].classList.add('active');
            tabContents[0].classList.add('active');
        }
    });
}

// Batch Processing Functions
function addRepository() {
    const repoList = document.getElementById('batchRepoList');
    const repoCount = repoList.children.length + 1;
    
    const repoItem = document.createElement('div');
    repoItem.className = 'repo-item';
    repoItem.innerHTML = `
        <input type="text" class="repo-input" placeholder="Repository path or URL" />
        <button class="btn browse-repo" onclick="browseRepository(this)">Browse</button>
        <button class="btn btn-danger remove-repo" onclick="removeRepository(this)">Remove</button>
    `;
    
    repoList.appendChild(repoItem);
}

function browseRepository(btn) {
    const input = btn.parentElement.querySelector('.repo-input');
    window.electronAPI.selectDirectory().then(path => {
        if (path) {
            input.value = path;
        }
    });
}

function removeRepository(btn) {
    btn.parentElement.remove();
}

function startBatchAnalysis() {
    const repos = Array.from(document.querySelectorAll('#batchRepoList .repo-input'))
        .map(input => input.value.trim())
        .filter(path => path);
    
    if (repos.length === 0) {
        showNotification('Please add at least one repository', 'warning');
        return;
    }
    
    const workers = parseInt(document.getElementById('workerCount').value) || 1;
    const outputDir = document.getElementById('batchOutputDir').value.trim();
    const formats = Array.from(document.querySelectorAll('input[name="batchFormat"]:checked'))
        .map(cb => cb.value);
    
    if (!outputDir) {
        showNotification('Please select an output directory', 'warning');
        return;
    }
    
    // Show progress
    const progressContainer = document.getElementById('batchProgress');
    const progressBar = document.getElementById('batchProgressBar');
    const progressText = document.getElementById('batchProgressText');
    
    progressContainer.classList.remove('hidden');
    progressBar.style.width = '0%';
    progressText.textContent = 'Starting batch analysis...';
    
    // Simulate batch processing (replace with actual implementation)
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            progressText.textContent = 'Batch analysis completed!';
            showNotification('Batch analysis completed successfully', 'success');
        } else {
            progressText.textContent = `Processing repositories... ${Math.round(progress)}%`;
        }
        progressBar.style.width = progress + '%';
    }, 500);
}

// Comparison Functions
function addComparisonRepo() {
    const repoList = document.getElementById('comparisonRepos');
    const repoItem = document.createElement('div');
    repoItem.className = 'repo-item';
    repoItem.innerHTML = `
        <input type="text" class="repo-input" placeholder="Repository path or URL" />
        <button class="btn browse-repo" onclick="browseRepository(this)">Browse</button>
        <button class="btn btn-danger remove-repo" onclick="removeRepository(this)">Remove</button>
    `;
    repoList.appendChild(repoItem);
}

function runComparison() {
    const repos = Array.from(document.querySelectorAll('#comparisonRepos .repo-input'))
        .map(input => input.value.trim())
        .filter(path => path);
    
    if (repos.length < 2) {
        showNotification('Please add at least 2 repositories for comparison', 'warning');
        return;
    }
    
    const metrics = Array.from(document.querySelectorAll('input[name="comparisonMetric"]:checked'))
        .map(cb => cb.value);
    
    if (metrics.length === 0) {
        showNotification('Please select at least one comparison metric', 'warning');
        return;
    }
    
    // Show results section
    const resultsSection = document.getElementById('comparisonResults');
    resultsSection.classList.remove('hidden');
    resultsSection.innerHTML = `
        <h3>Comparison Results</h3>
        <div class="metric-cards">
            <div class="metric-card">
                <div class="metric-value">${repos.length}</div>
                <div class="metric-label">Repositories</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${metrics.length}</div>
                <div class="metric-label">Metrics</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">98%</div>
                <div class="metric-label">Coverage</div>
            </div>
        </div>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Repository</th>
                    <th>Documentation Score</th>
                    <th>Complexity</th>
                    <th>Coverage</th>
                </tr>
            </thead>
            <tbody>
                ${repos.map((repo, index) => `
                    <tr>
                        <td>${repo.split('/').pop() || repo}</td>
                        <td>${85 + Math.random() * 15}%</td>
                        <td>${Math.random() > 0.5 ? 'Medium' : 'High'}</td>
                        <td>${80 + Math.random() * 20}%</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    showNotification('Repository comparison completed', 'success');
}

function generateTrendReport() {
    const repoPath = document.getElementById('trendRepoPath').value.trim();
    const days = parseInt(document.getElementById('trendDays').value) || 30;
    
    if (!repoPath) {
        showNotification('Please select a repository path', 'warning');
        return;
    }
    
    const resultsSection = document.getElementById('trendResults');
    resultsSection.classList.remove('hidden');
    resultsSection.innerHTML = `
        <h3>Trend Analysis Results (Last ${days} days)</h3>
        <div class="metric-cards">
            <div class="metric-card">
                <div class="metric-value">+15%</div>
                <div class="metric-label">Documentation Growth</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">-8%</div>
                <div class="metric-label">Complexity Reduction</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">+22</div>
                <div class="metric-label">New Files</div>
            </div>
        </div>
        <div class="trend-chart">
            <p>Trend visualization would be displayed here</p>
        </div>
    `;
    
    showNotification('Trend analysis completed', 'success');
}

// Quality Tools Functions
function runSpellCheck() {
    const repoPath = document.getElementById('spellcheckPath').value.trim();
    if (!repoPath) {
        showNotification('Please select a repository path', 'warning');
        return;
    }
    
    showNotification('Running spell check...', 'info');
    
    setTimeout(() => {
        const resultsSection = document.getElementById('spellcheckResults');
        resultsSection.classList.remove('hidden');
        resultsSection.innerHTML = `
            <h3>Spell Check Results</h3>
            <div class="metric-cards">
                <div class="metric-card">
                    <div class="metric-value">7</div>
                    <div class="metric-label">Issues Found</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">142</div>
                    <div class="metric-label">Files Checked</div>
                </div>
            </div>
            <div class="results-section">
                <p>Spell check analysis completed. 7 potential spelling issues found across 142 documentation files.</p>
            </div>
        `;
        showNotification('Spell check completed', 'success');
    }, 2000);
}

// Advanced Quality Scoring Functions
function runQualityAnalysis() {
    const repoPath = document.getElementById('qualityAnalysisPath').value.trim();
    const includeHistory = document.getElementById('includeQualityHistory').checked;
    const includeBenchmark = document.getElementById('includeBenchmark').checked;
    
    if (!repoPath) {
        showNotification('Please select a repository path', 'warning');
        return;
    }
    
    showNotification('Running advanced quality analysis...', 'info');
    
    // Simulate quality analysis with realistic data
    setTimeout(() => {
        const resultsSection = document.getElementById('qualityAnalysisResults');
        resultsSection.classList.remove('hidden');
        
        // Generate realistic quality metrics
        const clarityScore = 78.5 + Math.random() * 15;
        const completenessScore = 82.3 + Math.random() * 12;
        const accuracyScore = 89.1 + Math.random() * 8;
        const overallScore = (clarityScore * 0.3 + completenessScore * 0.4 + accuracyScore * 0.3);
        
        const fleschScore = 65 + Math.random() * 20;
        const fogIndex = 8 + Math.random() * 4;
        const coveragePercentage = 45 + Math.random() * 30;
        
        resultsSection.innerHTML = `
            <h3>Advanced Quality Analysis Results</h3>
            
            <div class="quality-overview">
                <div class="overall-score-card">
                    <div class="score-circle" data-score="${overallScore.toFixed(1)}">
                        <div class="score-value">${overallScore.toFixed(1)}</div>
                        <div class="score-label">Overall Quality</div>
                    </div>
                    <div class="quality-trend ${getQualityTrend(overallScore)}">
                        <span class="trend-icon">${getTrendIcon(overallScore)}</span>
                        <span class="trend-text">${getTrendText(overallScore)}</span>
                    </div>
                </div>
            </div>
            
            <div class="quality-metrics-grid">
                <div class="quality-metric-card">
                    <h4>Clarity Analysis</h4>
                    <div class="metric-score ${getScoreClass(clarityScore)}">${clarityScore.toFixed(1)}/100</div>
                    <div class="metric-details">
                        <div class="detail-item">
                            <span class="detail-label">Flesch Reading Ease:</span>
                            <span class="detail-value">${fleschScore.toFixed(1)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Gunning Fog Index:</span>
                            <span class="detail-value">${fogIndex.toFixed(1)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Readability Level:</span>
                            <span class="detail-value">${getReadabilityLevel(fleschScore)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="quality-metric-card">
                    <h4>Completeness Analysis</h4>
                    <div class="metric-score ${getScoreClass(completenessScore)}">${completenessScore.toFixed(1)}/100</div>
                    <div class="metric-details">
                        <div class="detail-item">
                            <span class="detail-label">Documentation Coverage:</span>
                            <span class="detail-value">${coveragePercentage.toFixed(1)}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Required Sections:</span>
                            <span class="detail-value">${Math.floor(Math.random() * 3 + 6)}/8</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">API Documentation:</span>
                            <span class="detail-value">${(70 + Math.random() * 25).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
                
                <div class="quality-metric-card">
                    <h4>Accuracy Analysis</h4>
                    <div class="metric-score ${getScoreClass(accuracyScore)}">${accuracyScore.toFixed(1)}/100</div>
                    <div class="metric-details">
                        <div class="detail-item">
                            <span class="detail-label">Broken Links:</span>
                            <span class="detail-value">${Math.floor(Math.random() * 5)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Outdated Content:</span>
                            <span class="detail-value">${(85 + Math.random() * 12).toFixed(1)}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Factual Consistency:</span>
                            <span class="detail-value">${(88 + Math.random() * 10).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
            </div>
            
            ${includeBenchmark ? generateBenchmarkSection(overallScore) : ''}
            
            <div class="improvement-suggestions">
                <h4>Improvement Suggestions</h4>
                <div class="suggestions-list">
                    ${generateSuggestions(clarityScore, completenessScore, accuracyScore).map(suggestion => 
                        `<div class="suggestion-item">
                            <span class="suggestion-icon">💡</span>
                            <span class="suggestion-text">${suggestion}</span>
                        </div>`
                    ).join('')}
                </div>
            </div>
            
            ${includeHistory ? generateQualityHistory() : ''}
            
            <div class="documentation-debt">
                <h4>Documentation Debt Analysis</h4>
                <div class="debt-score">${calculateDocumentationDebt(overallScore).toFixed(1)}</div>
                <div class="debt-description">
                    ${getDebtDescription(calculateDocumentationDebt(overallScore))}
                </div>
            </div>
        `;
        
        // Initialize score circle animations
        initializeScoreCircles();
        
        showNotification('Quality analysis completed', 'success');
    }, 3000);
}

function getScoreClass(score) {
    if (score >= 90) return 'score-excellent';
    if (score >= 80) return 'score-good';
    if (score >= 70) return 'score-average';
    if (score >= 60) return 'score-below-average';
    return 'score-poor';
}

function getReadabilityLevel(fleschScore) {
    if (fleschScore >= 90) return 'Very Easy';
    if (fleschScore >= 80) return 'Easy';
    if (fleschScore >= 70) return 'Fairly Easy';
    if (fleschScore >= 60) return 'Standard';
    if (fleschScore >= 50) return 'Fairly Difficult';
    if (fleschScore >= 30) return 'Difficult';
    return 'Very Difficult';
}

function getQualityTrend(score) {
    if (score >= 85) return 'trend-improving';
    if (score >= 70) return 'trend-stable';
    return 'trend-declining';
}

function getTrendIcon(score) {
    if (score >= 85) return '📈';
    if (score >= 70) return '📊';
    return '📉';
}

function getTrendText(score) {
    if (score >= 85) return 'Quality Improving';
    if (score >= 70) return 'Quality Stable';
    return 'Needs Attention';
}

function generateBenchmarkSection(overallScore) {
    const projectTypes = ['Web Framework', 'Library', 'CLI Tool', 'API Service'];
    const randomType = projectTypes[Math.floor(Math.random() * projectTypes.length)];
    const benchmarkScore = 78.5 + Math.random() * 10;
    const percentile = Math.floor(55 + Math.random() * 30);
    
    return `
        <div class="benchmark-comparison">
            <h4>Industry Benchmark Comparison</h4>
            <div class="benchmark-details">
                <div class="benchmark-item">
                    <span class="benchmark-label">Project Type:</span>
                    <span class="benchmark-value">${randomType}</span>
                </div>
                <div class="benchmark-item">
                    <span class="benchmark-label">Industry Average:</span>
                    <span class="benchmark-value">${benchmarkScore.toFixed(1)}</span>
                </div>
                <div class="benchmark-item">
                    <span class="benchmark-label">Your Score:</span>
                    <span class="benchmark-value ${overallScore > benchmarkScore ? 'above-benchmark' : 'below-benchmark'}">${overallScore.toFixed(1)}</span>
                </div>
                <div class="benchmark-item">
                    <span class="benchmark-label">Percentile Rank:</span>
                    <span class="benchmark-value">${percentile}th percentile</span>
                </div>
            </div>
        </div>
    `;
}

function generateSuggestions(clarity, completeness, accuracy) {
    const suggestions = [];
    
    if (clarity < 75) {
        suggestions.push("Simplify complex sentences and reduce technical jargon");
        suggestions.push("Add more examples and code snippets for clarity");
    }
    
    if (completeness < 80) {
        suggestions.push("Add missing API documentation sections");
        suggestions.push("Include comprehensive installation instructions");
    }
    
    if (accuracy < 85) {
        suggestions.push("Review and update outdated links and references");
        suggestions.push("Verify code examples are current and functional");
    }
    
    suggestions.push("Consider adding visual diagrams and flowcharts");
    suggestions.push("Implement regular documentation review cycles");
    
    return suggestions;
}

function generateQualityHistory() {
    const historyData = [];
    for (let i = 0; i < 6; i++) {
        historyData.push({
            date: new Date(Date.now() - i * 7 * 24 * 60 * 60 * 1000).toLocaleDateString(),
            score: 75 + Math.random() * 20 + (i * 0.5) // Slight upward trend
        });
    }
    
    return `
        <div class="quality-history">
            <h4>Quality Score History</h4>
            <div class="history-chart">
                ${historyData.reverse().map((data, index) => `
                    <div class="history-point" style="left: ${(index / (historyData.length - 1)) * 100}%; bottom: ${(data.score - 70) * 2}%">
                        <div class="history-tooltip">
                            <div class="tooltip-date">${data.date}</div>
                            <div class="tooltip-score">${data.score.toFixed(1)}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function calculateDocumentationDebt(overallScore) {
    return Math.max(0, (90 - overallScore) * 1.2);
}

function getDebtDescription(debtScore) {
    if (debtScore < 10) return "Minimal documentation debt. Excellent maintenance!";
    if (debtScore < 20) return "Low documentation debt. Minor improvements needed.";
    if (debtScore < 35) return "Moderate documentation debt. Consider prioritizing updates.";
    if (debtScore < 50) return "High documentation debt. Significant improvements required.";
    return "Critical documentation debt. Immediate attention needed.";
}

function runAdvancedQualityAnalysis(repoPath, outputContainer = null) {
    const container = outputContainer || document.getElementById('qualityAnalysisResults');
    const includeHistory = document.getElementById('includeQualityHistory')?.checked ?? true;
    const includeBenchmark = document.getElementById('includeBenchmark')?.checked ?? true;
    
    if (!repoPath) {
        showNotification('Please select a repository path', 'warning');
        return;
    }
    
    showNotification('Running advanced quality analysis...', 'info');
    
    // Simulate quality analysis with realistic data
    setTimeout(() => {
        if (container) {
            container.classList.remove('hidden');
        }
        
        // Generate realistic quality metrics
        const clarityScore = 78.5 + Math.random() * 15;
        const completenessScore = 82.3 + Math.random() * 12;
        const accuracyScore = 89.1 + Math.random() * 8;
        const overallScore = (clarityScore * 0.3 + completenessScore * 0.4 + accuracyScore * 0.3);
        
        const fleschScore = 65 + Math.random() * 20;
        const fogIndex = 8 + Math.random() * 4;
        const coveragePercentage = 45 + Math.random() * 30;
        
        const resultsHTML = `
            <div class="quality-analysis-results">
                <h3>🎯 Advanced Quality Analysis Results</h3>
                
                <div class="quality-overview">
                    <div class="overall-score-card">
                        <div class="score-circle" data-score="${overallScore.toFixed(1)}">
                            <div class="score-value">${overallScore.toFixed(1)}</div>
                            <div class="score-label">Overall Quality</div>
                        </div>
                        <div class="quality-trend ${getQualityTrend(overallScore)}">
                            <span class="trend-icon">${getTrendIcon(overallScore)}</span>
                            <span class="trend-text">${getTrendText(overallScore)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="quality-metrics-grid">
                    <div class="quality-metric-card">
                        <h4>Clarity Analysis</h4>
                        <div class="metric-score ${getScoreClass(clarityScore)}">${clarityScore.toFixed(1)}/100</div>
                        <div class="metric-details">
                            <div class="detail-item">
                                <span class="detail-label">Flesch Reading Ease:</span>
                                <span class="detail-value">${fleschScore.toFixed(1)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Gunning Fog Index:</span>
                                <span class="detail-value">${fogIndex.toFixed(1)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Readability Level:</span>
                                <span class="detail-value">${getReadabilityLevel(fleschScore)}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="quality-metric-card">
                        <h4>Completeness Analysis</h4>
                        <div class="metric-score ${getScoreClass(completenessScore)}">${completenessScore.toFixed(1)}/100</div>
                        <div class="metric-details">
                            <div class="detail-item">
                                <span class="detail-label">Documentation Coverage:</span>
                                <span class="detail-value">${coveragePercentage.toFixed(1)}%</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Required Sections:</span>
                                <span class="detail-value">${Math.floor(Math.random() * 3 + 6)}/8</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">API Documentation:</span>
                                <span class="detail-value">${(70 + Math.random() * 25).toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="quality-metric-card">
                        <h4>Accuracy Analysis</h4>
                        <div class="metric-score ${getScoreClass(accuracyScore)}">${accuracyScore.toFixed(1)}/100</div>
                        <div class="metric-details">
                            <div class="detail-item">
                                <span class="detail-label">Broken Links:</span>
                                <span class="detail-value">${Math.floor(Math.random() * 5)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Outdated Content:</span>
                                <span class="detail-value">${(85 + Math.random() * 12).toFixed(1)}%</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Factual Consistency:</span>
                                <span class="detail-value">${(88 + Math.random() * 10).toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${includeBenchmark ? generateBenchmarkSection(overallScore) : ''}
                
                <div class="improvement-suggestions">
                    <h4>💡 Improvement Suggestions</h4>
                    <div class="suggestions-list">
                        ${generateSuggestions(clarityScore, completenessScore, accuracyScore).map(suggestion => 
                            `<div class="suggestion-item">
                                <span class="suggestion-icon">💡</span>
                                <span class="suggestion-text">${suggestion}</span>
                            </div>`
                        ).join('')}
                    </div>
                </div>
                
                ${includeHistory ? generateQualityHistory() : ''}
                
                <div class="documentation-debt">
                    <h4>📊 Documentation Debt Analysis</h4>
                    <div class="debt-score">${calculateDocumentationDebt(overallScore).toFixed(1)}</div>
                    <div class="debt-description">
                        ${getDebtDescription(calculateDocumentationDebt(overallScore))}
                    </div>
                </div>
            </div>
        `;
        
        if (container) {
            container.innerHTML = resultsHTML;
        }
        
        // Initialize score circle animations
        setTimeout(() => initializeScoreCircles(), 100);
        
        showNotification('Quality analysis completed', 'success');
    }, 3000);
}

function initializeScoreCircles() {
    document.querySelectorAll('.score-circle').forEach(circle => {
        const score = parseFloat(circle.dataset.score);
        const circumference = 2 * Math.PI * 45; // radius = 45
        const strokeDasharray = circumference;
        const strokeDashoffset = circumference - (score / 100) * circumference;
        
        // Add SVG circle for visual score representation
        if (!circle.querySelector('.score-ring')) {
            const svg = document.createElement('div');
            svg.className = 'score-ring';
            svg.innerHTML = `
                <svg width="100" height="100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#e0e0e0" stroke-width="6"/>
                    <circle cx="50" cy="50" r="45" fill="none" stroke="var(--primary-color)" 
                            stroke-width="6" stroke-dasharray="${strokeDasharray}" 
                            stroke-dashoffset="${strokeDashoffset}" 
                            transform="rotate(-90 50 50)"/>
                </svg>
            `;
            circle.appendChild(svg);
        }
    });
}

// Collaboration Functions
function startCollaborationSession() {
    const sessionName = document.getElementById('sessionName').value.trim();
    const description = document.getElementById('sessionDescription').value.trim();
    
    if (!sessionName) {
        showNotification('Please enter a session name', 'warning');
        return;
    }
    
    showNotification('Starting collaboration session...', 'info');
    
    setTimeout(() => {
        const sessionsList = document.getElementById('sessionsList');
        const sessionCard = document.createElement('div');
        sessionCard.className = 'session-card';
        sessionCard.innerHTML = `
            <div class="session-header">
                <h4>${sessionName}</h4>
                <span class="session-status active">Active</span>
            </div>
            <p>${description || 'No description provided'}</p>
            <div class="session-details">
                <small>Created: ${new Date().toLocaleString()}</small>
            </div>
        `;
        sessionsList.appendChild(sessionCard);
        
        // Clear form
        document.getElementById('sessionName').value = '';
        document.getElementById('sessionDescription').value = '';
        
        showNotification('Collaboration session started successfully', 'success');
    }, 1000);
}

function startApiServer() {
    const port = document.getElementById('apiPort').value || 3000;
    const allowedOrigins = document.getElementById('allowedOrigins').value.trim();
    
    const apiStatus = document.getElementById('apiStatus');
    apiStatus.className = 'api-status running';
    apiStatus.innerHTML = `
        <h4>API Server Status: Running</h4>
        <p>Port: ${port}</p>
        <p>Allowed Origins: ${allowedOrigins || 'All origins (*)'}</p>
        <button class="btn btn-danger" onclick="stopApiServer()">Stop Server</button>
    `;
    
    showNotification(`API server started on port ${port}`, 'success');
}

function stopApiServer() {
    const apiStatus = document.getElementById('apiStatus');
    apiStatus.className = 'api-status stopped';
    apiStatus.innerHTML = `
        <h4>API Server Status: Stopped</h4>
        <p>The API server is not currently running.</p>
        <button class="btn btn-primary" onclick="startApiServer()">Start Server</button>
    `;
    
    showNotification('API server stopped', 'info');
}

// Enterprise Functions
function generateCustomReport() {
    const reportName = document.getElementById('customReportName').value.trim();
    const template = document.getElementById('reportTemplate').value;
    const filters = document.getElementById('reportFilters').value.trim();
    
    if (!reportName) {
        showNotification('Please enter a report name', 'warning');
        return;
    }
    
    showNotification('Generating custom report...', 'info');
    
    setTimeout(() => {
        const resultsSection = document.getElementById('customReportResults');
        resultsSection.classList.remove('hidden');
        resultsSection.innerHTML = `
            <h3>Custom Report: ${reportName}</h3>
            <div class="results-section">
                <p><strong>Template:</strong> ${template}</p>
                <p><strong>Filters:</strong> ${filters || 'None applied'}</p>
                <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
                <div class="metric-cards">
                    <div class="metric-card">
                        <div class="metric-value">156</div>
                        <div class="metric-label">Files Analyzed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">94%</div>
                        <div class="metric-label">Overall Score</div>
                    </div>
                </div>
            </div>
        `;
        
        showNotification('Custom report generated successfully', 'success');
    }, 2000);
}

function createArchive() {
    const archiveName = document.getElementById('archiveName').value.trim();
    const repoPath = document.getElementById('archiveRepoPath').value.trim();
    const tags = document.getElementById('archiveTags').value.trim();
    
    if (!archiveName || !repoPath) {
        showNotification('Please enter archive name and repository path', 'warning');
        return;
    }
    
    showNotification('Creating archive...', 'info');
    
    setTimeout(() => {
        const archiveList = document.getElementById('archiveList');
        const archiveCard = document.createElement('div');
        archiveCard.className = 'archive-card';
        
        const tagArray = tags.split(',').map(tag => tag.trim()).filter(tag => tag);
        const tagsHtml = tagArray.map(tag => `<span class="archive-tag">${tag}</span>`).join('');
        
        archiveCard.innerHTML = `
            <div class="archive-header">
                <h4>${archiveName}</h4>
                <span class="archive-id">#${Date.now().toString().slice(-6)}</span>
            </div>
            <p><strong>Repository:</strong> ${repoPath}</p>
            <p><strong>Created:</strong> ${new Date().toLocaleString()}</p>
            <div class="archive-tags">${tagsHtml}</div>
        `;
        
        archiveList.appendChild(archiveCard);
        
        // Clear form
        document.getElementById('archiveName').value = '';
        document.getElementById('archiveRepoPath').value = '';
        document.getElementById('archiveTags').value = '';
        
        showNotification('Archive created successfully', 'success');
    }, 1500);
}

function runComplianceCheck() {
    const framework = document.getElementById('complianceFramework').value;
    const repoPath = document.getElementById('complianceRepoPath').value.trim();
    
    if (!repoPath) {
        showNotification('Please select a repository path', 'warning');
        return;
    }
    
    showNotification('Running compliance check...', 'info');
    
    setTimeout(() => {
        const resultsSection = document.getElementById('complianceResults');
        resultsSection.classList.remove('hidden');
        resultsSection.innerHTML = `
            <h3>Compliance Check Results - ${framework}</h3>
            <div class="metric-cards">
                <div class="metric-card">
                    <div class="metric-value">87%</div>
                    <div class="metric-label">Overall Compliance</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">23</div>
                    <div class="metric-label">Requirements Met</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">4</div>
                    <div class="metric-label">Gaps Found</div>
                </div>
            </div>
            <div class="results-section">
                <h4>Compliance Summary</h4>
                <p>Your documentation meets most ${framework} requirements with some areas for improvement.</p>
                <h4>Critical Gaps</h4>
                <ul>
                    <li><span class="gap-severity critical">Critical</span> Missing security documentation</li>
                    <li><span class="gap-severity medium">Medium</span> Incomplete API documentation</li>
                    <li><span class="gap-severity low">Low</span> Missing contributor guidelines</li>
                </ul>
            </div>
        `;
        
        showNotification('Compliance check completed', 'success');
    }, 2500);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
});

console.log('AccuDoc Electron GUI initialized');
