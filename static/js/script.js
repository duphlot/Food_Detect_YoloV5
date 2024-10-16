// JavaScript to handle video feed and detected foods
const video = document.getElementById('video');
video.onerror = function() {
    console.error('Failed to load video feed');
};

// Function to update detected foods
function updateDetectedFoods(foods) {
    const foodList = document.getElementById('food-list');
    foodList.innerHTML = '';
    foods.forEach(food => {
        const li = document.createElement('li');
        li.textContent = `${food.name} - Expiry: ${food.expiry_date}`;
        foodList.appendChild(li);
    });
}

// Example detected foods (replace with actual detection logic)
const detectedFoods = [
    { name: 'Apple', expiry_date: '2023-10-10' },
    { name: 'Banana', expiry_date: '2023-10-12' }
];
updateDetectedFoods(detectedFoods);