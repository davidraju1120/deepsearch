// Deep Researcher Agent - Web Interface JavaScript

// Global variables
let currentQueryResult = null;
let isProcessing = false;

// API Base URL
const API_BASE = '/api';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize event listeners
    initializeEventListeners();
    
    // Load initial status
    loadSystemStatus();
    
    // Setup file upload drag and drop
    setupFileUpload();
    
    console.log('Deep Researcher Agent Web Interface initialized');
}

function initializeEventListeners() {
    // Query form submission
    document.getElementById('queryForm').addEventListener('submit', handleQuerySubmit);
    
    // Clear button
    document.getElementById('clearBtn').addEventListener('click', clearQueryForm);
    
    // Text ingestion form
    document.getElementById('textForm').addEventListener('submit', handleTextSubmit);
    
    // File ingestion form
    document.getElementById('fileForm').addEventListener('submit', handleFileSubmit);
    
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', handleTabSwitch);
    });
    
    // Modal buttons
    document.getElementById('statusBtn').addEventListener('click', () => showModal('statusModal'));
    document.getElementById('helpBtn').addEventListener('click', () => showModal('helpModal'));
    document.getElementById('explainBtn').addEventListener('click', handleExplainReasoning);
    document.getElementById('exportBtn').addEventListener('click', () => showModal('exportModal'));
    
    // Export form submission
    document.getElementById('exportForm').addEventListener('submit', handleExportSubmit);
    
    // Close modal buttons
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });
    
    // Close modal on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });
    
    // Escape key to close modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                closeModal(modal.id);
            });
        }
    });
}

// ===== QUERY HANDLING =====

