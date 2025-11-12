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

        if (query.length < 2) return;

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
    document.getElementById('result').textContent = data.message;
}
