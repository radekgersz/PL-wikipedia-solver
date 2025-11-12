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


// --- Your existing path-finding function ---
async function findShortestPath() {
    const start = document.getElementById('start').value;
    const end = document.getElementById('end').value;

    const res = await fetch('/find', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ start, end })
    });

    const data = await res.json();
    const resultEl = document.getElementById('result');
    resultEl.innerHTML = ''; // clear previous result

    if (!data.path || data.path.length === 0) {
        resultEl.textContent = data.message;
        return;
    }

    // Create clickable links with arrows
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

        resultEl.appendChild(link);

        if (i < data.path.length - 1) {
            const arrow = document.createElement('span');
            arrow.textContent = '  --->  ';
            resultEl.appendChild(arrow);
        }
    });
}