async function handleQuerySubmit(e) {
    e.preventDefault();
    
    if (isProcessing) {
        showNotification('Please wait for the current query to finish processing.', 'warning');
        return;
    }
    
    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();
    
    if (!query) {
        showNotification('Please enter a research query.', 'error');
        return;
    }
    
    const enableRefinement = document.getElementById('enableRefinement').checked;
    const enableSummarization = document.getElementById('enableSummarization').checked;
    
    try {
        isProcessing = true;
        showLoadingSpinner(true);
        
        const response = await axios.post(`${API_BASE}/query`, {
            query: query,
            enable_refinement: enableRefinement,
            enable_summarization: enableSummarization
        });
        
        if (response.data.error) {
            throw new Error(response.data.error);
        }
        
        console.log('Query response received:', response.data);
        console.log('Answer field:', response.data.answer);
        console.log('Response field:', response.data.response);
        console.log('Result field:', response.data.result);
        console.log('Text field:', response.data.text);

        currentQueryResult = response.data;
        displayResults(response.data);
        
        showNotification('Query processed successfully!', 'success');
        
    } catch (error) {
        console.error('Error processing query:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        isProcessing = false;
        showLoadingSpinner(false);
    }
}

function displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');

    console.log('displayResults called with:', result);

    // Build results HTML - Two-step process
    let html = '';

    // Immediate AI Answer (most prominent)
    // Check for answer in different possible formats
    const answer = result.answer || result.response || result.result || result.text || 'No answer available';
    console.log('Extracted answer:', answer);

    if (answer && answer !== 'No answer available') {
        html += `
            <div class="ai-response">
                <div class="ai-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="ai-message">
                    <div class="ai-answer">
                        ${formatAnswer(answer)}
                    </div>
                    <div class="deep-research-section" id="deepResearchSection" style="display: none;">
                        <button id="deepResearchBtn" class="btn btn-secondary deep-research-btn">
                            <i class="fas fa-search-plus"></i>
                            Deep Research
                        </button>
                        <p class="deep-research-text">Get comprehensive analysis from local knowledge base</p>
                    </div>
                </div>
            </div>
        `;
        console.log('Answer displayed successfully');
    } else {
        // If no answer found, show error message
        console.log('No answer found, showing error message');
        html += `
            <div class="ai-response" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
                <div class="ai-avatar">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="ai-message">
                    <div class="ai-answer">
                        <p><strong>No answer generated.</strong></p>
                        <p>This might be because:</p>
                        <ul>
                            <li>No documents are available in the system</li>
                            <li>The query couldn't find relevant information</li>
                            <li>There was an error processing the request</li>
                        </ul>
                        <p>Please try uploading some documents first or check the console for errors.</p>
                    </div>
                </div>
            </div>
        `;
    }

    // Sources (if available, shown compactly)
    if (result.retrieved_documents && result.retrieved_documents.length > 0) {
        console.log('🔍 Displaying sources:', result.retrieved_documents.length);
        console.log('📄 Sample document:', result.retrieved_documents[0]);

        html += `
            <div class="sources-compact">
                <h4><i class="fas fa-book"></i> Based on ${result.retrieved_documents.length} source${result.retrieved_documents.length > 1 ? 's' : ''}</h4>
                <div class="sources-list">
        `;

        result.retrieved_documents.forEach((doc, index) => {
            const docId = doc.id || `Document ${index + 1}`;
            const docContent = doc.content ? doc.content.substring(0, 150) + '...' : 'No content available';

        console.log('📄 Processing document:', docId);

            html += `
                    <div class="source-item">
                        <i class="fas fa-file-text"></i>
                        <div class="source-content">
                            <div class="source-header">
                                <strong>${escapeHtml(docId)}</strong>
                                <button class="btn-view-doc" onclick="viewDocument('${escapeHtml(docId)}', \`${escapeHtml(doc.content || 'No content available').replace(/`/g, '\\`').replace(/\${/g, '\\${')}\`)">
                                    <i class="fas fa-eye"></i> View
                                </button>
                            </div>
                            <p class="source-snippet">${escapeHtml(docContent)}</p>
                            ${doc.metadata ? `
                                <div class="source-meta">
                                    <small>Length: ${doc.content ? doc.content.length : 0} characters</small>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
        });

        html += `
                </div>
            </div>
        `;
    } else {
        console.log('❌ No retrieved_documents in result:', result);

        // Fallback: try to show any available documents in different formats
        if (result.documents || result.sources || result.source_documents) {
            console.log('🔄 Trying alternative document formats...');
            const docs = result.documents || result.sources || result.source_documents;
            if (Array.isArray(docs) && docs.length > 0) {
                html += `
                    <div class="sources-compact">
                        <h4><i class="fas fa-book"></i> Based on ${docs.length} source${docs.length > 1 ? 's' : ''} (Alternative format)</h4>
                        <div class="sources-list">
                `;

                docs.forEach((doc, index) => {
                    const docId = doc.id || doc.title || `Document ${index + 1}`;
                    const docContent = doc.content || doc.text || 'No content available';
                    const snippet = docContent.substring(0, 150) + '...';

                    html += `
                            <div class="source-item">
                                <i class="fas fa-file-text"></i>
                                <div class="source-content">
                                    <div class="source-header">
                                        <strong>${escapeHtml(docId)}</strong>
                                        <button class="btn-view-doc" onclick="viewDocument('${escapeHtml(docId)}', \`${escapeHtml(docContent).replace(/`/g, '\\`').replace(/\${/g, '\\${')}\`)">
                                            <i class="fas fa-eye"></i> View
                                        </button>
                                    </div>
                                    <p class="source-snippet">${escapeHtml(snippet)}</p>
                                </div>
                            </div>
                        `;
                });

                html += `
                        </div>
                    </div>
                `;
            }
        }
    }

    resultsContent.innerHTML = html;
    resultsSection.style.display = 'block';

    // Show deep research button after a delay
    setTimeout(() => {
        const deepResearchSection = document.getElementById('deepResearchSection');
        if (deepResearchSection) {
            deepResearchSection.style.display = 'block';
            deepResearchSection.style.animation = 'fadeInUp 0.5s ease-out';
        }
    }, 2000);

    // Add event listener for deep research button
    setTimeout(() => {
        const deepResearchBtn = document.getElementById('deepResearchBtn');
        if (deepResearchBtn) {
            deepResearchBtn.addEventListener('click', () => handleDeepResearch(result));
        }
    }, 2000);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

