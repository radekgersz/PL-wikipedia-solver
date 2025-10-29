async function findShortestPath() {
    const start = document.getElementById('start').value;
    const end = document.getElementById('end').value;
    const res = await fetch('/find', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({start, end})
    });
    const data = await res.json();
    document.getElementById('result').textContent = data.message;
}