// --- Autocomplete setup ---

async function fetchSuggestions(query) {
    const response = await fetch(`/suggest?q=${encodeURIComponent(query)}`);
    if (!response.ok) return [];
    return await response.json();
}

function setupAutocomplete(inputId) {
    const input = document.getElementById(inputId);
    const suggestionBox = document.createElement('div');
    suggestionBox.classList.add('suggestions');
    input.parentNode.insertBefore(suggestionBox, input.nextSibling);

    input.addEventListener('input', async () => {
        const query = input.value.trim();
        suggestionBox.innerHTML = '';
        suggestionBox.classList.remove('active'); // 🔹 hide initially

        if (query.length < 1) return;

        const suggestions = await fetchSuggestions(query);
        if (suggestions.length === 0) return; // nothing to show

        suggestions.forEach(title => {
            const item = document.createElement('div');
            item.textContent = title;
            item.classList.add('suggestion-item');
            item.addEventListener('click', () => {
                input.value = title;
                suggestionBox.innerHTML = '';
                suggestionBox.classList.remove('active');
            });
            suggestionBox.appendChild(item);
        });

        suggestionBox.classList.add('active'); // 🔹 show when filled
    });

    document.addEventListener('click', (e) => {
        if (!suggestionBox.contains(e.target) && e.target !== input) {
            suggestionBox.innerHTML = '';
            suggestionBox.classList.remove('active');
        }
    });
}
// Activate autocomplete on both input fields
setupAutocomplete('start');
setupAutocomplete('end');
document.getElementById('swap-btn').addEventListener('click', () => {
    const startInput = document.getElementById('start');
    const endInput = document.getElementById('end');
    const temp = startInput.value;
    startInput.value = endInput.value;
    endInput.value = temp;
});


async function findShortestPath() {
    const start = document.getElementById('start').value.trim();
    const end = document.getElementById('end').value.trim();
    const resultEl = document.getElementById('result');
    resultEl.innerHTML = '';

    if (!start || !end) {
        resultEl.textContent = 'Please enter both start and end article titles before searching.';
        resultEl.style.color = 'red';
        return;
    }

    const res = await fetch('/find', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start, end })
    });

    const data = await res.json();

    // --- show redirect info, if any ---
    if (data.redirects && data.redirects.length > 0) {
        const infoDiv = document.createElement('div');
        infoDiv.style.color = '#666';
        infoDiv.style.fontSize = '0.95rem';
        infoDiv.style.marginBottom = '8px';
        infoDiv.innerHTML = data.redirects.join('<br>');
        resultEl.appendChild(infoDiv);
    }

    // --- handle path ---
    if (!data.path || data.path.length === 0) {
        const msg = document.createElement('div');
        msg.textContent = data.message;
        msg.style.color = '#444';
        resultEl.appendChild(msg);
        return;
    }

    const pathDiv = document.createElement('div');
    data.path.forEach((title, i) => {
        const link = document.createElement('a');
        link.href = `https://pl.wikipedia.org/wiki/${encodeURIComponent(title)}`;
        link.textContent = title;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.style.color = '#007BFF';
        link.style.textDecoration = 'none';
        link.addEventListener('mouseover', () => link.style.textDecoration = 'underline');
        link.addEventListener('mouseout', () => link.style.textDecoration = 'none');
        pathDiv.appendChild(link);

        if (i < data.path.length - 1) {
            const arrow = document.createElement('span');
            arrow.textContent = '  --->  ';
            pathDiv.appendChild(arrow);
        }
    });
    resultEl.appendChild(pathDiv);
}

