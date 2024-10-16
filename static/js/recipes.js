// JavaScript to handle recipe suggestions
document.addEventListener('DOMContentLoaded', () => {
    const recipeList = document.getElementById('recipe-list');

    // Example food items (replace with actual data from your warehouse)
    const availableFoods = [
        { name: 'Apple', expiry_date: '2023-10-10' },
        { name: 'Banana', expiry_date: '2023-10-12' },
        { name: 'Carrot', expiry_date: '2023-10-15' }
    ];

    // Example recipes (replace with actual recipe logic)
    const recipes = [
        {
            name: 'Fruit Salad',
            ingredients: ['Apple', 'Banana'],
            instructions: 'Mix all the fruits together and serve chilled.'
        },
        {
            name: 'Carrot Soup',
            ingredients: ['Carrot'],
            instructions: 'Boil carrots and blend them to make a soup.'
        }
    ];

    // Function to suggest recipes based on available foods
    function suggestRecipes(availableFoods, recipes) {
        const suggestedRecipes = recipes.filter(recipe => {
            return recipe.ingredients.every(ingredient => {
                return availableFoods.some(food => food.name === ingredient);
            });
        });

        return suggestedRecipes;
    }

    // Display suggested recipes
    function displayRecipes(recipes) {
        recipeList.innerHTML = '';
        recipes.forEach(recipe => {
            const div = document.createElement('div');
            div.className = 'recipe';
            div.innerHTML = `
                <h3>${recipe.name}</h3>
                <p><strong>Ingredients:</strong> ${recipe.ingredients.join(', ')}</p>
                <p><strong>Instructions:</strong> ${recipe.instructions}</p>
            `;
            recipeList.appendChild(div);
        });
    }

    const suggestedRecipes = suggestRecipes(availableFoods, recipes);
    displayRecipes(suggestedRecipes);
});