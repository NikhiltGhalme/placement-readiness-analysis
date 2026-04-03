document.addEventListener('DOMContentLoaded', () => {
    let taskId = null;
    let pollInterval = null;

    const btnRun = document.getElementById('btn-run');
    const idleState = document.getElementById('idle-state');
    const runningState = document.getElementById('running-state');
    const resultsState = document.getElementById('results-state');

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => {
                b.classList.remove('text-emerald-600', 'border-b-2', 'border-emerald-600');
                b.classList.add('text-gray-500');
            });
            btn.classList.add('text-emerald-600', 'border-b-2', 'border-emerald-600');
            btn.classList.remove('text-gray-500');
            document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
            document.querySelector(`.tab-content[data-tab="${btn.dataset.tab}"]`).classList.remove('hidden');
        });
    });

    btnRun.addEventListener('click', async () => {
        btnRun.disabled = true;
        btnRun.textContent = 'Starting...';
        try {
            const resp = await fetch('/api/analysis/run', { method: 'POST' });
            const data = await resp.json();
            taskId = data.task_id;
            idleState.classList.add('hidden');
            runningState.classList.remove('hidden');
            pollInterval = setInterval(pollStatus, 2000);
        } catch (err) {
            showToast('Failed to start analysis: ' + err.message, 'error');
            btnRun.disabled = false;
            btnRun.textContent = 'Run Full Analysis';
        }
    });

    async function pollStatus() {
        try {
            const resp = await fetch(`/api/analysis/status/${taskId}`);
            const status = await resp.json();

            const phase = status.phase || 0;
            const pct = Math.round((phase / 7) * 100);
            document.getElementById('analysis-progress-bar').style.width = pct + '%';
            document.getElementById('phase-num').textContent = phase;
            document.getElementById('phase-message').textContent = status.message || '';

            // Update phase indicators
            document.querySelectorAll('.phase-item').forEach(el => {
                const p = parseInt(el.dataset.phase);
                const circle = el.querySelector('span');
                if (p < phase) {
                    circle.classList.remove('bg-gray-200', 'bg-emerald-500');
                    circle.classList.add('bg-emerald-500', 'text-white');
                    circle.textContent = '✓';
                } else if (p === phase) {
                    circle.classList.remove('bg-gray-200');
                    circle.classList.add('bg-emerald-500', 'text-white');
                }
            });

            if (status.done) {
                clearInterval(pollInterval);
                if (status.error) {
                    showToast(status.message, 'error');
                    runningState.classList.add('hidden');
                    idleState.classList.remove('hidden');
                    btnRun.disabled = false;
                    btnRun.textContent = 'Run Full Analysis';
                } else {
                    await loadResults();
                }
            }
        } catch (err) {
            console.error('Poll error:', err);
        }
    }

    async function loadResults() {
        try {
            const resp = await fetch(`/api/analysis/results/${taskId}`);
            const results = await resp.json();
            runningState.classList.add('hidden');
            resultsState.classList.remove('hidden');
            renderResults(results);
            showToast('Analysis complete!', 'success');
        } catch (err) {
            showToast('Failed to load results', 'error');
        }
    }

    function chartImg(chartName, container) {
        const url = `/api/analysis/chart/${taskId}/${chartName}`;
        const div = document.createElement('div');
        div.className = 'cursor-pointer hover:opacity-90 transition';
        div.innerHTML = `<img src="${url}" class="rounded-lg shadow border" loading="lazy">`;
        div.addEventListener('click', () => {
            document.getElementById('modal-img').src = url;
            document.getElementById('img-modal').classList.remove('hidden');
        });
        container.appendChild(div);
    }

    function renderResults(results) {
        const edaContainer = document.getElementById('eda-charts');
        const edaCharts = results.charts.filter(c => {
            const num = parseInt(c.split('_')[0]);
            return num <= 10 || num === 20;
        });
        edaCharts.forEach(c => chartImg(c, edaContainer));

        // Classification table
        const classBody = document.querySelector('#class-table tbody');
        const bestClf = results.summary.best_classification_model;
        for (const [name, m] of Object.entries(results.classification)) {
            const isBest = name === bestClf;
            const row = document.createElement('tr');
            row.className = isBest ? 'bg-green-50 font-semibold' : 'hover:bg-gray-50';
            row.innerHTML = `<td class="px-4 py-2 border">${name}${isBest ? ' ★' : ''}</td>
                <td class="px-4 py-2 border text-center">${m.Accuracy}</td>
                <td class="px-4 py-2 border text-center">${m.Precision}</td>
                <td class="px-4 py-2 border text-center">${m.Recall}</td>
                <td class="px-4 py-2 border text-center">${m['F1-Score']}</td>
                <td class="px-4 py-2 border text-center">${m['AUC-ROC']}</td>
                <td class="px-4 py-2 border text-center">${m['CV Accuracy']}</td>`;
            classBody.appendChild(row);
        }

        // Classification charts (11-14)
        const classCharts = document.getElementById('class-charts');
        results.charts.filter(c => { const n = parseInt(c.split('_')[0]); return n >= 11 && n <= 14; })
            .forEach(c => chartImg(c, classCharts));

        // Regression table
        const regBody = document.querySelector('#reg-table tbody');
        const bestReg = results.summary.best_regression_model;
        for (const [name, m] of Object.entries(results.regression)) {
            const isBest = name === bestReg;
            const row = document.createElement('tr');
            row.className = isBest ? 'bg-green-50 font-semibold' : 'hover:bg-gray-50';
            row.innerHTML = `<td class="px-4 py-2 border">${name}${isBest ? ' ★' : ''}</td>
                <td class="px-4 py-2 border text-center">${m['R2 Score']}</td>
                <td class="px-4 py-2 border text-center">${m.MAE}</td>
                <td class="px-4 py-2 border text-center">${m.RMSE}</td>
                <td class="px-4 py-2 border text-center">${m['CV R2']}</td>`;
            regBody.appendChild(row);
        }

        // Regression charts (15-19)
        const regCharts = document.getElementById('reg-charts');
        results.charts.filter(c => { const n = parseInt(c.split('_')[0]); return n >= 15 && n <= 19; })
            .forEach(c => chartImg(c, regCharts));

        // Insights
        const insightsDiv = document.getElementById('insights-content');
        const summary = results.summary;
        insightsDiv.innerHTML = `
            <div class="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                <h4 class="font-bold text-emerald-700 mb-2">Best Models</h4>
                <p class="text-sm">Classification: <strong>${summary.best_classification_model}</strong> (Accuracy: ${(summary.best_classification_accuracy * 100).toFixed(2)}%, AUC: ${summary.best_classification_auc})</p>
                <p class="text-sm">Regression: <strong>${summary.best_regression_model}</strong> (R²: ${summary.best_regression_r2}, MAE: ${summary.best_regression_mae} LPA)</p>
            </div>
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 class="font-bold text-blue-700 mb-2">Top Features</h4>
                <p class="text-sm mb-1"><strong>Classification:</strong> ${summary.top5_classification_features.join(', ')}</p>
                <p class="text-sm"><strong>Salary Prediction:</strong> ${summary.top5_regression_features.join(', ')}</p>
            </div>
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 class="font-bold text-gray-700 mb-2">Key Insights</h4>
                <ul class="list-disc list-inside text-sm space-y-1">
                    ${summary.insights.map(i => `<li>${i}</li>`).join('')}
                </ul>
            </div>
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 class="font-bold text-yellow-700 mb-2">Recommendations</h4>
                <ul class="list-disc list-inside text-sm space-y-1">
                    ${summary.recommendations.map(r => `<li>${r}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    document.getElementById('btn-download-report').addEventListener('click', () => {
        if (taskId) window.open(`/api/analysis/pdf/${taskId}`, '_blank');
    });
});
