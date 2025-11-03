const apiBaseUrl = 'http://127.0.0.1:8000/api/items/'; // Your API endpoint

// Function to fetch and display items
async function fetchItems() {
    try {
        const response = await fetch(apiBaseUrl);
        const items = await response.json();
        const itemsList = document.getElementById('items-list');
        itemsList.innerHTML = ''; // Clear existing items

        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item.name;
            itemsList.appendChild(li);
        });
    } catch (error) {
        console.error('Error fetching items:', error);
    }
}

// Function to add a new item
async function addItem(name) {
    try {
        const response = await fetch(apiBaseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name }),
        });

        if (response.ok) {
            fetchItems(); // Refresh the list after a successful addition
            document.getElementById('name-input').value = ''; // Clear the input field
        } else {
            console.error('Error adding item:', response.statusText);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
}

// Event listener for the form submission
document.getElementById('add-item-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const nameInput = document.getElementById('name-input');
    if (nameInput.value) {
        addItem(nameInput.value);
    }
});

// Initial fetch when the page loads
document.addEventListener('DOMContentLoaded', fetchItems);