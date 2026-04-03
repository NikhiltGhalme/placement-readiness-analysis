document.addEventListener('DOMContentLoaded', () => {
    let downloadFilename = null;

    document.getElementById('btn-generate').addEventListener('click', async () => {
        const n = parseInt(document.getElementById('n-records').value);
        const seed = parseInt(document.getElementById('seed').value);

        const genText = document.getElementById('gen-text');
        const genLoader = document.getElementById('gen-loader');
        const btn = document.getElementById('btn-generate');

        genText.classList.add('hidden');
        genLoader.classList.remove('hidden');
        btn.disabled = true;

        try {
            const resp = await fetch('/api/generator/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ n_records: n, seed: seed }),
            });
            const data = await resp.json();

            if (data.error) {
                showToast(data.error, 'error');
                return;
            }

            downloadFilename = data.filename;

            document.getElementById('total-count').textContent = data.total_records;
            document.getElementById('placed-count').textContent = data.placed;
            document.getElementById('unplaced-count').textContent = data.unplaced;

            const branchDiv = document.getElementById('branch-dist');
            branchDiv.innerHTML = Object.entries(data.branch_distribution).map(([k, v]) =>
                `<div class="bg-gray-100 rounded px-3 py-2 text-sm"><span class="font-medium">${k}:</span> ${v}</div>`
            ).join('');

            // Preview table
            const rows = data.sample_rows;
            if (rows.length > 0) {
                const cols = Object.keys(rows[0]);
                const thead = document.querySelector('#preview-table thead');
                thead.innerHTML = `<tr>${cols.map(c => `<th class="px-2 py-1 border bg-gray-800 text-white whitespace-nowrap">${c}</th>`).join('')}</tr>`;
                const tbody = document.querySelector('#preview-table tbody');
                tbody.innerHTML = rows.map(row =>
                    `<tr class="hover:bg-gray-50">${cols.map(c => `<td class="px-2 py-1 border whitespace-nowrap">${row[c] ?? ''}</td>`).join('')}</tr>`
                ).join('');
            }

            document.getElementById('gen-results').classList.remove('hidden');
            showToast('Dataset generated successfully!', 'success');
        } catch (err) {
            showToast('Error: ' + err.message, 'error');
        } finally {
            genText.classList.remove('hidden');
            genLoader.classList.add('hidden');
            btn.disabled = false;
        }
    });

    document.getElementById('btn-download').addEventListener('click', () => {
        if (downloadFilename) {
            window.open(`/api/generator/download/${downloadFilename}`, '_blank');
        }
    });
});
