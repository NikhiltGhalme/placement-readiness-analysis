document.addEventListener('DOMContentLoaded', () => {
    let currentStep = 1;
    const totalSteps = 5;
    const form = document.getElementById('readiness-form');
    const steps = document.querySelectorAll('.wizard-step');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnSubmit = document.getElementById('btn-submit');
    const progressBar = document.getElementById('progress-bar');
    const stepLabels = document.querySelectorAll('.step-label');
    let sessionId = null;

    function showStep(step) {
        steps.forEach(s => s.classList.add('hidden'));
        document.querySelector(`.wizard-step[data-step="${step}"]`).classList.remove('hidden');
        btnPrev.classList.toggle('hidden', step === 1);
        btnNext.classList.toggle('hidden', step === totalSteps);
        btnSubmit.classList.toggle('hidden', step !== totalSteps);
        progressBar.style.width = `${(step / totalSteps) * 100}%`;
        stepLabels.forEach(l => {
            const s = parseInt(l.dataset.step);
            l.classList.toggle('text-indigo-600', s <= step);
            l.classList.toggle('text-gray-400', s > step);
        });
    }

    function validateCurrentStep() {
        const stepEl = document.querySelector(`.wizard-step[data-step="${currentStep}"]`);
        const inputs = stepEl.querySelectorAll('[required]');
        for (const input of inputs) {
            if (input.type === 'radio') {
                const name = input.name;
                if (!stepEl.querySelector(`input[name="${name}"]:checked`)) {
                    showToast(`Please select a value for ${name}`, 'error');
                    return false;
                }
            } else if (!input.value) {
                input.focus();
                showToast('Please fill all required fields', 'error');
                return false;
            }
        }
        return true;
    }

    btnNext.addEventListener('click', () => {
        if (validateCurrentStep() && currentStep < totalSteps) {
            currentStep++;
            showStep(currentStep);
        }
    });

    btnPrev.addEventListener('click', () => {
        if (currentStep > 1) {
            currentStep--;
            showStep(currentStep);
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!validateCurrentStep()) return;

        const submitText = document.getElementById('submit-text');
        const submitLoader = document.getElementById('submit-loader');
        submitText.classList.add('hidden');
        submitLoader.classList.remove('hidden');
        btnSubmit.disabled = true;

        // Gather languages from checkboxes
        const langs = Array.from(document.querySelectorAll('input[name="lang"]:checked')).map(c => c.value);

        const data = {
            name: form.name.value,
            branch: form.branch.value,
            year: form.year.value,
            cgpa: parseFloat(form.cgpa.value),
            pct_12: parseFloat(form.pct_12.value),
            pct_10: parseFloat(form.pct_10.value),
            dsa: parseInt(form.dsa.value),
            oops: parseInt(form.oops.value),
            coding_solved: form.coding_solved.value,
            languages: langs.length > 0 ? langs.join(', ') : 'None',
            backend: form.backend.value,
            frontend: form.frontend.value,
            database: form.database.value,
            system_design: form.system_design.value,
            fullstack_project: form.fullstack_project.value,
            projects: form.projects.value,
            internship: form.internship.value,
            opensource: form.opensource.value,
            communication: parseInt(form.communication.value),
            english: parseInt(form.english.value),
            confidence: parseInt(form.confidence.value),
            mock_interviews: form.mock_interviews.value,
            expected_salary: parseFloat(form.expected_salary.value),
            applying: form.applying.value,
        };

        try {
            const resp = await fetch('/api/readiness/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            const result = await resp.json();
            if (result.error) {
                showToast(result.error, 'error');
            } else {
                sessionId = result.session_id;
                renderResults(result);
                showToast('Report generated successfully!', 'success');
            }
        } catch (err) {
            showToast('Error: ' + err.message, 'error');
        } finally {
            submitText.classList.remove('hidden');
            submitLoader.classList.add('hidden');
            btnSubmit.disabled = false;
        }
    });

    document.getElementById('btn-download-pdf').addEventListener('click', () => {
        if (sessionId) window.open(`/api/readiness/pdf/${sessionId}`, '_blank');
    });

    function renderResults(result) {
        const analysis = result.analysis;
        const comparison = result.comparison;

        document.getElementById('results-section').classList.remove('hidden');
        document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });

        // Score gauge
        const score = analysis.overall_score;
        document.getElementById('score-number').textContent = score + '%';
        const gaugeCtx = document.getElementById('score-gauge').getContext('2d');
        const scoreColor = score >= 75 ? '#22c55e' : score >= 55 ? '#f59e0b' : score >= 35 ? '#f97316' : '#ef4444';

        if (window._gaugeChart) window._gaugeChart.destroy();
        window._gaugeChart = new Chart(gaugeCtx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [scoreColor, '#e5e7eb'],
                    borderWidth: 0,
                }]
            },
            options: {
                cutout: '75%',
                responsive: true,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                rotation: -90,
                circumference: 180,
            }
        });

        // Badge
        const badge = document.getElementById('prediction-badge');
        const level = analysis.predicted_placement;
        const badgeColors = { HIGH: 'bg-green-500', MODERATE: 'bg-yellow-500', LOW: 'bg-orange-500', 'VERY LOW': 'bg-red-500' };
        badge.className = `inline-block px-6 py-2 rounded-full text-white font-bold text-lg ${badgeColors[level]}`;
        badge.textContent = `${level} Chance of Placement`;

        // Salary
        document.getElementById('salary-range').textContent =
            `Estimated Salary: ${analysis.salary_range[0].toFixed(1)} - ${analysis.salary_range[1].toFixed(1)} LPA`;

        // Category Chart
        const categories = Object.keys(analysis.scores);
        const catScores = categories.map(c => analysis.scores[c].score);
        const catCtx = document.getElementById('category-chart').getContext('2d');
        if (window._catChart) window._catChart.destroy();
        window._catChart = new Chart(catCtx, {
            type: 'bar',
            data: {
                labels: categories,
                datasets: [{
                    label: 'Score',
                    data: catScores,
                    backgroundColor: ['#6366f1', '#22c55e', '#f59e0b', '#ef4444'],
                    borderRadius: 6,
                }]
            },
            options: {
                indexAxis: 'y',
                scales: { x: { max: 100, beginAtZero: true } },
                plugins: { legend: { display: false } },
            }
        });

        // Strengths
        const sList = document.getElementById('strengths-list');
        sList.innerHTML = analysis.strengths.length
            ? analysis.strengths.map(s => `<li class="flex items-start"><span class="text-green-500 mr-2 mt-0.5 font-bold">+</span><span>${s}</span></li>`).join('')
            : '<li class="text-gray-500">No notable strengths identified yet. Keep working!</li>';

        // Weaknesses
        const wList = document.getElementById('weaknesses-list');
        wList.innerHTML = analysis.weaknesses.length
            ? analysis.weaknesses.map(w => `<li class="flex items-start"><span class="text-red-500 mr-2 mt-0.5 font-bold">!</span><span>${w}</span></li>`).join('')
            : '<li class="text-gray-500">No major concerns. Great job!</li>';

        // Suggestions
        const sugList = document.getElementById('suggestions-list');
        sugList.innerHTML = analysis.suggestions.map((s, i) => `
            <details class="border border-gray-200 rounded-lg">
                <summary class="px-4 py-3 cursor-pointer font-medium text-gray-700 hover:bg-gray-50">[${i + 1}] ${s.title}</summary>
                <div class="px-4 py-3 text-gray-600 border-t bg-gray-50">${s.text}</div>
            </details>
        `).join('');
        if (!analysis.suggestions.length) {
            sugList.innerHTML = '<p class="text-gray-500">Great job! You\'re well-prepared. Keep practicing and stay consistent.</p>';
        }

        // Comparison Chart
        const compCtx = document.getElementById('comparison-chart').getContext('2d');
        const compLabels = ['CGPA', 'DSA', 'Communication', 'Confidence'];
        const yourVals = [comparison.cgpa.yours, comparison.dsa.yours, comparison.communication.yours, comparison.confidence.yours];
        const placedVals = [comparison.cgpa.placed_avg, comparison.dsa.placed_avg, comparison.communication.placed_avg, comparison.confidence.placed_avg];
        if (window._compChart) window._compChart.destroy();
        window._compChart = new Chart(compCtx, {
            type: 'bar',
            data: {
                labels: compLabels,
                datasets: [
                    { label: 'Your Score', data: yourVals, backgroundColor: '#6366f1' },
                    { label: 'Placed Average', data: placedVals, backgroundColor: '#22c55e' },
                ]
            },
            options: { plugins: { legend: { position: 'top' } } }
        });

        // Priorities
        const pList = document.getElementById('priorities-list');
        pList.innerHTML = analysis.priorities.map(p => `<li>${p}</li>`).join('');
        if (!analysis.priorities.length) {
            pList.innerHTML = '<li>You\'re on the right track! Keep going.</li>';
        }
    }
});