async function handleDeepResearch(result) {
    const deepResearchBtn = document.getElementById('deepResearchBtn');
    const deepResearchSection = document.getElementById('deepResearchSection');

    if (isProcessing) {
        showNotification('Please wait for the current process to finish.', 'warning');
        return;
    }

    try {
        isProcessing = true;
        deepResearchBtn.disabled = true;
        deepResearchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Researching...';

        const response = await axios.post(`${API_BASE}/deep-research`, {
            query: result.query || result.original_query,
            original_result: result
        });

        if (response.data.error) {
            throw new Error(response.data.error);
        }

        // Display deep research results
        displayDeepResearchResults(response.data);

        showNotification('Deep research completed successfully!', 'success');

    } catch (error) {
        console.error('Error performing deep research:', error);
        showNotification(`Deep research error: ${error.message}`, 'error');
    } finally {
        isProcessing = false;
        deepResearchBtn.disabled = false;
        deepResearchBtn.innerHTML = '<i class="fas fa-search-plus"></i> Deep Research';
    }
}

function displayDeepResearchResults(result) {
    const resultsContent = document.getElementById('resultsContent');
    const deepResearchSection = document.getElementById('deepResearchSection');

    // Hide the deep research button section
    if (deepResearchSection) {
        deepResearchSection.style.display = 'none';
    }

    // Add deep research results to the existing content
    let deepResearchHtml = '';

    if (result.local_results && result.local_results.length > 0) {
        deepResearchHtml += `
            <div class="deep-research-results">
                <h3><i class="fas fa-database"></i> Local Knowledge Base Results</h3>
                <div class="local-results">
        `;

        result.local_results.forEach((localResult, index) => {
            deepResearchHtml += `
                <div class="local-result-item">
                    <div class="local-result-header">
                        <h4><i class="fas fa-file-text"></i> ${escapeHtml(localResult.id || `Document ${index + 1}`)}</h4>
                        <span class="local-result-type">Local Document</span>
                    </div>
                    <p class="local-result-content">${escapeHtml(localResult.content ? localResult.content.substring(0, 200) + '...' : 'No content preview available')}</p>
                    ${localResult.metadata ? `
                        <div class="local-result-meta">
                            <small>Length: ${localResult.content ? localResult.content.length : 0} characters</small>
                        </div>
                    ` : ''}
                </div>
            `;
        });

        deepResearchHtml += `
                </div>
            </div>
        `;
    }

    if (result.enhanced_answer) {
        deepResearchHtml += `
            <div class="enhanced-answer">
                <h3><i class="fas fa-brain"></i> Enhanced Local Analysis</h3>
                <div class="ai-response enhanced">
                    <div class="ai-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="ai-message">
                        <div class="ai-answer">
                            ${formatAnswer(result.enhanced_answer)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    if (result.research_summary) {
        deepResearchHtml += `
            <div class="research-summary">
                <h3><i class="fas fa-file-alt"></i> Research Summary</h3>
                <div class="summary-content">
                    ${formatAnswer(result.research_summary)}
                </div>
            </div>
        `;
    }

    if (result.reasoning_steps && result.reasoning_steps.length > 0) {
        deepResearchHtml += `
            <div class="reasoning-explanation">
                <h3><i class="fas fa-list-ol"></i> Deep Research Reasoning Steps</h3>
                <ol class="reasoning-steps">
        `;

        result.reasoning_steps.forEach(step => {
            deepResearchHtml += `
                <li>
                    <strong>Step ${step.step_number}: ${escapeHtml(step.step_type)}</strong><br>
                    ${escapeHtml(step.description)}<br>
                    <small><strong>Purpose:</strong> ${escapeHtml(step.purpose)}</small><br>
                    <small><strong>Outcome:</strong> ${escapeHtml(step.outcome)}</small>
                </li>
            `;
        });

        deepResearchHtml += `
                </ol>
            </div>
        `;
    }

    // Insert deep research results after the original answer
    const existingContent = resultsContent.innerHTML;
    resultsContent.innerHTML = existingContent + deepResearchHtml;

    // Scroll to the deep research results
    const deepResearchResults = document.querySelector('.deep-research-results');
    if (deepResearchResults) {
        deepResearchResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function viewDocument(docId, content) {
    // Create and show document modal
    const docModal = document.createElement('div');
    docModal.className = 'modal show';
    docModal.id = 'documentModal';
    docModal.innerHTML = `
        <div class="modal-content document-modal">
            <div class="modal-header">
                <h3><i class="fas fa-file-text"></i> ${docId}</h3>
                <button class="close-btn" onclick="closeModal('documentModal')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="document-content">
                    <div class="document-text">${content}</div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(docModal);

    // Add event listeners
    docModal.addEventListener('click', (e) => {
        if (e.target === docModal) {
            closeModal('documentModal');
        }
    });

    // Focus management for accessibility
    setTimeout(() => {
        const closeBtn = docModal.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.focus();
        }
    }, 100);
}

