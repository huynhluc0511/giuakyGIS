// Shared Cart Utilities for FastFood Universe
// Place in {% static 'js/cart.js' %} across templates

// Cart key in localStorage
const CART_KEY = 'cart_data';

// Initialize cart badge (call on page load)
function initCartBadge(badgeSelector) {
    const badge = document.querySelector(badgeSelector);
    if (!badge) return;
    
    updateCartBadge(badge);
    // Listen for storage changes across tabs
    window.addEventListener('storage', (e) => {
        if (e.key === CART_KEY) updateCartBadge(badge);
    });
}

// Update single badge
function updateCartBadge(badgeEl) {
    const cart = getCart();
    const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
    if (totalQty > 0) {
        badgeEl.textContent = totalQty;
        badgeEl.style.visibility = 'visible';
    } else {
        badgeEl.style.visibility = 'hidden';
    }
    console.log(`Cart updated: ${totalQty} items`);
}

// Get cart from localStorage
function getCart() {
    try {
        return JSON.parse(localStorage.getItem(CART_KEY)) || [];
    } catch (e) {
        console.error('Cart read error:', e);
        return [];
    }
}

// Add/update item in cart
function addToCart(productId, name, price, img, note = '') {
    console.log(`Adding to cart: ${name} @ ${price}đ, note: ${note}`);
    
    let cart = getCart();
    const existing = cart.find(item => item.id === productId && item.note === note);
    
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({ id: productId, name, price, qty: 1, img, note });
    }
    
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    console.log(`Cart now has ${cart.length} unique items`);
    
    // Update any badges on page
    document.querySelectorAll('.cart-badge, #cart-qty').forEach(badge => {
        if (badge.textContent) updateCartBadge(badge);
    });
    
    // Success notification
    showNotification(`${name} đã được thêm vào giỏ! (+1)`);
    return cart;
}

// Remove item
function removeFromCart(productId, note = '') {
    const cart = getCart().filter(item => !(item.id === productId && item.note === note));
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
}

// Change quantity
function changeQty(productId, note = '', delta) {
    const cart = getCart();
    const item = cart.find(i => i.id === productId && i.note === note);
    if (item) {
        item.qty = Math.max(1, item.qty + delta);
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
    }
}

// Clear cart
function clearCart() {
    localStorage.removeItem(CART_KEY);
}

// Notification
function showNotification(message, duration = 3000) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px; background: linear-gradient(135deg, #2a9d8f, #1e7a6e);
        color: white; padding: 15px 25px; border-radius: 10px; font-weight: 600;
        box-shadow: 0 10px 25px rgba(42,157,143,0.3); z-index: 9999;
        transform: translateX(400px); opacity: 0; font-family: Poppins, sans-serif;
    `;
    notification.innerHTML = `<i class="fa-solid fa-check-circle"></i> ${message}`;
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 100);
    
    // Animate out
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        notification.style.opacity = '0';
        setTimeout(() => document.body.removeChild(notification), 400);
    }, duration);
}

// Debug: Log cart state
function debugCart() {
    const cart = getCart();
    console.table(cart);
    alert(`Cart has ${cart.reduce((sum, i) => sum + i.qty, 0)} items. Check console for details.`);
}

// Show order options UI (hamburger specific)
function showOptions(productId) {
    console.log(`Opening options for ${productId}`);
    const details = document.getElementById(productId);
    const addBtn = details.querySelector('.btn-add');
    
    // Close others
    document.querySelectorAll('.order-details').forEach(d => {
        if (d.id !== productId) d.classList.remove('active');
    });
    
    details.querySelector('.order-details').classList.add('active');
    addBtn.style.display = 'none';
}

// Export for global use
window.FastFoodCart = {
    initCartBadge,
    addToCart,
    removeFromCart,
    changeQty,
    clearCart,
    showNotification,
    showOptions,
    debugCart
};

