const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  // Show user message
  addMessage(message, "user");

  // Clear input
  userInput.value = "";

  try {
    // Call backend API
    const response = await fetch(
      `http://127.0.0.1:8000/api/api/ask_product?query=${encodeURIComponent(message)}`
    );
    const data = await response.json();

    // Handle bot response
    if (data && data.answer) {
      renderBotResponse(data.answer);
    } else {
      addMessage("⚠️ Sorry, I couldn’t fetch product info.", "bot");
    }
  } catch (error) {
    console.error("Error:", error);
    addMessage("❌ Server error. Please try again.", "bot");
  }
}

function addMessage(text, sender) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add(sender === "user" ? "user-message" : "bot-message");
  messageDiv.innerText = text;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Render bot response with product cards if image links exist
function renderBotResponse(text) {
  // Regex to find markdown-style image links
  const regex = /\[(.*?)\]\((https?:\/\/[^\s)]+)\)/g;

  // If no images, just render text
  if (!regex.test(text)) {
    addMessage(text, "bot");
    return;
  }

  // Reset regex (since .test advances it)
  const matches = [...text.matchAll(regex)];

  // Extract products
  matches.forEach(match => {
    const productName = match[1];
    const imageUrl = match[2];

    const productCard = document.createElement("div");
    productCard.classList.add("product-card");

    productCard.innerHTML = `
      <img src="${imageUrl}" alt="${productName}">
      <div class="product-info">
        <h4>${productName}</h4>
        <p>Click to view more details</p>
      </div>
    `;

    chatBox.appendChild(productCard);
  });

  chatBox.scrollTop = chatBox.scrollHeight;
}
