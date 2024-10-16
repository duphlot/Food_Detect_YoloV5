document.addEventListener('DOMContentLoaded', function() {
    function fetchDetectedFoods() {
        fetch('/static/data/data.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const warehouseItemsContainer = document.getElementById('warehouse-items');
                warehouseItemsContainer.innerHTML = ''; // Clear any existing content
                data.forEach(item => {
                    const itemElement = document.createElement('div');
                    itemElement.classList.add('warehouse-item');
                    itemElement.innerHTML = `
                        <h3>Name: ${item.name}</p>
                        <p>Expiry: ${item.expiry}</p>
                    `;
                    warehouseItemsContainer.appendChild(itemElement);
                });
            })
            .catch(error => console.error('Error fetching data:', error));
    }

    // Fetch detected foods when the page loads
    fetchDetectedFoods();

    // Optionally, you can set an interval to refresh the data periodically
    // setInterval(fetchDetectedFoods, 5000);
});