// ===== INGESTION HANDLING =====

async function handleTextSubmit(e) {
    e.preventDefault();
    
    const textInput = document.getElementById('textInput');
    const text = textInput.value.trim();
    
    if (!text) {
        showNotification('Please enter text content to ingest.', 'error');
        return;
    }
    
    try {
        showLoadingSpinner(true);
        
        const response = await axios.post(`${API_BASE}/ingest/text`, {
            text: text
        });
        
        if (response.data.error) {
            throw new Error(response.data.error);
        }
        
        textInput.value = '';
        showNotification(`Text ingested successfully! Document ID: ${response.data.document_id}`, 'success');
        
    } catch (error) {
        console.error('Error ingesting text:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoadingSpinner(false);
    }
}

async function handleFileSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a file to upload.', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoadingSpinner(true);
        
        const response = await axios.post(`${API_BASE}/ingest/file`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        if (response.data.error) {
            throw new Error(response.data.error);
        }
        
        fileInput.value = '';
        showNotification(`File uploaded successfully! Document IDs: ${response.data.document_ids.join(', ')}`, 'success');
        
    } catch (error) {
        console.error('Error uploading file:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoadingSpinner(false);
    }
}

// ===== FILE UPLOAD SETUP =====

function setupFileUpload() {
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('fileInput');
    
    // Drag and drop events
    fileUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUploadArea.classList.add('dragover');
    });
    
    fileUploadArea.addEventListener('dragleave', () => {
        fileUploadArea.classList.remove('dragover');
    });
    
    fileUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileUploadDisplay(files[0]);
        }
    });
    
    // File input change event
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            updateFileUploadDisplay(e.target.files[0]);
        }
    });
}

function updateFileUploadDisplay(file) {
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileName = file.name;
    const fileSize = formatFileSize(file.size);
    
    fileUploadArea.innerHTML = `
        <i class="fas fa-file-check"></i>
        <p><strong>${escapeHtml(fileName)}</strong></p>
        <p><small>${fileSize}</small></p>
        <input type="file" id="fileInput" accept=".pdf,.docx,.txt,.md" required style="display: none;">
    `;
    
    // Re-attach event listener to the new file input
    const newFileInput = document.getElementById('fileInput');
    newFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            updateFileUploadDisplay(e.target.files[0]);
        }
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ===== TAB HANDLING =====

function handleTabSwitch(e) {
    const tabBtn = e.target.closest('.tab-btn');
    if (!tabBtn) return;
    
    const tabName = tabBtn.dataset.tab;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    tabBtn.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetTab = document.getElementById(tabName + 'Tab');
    if (targetTab) {
        targetTab.classList.add('active');
    }
}

// ===== MODAL HANDLING =====

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        
        // Load status if opening status modal
        if (modalId === 'statusModal') {
            loadSystemStatus();
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

// ===== STATUS HANDLING =====

async function loadSystemStatus() {
    try {
        const response = await axios.get(`${API_BASE}/status`);
        
        if (response.data.error) {
            throw new Error(response.data.error);
        }
        
        displaySystemStatus(response.data);
        
    } catch (error) {
        console.error('Error loading system status:', error);
        const statusContent = document.getElementById('statusContent');
        if (statusContent) {
            statusContent.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading system status: ${error.message}</p>
                </div>
            `;
        }
    }
}

function formatAnswer(answer) {
    // Simple formatting for better readability
    return answer
        .split('\n')
        .map(paragraph => paragraph.trim())
        .filter(paragraph => paragraph.length > 0)
        .map(paragraph => `<p>${escapeHtml(paragraph)}</p>`)
        .join('');
}
    
function displaySystemStatus(status) {
    const statusContent = document.getElementById('statusContent');
    if (!statusContent) return;

    const html = `
        <div class="status-grid">
            <div class="status-item">
                <h4>Documents</h4>
                <p>${status.document_store?.total_documents || 0}</p>
            </div>
            <div class="status-item">
                <h4>Embedding Model</h4>
                <p>${escapeHtml(status.embedding_model?.model_name || 'Unknown')}</p>
            </div>
            <div class="status-item ${status.config_summary?.reasoning_enabled ? 'enabled' : 'disabled'}">
                <h4>Reasoning</h4>
                <p>${status.config_summary?.reasoning_enabled ? 'Enabled' : 'Disabled'}</p>
            </div>
            <div class="status-item ${status.config_summary?.query_refinement_enabled ? 'enabled' : 'disabled'}">
                <h4>Query Refinement</h4>
                <p>${status.config_summary?.query_refinement_enabled ? 'Enabled' : 'Disabled'}</p>
            </div>
            <div class="status-item ${status.config_summary?.summarization_enabled ? 'enabled' : 'disabled'}">
                <h4>Summarization</h4>
                <p>${status.config_summary?.summarization_enabled ? 'Enabled' : 'Disabled'}</p>
            </div>
            <div class="status-item">
                <h4>Total Queries</h4>
                <p>${status.query_handler?.query_stats?.total_queries || 0}</p>
            </div>
            <div class="status-item">
                <h4>Refinement Sessions</h4>
                <p>${status.query_refiner?.active_sessions || 0}</p>
            </div>
            <div class="status-item">
                <h4>Exports</h4>
                <p>${status.export_manager?.performance_metrics?.exports_created || 0}</p>
            </div>
        </div>
    `;

    statusContent.innerHTML = html;
}

// ===== EXPLANATION HANDLING =====

async function handleExplainReasoning() {
    if (!currentQueryResult) {
        showNotification('No query result to explain. Please run a query first.', 'warning');
        return;
    }
    
    try {
        showLoadingSpinner(true);
        
        const response = await axios.post(`${API_BASE}/explain`, {
            query_result: currentQueryResult
        });
        
        if (response.data.error) {
            throw new Error(response.data.error);
        }
        
        displayExplanation(response.data);
        
    } catch (error) {
        console.error('Error getting explanation:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoadingSpinner(false);
    }
}

function displayExplanation(explanation) {
    let html = `
        <div class="explanation-content">
            <div class="result-item">
                <h4><i class="fas fa-search"></i> Original Query</h4>
                <p><strong>${escapeHtml(explanation.original_query || 'Unknown')}</strong></p>
            </div>
            
            <div class="result-item">
                <h4><i class="fas fa-lightbulb"></i> Final Answer</h4>
                <p>${formatAnswer(explanation.final_answer || 'No answer available')}</p>
            </div>
            
            <div class="result-item">
                <h4><i class="fas fa-chart-line"></i> Confidence Score</h4>
                <div class="confidence-score">
                    <i class="fas fa-chart-line"></i>
                    ${(explanation.confidence_score * 100).toFixed(1)}%
                </div>
            </div>
            
            <div class="result-item">
                <h4><i class="fas fa-info-circle"></i> Reasoning Summary</h4>
                <p>${escapeHtml(explanation.reasoning_summary || 'No summary available')}</p>
            </div>
            
            <div class="result-item">
                <h4><i class="fas fa-list-ol"></i> Reasoning Steps</h4>
                <ol class="reasoning-steps">
    `;
    
    if (explanation.steps && explanation.steps.length > 0) {
        explanation.steps.forEach(step => {
            html += `
                <li>
                    <strong>Step ${step.step_number}: ${escapeHtml(step.step_type || 'Unknown')}</strong><br>
                    ${escapeHtml(step.description || 'No description')}<br>
                    <small><strong>Purpose:</strong> ${escapeHtml(step.purpose || 'Process information')}</small><br>
                    <small><strong>Outcome:</strong> ${escapeHtml(step.outcome || 'Completed')}</small>
                </li>
            `;
        });
    } else {
        html += '<li>No reasoning steps available</li>';
    }
    
    html += `
                </ol>
            </div>
            
            <div class="result-item">
                <h4><i class="fas fa-book"></i> Document Count</h4>
                <p>${explanation.document_count || 0} documents used in reasoning</p>
            </div>
        </div>
    `;
    
    // Create and show explanation modal
    const explanationModal = document.createElement('div');
    explanationModal.className = 'modal show';
    explanationModal.id = 'explanationModal';
    explanationModal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-lightbulb"></i> Reasoning Explanation</h3>
                <button class="close-btn" onclick="closeModal('explanationModal')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                ${html}
            </div>
        </div>
    `;
    
    document.body.appendChild(explanationModal);
    
    // Add event listeners
    explanationModal.addEventListener('click', (e) => {
        if (e.target === explanationModal) {
            closeModal('explanationModal');
        }
    });
}

// ===== EXPORT HANDLING =====

async function handleExportSubmit(e) {
    e.preventDefault();
    
    if (!currentQueryResult) {
        showNotification('No query result to export. Please run a query first.', 'warning');
        return;
    }
    
    const format = document.getElementById('exportFormat').value;
    const filename = document.getElementById('exportFilename').value.trim();
    
    try {
        showLoadingSpinner(true);
        closeModal('exportModal');
        
        const response = await axios.post(`${API_BASE}/export`, {
            query_result: currentQueryResult,
            format: format,
            filename: filename
        });
        
        if (response.data.error) {
            throw new Error(response.data.error);
        }
        
        showNotification(`Result exported successfully to: ${response.data.export_path}`, 'success');
        
    } catch (error) {
        console.error('Error exporting result:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoadingSpinner(false);
    }
}

// ===== UTILITY FUNCTIONS =====

function showLoadingSpinner(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatAnswer(answer) {
    // Simple formatting for better readability
    return answer
        .split('\n')
        .map(paragraph => paragraph.trim())
        .filter(paragraph => paragraph.length > 0)
        .map(paragraph => `<p>${escapeHtml(paragraph)}</p>`)
        .join('');
}

// Add notification styles dynamically
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        max-width: 500px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-left: 4px solid;
    }
    
    .notification-success .notification-content {
        border-left-color: #10b981;
    }
    
    .notification-error .notification-content {
        border-left-color: #ef4444;
    }
    
    .notification-warning .notification-content {
        border-left-color: #f59e0b;
    }
    
    .notification-info .notification-content {
        border-left-color: #3b82f6;
    }
    
    .notification-content i {
        font-size: 1.25rem;
    }
    
    .notification-success i {
        color: #10b981;
    }
    
    .notification-error i {
        color: #ef4444;
    }
    
    .notification-warning i {
        color: #f59e0b;
    }
    
    .notification-info i {
        color: #3b82f6;
    }
    
    .reasoning-steps {
        padding-left: 1.5rem;
    }
    
    .reasoning-steps li {
        margin-bottom: 1rem;
        padding-left: 0.5rem;
    }
    
    .error-message {
        text-align: center;
        padding: 2rem;
        color: #ef4444;
    }
    
    .error-message i {
        font-size: 2rem;
        margin-bottom: 1rem;
        display: block;
    }
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
